"""weather_for(ts) -> dict(snowing, temp_c, snow_last_6h), the input A's forecast() expects.

Team rule: raw data is UTC; A keeps it UTC; B converts to Calgary local time at the simulator boundary.
So data/processed/weather_hourly.csv holds UTC timestamps (column `timestamp`, or ECCC's
`Date/Time (UTC)`), and this module converts them to America/Edmonton on read.
`ts` passed in is naive Calgary local time (what the simulator uses). Until the file exists,
returns calm weather and warns once, so B and C can still run end to end.
"""
import warnings
from pathlib import Path

import pandas as pd

from common import LOCAL_TZ

WEATHER = Path(__file__).resolve().parent / "data" / "processed" / "weather_hourly.csv"
CALM = {"snowing": False, "temp_c": 5.0, "snow_last_6h": False}
_cache = None


def utc_to_local(col) -> pd.Series:
    """UTC timestamps (strings, naive, or tz-aware) -> naive Calgary local time (MST/MDT handled)."""
    return pd.to_datetime(col, utc=True).dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)


def load_weather(path=None) -> pd.DataFrame:
    w = pd.read_csv(path or WEATHER)
    col = "timestamp" if "timestamp" in w.columns else "Date/Time (UTC)"
    w["local"] = utc_to_local(w[col]).dt.floor("h")
    return w.drop_duplicates("local", keep="last").set_index("local")


def weather_for(ts) -> dict:
    global _cache
    if _cache is None:
        if WEATHER.exists():
            _cache = load_weather()
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
