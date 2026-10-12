# Project 2: Demand Forecasting (Time Series)

**Repo:** [GitHub link]

## Business problem
- **Who has the problem:** [e.g. retail store / warehouse planner]
- **Why it matters:** [stock-outs lose sales, overstock ties up money]
- **Decision the model supports:** [how much to order for the next 2-4 weeks]

## Data
- **Source:** [Favorita Store Sales / M5, link]
- **Subset used:** [stores, products, date range]
- **Target:** [daily/weekly sales]
- **Key features:** [lags, rolling means, calendar, promotions, holidays]
- **Data issues:** [gaps, zeros, outliers, leakage through future features]

## Tech stack
| Area | Tools |
|---|---|
| Language | Python 3.11+ |
| Data and EDA | pandas, NumPy, Matplotlib, Seaborn |
| SQL | PostgreSQL (load data, aggregate with window functions and joins) |
| Classical ML | scikit-learn, XGBoost (lag and calendar features) |
| Neural network | PyTorch: RNN and LSTM (sequence windows) |
| Validation | TimeSeriesSplit / walk-forward |
| Statistics | significance check of improvement over baseline |
| Environment | Jupyter Notebook, uv |
| Version control | Git, GitHub |

## Approach
- **Baselines:** [naive, seasonal naive]
- **Classical ML:** [XGBoost with lag/rolling features]
- **Neural networks:** [RNN, LSTM: window length, hidden size, regularization, early stopping]
- **Validation:** [walk-forward, no random split]
- **Metrics:** [MAE, RMSE, WAPE] and why
- **Comparison:** [do RNN/LSTM beat the baselines and XGBoost? at what cost?]

## Results
- **Best model vs baseline:** [metric values]
- **Business effect (simulated):** [stock-outs / overstock reduced under stated assumptions]
- **Limitations:** [what the simulation does not prove]

## Takeaway
- **Which model won and why:** [...]
- **Next step:** [e.g. add promotions, hierarchical forecasts, retraining schedule]
