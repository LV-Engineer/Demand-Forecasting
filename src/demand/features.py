import pandas as pd
from demand.config import HORIZON

GROUP = ["store_nbr", "family"]
LAGS = [28, 35, 42, 56]
ROLL_WINDOWS = [7, 28, 56]

def add_lags(df: pd.DataFrame, lags: list[int] = LAGS) -> pd.DataFrame:
    df = df.sort_values(GROUP + ["date"]).copy()
    sales = df.sales.where(~df.is_closed)
    grouped = sales.groupby([df.store_nbr, df.family], observed=True)
    for lag in lags:
        df[f"sales_lag_{lag}"] = grouped.shift(lag)
    return df

def add_rolling(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(GROUP + ["date"]).copy()
    sales = df.sales.where(~df.is_closed)
    lagged = sales.groupby([df.store_nbr, df.family], observed=True).shift(HORIZON)
    rolled = lagged.groupby([df.store_nbr, df.family], observed=True)
    for window in ROLL_WINDOWS:
        df[f"sales_roll_mean_{window}"] = (
            rolled.rolling(window, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        )
    df["sales_roll_std_28"] = (
        rolled.rolling(28, min_periods=2).std().reset_index(level=[0, 1], drop=True)
    )
    return df

def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    date = df.date.dt
    df["dayofweek"] = date.dayofweek
    df["day"] = date.day
    df["month"] = date.month

    christmas = pd.to_datetime(date.year.astype(str) + "-12-25")
    christmas = christmas.where(df.date <= christmas, christmas + pd.DateOffset(years=1))
    df["days_to_christmas"] = (christmas - df.date).dt.days.clip(upper=60)
    return df

def add_promotion(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(GROUP + ["date"]).copy()
    by = [df.store_nbr, df.family]
    lagged = df.onpromotion.groupby(by, observed=True).shift(HORIZON)
    usual = (
        lagged.groupby(by, observed=True)
        .rolling(56, min_periods=7).mean().reset_index(level=[0, 1], drop=True)
    )
    df["promo_rel"] = df.onpromotion / (usual + 1)
    return df

CATEGORICAL = ["store_nbr", "family"]
LAG_COLS = [f"sales_lag_{lag}" for lag in LAGS]
ROLL_COLS = [f"sales_roll_mean_{w}" for w in ROLL_WINDOWS] + ["sales_roll_std_28"]
CALENDAR_COLS = ["dayofweek", "day", "month", "days_to_christmas"]
HOLIDAY_COLS = ["holiday_national", "holiday_local", "is_event"]
PROMO_COLS = ["onpromotion", "promo_rel"]

FEATURES = CATEGORICAL + LAG_COLS + ROLL_COLS + CALENDAR_COLS + HOLIDAY_COLS + PROMO_COLS

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    for step in (add_lags, add_rolling, add_calendar, add_promotion):
        df = step(df)
    return df.reset_index(drop=True)

def usable_rows(df: pd.DataFrame, history_start: pd.Timestamp) -> pd.DataFrame:
    start = history_start + pd.Timedelta(days=max(LAGS))
    return df[(df.date >= start) & ~df.is_closed]