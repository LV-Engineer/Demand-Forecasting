# Project 2: Demand Forecasting (Time Series)

**Repo:** https://github.com/LV-Engineer/Demand-Forecasting

## Business problem
- **Who has the problem:** a supermarket chain's replenishment planner (Corporación Favorita, Ecuador).
- **Why it matters:** stock-outs lose sales, overstock ties up money and spoils (food, produce).
- **Decision the model supports:** how much to order for each store and product family for the next 28 days.

## Data
- **Source:** Favorita Store Sales, Kaggle competition: https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data
- **Subset used:** 5 stores (44, 3, 51, 11, 24: types A, B, D; Quito, Guayaquil, Cayambe) x 5 families (GROCERY I, BEVERAGES, PRODUCE, CLEANING, DAIRY) = 25 series, 2015-08-16 to 2017-08-15 (731 days; 18,225 rows in the source view, 18,275 after filling the two missing Dec 25 days).
- **Target:** daily `sales` per store and family.
- **Key features:** sales lags (28, 35, 42, 56 days) and rolling mean/std shifted by 28 days, calendar (day of week, day, month, days to Christmas), holiday and event flags, `onpromotion` and its relative version. Oil price and payday were tested and removed.
- **Data issues:** Dec 25 is missing (filled), closed days (Dec 25 and Jan 1), the April 2016 earthquake, an oil price that trends over time (harmful as a feature), `transactions` is not known in the future (leakage, EDA only).

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
- **Baselines:** naive, seasonal naive, and the median of the last 4 weeks per weekday with closed days excluded (the strongest one).
- **Classical ML:** Ridge, XGBoost and LightGBM on 18 features; for the boosters the target is divided by the series level; a small hyperparameter grid gave less than 1%.
- **Neural networks:** RNN and LSTM, one layer with hidden size 64, window of 56 days, series embedding, known features of the next 28 days, 28 outputs at once; AdamW with weight decay, dropout 0.2, L1 loss, early stopping; 3 seeds.
- **Validation:** 8 walk-forward folds of 28 days with an expanding train window, no random split; the last 28 days are a hold-out used once.
- **Metrics:** MAE (units), RMSE (penalizes large misses) and WAPE (sum of absolute errors divided by sum of sales: comparable across series of different scale and safe with zeros, unlike MAPE).
- **Forecast horizon:** 28 days.
- **Cost assumptions (units, no prices in Favorita):** under-forecast cost = 3, over-forecast cost = 1 per unit, weekly ordering; sensitivity analysis from 1:1 to 5:1.
- **Comparison:** paired bootstrap over (fold, series) units and a Wilcoxon test over folds; the networks were compared by accuracy and training time (about 50 s per fold against about 1 s).

## Results
- **Best model vs baseline:** XGBoost with the scaled target. Walk-forward: MAE 517, RMSE 884, WAPE 0.105 against 695, 1194, 0.141 for the seasonal median baseline (25% lower WAPE, better in 8 of 8 folds, Wilcoxon p 0.004). Hold-out: WAPE 0.091 against 0.118 (23% lower). LightGBM is practically tied (0.107). RNN and LSTM reach 0.125 and are not convincingly better than the baseline; Ridge (0.152) is worse.
- **Business effect (simulated):** with a stock-out cost 3 times the overstock cost and weekly ordering, XGBoost lowers the cost by 23% on walk-forward (LightGBM 25%) and by 13% on the hold-out, and raises the share of demand covered from 94.7% to 95.6%. For cost ratios from 1:1 to 5:1 the boosters stay 21-31% cheaper than the baseline; the networks beat the baseline only when stock-outs are cheap.
- **Limitations:** costs are assumed units (no prices or margins in the data); weekly netting assumes stock carries over inside a week, and lead times, shelf life and capacity are ignored; only two Decembers in the data; the hold-out is a single 28-day window; features and parameters were chosen on the same walk-forward folds; a safety factor tuned on walk-forward (orders 7.5% above the forecast) raised the cost on the calm hold-out, so a fixed safety stock is not recommended.

## Takeaway
- **Which model won and why:** XGBoost with the target divided by the series level. Trees learn the interaction of weekday, store and family and handle missing values, and the scaling lets them learn the shape of the demand instead of the scale of each series. LightGBM is equal; the networks are about 50 times slower and worse; Ridge cannot capture the interactions. Removing the oil price lag (a trending proxy for time) fixed the weakest fold.
- **Next step:** quantile forecasts (for example the 75th percentile) for the asymmetric costs instead of a fixed safety factor, more history so that holidays are learned from more than two years, planned promotions as future information, hierarchical forecasts, and a retraining schedule.
