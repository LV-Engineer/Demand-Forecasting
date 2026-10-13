# Project 2: Demand Forecasting (Time Series)

**Repo:** https://github.com/LV-Engineer/Demand-Forecasting

## Business problem
- **Who has the problem:** a supermarket chain's replenishment planner (Corporación Favorita, Ecuador).
- **Why it matters:** stock-outs lose sales, overstock ties up money and spoils (food, produce).
- **Decision the model supports:** how much to order for each store and product family for the next 28 days.

## Data
- **Source:** Favorita Store Sales, Kaggle competition: https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data
- **Subset used:** 5 stores (44, 3, 51, 11, 24: types A, B, D; Quito, Guayaquil, Cayambe) x 5 families (GROCERY I, BEVERAGES, PRODUCE, CLEANING, DAIRY) = 25 series, 2015-08-16 to 2017-08-15 (730 days, 18,250 rows).
- **Target:** daily `sales` per store and family.
- **Key features:** lags, rolling means, calendar, `onpromotion`, holidays, oil price.
- **Data issues:** Dec 25 is missing, the April 2016 earthquake, oil price gaps on weekends, `transactions` is not known in the future (leakage, EDA only).

## Tech stack
| Area | Tools |
|---|---|
| Language | Python 3.13 |
| Data and EDA | pandas, NumPy, Matplotlib, Seaborn |
| SQL | PostgreSQL (load data, build the subset view with joins) |
| Classical ML | scikit-learn (Ridge), XGBoost, LightGBM (lag and calendar features) |
| Neural network | PyTorch: RNN and LSTM (sequence windows) |
| Validation | TimeSeriesSplit / walk-forward |
| Statistics | significance check of improvement over baseline |
| Environment | Jupyter Notebook, uv |
| Version control | Git, GitHub |

## Approach
- **Baselines:** [naive, seasonal naive]
- **Classical ML:** [Ridge as a linear model, XGBoost and LightGBM with lag/rolling features]
- **Neural networks:** [RNN, LSTM: window length, hidden size, regularization, early stopping]
- **Validation:** walk-forward, no random split; the last 28 days are a hold-out until the final comparison.
- **Metrics:** [MAE, RMSE, WAPE] and why
- **Forecast horizon:** 28 days.
- **Cost assumptions (units, no prices in Favorita):** under-forecast cost = 3, over-forecast cost = 1 per unit; sensitivity analysis from 1 to 5.
- **Comparison:** [do RNN/LSTM beat the baselines, Ridge, XGBoost and LightGBM? at what cost?]

## Results
- **Best model vs baseline:** [metric values]
- **Business effect (simulated):** [stock-outs / overstock reduced under stated assumptions]
- **Limitations:** [what the simulation does not prove]

## Takeaway
- **Which model won and why:** [...]
- **Next step:** [e.g. add promotions, hierarchical forecasts, retraining schedule]
