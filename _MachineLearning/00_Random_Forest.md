
---

## title: "Random Forest - Methodology 🌲" category: densys excerpt: "This post explains how Random Forest works, step by step. It covers bootstrap sampling, random feature selection, decision tree growth, and aggregation." image: /images/Random_Forest.png layout: single author_profile: true permalink: /MachineLearning/ml2.md/ usemathjax: true

# Random Forest: Methodology

> **Series:** Machine Learning Algorithms | **Part:** 1 of 2 (Theory)

---

## 1. What is Random Forest?

**Random Forest (RF)** is one of the most popular and powerful machine learning algorithms. It was first introduced by [Breiman (2001)](https://doi.org/10.1023/A:1010933404324) and can be used for both **classification** and **regression** tasks.

The core idea is simple: instead of training one decision tree, Random Forest trains **many decision trees** and combines their predictions. This approach is called an **ensemble method**.

- For **classification**, the final prediction is the **majority vote** across all trees.
- For **regression**, the final prediction is the **average** of all tree outputs.

By combining many trees, Random Forest improves accuracy and reduces overfitting compared to a single decision tree.

![RF algorithm explained](https://claude.ai/images/pic1.png) _Figure 3.5: RF algorithm explained. The dataset is split into multiple bootstrap samples, each used to train a separate decision tree. The final result is produced by majority voting (classification) or averaging (regression). (Figure adapted from [Jain, A.](https://medium.com/@abhishekjaindore24/everything-about-random-forest-90c106d63989))_

---

## 2. Methodology: The 4-Step Process

The RF algorithm works in four steps. The figure above shows how each step connects to the next.

---

### Step 1: Bootstrap Sampling (Bagging)

The first step is to create multiple different training datasets from the original data. This process is called **bootstrap sampling** (or **bagging**, short for Bootstrap AGGregatING).

**How it works:**

From the original training dataset of $n$ rows, $B$ bootstrap samples are generated. A bootstrap sample is a random sample drawn **with replacement**. This means the same row can appear more than once in a sample, while some rows may not appear at all.

On average:

- Each bootstrap sample contains approximately **63% unique rows**.
- The remaining **37%**, called **out-of-bag (OOB) samples**, are not used in training that tree. They can be used for internal validation without touching the test set.

Each tree $b$ is trained exclusively on its own bootstrap sample $\mathcal{D}^{*b}$:

$$ \mathcal{D}^{*b} = \{ (\mathbf{x}_{i}^{*}, y_{i}^{*}) \}_{i=1}^{n} \sim \text{Sample with replacement from } \mathcal{D} \tag{3.10} $$

> **Why is this useful?** Each tree sees a slightly different version of the data. This difference makes each tree's errors uncorrelated with each other. When you average uncorrelated errors, they cancel out, which reduces the overall variance of the model.

---

### Step 2: Random Feature Selection

At each **split node** of each tree, only a random subset of $m$ features is considered, rather than all $p$ available features. The best split is then chosen only from those $m$ candidates.

**Why not use all features?**

If all features were considered at every split, a single dominant feature (for example, `AmbientTemperature`) would appear at the root of nearly every tree. This would make all trees very similar to each other. By restricting the features considered at each split, the trees are forced to use other physically meaningful features (like `icing\_hours\_consecutive` or `RelativeHumidity`), which makes them more diverse and less correlated.

The default feature subset size is:

$$ m = \begin{cases} \sqrt{p} & \text{classification} \ p & \text{regression} \end{cases} \tag{3.11} $$

where $p$ is the total number of features in the dataset.

---

### Step 3: Growing Decision Trees

Each tree in the forest is grown to its **maximum depth without pruning**. This means each tree is intentionally allowed to overfit its own bootstrap sample.

At each node, the algorithm selects the best split from the random subset of $m$ features using one of the following criteria:

**For classification**, the split minimises **Gini Impurity**:

$$ G = 1 - \sum_{k=1}^{K} \hat{p}^{2}_{mk} \tag{3.12} $$

where $\hat{p}_{mk}$ is the proportion of class $k$ samples at node $m$. A lower Gini value means a purer node, where most samples belong to the same class.

**For regression**, the split minimises the **Sum of Squared Errors (SSE)**:

$$ \text{SSE} = \sum_{i \in \text{left}} (y_{i} - \bar{y}_{L})^{2} + \sum_{i \in \text{right}} (y_{i} - \bar{y}_{R})^{2} \tag{3.13} $$

where $\bar{y}_{L}$ and $\bar{y}_{R}$ are the mean values of the left and right child nodes.

> **Key insight:** A single overfitted tree has high variance. It is sensitive to small changes in the data. However, when many such trees are averaged together in the next step, the variance is reduced while the bias stays approximately the same.

---

### Step 4: Aggregation

Once all $B$ trees are trained, their predictions are combined into a single final output.

**For regression**, the final prediction is the **mean** across all trees:

$$ \hat{f}_{\text{RF}}(\mathbf{x}) = \frac{1}{B} \sum_{b=1}^{B} \hat{f}^{*b}(\mathbf{x}) \tag{3.14} $$

Averaging reduces the variance by a factor of $1/B$ relative to a single tree, while the bias stays approximately unchanged.

**For classification**, the final prediction is the **majority vote**:

$$ \hat{y}_{\text{RF}}(\mathbf{x}) = \arg\max_{k} \sum_{b=1}^{B} \mathbf{1}[\hat{f}^{*b}(\mathbf{x}) = k] \tag{3.15} $$

where $k \in {0, 1}$ is the class label (for example, icing or no icing).

---

## 3. Hyperparameters

Tuning the hyperparameters of a Random Forest directly affects the balance between model accuracy and computational cost. The table below lists the key parameters.

|Parameter|Range Used|Effect|
|---|---|---|
|`n\_estimators`|100 - 500|Number of trees $B$. More trees improve stability but increase compute time. Test error plateaus, so there is no upper-bound overfitting risk.|
|`max\_features`|`sqrt`, `log2`|Features considered per split $m$. Smaller values decorrelate trees more aggressively. Default: $m = \sqrt{p}$ for classification, $m = p$ for regression.|
|`max\_depth`|10 - 30, `None`|Maximum depth of each tree. Deeper trees have lower bias but higher individual variance. `None` grows each tree fully before aggregation corrects the variance.|
|`min\_samples\_split`|2 - 20|Minimum samples required to split a node. Higher values reduce overfitting at the cost of slightly higher bias.|
|`min\_samples\_leaf`|5 - 20|Minimum samples required at a leaf node. Prevents overly specific leaves, which is important for zero-inflated targets.|
|`bootstrap`|`True`|Whether to use bootstrap sampling. Disabling it removes the row randomness that decorrelates the trees.|

> **Tuning strategy:** Parameters with a search range are tuned using an inner 3-fold cross-validation loop. RMSE is minimised for regression; $F_{1}$ score is maximised for classification. `bootstrap` and `max\_features` are fixed by design.

---

## 4. Advantages and Limitations

### Advantages

- **Resistant to overfitting.** The ensemble structure makes RF inherently robust, even on noisy data.
- **Works for both regression and classification.** The same underlying algorithm handles both task types.
- **Native feature importance.** Gini impurity reduction scores are available directly, supporting SHAP analysis.
- **Easily parallelisable.** Trees can be trained in parallel across CPU cores, making large model sweeps computationally feasible.

### Limitations

- **Hard to interpret.** Unlike a single decision tree (which can be read as a set of rules), a forest of 300 trees cannot be inspected directly. SHAP values are used to recover interpretability after training.
- **Computational cost at scale.** Training time is non-trivial at large dataset sizes. RF remains tractable due to parallel tree construction.
- **Memory usage.** Memory scales linearly with $B \times \text{tree size}$. This should be monitored for large future deployments.

---

## 5. Conclusion

Random Forest is a strong and reliable algorithm for both regression and classification tasks. Its ensemble design, built on bootstrap sampling and random feature selection, allows it to produce stable and accurate predictions even on noisy or imbalanced datasets. While it lacks the direct interpretability of a single decision tree, tools such as SHAP values can be used to explain its predictions after training.

In the next post, we will present the **practical application of Random Forest**, including how to implement it in Python, tune its hyperparameters, and evaluate its performance.

---

## References

- Breiman, L. (2001). _Random Forests_. Machine Learning, 45(1), 5-32. [https://doi.org/10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324)
- Jain, A. _Everything about Random Forest_. [Medium article](https://medium.com/@abhishekjaindore24/everything-about-random-forest-90c106d63989)