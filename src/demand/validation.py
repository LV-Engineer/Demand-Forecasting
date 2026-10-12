import numpy as np
import pandas as pd

from demand.config import HORIZON

def split_holdout(df: pd.DataFrame, horizon: int = HORIZON):
    cutoff = df.date.max() - pd.Timedelta(days=horizon)
    return df[df.date <= cutoff], df[df.date > cutoff]

def walk_forward_splits(dates, n_folds: int = 8, horizon: int = HORIZON, min_train: int = 365):
    days = pd.DatetimeIndex(np.sort(pd.unique(dates)))
    for k in reversed(range(n_folds)):
        val_end = len(days) - k * horizon
        val_start = val_end - horizon
        if val_start < min_train:
            raise ValueError(
                f"fold has {val_start} training days, need at least {min_train}; "
                "reduce n_folds or horizon"
            )
        yield days[:val_start], days[val_start:val_end]