"""One call signature for the simulator, whichever forecast is plugged in.

make_forecaster(source, inc, zones, holdout_days) -> fn(now) -> (DataFrame[zone_id, expected_incidents], storm_factor)

source="standin": B's stand-in (common.standin_forecast)
source="a":       A's forecast.forecast(day, hour, weather); storm factor = forecast total / baseline_forecast total
"""
from pathlib import Path

import pandas as pd

from common import A_ZONES, standin_forecast
from weather import weather_for


def make_forecaster(source, inc, zones, holdout_days=()):
    if source == "standin":
        return lambda now: standin_forecast(inc, zones, now, holdout_days=holdout_days)

    if source == "a":
        import forecast as A
        if not Path(A.ZONES_PATH).exists():          # A's stub points two folders up; use repo zones.csv
            A.ZONES_PATH = A_ZONES

        def fn(now):
            now = pd.Timestamp(now)
            f = A.forecast(now.date().isoformat(), now.hour, weather_for(now))
            b = A.baseline_forecast(now.date().isoformat(), now.hour)
            f = zones[["zone_id"]].merge(f, on="zone_id", how="left").fillna({"expected_incidents": 0.0})
            factor = float(f["expected_incidents"].sum() / max(b["expected_incidents"].sum(), 1e-9))
            return f[["zone_id", "expected_incidents"]], factor
        return fn

    raise ValueError(f"unknown forecast source: {source}")
