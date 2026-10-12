import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from demand.config import ROOT

def get_engine():
    load_dotenv(ROOT / ".env")
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    return create_engine(f"postgresql+psycopg://{user}:{password}@localhost:5432/{db}")

def load_subset() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM subset_full", get_engine(), parse_dates=["date"])

KEYS = ["store_nbr", "family", "date"]
STATIC_COLS = ["city", "state", "type", "cluster"]
CATEGORY_COLS = ["store_nbr", "family", *STATIC_COLS]
FLAG_COLS = ["holiday_local", "is_event"]

def clean(df: pd.DataFrame) -> pd.DataFrame:
    full = pd.date_range(df.date.min(), df.date.max())

    # oil price by calendar day (forward fill is causal)
    oil_by_date = (
        df.dropna(subset=["dcoilwtico"]).drop_duplicates("date")
        .set_index("date").dcoilwtico.reindex(full).ffill().bfill()
    )

    # one row per (store, family, day)
    series = df[["store_nbr", "family"]].drop_duplicates()
    grid = series.merge(pd.DataFrame({"date": full}), how="cross")
    df = grid.merge(df, on=KEYS, how="left")
    df["is_closed"] = df.sales.isna()

    # fill rows added for missing days
    static = df.dropna(subset=["city"]).drop_duplicates("store_nbr").set_index("store_nbr")
    for col in STATIC_COLS:
        df[col] = df[col].fillna(df.store_nbr.map(static[col]))
    df["sales"] = df.sales.fillna(0)
    df["onpromotion"] = df.onpromotion.fillna(0)
    df[FLAG_COLS] = df[FLAG_COLS].fillna(False)
    df["dcoilwtico"] = df.date.map(oil_by_date)

    # days with zero total sales are closed days
    total = df.groupby("date").sales.sum()
    df.loc[df.date.isin(total[total == 0].index), "is_closed"] = True
    df["holiday_national"] = df.holiday_national.fillna(False) | df.is_closed

    df = df.drop(columns="holiday_regional")
    df[CATEGORY_COLS] = df[CATEGORY_COLS].astype("category")
    df[FLAG_COLS + ["holiday_national"]] = df[FLAG_COLS + ["holiday_national"]].astype(bool)
    df = df.astype({"sales": "float32", "onpromotion": "int32", "dcoilwtico": "float32"})
    return df.sort_values(KEYS).reset_index(drop=True)