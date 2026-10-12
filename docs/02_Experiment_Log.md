# Experiment Log

One row per experiment. Same walk-forward splits everywhere.

| # | Model | Key settings | Validation | MAE | RMSE | WAPE | Notes |
|---|---|---|---|---|---|---|---|
| 1 | naive | last observed value repeated for 28 days | walk-forward, 8 folds x 28 days, open days only | 1239.1 | 2027.3 | 0.253 | flat line, ignores the weekly cycle |
| 2 | seasonal naive | period 7, copy of the last week | same | 985.1 | 1768.1 | 0.200 | fold 2 WAPE 0.473: closed Jan 1 is copied to all January Sundays |
| 3 | seasonal median | median of the last 4 weeks per weekday, closed days excluded | same | 695.4 | 1193.8 | 0.141 | strongest baseline, the one to beat |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |