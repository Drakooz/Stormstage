"""One call signature for the simulator, whichever forecast is plugged in.

make_forecaster(source, inc, zones, holdout_days) -> fn(now) -> (DataFrame[zone_id, expected_incidents], storm_factor)

source="standin": B's stand-in (common.standin_forecast); storm factor = incidents so far vs normal.
source="a":       A's forecast.forecast(day, hour, weather) gives the zone demand. The storm factor that
                  drives on-call call-ins is the LARGER of two signals:
                    weather lift = A's forecast with real weather / A's forecast with calm weather
                                   (same day and hours, so it isolates what the weather adds), and
                    nowcast      = reported incidents in the last 3 h vs normal for those hours
                                   (catches surges the weather alone does not explain).
                  If A's forecast cannot run for an hour (e.g. no training history on 1 Jan), that hour
                  falls back to B's stand-in and is counted in `fallbacks`.

Team rule: A works in UTC, B's simulator in Calgary local time. `now` here is naive Calgary local
time, so it is converted to UTC before calling A's forecast().
"""
from pathlib import Path

import pandas as pd

from common import A_ZONES, LOCAL_TZ, standin_forecast
from weather import weather_for

CALM = {"snowing": False, "temp_c": 5.0, "snow_last_6h": False}


def local_to_utc(ts) -> pd.Timestamp:
    """Naive Calgary local time -> UTC (DST gaps/overlaps resolved forward/first)."""
    return (pd.Timestamp(ts).tz_localize(LOCAL_TZ, nonexistent="shift_forward", ambiguous=True)
            .tz_convert("UTC"))


def make_forecaster(source, inc, zones, holdout_days=()):
    if source == "standin":
        return lambda now: standin_forecast(inc, zones, now, holdout_days=holdout_days)

    if source == "a":
        import forecast as A
        if not Path(A.ZONES_PATH).exists():          # older stub pointed outside the repo
            A.ZONES_PATH = A_ZONES
        fallbacks = []

        def fn(now):
            now = pd.Timestamp(now)
            utc = local_to_utc(now)
            day, hour = utc.date().isoformat(), int(utc.hour)
            standin, nowcast = standin_forecast(inc, zones, now, holdout_days=holdout_days)
            try:
                f = A.forecast(day, hour, weather_for(now))
                calm = A.forecast(day, hour, CALM)["expected_incidents"].sum()
            except ValueError:
                fallbacks.append(now)
                return standin, nowcast
            f = zones[["zone_id"]].merge(f, on="zone_id", how="left").fillna({"expected_incidents": 0.0})
            lift = float(f["expected_incidents"].sum() / calm) if calm > 0 else 1.0
            return f[["zone_id", "expected_incidents"]], max(lift, nowcast)

        fn.fallbacks = fallbacks
        return fn

    raise ValueError(f"unknown forecast source: {source}")
