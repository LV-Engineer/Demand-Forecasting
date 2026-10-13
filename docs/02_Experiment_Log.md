# Experiment Log

One row per experiment. Same walk-forward splits everywhere.

| # | Model | Key settings | Validation | MAE | RMSE | WAPE | Notes |
|---|---|---|---|---|---|---|---|
| 1 | naive | last observed value repeated for 28 days | walk-forward, 8 folds x 28 days, open days only | 1239.1 | 2027.3 | 0.253 | flat line, ignores the weekly cycle |
| 2 | seasonal naive | period 7, copy of the last week | same | 985.1 | 1768.1 | 0.200 | fold 2 WAPE 0.473: closed Jan 1 is copied to all January Sundays |
| 3 | seasonal median | median of the last 4 weeks per weekday, closed days excluded | same | 695.4 | 1193.8 | 0.141 | strongest baseline, the one to beat |
| 4 | Ridge | alpha 1.0, median imputation, scaling, one-hot for store, family, day of week, month | same | 769.4 | 1157.5 | 0.156 | worse than seasonal median on MAE and WAPE (one set of coefficients for all series, no interactions), better RMSE, fit 0.13 s |
| 5 | XGBoost | 500 trees, lr 0.05, depth 6, subsample 0.8, colsample 0.8, native categoricals | same | 622.6 | 1012.8 | 0.126 | beats seasonal median in 7 of 8 folds; loses fold 2 (January, WAPE 0.226 vs 0.198); fit 1.2 s per fold |
| 6 | XGBoost, reduced features | same params, without oil_lag_28 and is_payday (18 features) | same | 553.4 | 957.6 | 0.112 | beats seasonal median in all 8 folds; fold 2 WAPE 0.226 -> 0.116 once the trending oil lag is removed |
| 7 | Ridge, reduced features | alpha 1.0, same 18 features | same | 746.6 | 1140.5 | 0.152 | still worse than seasonal median on MAE and WAPE; fold 2 improved 0.207 -> 0.172 |
| 8 | LightGBM | 500 trees, lr 0.05, 31 leaves, subsample 0.8, colsample 0.8, 18 features | same | 553.8 | 936.5 | 0.112 | same level as XGBoost (differences are noise), RMSE 2% better, fit 0.8 s per fold |
| 9 | XGBoost, scaled target | same params, target divided by sales_roll_mean_56, 18 features | same | 517.3 | 883.6 | 0.105 | best so far, WAPE 26% below seasonal median; weights (sample_weight = level) did not help: 526.3 / 911.6 / 0.107 |
| 10 | LightGBM, scaled target | same params, target divided by sales_roll_mean_56, 18 features | same | 527.9 | 889.9 | 0.107 | scaling helps both boosters; weights again no gain: 529.4 / 894.9 / 0.107 |
| 11 | XGBoost, scaled target, tuned | grid over depth (3, 4, 6), lr (0.03, 0.05), min_child_weight (1, 5, 20); best: depth 6, lr 0.03, mcw 5 | same | 512.5 | 872.9 | 0.104 | gain over defaults below 1%, within noise; landscape is flat (all top 10 within 0.104-0.107), defaults kept; depth 3 gives the same WAPE twice as fast |
