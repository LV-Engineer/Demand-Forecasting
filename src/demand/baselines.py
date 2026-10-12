import numpy as np
import pandas as pd

from demand.data import KEYS

def seasonal_naive(train: pd.DataFrame, val: pd.DataFrame, period: int = 7) -> pd.DataFrame:
    days_ahead = (val.date - train.date.max()).dt.days
    shift = np.ceil(days_ahead / period).astype(int) * period
    source = val.assign(date=val.date - pd.to_timedelta(shift, unit="D"))
    known = train[KEYS + ["sales"]].rename(columns={"sales": "pred"})
    return source.merge(known, on=KEYS, how="left").assign(date=val.date.values)

def naive(train: pd.DataFrame, val: pd.DataFrame) -> pd.DataFrame:
    return seasonal_naive(train, val, period=1)

def seasonal_average(train: pd.DataFrame, val: pd.DataFrame, weeks: int = 4, agg: str = "median") -> pd.DataFrame:
    recent = train[(train.date > train.date.max() - pd.Timedelta(days=7 * weeks)) & ~train.is_closed]
    profile = (
        recent.assign(dow=recent.date.dt.dayofweek)
        .groupby(["store_nbr", "family", "dow"], observed=True)
        .sales.agg(agg).rename("pred").reset_index()
    )
    out = val.assign(dow=val.date.dt.dayofweek).merge(profile, on=["store_nbr", "family", "dow"], how="left")
    return out.drop(columns="dow")