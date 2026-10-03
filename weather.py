"""weather_for(ts) -> dict(snowing, temp_c, snow_last_6h), the input A's forecast() expects.

Reads data/processed/weather_hourly.csv when A adds it
(columns: timestamp, snowing, temp_c, snow_last_6h). Until then returns calm weather
and warns once, so B and C can still run end to end.
"""
import warnings
from pathlib import Path

import pandas as pd

WEATHER = Path(__file__).resolve().parent / "data" / "processed" / "weather_hourly.csv"
CALM = {"snowing": False, "temp_c": 5.0, "snow_last_6h": False}
_cache = None


def weather_for(ts) -> dict:
    global _cache
    if _cache is None:
        if WEATHER.exists():
            w = pd.read_csv(WEATHER, parse_dates=["timestamp"])
            _cache = w.set_index(w["timestamp"].dt.floor("h"))
        else:
            warnings.warn(f"{WEATHER} not found - using calm weather for every hour")
            _cache = False
    if _cache is False:
        return dict(CALM)
    key = pd.Timestamp(ts).floor("h")
    if key not in _cache.index:
        return dict(CALM)
    r = _cache.loc[key]
    return {"snowing": bool(r["snowing"]), "temp_c": float(r["temp_c"]), "snow_last_6h": bool(r["snow_last_6h"])}
