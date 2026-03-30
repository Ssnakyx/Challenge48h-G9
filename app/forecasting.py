"""
Very small forecasting module that relies on linear regression.
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def build_forecasts(indices_df: pd.DataFrame, horizon_hours: int = 6) -> pd.DataFrame:
    """Train a linear regression per station and predict N hours ahead."""

    if indices_df.empty:
        return pd.DataFrame()

    results: List[dict] = []

    for station_code, group in indices_df.groupby("station_code"):
        group = group.sort_values("timestamp")
        if len(group) < 5:
            continue
        group = group.copy()
        base_time = group["timestamp"].min()
        group["time_idx"] = (
            (group["timestamp"] - base_time).dt.total_seconds() / 3600.0
        )
        X = group[["time_idx"]].values
        y = group["composite_index"].values
        model = LinearRegression()
        model.fit(X, y)
        last_timestamp = group["timestamp"].iloc[-1]
        last_idx = group["time_idx"].iloc[-1]
        for step in range(1, horizon_hours + 1):
            target_idx = last_idx + step
            predicted = float(np.clip(model.predict([[target_idx]])[0], 0, 100))
            results.append(
                {
                    "station_code": station_code,
                    "station_name": group["station_name"].iloc[0],
                    "target_timestamp": last_timestamp + pd.Timedelta(hours=step),
                    "predicted_index": predicted,
                    "horizon_hours": step,
                    "model_version": "linreg-1",
                }
            )

    return pd.DataFrame(results)
