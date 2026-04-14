---
title: "Random Forest - Methodology 🌲" 
category: densys 
excerpt: "This post explains how Random Forest works, step by step. It covers bootstrap sampling, random feature selection, decision tree growth, and aggregation." 
image: /images/Naive_Bayes.png 
layout: single 
author_profile: true 
permalink: /MachineLearning/00_Random_Forest.md/ 
usemathjax: true
---

# Random Forest: Methodology

> **Series:** Machine Learning Algorithms | **Part:** 1 of 2 (Theory)

## 1. What is Random Forest?

**Random Forest (RF)** is a powerful ensemble learning method used for both **classification** and **regression**. By combining many decision trees, it improves accuracy and reduces the risk of overfitting.

- For **classification**, the final prediction is the **majority vote**.
- For **regression**, the final prediction is the **average** of all tree outputs.

![RF algorithm explained](/files/00_Tranditional_ML/Figures/00_RF/pic1.png)
*Figure 3.5: RF algorithm process (Source: Jain, A.)*

---

## 2. Methodology: The 4-Step Process

### Step 1: Bootstrap Sampling (Bagging)
Multiple training datasets are generated from the original data using **bootstrap sampling** (sampling with replacement). Each tree $b$ is trained on its own sample $\mathcal{D}^{*b}$:

$$\mathcal{D}^{*b} = \{ (\mathbf{x}_{i}^{*}, y_{i}^{*}) \}_{i=1}^{n} \sim \text{Sample with replacement from } \mathcal{D} \tag{3.10}$$

### Step 2: Random Feature Selection
At each node split, the algorithm only considers a random subset of $m$ features out of $p$ total features. The default size is:

$$m = \begin{cases} \sqrt{p} & \text{for classification} \\ p & \text{for regression} \end{cases} \tag{3.11}$$

### Step 3: Growing Decision Trees
Each tree is grown to its maximum depth without pruning. 

**For classification**, the split minimizes the **Gini Impurity (G)**:

$$G = 1 - \sum_{k=1}^{K} \hat{p}_{mk}^{2} \tag{3.12}$$

*Where $\hat{p}_{mk}$ is the proportion of class $k$ samples at node $m$.*

**For regression**, the split minimizes the **Sum of Squared Errors (SSE)**:

$$\text{SSE} = \sum_{i \in \text{left}} (y_{i} - \bar{y}_{L})^{2} + \sum_{i \in \text{right}} (y_{i} - \bar{y}_{R})^{2} \tag{3.13}$$

*Where $\bar{y}_{L}$ and $\bar{y}_{R}$ are the mean values of the child nodes.*

### Step 4: Aggregation
The individual predictions are combined into a final output.

**For regression (Mean):**
$$\hat{f}_{\text{RF}}(\mathbf{x}) = \frac{1}{B} \sum_{b=1}^{B} \hat{f}^{*b}(\mathbf{x}) \tag{3.14}$$

**For classification (Majority Vote):**
$$\hat{y}_{\text{RF}}(\mathbf{x}) = \arg\max_{k} \sum_{b=1}^{B} \mathbf{1}[\hat{f}^{*b}(\mathbf{x}) = k] \tag{3.15}$$

---

## 3. Hyperparameters

| Parameter | Range | Effect |
| :--- | :--- | :--- |
| `n_estimators` | 100 - 500 | Number of trees. More trees increase stability. |
| `max_features` | `sqrt`, `log2` | Features per split. Smaller values decorrelate trees. |
| `max_depth` | 10 - 30 | Maximum tree depth. Controls the bias-variance trade-off. |
| `min_samples_leaf`| 5 - 20 | Minimum samples at a leaf. Prevents overly specific nodes. |

---

## 4. Advantages and Limitations

### Advantages
* **Robustness:** Highly resistant to outliers and noise.
* **Feature Importance:** Naturally calculates which variables are most important.
* **Parallel Power:** Trees can be trained simultaneously across CPU cores.

### Limitations
* **Black Box:** Harder to interpret than a single tree.
* **Memory:** Can consume significant RAM with many deep trees.

---

## 5. Conclusion
Random Forest is a reliable "go-to" algorithm. While it lacks the simple visual rules of a single tree, its stability makes it a favorite for industrial applications.

**In the next post, we will present the practical application of Random Forest using Python.**
