# I. Introduction
"Multi-ridge regression" or stacking models using ridge regression refers to using L2-regularized linear regression as a meta-model to combine predictions from multiple base machine learning models. In this part 2, the base ML models are Ridge Regression, Random Forest, and LightGBM. For detail of the techniques, you can look at my machine learning algorithm sections in here D:\33_Obsidian\33_Github\ChuongTa.github.io\_MachineLearningProjects

![[Fig0_main_pipeline.png]]Fig 1_Main_pipeline


How Ridge Regression Combines Models

- **Stacking Meta-Regressor:** Instead of simple averaging, a ridge regression model treats the predictions of individual base models as its input features to predict the final target. [[1](https://medium.com/grabngoinfo/bagging-vs-boosting-vs-stacking-in-machine-learning-65fe4d1684c0), [2](https://www.linkedin.com/pulse/building-multi-output-regression-models-linear-ridge-r-awc3c), [3](https://www.certometer.com/blogs/machine-learning/understanding-ridge-regression), [4](https://www.sciencedirect.com/science/article/pii/S2589721725000807)]

- **L2 Penalty Control:** The ridge penalty prevents the meta-model from assigning overly large or unstable weights to any single base model, handling correlated model predictions gracefully. [[1](https://www.geeksforgeeks.org/machine-learning/what-is-ridge-regression/), [2](https://www.acte.in/what-is-regularization-in-machine-learning), [3](https://www.certometer.com/blogs/machine-learning/understanding-ridge-regression)]

- **Bias-Variance Balance:** It shrinks coefficients of weak or redundant base models toward zero, improving overall generalization on unseen data.

# II. Results
## 2.1 Ridge Regression


RE
![D:\33_Obsidian\33_Github\ChuongTa.github.io\_EnergyForecasting\Wave_Energy\2_Wave_Energy_Flux_Forecsating_part2\2_Stacking_Ensemble\images\Fig2swh_performance_bars.png](file:///d%3A/33_Obsidian/33_Github/ChuongTa.github.io/_EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig2swh_performance_bars.png)


![D:\33_Obsidian\33_Github\ChuongTa.github.io\_EnergyForecasting\Wave_Energy\2_Wave_Energy_Flux_Forecsating_part2\2_Stacking_Ensemble\images\Fig3mwp_performance_bars.png](file:///d%3A/33_Obsidian/33_Github/ChuongTa.github.io/_EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig3mwp_performance_bars.png)
## 2.2 Time series forecasting

In time series forecasting, each models are better in each lead time except random forest

For shorter lead time 1,3 ,6h Stacking model, LightGBM and Ridge has better performance in each different lead time

However, with higher lead time 12 until 48h, stacking model has the highest performance, however, for mean wave period, only 24h ahead stacking model wins, the other at 12 and 48h, ridge regresison wins
![[Fig_4stacking_forecast_1_3_6h.png]]





![[Fig5_stacking_forecast_12_24_48h.png]]