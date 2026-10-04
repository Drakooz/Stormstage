"""Shared helpers (B): incidents, zones, drive times, and a stand-in forecast.

Zones can come from A (`zones.csv`, columns zone_id, lat, lon) or from a citywide
~2 km grid built from the incidents. Incidents are assigned to their NEAREST zone centre.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
INCIDENTS = ROOT / "data" / "raw" / "calgary_traffic_incidents_2025.csv"
A_ZONES = ROOT / "zones.csv"

# ---- fixed assumptions (change only as a team) ----------------------------
LAT0, LON0 = 50.84, -114.32      # citywide grid origin (SW corner)
DLAT, DLON = 0.018, 0.028        # ~2 km x ~2 km cells in Calgary
SPEED_KMH = 40.0                 # snow-day average speed
DETOUR = 1.3                     # straight line -> road distance
SCENE_MIN = 30.0                 # time on scene per incident
MIN_ZONE_INCIDENTS = 5           # citywide grid: drop near-empty cells


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def drive_min(lat1, lon1, lat2, lon2):
    return haversine_km(lat1, lon1, lat2, lon2) * DETOUR / SPEED_KMH * 60.0


def load_incidents(path=INCIDENTS) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["start_dt"])
    df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
    df["day"] = df["start_dt"].dt.normalize()
    df["how"] = df["start_dt"].dt.dayofweek * 24 + df["start_dt"].dt.hour  # hour of week
    df = df.sort_values("start_dt").reset_index(drop=True)
    df["incident_id"] = np.arange(len(df))
    df["quadrant"] = df["quadrant"].astype(str).str.strip().str.upper()
    return df[["incident_id", "start_dt", "day", "how", "lat", "lon", "quadrant"]]


def grid_zones(inc: pd.DataFrame) -> pd.DataFrame:
    """Citywide ~2 km grid, keeping cells with at least MIN_ZONE_INCIDENTS incidents."""
    row = ((inc["lat"] - LAT0) // DLAT).astype(int)
    col = ((inc["lon"] - LON0) // DLON).astype(int)
    cells = pd.DataFrame({"row": row, "col": col}).value_counts().rename("n").reset_index()
    cells = cells[cells["n"] >= MIN_ZONE_INCIDENTS].sort_values(["row", "col"]).reset_index(drop=True)
    return pd.DataFrame({"zone_id": [f"G{r:02d}_{c:02d}" for r, c in zip(cells["row"], cells["col"])],
                         "lat": LAT0 + (cells["row"] + 0.5) * DLAT,
                         "lon": LON0 + (cells["col"] + 0.5) * DLON})


def a_zones() -> pd.DataFrame:
    return pd.read_csv(A_ZONES)[["zone_id", "lat", "lon"]]


def assign_zones(inc: pd.DataFrame, zones: pd.DataFrame) -> pd.DataFrame:
    """Add zone_id (nearest zone centre) and dist_km to each incident; add n (count) to zones."""
    d = haversine_km(inc["lat"].to_numpy()[:, None], inc["lon"].to_numpy()[:, None],
                     zones["lat"].to_numpy()[None, :], zones["lon"].to_numpy()[None, :])
    inc = inc.copy()
    inc["zone_id"] = zones["zone_id"].to_numpy()[d.argmin(axis=1)]
    inc["dist_km"] = d.min(axis=1)
    zones = zones.copy()
    zones["n"] = zones["zone_id"].map(inc["zone_id"].value_counts()).fillna(0).astype(int)
    quad = inc.groupby("zone_id")["quadrant"].agg(lambda q: q.mode().iat[0] if len(q) else "")
    zones["quadrant"] = zones["zone_id"].map(quad).fillna("")
    zones["name"] = np.where(zones["quadrant"] != "", zones["zone_id"] + " (" + zones["quadrant"] + ")",
                             zones["zone_id"])
    return inc, zones


def zone_matrix(zones: pd.DataFrame) -> np.ndarray:
    """Zone-to-zone drive minutes, shape (Z, Z)."""
    la, lo = zones["lat"].to_numpy(), zones["lon"].to_numpy()
    return drive_min(la[:, None], lo[:, None], la[None, :], lo[None, :])


def standin_forecast(inc, zones, now, horizon_h=3, holdout_days=(), today_weight_k=15.0, smooth_km=2.5):
    """B's stand-in until A's model is ready. Returns (DataFrame[zone_id, expected_incidents], storm_factor).

    expected(zone) = city rate for the next hours-of-week (history)
                     x storm factor (today's last 3 h vs history)
                     x zone share, blended from history and TODAY's incidents so far.
    Uses ONLY incidents that started before `now` (no peeking).
    """
    today = now.normalize()
    excluded = {pd.Timestamp(d) for d in holdout_days} | {today}
    hist = inc[~inc["day"].isin(excluded)]
    n_weeks = max(hist["day"].nunique() / 7.0, 1.0)
    city_rate = hist.groupby("how").size() / n_weeks

    def how_of(ts):
        return int(ts.dayofweek * 24 + ts.hour)

    ahead = sum(city_rate.get(how_of(now + pd.Timedelta(hours=h)), 0.0) for h in range(horizon_h))
    seen = inc[(inc["start_dt"] >= now - pd.Timedelta(hours=3)) & (inc["start_dt"] < now)]
    expected_seen = sum(city_rate.get(how_of(now - pd.Timedelta(hours=h)), 0.0) for h in range(1, 4))
    factor = 1.0 if expected_seen < 1 else float(np.clip((len(seen) + 1) / (expected_seen + 1), 0.5, 5.0))

    share = zones["zone_id"].map(hist.groupby("zone_id").size()).fillna(0).to_numpy(float)
    share /= max(share.sum(), 1e-9)
    so_far = inc[(inc["day"] == today) & (inc["start_dt"] < now)]
    if len(so_far):
        d = haversine_km(zones["lat"].to_numpy()[:, None], zones["lon"].to_numpy()[:, None],
                         so_far["lat"].to_numpy()[None, :], so_far["lon"].to_numpy()[None, :])
        today_share = np.exp(-(d / smooth_km) ** 2).sum(axis=1)
        today_share /= max(today_share.sum(), 1e-9)
        w = len(so_far) / (len(so_far) + today_weight_k)
        share = (1 - w) * share + w * today_share

    out = zones[["zone_id"]].copy()
    out["expected_incidents"] = ahead * factor * share
    return out, factor
