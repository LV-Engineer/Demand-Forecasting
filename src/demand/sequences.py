import numpy as np
import pandas as pd

from demand.features import GROUP

def day_features(df: pd.DataFrame) -> np.ndarray:
    day = df.date.dt
    dow = 2 * np.pi * day.dayofweek / 7
    month = 2 * np.pi * (day.month - 1) / 12
    return np.column_stack([
        np.sin(dow), np.cos(dow), np.sin(month), np.cos(month),
        df.days_to_christmas / 60,
        df.holiday_national, df.holiday_local, df.is_event, df.is_closed,
        np.log1p(df.onpromotion) / 5,
    ]).astype("float32")

def make_windows(df: pd.DataFrame, length: int = 56, horizon: int = 28) -> dict:
    df = df.sort_values(GROUP + ["date"]).reset_index(drop=True)
    feats = day_features(df)
    sales = df.sales.to_numpy("float32")
    closed = df.is_closed.to_numpy()
    dates = df.date.to_numpy()

    x_past, x_future, y, mask, level, series, end_date = [], [], [], [], [], [], []

    for sid, rows in enumerate(df.groupby(GROUP, observed=True).indices.values()):
        s, c, f, d = sales[rows], closed[rows], feats[rows], dates[rows]
        for end in range(length - 1, len(rows) - horizon):
            past = slice(end - length + 1, end + 1)
            future = slice(end + 1, end + horizon + 1)
            open_past = ~c[past]
            scale = max(float(s[past][open_past].mean()) if open_past.any() else 1.0, 1.0)

            ratio = np.where(c[past], 0.0, s[past] / scale)
            x_past.append(np.column_stack([ratio, f[past]]))
            x_future.append(f[future])
            y.append(s[future] / scale)
            mask.append(~c[future])
            level.append(scale)
            series.append(sid)
            end_date.append(d[end])

    return {
        "x_past": np.asarray(x_past, dtype="float32"),
        "x_future": np.asarray(x_future, dtype="float32"),
        "y": np.asarray(y, dtype="float32"),
        "mask": np.asarray(mask),
        "level": np.asarray(level, dtype="float32"),
        "series": np.asarray(series),
        "end_date": np.asarray(end_date),
    }