---
title: "Naive Bayes - Prediction probability Storm days 🌪️ "
category: densys
excerpt: "This is my 1st post about Machine Learning (ML). This is a topic I learnt from the book \"An Introduction to Statistical Learning\"."
image: /images/Naive_Bayes.png
layout: single
author_profile: true
permalink: /MachineLearning/ml1.md/
usemathjax: true
---

In this post, I use the Naive Bayes classifier to predict whether a day in a North Sea wind farm will become a storm day 🌪️.  
For more information on Naive Bayes, you can read this post on [DataCamp](https://databasecamp.de/en/ml/naive-bayes-algorithm).

![Naive Bayes diagram](/images/Naive_Bayes.png)

My features are wind speed 💨, air pressure 🌡️, and cloud cover ☁️, each recorded as simple categories such as high, medium, low.

From a small historical dataset, we estimate the probabilities of a storm, then use Naive Bayes to compute how likely a new day with given conditions (wind speed, pressure, clouds) will turn into a storm.

# Storm prediction dataset

| WindSpeed | Pressure | Cloud  | StormDay |
| --------- | -------- | ------ | -------- |
| high      | low      | high   | yes      |
| high      | low      | low    | yes      |
| high      | normal   | high   | yes      |
| medium    | low      | high   | yes      |
| medium    | normal   | low    | no       |
| low       | high     | low    | no       |
| low       | normal   | low    | no       |
| medium    | high     | high   | no       |

### Question

What is the probability of a storm day when

$$
(\text{Wind Speed}, \text{Pressure}, \text{Cloud}) = (\text{low}, \text{low}, \text{high}) \, ?
$$

---

The feature vector is

$$
X = (\text{Wind Speed}, \text{Pressure}, \text{Cloud}) = (\text{low}, \text{low}, \text{high}).
$$

The probability of a storm day given this feature is

$$
P(\text{StormDay = yes} \mid \text{WindSpeed = low}, \text{Pressure = low}, \text{Cloud = high}).
$$

Using the Naive Bayes assumption, we write

$$
P(X \mid \text{yes})
=
P(\text{low wind} \mid \text{yes}) \cdot
P(\text{low pressure} \mid \text{yes}) \cdot
P(\text{high cloud} \mid \text{yes}).
$$

From the dataset:

- Total days: \(8\)  
- Storm “yes”: \(4 \Rightarrow P(\text{yes}) = 4/8 = 0.5\)  
- Storm “no”: \(4 \Rightarrow P(\text{no}) = 4/8 = 0.5\)

Looking only at the 4 storm‑yes days:

- WindSpeed = low with storm = yes: \(0/4 \Rightarrow P(\text{low wind} \mid \text{yes}) = 0\)  
- Pressure = low with storm = yes: \(3/4 \Rightarrow P(\text{low pressure} \mid \text{yes}) = 0.75\)  
- Cloud = high with storm = yes: \(3/4 \Rightarrow P(\text{high cloud} \mid \text{yes}) = 0.75\)

Substituting into the Naive Bayes likelihood:

$$
P(X \mid \text{yes}) = 0 \times 0.75 \times 0.75 = 0.
$$

So the unnormalized score for “storm = yes” is

$$
P(\text{yes}) \cdot P(X \mid \text{yes}) = 0.5 \times 0 = 0.
$$

Therefore,

$$
P(\text{storm = yes} \mid X) = 0
$$

under **unsmoothed** Naive Bayes, because one conditional probability is zero.  
In a real model, we would use **Laplace smoothing** so a single missing combination does not force the probability to 0.

---

## Fixing the zero‑probability with Laplace smoothing

In the unsmoothed Naive Bayes calculation, we got

$$
P(\text{low wind} \mid \text{storm = yes}) = 0,
$$

which made

$$
P(X \mid \text{storm = yes}) = 0
$$

for

$$
X = (\text{low wind}, \text{low pressure}, \text{high cloud}).
$$

To avoid this, we apply **Laplace smoothing** with \(\alpha = 1\).

For a categorical feature value \(x\) and class \(y\),

$$
P_{\text{Laplace}}(x \mid y)
=
\frac{\text{count}(x, y) + \alpha}{\text{count}(y) + \alpha \cdot K},
$$

where \(K\) is the number of possible values of that feature.

In our example:

- Wind speed categories: \(K_{\text{wind}} = 3\) (low, medium, high)  
- Pressure categories: \(K_{\text{pressure}} = 3\) (low, normal, high)  
- Cloud categories: \(K_{\text{cloud}} = 2\) (low, high)  
- Storm = yes days: \(\text{count}(\text{yes}) = 4\)

Now compute the smoothed likelihoods for the storm = yes class.

1. Wind speed:

$$
P_{\text{L}}(\text{low wind} \mid \text{yes})
=
\frac{0 + 1}{4 + 1 \cdot 3}
=
\frac{1}{7}.
$$

2. Pressure:

$$
P_{\text{L}}(\text{low pressure} \mid \text{yes})
=
\frac{3 + 1}{4 + 1 \cdot 3}
=
\frac{4}{7}.
$$

3. Cloud:

$$
P_{\text{L}}(\text{high cloud} \mid \text{yes})
=
\frac{3 + 1}{4 + 1 \cdot 2}
=
\frac{4}{6}
=
\frac{2}{3}.
$$

The smoothed likelihood for \(X\) under storm = yes is

$$
P_{\text{L}}(X \mid \text{yes})
=
\frac{1}{7} \cdot \frac{4}{7} \cdot \frac{2}{3}
=
\frac{8}{147}.
$$

Using the prior \(P(\text{yes}) = 0.5\),

$$
\text{score}(\text{yes} \mid X)
\propto
P(\text{yes}) \cdot P_{\text{L}}(X \mid \text{yes})
=
0.5 \cdot \frac{8}{147}
=
\frac{4}{147}.
$$

---

## Smoothed likelihood for “storm = no”

For the 4 “storm = no” days we have:

- WindSpeed values: low, low, medium, medium  
- Pressure values: high, normal, normal, high  
- Cloud values: low, low, low, high  

With \(\alpha = 1\):

Wind speed (3 categories):

$$
P_{\text{L}}(\text{low wind} \mid \text{no})
=
\frac{2 + 1}{4 + 1 \cdot 3}
=
\frac{3}{7}.
$$

Pressure (3 categories):

$$
P_{\text{L}}(\text{low pressure} \mid \text{no})
=
\frac{0 + 1}{4 + 1 \cdot 3}
=
\frac{1}{7}.
$$

Cloud (2 categories):

$$
P_{\text{L}}(\text{high cloud} \mid \text{no})
=
\frac{1 + 1}{4 + 1 \cdot 2}
=
\frac{2}{6}
=
\frac{1}{3}.
$$

Thus the smoothed likelihood for \(X\) under “no” is

$$
P_{\text{L}}(X \mid \text{no})
=
\frac{3}{7} \cdot \frac{1}{7} \cdot \frac{1}{3}
=
\frac{3}{147}.
$$

With prior \(P(\text{no}) = 0.5\),

$$
\text{score}(\text{no} \mid X)
=
0.5 \cdot \frac{3}{147}
=
\frac{3}{294}.
$$

From above,

$$
\text{score}(\text{yes} \mid X)
=
\frac{4}{147}
=
\frac{8}{294}.
$$

---

## Final posterior probability

Now normalize the two scores:

$$
P(\text{storm = yes} \mid X)
=
\frac{\text{score}(\text{yes} \mid X)}
     {\text{score}(\text{yes} \mid X) + \text{score}(\text{no} \mid X)}
=
\frac{\frac{8}{294}}{\frac{8}{294} + \frac{3}{294}}
=
\frac{8}{11}
\approx 0.73.
$$

So after Laplace smoothing, the model predicts a storm with probability about \(73\%\) for  
\(X = (\text{low wind}, \text{low pressure}, \text{high cloud})\) – much better than the zero probability from the unsmoothed model 🎯
