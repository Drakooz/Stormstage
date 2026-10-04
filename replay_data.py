"""C: read B's precomputed replays. Drop-in for mock_data.py (same kinds of calls, real numbers).

    from replay_data import (STORM_DAYS, POLICIES, COMPARISON_POLICIES, get_zones,
                             get_truck_positions, get_metrics, get_decision_log, get_incidents)

All times are local Calgary time. Run `python export_replay.py` once to (re)build the files.
"""
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPLAY = ROOT / "data" / "processed" / "replay"

STORM_DAYS = tuple(sorted(p.name for p in REPLAY.iterdir() if p.is_dir())) if REPLAY.exists() else ()
LABEL_TO_KEY = {"Fixed staging": "fixed", "Fixed yards (naive)": "yards", "Historical hotspots": "hotspot",
                "StormStage": "stormstage"}
POLICIES = tuple(LABEL_TO_KEY)
COMPARISON_POLICIES = ("Fixed staging", "StormStage")


def _key(policy):
    return LABEL_TO_KEY.get(policy, policy)


@lru_cache(maxsize=None)
def _meta(day):
    return json.loads((REPLAY / day / "metrics.json").read_text())


@lru_cache(maxsize=None)
def _csv(day, key, kind):
    path = REPLAY / day / f"{key}_{kind}.csv"
    df = pd.read_csv(path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    return df


def get_zones() -> pd.DataFrame:
    """Citywide grid zones used by the replays: zone_id, lat, lon, n (incidents in 2025)."""
    return pd.read_csv(ROOT / "data" / "processed" / "zones_grid.csv")


def get_truck_positions(day, policy, hour, minute=0) -> pd.DataFrame:
    """On-duty trucks at day hour:minute -> unit_id, zone_id, lat, lon, status.

    status: staged | responding | on_scene | returning | relocating
    """
    df = _csv(day, _key(policy), "trucks")
    t = pd.Timestamp(day) + pd.Timedelta(hours=hour, minutes=minute)
    snap = df[df["time"] == df.loc[df["time"] <= t, "time"].max()]
    return snap[["unit_id", "zone_id", "lat", "lon", "status"]].reset_index(drop=True)


def get_metrics(day, policy) -> dict:
    """avg_response_min, p90_response_min, pct_within_15, relocation_count, activations, truck_hours, incidents."""
    return dict(_meta(day)["policies"][_key(policy)])


def get_decision_log(day, policy, hour) -> list:
    """Plain-English actions up to hour:59, e.g. '07:00 — Unit 7 called in: incidents forecast x2.3 normal'."""
    acts = _csv(day, _key(policy), "actions")
    msgs = [f"00:00 — {len(get_truck_positions(day, policy, 0))} units staged ({get_metrics(day, policy)['label']})."]
    if len(acts):
        upto = acts[acts["time"] < pd.Timestamp(day) + pd.Timedelta(hours=hour + 1)]
        msgs += [f"{t:%H:%M} — {r}" for t, r in zip(upto["time"], upto["reason"])]
    return msgs


def get_incidents(day, policy, hour) -> pd.DataFrame:
    """Incidents that started before hour+1: time, lat, lon, unit_id, response_min."""
    df = _csv(day, _key(policy), "incidents")
    return df[df["time"] < pd.Timestamp(day) + pd.Timedelta(hours=hour + 1)].reset_index(drop=True)


if __name__ == "__main__":
    d = STORM_DAYS[0]
    for p in COMPARISON_POLICIES:
        print(p, get_metrics(d, p))
        print(get_truck_positions(d, p, 15).head(), "\n")
    print("\n".join(get_decision_log(d, "StormStage", 9)))
