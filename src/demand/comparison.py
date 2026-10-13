import numpy as np
import pandas as pd

from demand.baselines import seasonal_average
from demand.data import KEYS
from demand.features import usable_rows, GROUP
from demand.models import design
from demand.validation import walk_forward_splits
from demand.config import SEED
from demand.nets import fit_net, predict_net, select_windows

COLUMNS = KEYS + ["sales", "pred", "fold", "model"]

def make_folds(train_part: pd.DataFrame, holdout: pd.DataFrame) -> list:
    folds = list(walk_forward_splits(train_part.date))
    last = (
        pd.DatetimeIndex(np.sort(train_part.date.unique())),
        pd.DatetimeIndex(np.sort(holdout.date.unique())),
    )
    return folds + [last]

def baseline_predictions(features, folds, history_start, name="seasonal_median_4w"):
    parts = []
    for fold, (train_dates, val_dates) in enumerate(folds, 1):
        train = features[features.date.isin(train_dates)]
        val = usable_rows(features[features.date.isin(val_dates)], history_start)
        pred = seasonal_average(train, val)
        parts.append(pred.assign(fold=fold, model=name)[COLUMNS])
    return tidy(pd.concat(parts, ignore_index=True))

def tabular_predictions(make_model, features, folds, history_start, name):
    parts = []
    for fold, (train_dates, val_dates) in enumerate(folds, 1):
        train = usable_rows(features[features.date.isin(train_dates)], history_start)
        val = usable_rows(features[features.date.isin(val_dates)], history_start)
        model = make_model()
        model.fit(design(train), train.sales)
        pred = model.predict(design(val)).clip(min=0)
        parts.append(val.assign(pred=pred, fold=fold, model=name)[COLUMNS])
    return tidy(pd.concat(parts, ignore_index=True))

def tidy(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.astype({"store_nbr": "int64", "family": str})


def net_predictions(cell, windows, features, folds, name, seed=SEED):
    keys = list(features.groupby(GROUP, observed=True).indices.keys())
    parts = []
    for fold, (train_dates, val_dates) in enumerate(folds, 1):
        train_mask, stop_mask, valid_mask = select_windows(windows, train_dates[-1].to_datetime64())
        net, _ = fit_net(windows, train_mask, stop_mask, cell=cell, seed=seed)

        pred = predict_net(net, windows, valid_mask)
        actual = windows["y"][valid_mask] * windows["level"][valid_mask][:, None]
        series = windows["series"][valid_mask]
        days = len(val_dates)
        frame = pd.DataFrame({
            "date": np.tile(val_dates.to_numpy(), len(series)),
            "store_nbr": np.repeat([keys[s][0] for s in series], days),
            "family": np.repeat([keys[s][1] for s in series], days),
            "sales": actual.ravel(),
            "pred": pred.ravel(),
            "fold": fold,
            "model": name,
        })
        parts.append(frame[windows["mask"][valid_mask].ravel()])
    return tidy(pd.concat(parts, ignore_index=True))[COLUMNS]