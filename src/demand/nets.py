import copy

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from demand.config import HORIZON, SEED

INPUTS = ("x_past", "x_future", "series")

class ForecastNet(nn.Module):
    def __init__(self, cell: str = "lstm", n_past: int = 11, n_future: int = 10,
                 n_series: int = 25, horizon: int = 28, hidden: int = 64,
                 embed: int = 8, dropout: float = 0.2):
        super().__init__()
        rnn = {"rnn": nn.RNN, "lstm": nn.LSTM}[cell]
        self.embed = nn.Embedding(n_series, embed)
        self.rnn = rnn(n_past, hidden, batch_first=True)
        self.head = nn.Sequential(
            nn.Linear(hidden + embed + horizon * n_future, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, horizon),
        )

    def forward(self, x_past, x_future, series):
        out, _ = self.rnn(x_past)
        summary = out[:, -1]
        z = torch.cat([summary, self.embed(series), x_future.flatten(1)], dim=1)
        return self.head(z)

def select_windows(windows: dict, train_last, horizon: int = HORIZON, inner: int = 14):
    end = windows["end_date"]
    last_end = train_last - np.timedelta64(horizon, "D")
    inner_start = last_end - np.timedelta64(inner - 1, "D")
    train = end <= inner_start - np.timedelta64(horizon, "D")
    stop = (end >= inner_start) & (end <= last_end)
    valid = end == train_last
    return train, stop, valid

def masked_l1(pred, y, mask):
    mask = mask.float()
    return ((pred - y).abs() * mask).sum() / mask.sum()

def fit_net(windows: dict, train_mask, stop_mask, cell: str = "lstm", epochs: int = 60,
            patience: int = 8, lr: float = 1e-3, weight_decay: float = 1e-4,
            batch_size: int = 128, seed: int = SEED, **net_params):
    torch.manual_seed(seed)
    data = {k: torch.as_tensor(windows[k]) for k in (*INPUTS, "y", "mask")}

    def part(mask):
        return [data[k][torch.as_tensor(mask)] for k in (*INPUTS, "y", "mask")]

    loader = DataLoader(TensorDataset(*part(train_mask)), batch_size=batch_size, shuffle=True)
    *stop_inputs, stop_y, stop_m = part(stop_mask)

    net = ForecastNet(cell, **net_params)
    optimizer = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=weight_decay)

    best, best_state, wait, history = float("inf"), None, 0, []
    for epoch in range(epochs):
        net.train()
        for x_past, x_future, series, y, mask in loader:
            optimizer.zero_grad()
            loss = masked_l1(net(x_past, x_future, series), y, mask)
            loss.backward()
            optimizer.step()

        net.eval()
        with torch.no_grad():
            stop_loss = masked_l1(net(*stop_inputs), stop_y, stop_m).item()
        history.append(stop_loss)

        if stop_loss < best:
            best, best_state, wait = stop_loss, copy.deepcopy(net.state_dict()), 0
        else:
            wait += 1
            if wait >= patience:
                break

    net.load_state_dict(best_state)
    return net, history


def predict_net(net, windows: dict, mask) -> np.ndarray:
    mask = torch.as_tensor(mask)
    net.eval()
    with torch.no_grad():
        ratio = net(*[torch.as_tensor(windows[k])[mask] for k in INPUTS]).numpy()
    return np.clip(ratio, 0, None) * windows["level"][mask][:, None]
