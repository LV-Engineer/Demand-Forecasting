import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from demand.features import CATEGORICAL, FEATURES
from demand.config import SEED

RIDGE_CATEGORICAL = CATEGORICAL + ["dayofweek", "month"]
RIDGE_NUMERIC = [f for f in FEATURES if f not in RIDGE_CATEGORICAL]

def design(df: pd.DataFrame, features=FEATURES) -> pd.DataFrame:
    X = df[features].copy()
    flags = X.select_dtypes("bool").columns
    X[flags] = X[flags].astype(int)
    return X

def make_ridge(alpha: float = 1.0) -> Pipeline:
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    prep = ColumnTransformer([
        ("num", numeric, RIDGE_NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore"), RIDGE_CATEGORICAL),
    ])
    return Pipeline([("prep", prep), ("model", Ridge(alpha=alpha))])

def make_xgb(**params) -> XGBRegressor:
    defaults = dict(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        enable_categorical=True,
        tree_method="hist",
        random_state=SEED,
        n_jobs=-1,
    )
    return XGBRegressor(**{**defaults, **params})

def make_lgbm(**params) -> LGBMRegressor:
    defaults = dict(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.8,
        random_state=SEED,
        n_jobs=-1,
        verbose=-1,
    )
    return LGBMRegressor(**{**defaults, **params})

class ScaledTarget:
    def __init__(self, make_model, scale_col: str = "sales_roll_mean_56", weighted: bool = False):
        self.model = make_model()
        self.scale_col = scale_col
        self.weighted = weighted

    def _scale(self, X):
        return X[self.scale_col].clip(lower=1)

    def fit(self, X, y):
        scale = self._scale(X)
        if self.weighted:
            self.model.fit(X, y / scale, sample_weight=scale)
        else:
            self.model.fit(X, y / scale)
        return self

    def predict(self, X):
        return self.model.predict(X) * self._scale(X).to_numpy()

    @property
    def feature_importances_(self):
        return self.model.feature_importances_