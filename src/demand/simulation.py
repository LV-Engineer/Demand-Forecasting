import pandas as pd

KEYS = ["model", "fold", "store_nbr", "family"]

def period_table(predictions: pd.DataFrame, period: int = 7) -> pd.DataFrame:
    df = predictions.copy()
    start = df.groupby("fold").date.transform("min")
    df["period"] = (df.date - start).dt.days // period
    return df.groupby(KEYS + ["period"], as_index=False).agg(
        actual=("sales", "sum"), order=("pred", "sum")
    )

def add_costs(table: pd.DataFrame, under: float = 3.0, over: float = 1.0) -> pd.DataFrame:
    short = (table.actual - table.order).clip(lower=0)
    excess = (table.order - table.actual).clip(lower=0)
    return table.assign(short=short, excess=excess, cost=under * short + over * excess)

def summarize(table: pd.DataFrame, reference: str = "seasonal_median_4w") -> pd.DataFrame:
    total = table.groupby("model")[["actual", "short", "excess", "cost"]].sum()
    total["fill_rate"] = 1 - total.short / total.actual
    total["cost_per_unit"] = total.cost / total.actual
    total["cost_vs_reference"] = 1 - total.cost / total.loc[reference, "cost"]
    return total.sort_values("cost")

def sensitivity(table: pd.DataFrame, ratios=(1, 2, 3, 4, 5)) -> pd.DataFrame:
    return pd.DataFrame({
        f"{ratio}:1": summarize(add_costs(table, under=ratio))["cost_vs_reference"]
        for ratio in ratios
    }).round(3)

def scale_orders(table: pd.DataFrame, factor: float) -> pd.DataFrame:
    return table.assign(order=table.order * factor)

def best_factor(table: pd.DataFrame, factors, under: float = 3.0, over: float = 1.0):
    cost = pd.DataFrame({
        factor: add_costs(scale_orders(table, factor), under, over).groupby("model").cost.sum()
        for factor in factors
    })
    return cost.idxmin(axis=1), cost