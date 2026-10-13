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
| 12 | RNN | 1 layer, hidden 64, embedding 8, dropout 0.2, AdamW lr 1e-3 wd 1e-4, early stopping patience 8, window 56 days, target ratio to level, direct 28 outputs, seed 42 | same | 611.1 | 1058.3 | 0.125 | beats seasonal median, loses to XGBoost scaled (0.105); fit 50 s per fold, about 50x slower |
| 13 | LSTM | same as RNN | same | 616.6 | 1030.9 | 0.125 | same WAPE as RNN, gates do not help; fold results vary a lot (WAPE 0.093 to 0.156); single seed |
| 14 | RNN, 3 seeds | same as row 12, mean of seeds 42, 1, 2 | same | 602.6 | 1041.5 | 0.123 | WAPE per seed 0.121-0.125, stable; still behind XGBoost scaled (0.105) |
| 15 | LSTM, 3 seeds | same as row 13, mean of seeds 42, 1, 2 | same | 607.8 | 1014.4 | 0.123 | WAPE per seed 0.122-0.125; RMSE about 3% below RNN, no gain on WAPE |
| 16 | XGBoost, scaled target, hold-out | final model trained on the full training part, hold-out 2017-07-19 to 2017-08-15 (28 days, used once) | hold-out | 405.4 | 679.9 | 0.091 | 23% below seasonal median on the same days (0.118), consistent with walk-forward (0.105, 25%); same model order as in walk-forward |
| 17 | seasonal median, hold-out | same hold-out | hold-out | 526.5 | 899.2 | 0.118 | reference for row 16; whole month is easier than the average fold for every model |
