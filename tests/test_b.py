"""Sanity tests for B's placement + simulator. Run: python -m pytest -q"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import simulate as S  # noqa: E402
from forecast_adapter import make_forecaster  # noqa: E402
from place import expected_cost, place_trucks  # noqa: E402


@pytest.fixture(scope="module")
def world():
    inc, zones, T = S.setup("grid")
    return inc, zones, T, make_forecaster("standin", inc, zones, holdout_days=S.DEMO_DAYS)


def test_place_beats_random():
    rng = np.random.default_rng(0)
    pts = rng.uniform(0, 10, size=(40, 2))
    T = np.linalg.norm(pts[:, None] - pts[None], axis=2)
    demand = rng.uniform(0, 1, size=40)
    sites, _ = place_trucks(demand, T, 4)
    random_sites = list(rng.choice(40, 4, replace=False))
    assert len(set(sites)) == 4
    assert expected_cost(sites, demand, T) <= expected_cost(random_sites, demand, T)


def test_move_penalty_blocks_small_moves():
    T = np.array([[0, 1, 9], [1, 0, 9], [9, 9, 0]], float)
    demand = np.array([1.0, 1.1, 0.0])
    _, reasons = place_trucks(demand, T, 1, current=[0], move_penalty_min=5.0)
    assert reasons == []                     # moving 0 -> 1 saves only ~0.1 expected min


@pytest.mark.parametrize("policy", ["yards", "fixed", "hotspot", "stormstage"])
def test_every_incident_served(world, policy):
    inc, zones, T, fc = world
    day = S.DEMO_DAYS[0]
    log, moves, th = S.simulate(inc, zones, T, day, policy, fc)
    assert len(log) == (inc["day"] == pd.Timestamp(day)).sum()
    assert (log["response_min"] >= 0).all()
    assert th >= 24 * S.K - 1e-6


def test_forecast_never_peeks(world):
    inc, zones, T, fc = world
    now = pd.Timestamp("2025-02-04 09:00")
    a, fa = fc(now)
    later = inc.copy()
    later.loc[later["start_dt"] >= now, ["lat", "lon"]] = (51.0, -114.0)   # scramble the future
    fc2 = make_forecaster("standin", later, zones, holdout_days=S.DEMO_DAYS)
    b, fb = fc2(now)
    assert fa == fb
    assert np.allclose(a["expected_incidents"], b["expected_incidents"])


def test_stormstage_calls_in_trucks_on_storm_day(world):
    inc, zones, T, fc = world
    _, moves, th = S.simulate(inc, zones, T, "2025-02-04", "stormstage", fc)
    assert (moves["action"] == "activate").any()
    assert th > 24 * S.K


def test_time_boundary(tmp_path, monkeypatch):
    import weather
    from forecast_adapter import local_to_utc
    # winter: MST = UTC-7; summer: MDT = UTC-6
    assert local_to_utc("2025-02-04 17:00").hour == 0
    assert local_to_utc("2025-07-15 17:00").hour == 23
    f = tmp_path / "w.csv"
    pd.DataFrame({"timestamp": ["2025-02-05T00:00:00Z", "2025-07-15T23:00:00Z"],
                  "snowing": [True, False], "temp_c": [-12.0, 24.0],
                  "snow_last_6h": [True, False]}).to_csv(f, index=False)
    monkeypatch.setattr(weather, "WEATHER", f)
    monkeypatch.setattr(weather, "_cache", None)
    assert weather.weather_for("2025-02-04 17:30")["snowing"] is True      # 00:00 UTC = 17:00 MST
    assert weather.weather_for("2025-07-15 17:10")["temp_c"] == 24.0        # 23:00 UTC = 17:00 MDT
