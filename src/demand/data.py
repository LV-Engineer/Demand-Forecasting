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