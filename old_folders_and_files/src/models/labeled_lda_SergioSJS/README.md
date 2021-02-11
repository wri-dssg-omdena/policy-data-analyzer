## Implement of L-LDA Model(Labeled Latent Dirichlet Allocation Model) with python

Copied from [SergioSJS/labeled_lda](https://github.com/SergioSJS/labeled_lda)

References:
   * *RAMAGE, Daniel et al. Labeled LDA: A supervised topic model for credit attribution in multi-labeled corpora. In: Proceedings of the 2009 Conference on Empirical Methods in Natural Language Processing: Volume 1-Volume 1. Association for Computational Linguistics, 2009. p. 248-256.*
   * *HEINRICH, Gregor. Parameter estimation for text analysis. Technical report, 2005.*
   * *LBLEI, David M.; NG, Andrew Y.; JORDAN, Michael I. Latent dirichlet allocation. Journal of machine Learning research, v. 3, n. Jan, p. 993-1022, 2003*
   
### An efficient implementation based on Gibbs sampling

**The following descriptions come from *Labeled LDA: A supervised topic model for credit attribution in multi-labeled corpora, Daniel Ramage...***

##### Introduction:
Labeled LDA is a topic model that constrains Latent Dirichlet Allocation by defining a one-to-one correspondence between LDA’s latent topics and user tags.
Labeled LDA can directly learn topics(tags) correspondences.

##### Gibbs sampling:
* Graphical model of Labeled LDA:
<!-- ![https://github.com/JoeZJH/Labeled-LDA/blob/master/assets/graphical-of-labeled-lda.png](https://github.com/JoeZJH/Labeled-LDA/blob/master/assets/graphical-of-labeled-lda.png) -->

<img src="https://github.com/JoeZJH/Labeled-LDA-Python/blob/master/assets/graphical-of-labeled-lda.png" width="400" height="265"/>

* Generative process for Labeled LDA:
<!-- ![https://github.com/JoeZJH/Labeled-LDA/blob/master/assets/generative-process-for-labeled-lda.png](https://github.com/JoeZJH/Labeled-LDA/blob/master/assets/generative-process-for-labeled-lda.png) -->
<img src="https://github.com/JoeZJH/Labeled-LDA-Python/blob/master/assets/generative-process-for-labeled-lda.png" width="400" height="400"/>

* Gibbs sampling equation:
<!-- ![https://github.com/JoeZJH/Labeled-LDA/blob/master/assets/gibbs-sampling-equation.png](https://github.com/JoeZJH/Labeled-LDA/blob/master/assets/gibbs-sampling-equation.png) -->
<img src="https://github.com/JoeZJH/Labeled-LDA-Python/blob/master/assets/gibbs-sampling-equation.png" width="400" height="85"/>

### Usage
* new llda model
* training
* ?is_convergence
* update
* inference
* save model to disk
* load model from disk
* get top-k terms of target topic


### Example 

Run the example in `/src/models/labeled_lda-master` as follows:

```
python -m example.example
```