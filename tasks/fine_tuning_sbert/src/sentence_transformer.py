"""
Refactoring the sentence transformer model.fit() function for our purpose here
Implementing the Early Stopping feature that will be useful for us

Original source code: https://github.com/UKPLab/sentence-transformers/blob/master/sentence_transformers/SentenceTransformer.py#L434
"""

from typing import Iterable, Dict, Tuple, Type, Callable
import os
import transformers
import wandb
from sentence_transformers import SentenceTransformer

from sentence_transformers.evaluation import LabelAccuracyEvaluator, SentenceEvaluator
from torch import nn
import torch
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from tqdm.autonotebook import trange
from statistics import mean


class EarlyStoppingSentenceTransformer(SentenceTransformer):

    def fit(self,
            train_objectives: Iterable[Tuple[DataLoader, nn.Module]],
            evaluator: SentenceEvaluator = None,
            epochs: int = 1,
            steps_per_epoch=None,
            scheduler: str = 'WarmupLinear',
            warmup_steps: int = 10000,
            optimizer_class: Type[Optimizer] = transformers.AdamW,
            optimizer_params: Dict[str, object] = {
                'lr': 2e-5, 'correct_bias': True},
            weight_decay: float = 0.01,
            evaluation_steps: int = 0,
            output_path: str = None,
            save_best_model: bool = True,
            max_grad_norm: float = 1,
            use_amp: bool = False,
            callback: Callable[[float, int, int], None] = None,
            show_progress_bar: bool = True,
            baseline: float = 0.01,
            patience: int = 5,
            ):
        """
        Train the model with the given training objective
        Each training objective is sampled in turn for one batch.
        We sample only as many batches from each objective as there are in the smallest one
        to make sure of equal training with each dataset.
        :param train_objectives: Tuples of (DataLoader, LossFunction). Pass more than one for multi-task learning
        :param evaluator: An evaluator (sentence_transformers.evaluation) evaluates the model performance during training on held-out dev data. It is used to determine the best model that is saved to disc.
        :param epochs: Number of epochs for training
        :param steps_per_epoch: Number of training steps per epoch. If set to None (default), one epoch is equal the DataLoader size from train_objectives.
        :param scheduler: Learning rate scheduler. Available schedulers: constantlr, warmupconstant, warmuplinear, warmupcosine, warmupcosinewithhardrestarts
        :param warmup_steps: Behavior depends on the scheduler. For WarmupLinear (default), the learning rate is increased from o up to the maximal learning rate. After these many training steps, the learning rate is decreased linearly back to zero.
        :param optimizer_class: Optimizer
        :param optimizer_params: Optimizer parameters
        :param weight_decay: Weight decay for model parameters
        :param evaluation_steps: If > 0, evaluate the model using evaluator after each number of training steps
        :param output_path: Storage path for the model and evaluation files
        :param save_best_model: If true, the best model (according to evaluator) is stored at output_path
        :param max_grad_norm: Used for gradient normalization.
        :param use_amp: Use Automatic Mixed Precision (AMP). Only for Pytorch >= 1.6.0
        :param callback: Callback function that is invoked after each evaluation.
                It must accept the following three parameters in this order:
                `score`, `epoch`, `steps`
        :param show_progress_bar: If True, output a tqdm progress bar
        :param baseline: minimum improvement in the accuracy for a new model to be saved and best_score to be updated
        :param patience: maximum number of epochs to go without an improvement in the accuracy
        """
        self.acc_list = [1e-6]  # stores the accuracy while training
        training_acc_list = []

        t_evaluator = LabelAccuracyEvaluator(dataloader=train_objectives[0][0], softmax_model=train_objectives[0][1],
                                             name='lae-training')

        self.baseline = baseline
        self.patience = patience

        if use_amp:
            from torch.cuda.amp import autocast
            scaler = torch.cuda.amp.GradScaler()

        self.to(self._target_device)

        if output_path is not None:
            os.makedirs(output_path, exist_ok=True)

        dataloaders = [dataloader for dataloader, _ in train_objectives]

        # Use smart batching
        for dataloader in dataloaders:
            dataloader.collate_fn = self.smart_batching_collate

        loss_models = [loss for _, loss in train_objectives]
        for loss_model in loss_models:
            loss_model.to(self._target_device)

        self.best_score = -9999999

        if steps_per_epoch is None or steps_per_epoch == 0:
            steps_per_epoch = min([len(dataloader)
                                  for dataloader in dataloaders])

        num_train_steps = int(steps_per_epoch * epochs)

        # Prepare optimizers
        optimizers = []
        schedulers = []
        for loss_model in loss_models:
            param_optimizer = list(loss_model.named_parameters())

            no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
            optimizer_grouped_parameters = [
                {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
                 'weight_decay': weight_decay},
                {'params': [p for n, p in param_optimizer if any(
                    nd in n for nd in no_decay)], 'weight_decay': 0.0}
            ]

            optimizer = optimizer_class(
                optimizer_grouped_parameters, **optimizer_params)
            scheduler_obj = self._get_scheduler(optimizer, scheduler=scheduler, warmup_steps=warmup_steps,
                                                t_total=num_train_steps)

            optimizers.append(optimizer)
            schedulers.append(scheduler_obj)

        global_step = 0
        data_iterators = [iter(dataloader) for dataloader in dataloaders]

        num_train_objectives = len(train_objectives)

        skip_scheduler = False
        for epoch in trange(epochs, desc="Epoch", disable=not show_progress_bar):
            training_steps = 0

            for loss_model in loss_models:
                loss_model.zero_grad()
                loss_model.train()

            for _ in trange(steps_per_epoch, desc="Iteration", smoothing=0.05, disable=not show_progress_bar):
                for train_idx in range(num_train_objectives):
                    loss_model = loss_models[train_idx]
                    optimizer = optimizers[train_idx]
                    scheduler = schedulers[train_idx]
                    data_iterator = data_iterators[train_idx]

                    try:
                        data = next(data_iterator)
                    except StopIteration:
                        data_iterator = iter(dataloaders[train_idx])
                        data_iterators[train_idx] = data_iterator
                        data = next(data_iterator)

                    features, labels = data

                    if use_amp:
                        with autocast():
                            loss_value = loss_model(features, labels)

                        scale_before_step = scaler.get_scale()
                        scaler.scale(loss_value).backward()
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            loss_model.parameters(), max_grad_norm)
                        scaler.step(optimizer)
                        scaler.update()

                        skip_scheduler = scaler.get_scale() != scale_before_step
                    else:
                        loss_value = loss_model(features, labels)
                        loss_value.backward()
                        torch.nn.utils.clip_grad_norm_(
                            loss_model.parameters(), max_grad_norm)
                        optimizer.step()

                    optimizer.zero_grad()

                    if not skip_scheduler:
                        scheduler.step()

                training_steps += 1
                global_step += 1

                if evaluation_steps > 0 and training_steps % evaluation_steps == 0:
                    for loss_model in loss_models:
                        loss_model.zero_grad()
                        loss_model.train()

            # training evaluation
            training_acc_evaluated = t_evaluator(
                self, output_path=output_path, epoch=epoch, steps=-1)
            training_acc_list.append(training_acc_evaluated)

            wandb.log({"train_acc": training_acc_evaluated,
                      "epoch": epoch})

            # validation evaluation
            flag = self._eval_during_training(
                evaluator, output_path, save_best_model, epoch, -1, callback)

            if flag is True:
                print(f'Epoch: {epoch}')
                print(f"Best score: {self.best_score}")
                print('=' * 60)
            else:
                print('TRAINING EXITED. Best model has been found.')
                print(f'Epoch: {epoch}')
                print(f"Best score: {self.best_score}")
                print('=' * 60)
                return

            # removing the unnecessary first element in ACC_LIST that needed to be there for epoch 1
            if epoch == 0:
                del self.acc_list[0]

        # No evaluator, but output path: save final model version
        if evaluator is None and output_path is not None:
            self.save(output_path)

    def _eval_during_training(self, evaluator, output_path, epoch, steps):
        """Runs evaluation during the training"""

        score_dict = evaluator(self, epoch=epoch, steps=steps)

        score = score_dict["accuracy"]
        self.acc_list.append(score)

        wandb.log({"validation_acc": score, "epoch": epoch})
        wandb.log(
            {"Macro F1 validation": score_dict['macro_f1'], "epoch": epoch})
        wandb.log(
            {"Weighted F1 validation": score_dict['weighted_f1'], "epoch": epoch})

        prev_score = self.acc_list[-2]
        moving_average = mean(self.acc_list[-self.patience - 1: -1])

        print(
            f"{'=' * 60}\nCurrent Score is: {score}\nCurrent ACC_LIST is: {self.acc_list}")

        if score >= moving_average or len(
                self.acc_list) - 1 <= self.patience:  # score is >= the moving average in the last PATIENCE values
            if score > prev_score and score - prev_score >= self.baseline:  # better score
                if score > self.best_score:  # checking for local maxima
                    self.best_score = score
                    self.save(output_path)
                return True  # continue training whether this is local maxima or not
            elif score >= prev_score and score - prev_score < self.baseline:
                if score > self.best_score:  # checking for local maxima
                    self.best_score = score
                    self.save(output_path)
                return False  # end training whether this is local maxima or not, no more training happening after this plateau
            else:
                # if current score < previous score
                return True  # do not save the model but continue training
        else:
            print(
                f'Current score ({score}) less than moving average ({moving_average})')
            return False  # if this accuracy is less than moving average, we do not want to save the weights of this epoch
