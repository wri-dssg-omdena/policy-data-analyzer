import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_curve, f1_score, accuracy_score, precision_score, \
    recall_score, average_precision_score
from sklearn.preprocessing import label_binarize
import numpy as np
import matplotlib.pyplot as plt
import itertools
from itertools import cycle
import matplotlib.colors as mcolors

import sys

sys.path.append("../../")

METRICS = ["Precision", "Recall (Sensitivity)", "True negative rate (Specificity)", "F1-score"]


class ModelEvaluator:
    def __init__(self, label_names, output_path="../output/", y_true=None, y_pred=None):
        self.label_names = label_names
        self.df_indices = label_names + ["Macro avg", "Weighted avg"]
        self.output_path = output_path
        self.n_classes = len(label_names)

        if y_true is not None and y_pred is not None:
            self.update(y_true, y_pred)

    def update(self, y_true, y_pred):
        """
        Given a set of true labels and model predictions, calculate and store the following metrics:
            - Confusion matrix
            - FP: Number of false positives
            - FN: Number of false negatives
            - TP: Number of true positives
            - TN: Number of true negatives
            - Recall
            - Specificity
            - Precision
            - F1-score
            - Accuracy
            - FDR: False discovery rate
            - NPV: Negative predictive value
            - FPR: False positive rate
            - False negative rate
        """
        # Ignore division by 0 errors
        settings = np.seterr(divide='ignore', invalid='ignore')

        # ---- Set up raw components ----
        self.cm = confusion_matrix(y_true, y_pred)
        self.FP = self.cm.sum(axis=0) - np.diag(self.cm)
        self.FN = self.cm.sum(axis=1) - np.diag(self.cm)
        self.TP = np.diag(self.cm)
        self.TN = self.cm.sum() - (self.FP + self.FN + self.TP)

        # ---- Useful metrics at the class level ----
        self.recall = self.TP / (self.TP + self.FN)
        self.specificity = self.TN / (self.TN + self.FP)
        self.precision = self.TP / (self.TP + self.FP)
        self.f1 = (2 * self.precision * self.recall) / (self.precision + self.recall)

        # ---- Useful metrics across all classes ----
        self.avg_precision = np.array(
            [precision_score(y_true, y_pred, average='macro'), precision_score(y_true, y_pred, average='weighted')])
        self.avg_recall = np.array(
            [recall_score(y_true, y_pred, average='macro'), recall_score(y_true, y_pred, average='weighted')])
        self.avg_specificity = np.array([np.mean(self.specificity), self.weighted_avg(self.specificity, y_true, )])
        self.avg_f1 = np.array(
            [f1_score(y_true, y_pred, average='macro'), f1_score(y_true, y_pred, average='weighted')])
        self.accuracy = accuracy_score(y_true, y_pred)
        self.acc = np.array(["-----", "-----", "-----", self.accuracy])

        # ---- Extra metrics at the class level ----
        self.FDR = self.FP / (self.TP + self.FP)  # False discovery rate
        self.NPV = self.TN / (self.TN + self.FN)  # Negative predictive value
        self.FPR = self.FP / (self.FP + self.TN)  # Fall out or false positive rate
        self.FNR = self.FN / (self.TP + self.FN)  # False negative rate


    def evaluate(self, y_true, y_pred, plot_cm=False, normalize=False, exp_name=None):
        """
        Given a set of true labels and model predictions, runs a series of selected evaluation metrics:
            - Precision
            - Recall (Sensitivity)
            - Accuracy
            - Specificity
            - Confusion matrix
            - Precision-Recall curve

        Parameters:
            `plot_cm`: (boolean) Plot confusion matrix
            `plot_prc`: (boolean) Plot precision-recall curve (averaged for all classes)
            `plot_prc_multi`: (boolean) Plot the multi-class version of the precision-recall curve (`plot_prc` MUST be `True` if this is set to `True`)
            `normalize`: (boolean) Normalize the confusion matrix content
            `store`: (boolean) Store the plots and the results dataframe. If this is set to `True`, then `exp_name` MUST have a value and it can't be None. The files will be stored in the `model_evaluation/output/` folder.
            `exp_name`: (str) The name of the model or the experiment, useful if we will want to store files (e.g `test_BETO_1`).
        """

        self.update(y_true, y_pred)

        data = np.stack((self.precision, self.recall, self.specificity, self.f1)).T
        avgs = np.array([self.avg_precision, self.avg_recall, self.avg_specificity, self.avg_f1]).T
        data_with_avgs = np.concatenate((data, avgs))

        metrics_df = pd.DataFrame(data_with_avgs, index=self.df_indices, columns=METRICS)
        metrics_df = metrics_df.applymap(lambda x: round(x, 2))
        metrics_df.loc['Accuracy'] = self.acc

        line = pd.DataFrame(dict(zip(METRICS, ["-----"] * len(METRICS))), index=["-----"])
        metrics_df = pd.concat([metrics_df.iloc[:self.n_classes], line, metrics_df.iloc[self.n_classes:]])
        self.metrics_df = metrics_df.fillna(0)

        if plot_cm:
            self.plot_confusion_matrix(color_map="Blues",
                                       normalize=normalize,
                                       exp_name=f"{self.output_path}{exp_name}")

        if exp_name:
            fname = f"{self.output_path + exp_name}_results.csv"
            self.metrics_df.to_csv(fname)
            print(f"Stored results: {fname}")

        return self.metrics_df

    def get_counts_per_label(self, y_true):
        """
        Return a map of {label: number of data points with that label} for the given list of labels

        Parameters:
            - y_true: a list of labels (integers)
        """
        label_counts = [0] * self.n_classes
        for label in y_true:
            label_counts[label] += 1
        return label_counts

    def weighted_avg(self, metric_array, y_true):
        """
        Given a numpy array of a particular metric for all classes (i.e precision for all classes),
        return a weighted average of the metric, where the weights are the number of data points that
        have a given label.

        Parameters:
            - metric array: a 1D-numpy array of floats representing metrics
            - y_true: a list of labels (integers)
        """
        weights = self.get_counts_per_label(y_true)
        weighted_metrics = sum(metric_array * weights)
        return weighted_metrics / len(y_true)


    def plot_confusion_matrix(self, title='Confusion matrix',
                              color_map=None,
                              normalize=True,
                              exp_name=None):
        """
        Adapted from: https://stackoverflow.com/questions/19233771/sklearn-plot-confusion-matrix-with-labels
        """
        if color_map is None:
            color_map = plt.get_cmap('Blues')

        plt.figure(figsize=(8, 6))
        plt.imshow(self.cm, interpolation='nearest', cmap=color_map)

        plt.title(title)
        plt.colorbar()
        plt.style.use('seaborn-white')

        if self.label_names:
            tick_marks = np.arange(len(self.label_names))
            plt.xticks(tick_marks, self.label_names, rotation=45)
            plt.yticks(tick_marks, self.label_names)

        if normalize:
            self.cm = self.cm.astype('float') / self.cm.sum(axis=1)[:, np.newaxis]

        thresh = self.cm.max() / 1.5 if normalize else self.cm.max() / 2
        for i, j in itertools.product(range(self.cm.shape[0]), range(self.cm.shape[1])):
            if normalize:
                plt.text(j, i, "{:0.2f}".format(self.cm[i, j]),
                         horizontalalignment="center",
                         color="white" if self.cm[i, j] > thresh else "black")
            else:
                plt.text(j, i, "{:,}".format(self.cm[i, j]),
                         horizontalalignment="center",
                         color="white" if self.cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.xlabel('Predicted label')
        plt.ylabel('True label')

        if exp_name:
            fname = f"{exp_name}_cm.png"
            plt.savefig(fname)
            print(f"Stored confusion matrix: {fname}")

        plt.show()

    def plot_precision_recall_curve(self, y_true, y_pred, bin_class=False, all_classes=False,
                                    exp_name=None):
        """
        Plots the precision-recall curve for either a binary or multi-class classification model.

        Parameters:
            y_true: (np.array[int]) The true labels for the dataset
            y_pred: If binary_class is True, y_pred should be a numpy array of floats holding the prediction probabilities,
                else y_pred should be a numpy array of ints holding the predictions themselves
            bin_class: (boolean) Whether we should plot the curve for a binary classification setting
            all_classes: (boolean) In a multi-class classification problem, whether we should plot the curve for all classes or just the average
            store: (boolean) Whether we want to store this plot or not
            exp_name: (str) The name of the experiment, used to name the file to store the plot. Requires store=True
        """

        if bin_class:
            if not isinstance(y_pred.flat[0], np.floating):
                print("Error: Array of predictions should contain probabilities [0.3, 0.75] instead of labels [0, 1] for binary classification problems.")
                return

            random_pred_precision = y_true.mean()

            precision, recall, _ = precision_recall_curve(y_true, y_pred)
            average_precision = average_precision_score(y_true, y_pred)

            plt.figure()
            plt.plot([0, 1], [random_pred_precision, random_pred_precision], linestyle='--', label='Random Prediction')
            plt.step(recall, precision, where='post')

            plt.xlabel('Recall')
            plt.ylabel('Precision')

            plt.ylim([0.0, 1.05])
            plt.xlim([0.0, 1.0])
            plt.title('Precision-Recall Curve. Avg Precision=' + str(round(average_precision, 2)))

            if exp_name:
                fname = f"{self.output_path}{exp_name}_prc.png"
                plt.savefig(fname)
                print(f"Stored Precision-Recall Curve: {fname}")

            plt.show()

        else:
            y_true_bin = label_binarize(y_true, classes=range(self.n_classes))
            y_pred_bin = label_binarize(y_pred, classes=range(self.n_classes))

            precision = dict()
            recall = dict()
            average_precision = dict()

            for i in range(self.n_classes):
                precision[i], recall[i], _ = precision_recall_curve(y_true_bin[:, i],
                                                                    y_pred_bin[:, i])
                average_precision[i] = average_precision_score(y_true_bin[:, i], y_pred_bin[:, i])

            # A "micro-average": quantifying score on all classes jointly
            precision["micro"], recall["micro"], _ = precision_recall_curve(y_true_bin.ravel(),
                                                                            y_pred_bin.ravel())
            average_precision["micro"] = average_precision_score(y_true_bin, y_pred_bin,
                                                                 average="micro")

            random_pred_precision = y_true_bin.mean()

            if all_classes:

                # Setup plot details
                colors = cycle(list(mcolors.TABLEAU_COLORS.keys()))
                plt.figure(figsize=(7, 8))
                plt.style.use('seaborn-white')

                # Plot f1 score lines
                f_scores = np.linspace(0.2, 0.8, num=4)
                lines = []
                labels = []
                for f_score in f_scores:
                    x = np.linspace(0.01, 1)
                    y = f_score * x / (2 * x - f_score)
                    l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
                    plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))

                # Plot precision-recall lines
                lines.append(l)
                labels.append('iso-f1 curves')
                l, = plt.plot(recall["micro"], precision["micro"], color='gold', lw=2)
                lines.append(l)
                labels.append('Micro-average Precision-Recall (area = {0:0.2f})'
                              ''.format(average_precision["micro"]))

                for i, color in zip(range(self.n_classes), colors):
                    l, = plt.plot(recall[i], precision[i], color=color, lw=2)
                    lines.append(l)
                    labels.append('Precision-Recall for class {0} (area = {1:0.2f})'
                                  ''.format(i, average_precision[i]))

                rand_l, = plt.plot([0, 1], [random_pred_precision, random_pred_precision], linestyle='--')
                lines.append(rand_l)
                labels.append("Precision-Recall for Random Classifier")

                # Final touches on plot
                fig = plt.gcf()
                fig.subplots_adjust(bottom=0.25)
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('Recall')
                plt.ylabel('Precision')
                plt.title('Multiclass Precision-Recall Curve')
                plt.legend(lines, labels, loc=(0, -.68), prop=dict(size=14))

                if exp_name:
                    fname = f"{self.output_path}{exp_name}_prc.png"
                    plt.savefig(fname)
                    print(f"Stored Precision-Recall Curve: {fname}")
                plt.show()

            else:
                plt.figure()
                plt.plot([0, 1], [random_pred_precision, random_pred_precision], linestyle='--', label='Random Prediction')
                plt.step(recall["micro"], precision["micro"], where='post')

                plt.xlabel('Recall')
                plt.ylabel('Precision')

                plt.ylim([0.0, 1.05])
                plt.xlim([0.0, 1.0])
                plt.title('Averaged Precision-Recall Curve')

                if exp_name:
                    fname = f"{self.output_path}{exp_name}_prc.png"
                    plt.savefig(fname)
                    print(f"Stored Precision-Recall Curve: {fname}")

                plt.show()

    def plot_data_distribution(self, data, normalize=True):
        weights = np.array(self.get_counts_per_label(data))
        if normalize:
            weights = weights / sum(weights)

        plt.bar(self.label_names, weights)
        plt.xticks(self.label_names, rotation=90)
        plt.title("Data Distribution")
        plt.xlabel("Label")
        plt.ylabel("Percentage of label in data")
        plt.show()

        print("Label counts:")
        print(dict(zip(self.label_names, weights)))
