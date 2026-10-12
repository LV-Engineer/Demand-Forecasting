import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

def wape(y_true, y_pred) -> float:
    return float(mean_absolute_error(y_true, y_pred) / np.mean(np.abs(y_true)))

def evaluate(y_true, y_pred) -> dict:
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": root_mean_squared_error(y_true, y_pred),
        "WAPE": wape(y_true, y_pred),
    }