# Data

The data files are **not committed** (`data/*` is in `.gitignore`). This README is the only tracked file in the folder.

## Source

- Dataset: Favorita Store Sales - Time Series Forecasting (Kaggle competition)
- Download: https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data
- License: competition data, Kaggle rules section 7A allows non-commercial use, including academic research and
  education. Redistribution is not allowed. Used here for educational and portfolio purposes only; the raw data
  is not redistributed in this repository.
- Origin: sales of Corporación Favorita, an Ecuadorian grocery retailer.

## How to reproduce

1. Log in to Kaggle, accept the competition rules on the Rules tab, and download the archive from the link above.
2. Unzip it into `data/raw/`.
3. Delete `test.csv` and `sample_submission.csv`. They have no target and are not used.
4. Start PostgreSQL and load the tables:

```bash
docker compose up -d
docker compose exec db psql -U demand -d demand -f /sql/01_schema.sql
docker compose exec db psql -U demand -d demand -f /sql/02_load.sql
docker compose exec db psql -U demand -d demand -f /sql/03_subset.sql
docker compose exec db psql -U demand -d demand -f /sql/04_holidays.sql
```

Files in `data/raw/` are never edited by hand. The subset and the holiday flags are built by SQL views
(`subset`, `holiday_flags`, `subset_full`), so no cleaned copy of the raw files is stored.

## Structure

```
data/
  README.md     # this file (tracked)
  raw/          # original CSV files (ignored)
  processed/    # subset.parquet read from the subset_full view (ignored)
```

## Facts about the raw files

Checked by reading the files:

- `train.csv`: 3,000,888 rows, one row per date x store x product family, 2013-01-01 to 2017-08-15,
  1,684 unique dates (Dec 25 is missing).
- 54 stores (`stores.csv`) and 33 product families.
- `oil.csv`: 1,218 rows, the price is empty on days without trading.
- `holidays_events.csv`: 350 rows, `transactions.csv`: 83,488 rows.
- Zero sales share over the last 2 years differs a lot by family: 0.02 for GROCERY I, BEVERAGES, PRODUCE,
  CLEANING and DAIRY, but 0.93 for BOOKS and 0.88 for BABY CARE. Sparse families are not used.

## Subset used

- Stores: 44, 3, 51, 11, 24 (types A, B, D; Quito, Guayaquil, Cayambe).
- Families: GROCERY I, BEVERAGES, PRODUCE, CLEANING, DAIRY.
- Period: 2015-08-16 to 2017-08-15.
- 25 series, 731 days: 18,225 rows in the `subset` view; `clean()` adds the two missing Dec 25 days
  (50 rows) and gives 18,275 rows.

## Target

- `sales`: units sold per store and family per day (can be fractional for goods sold by weight).

## Column roles

| Role | Columns |
| --- | --- |
| Target | `sales` |
| Identifiers, excluded | `id` |
| Series keys | `store_nbr`, `family` |
| Features used | `date` (calendar), `onpromotion`, holiday flags `holiday_national`, `holiday_local`, `is_event`, series keys `store_nbr` and `family`; store attributes (`city`, `state`, `type`, `cluster`) follow from `store_nbr` and are not used separately |
| Tested and removed | oil price `dcoilwtico` lagged by 28 days (a trending proxy for time, it hurt validation), payday flag (no effect), `holiday_regional` (always false in the subset) |
| Leakage, EDA only | `transactions` (not known at forecast time) |

Why these decisions:

- `transactions` is the number of receipts per store per day. It is not available for future dates, so using it
  as a feature would leak information.
- Holidays with `transferred = True` are dropped, because the holiday was moved and the day was a normal one.
  The `Transfer` rows mark the real days off. `Work Day` rows are dropped. `Event` rows get a separate flag.
- Regional holidays are matched to stores by `state`, local ones by `city`.
- Oil price gaps are left as NULL in SQL and filled by forward fill in `clean()`; the oil price is not used as a
  feature in the final models.

The roles above were confirmed in EDA and by ablation; see `docs/02_Experiment_Log.md` and
`notebooks/05_models.ipynb`.
