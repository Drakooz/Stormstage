"""A: forecast() and baseline_forecast().

STUB VERSION: returns fake but plausible numbers so B and C can build against
the real interface. Replace the body of forecast() with the Poisson model later.
DO NOT change function names or output column names.
"""
import numpy as np
import pandas as pd
from pathlib import Path

ZONES_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "zones.csv"


def _zones() -> pd.DataFrame:
    return pd.read_csv(ZONES_PATH)


def forecast(day, hour: int, weather: dict) -> pd.DataFrame:
    """Expected incidents per zone over the NEXT 3 hours.

    day:     date or 'YYYY-MM-DD'
    hour:    0-23, the hour we are forecasting from
    weather: dict with keys snowing (bool), temp_c (float), snow_last_6h (bool)
    returns: DataFrame[zone_id, expected_incidents]
    """
    zones = _zones()
    # Fixed per-zone base rate (stable across calls) so the stub is deterministic.
    rng = np.random.default_rng(42)
    base = rng.uniform(0.1, 0.6, size=len(zones))  # incidents per 3 h on a normal day

    # Fake storm multiplier, roughly the 4x spike from the data.
    mult = 1.0
    if weather.get("snowing"):
        mult *= 3.0
    if weather.get("temp_c", 5) < 0:
        mult *= 1.3
    if weather.get("snow_last_6h"):
        mult *= 1.2

    # Fake rush-hour bump.
    rush = 1.5 if hour in (7, 8, 16, 17, 18) else 1.0

    return pd.DataFrame({
        "zone_id": zones["zone_id"],
        "expected_incidents": np.round(base * mult * rush, 2),
    })


def baseline_forecast(day, hour: int) -> pd.DataFrame:
    """Baseline: same hour last week. STUB: flat low rate for now."""
    zones = _zones()
    return pd.DataFrame({"zone_id": zones["zone_id"], "expected_incidents": 0.3})


if __name__ == "__main__":
    calm = forecast("2025-02-04", 8, {"snowing": False, "temp_c": 3, "snow_last_6h": False})
    storm = forecast("2025-02-04", 8, {"snowing": True, "temp_c": -8, "snow_last_6h": True})
    print(calm.head(), "\n", storm.head())
