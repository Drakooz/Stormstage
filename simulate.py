"""B: replay a real day of incidents under a staging policy and score response times.

Policies (same simulator, same incidents, same drive-time model)
  yards      - NAIVE baseline: K trucks parked all day at 6 hand-picked yards around the city
  fixed      - STRONG baseline: K trucks placed once on whole-year demand (best static plan)
  hotspot    - K trucks placed once on LAST WEEK's busiest zones
  stormstage - K base trucks re-placed hourly from the forecast, PLUS up to EXTRA on-call trucks
               activated when the storm factor (forecast vs normal) reaches SURGE_AT

Run:
  python simulate.py                              # stand-in forecast, citywide grid zones
  python simulate.py --forecast a --zones a       # A's forecast() and A's zones.csv
"""
import argparse

import numpy as np
import pandas as pd

from common import (SCENE_MIN, a_zones, assign_zones, drive_min, grid_zones, load_incidents,
                    zone_matrix)
from forecast_adapter import make_forecaster
from place import place_trucks

K = 6                    # trucks on duty all day
EXTRA = 3                # on-call trucks StormStage may activate
SURGE_AT = 1.5           # storm factor that triggers on-call trucks
MOVE_PENALTY_MIN = 3.0   # a relocation must save at least this many expected minutes
DEMO_DAYS = ["2025-02-04", "2025-02-14", "2025-11-24"]
YARDS = [(51.045, -114.070), (51.100, -114.150), (51.090, -113.980),
         (50.980, -114.120), (50.950, -114.030), (51.150, -114.070)]


def _nearest_zone(zones, lat, lon):
    return int(drive_min(zones["lat"].to_numpy(), zones["lon"].to_numpy(), lat, lon).argmin())


def fixed_sites(inc, zones, T, holdout_days, k):
    hist = inc[~inc["day"].isin([pd.Timestamp(d) for d in holdout_days])]
    demand = zones["zone_id"].map(hist.groupby("zone_id").size()).fillna(0).to_numpy()
    return place_trucks(demand, T, k)[0]


def hotspot_sites(inc, zones, day, k):
    last_week = inc[(inc["day"] >= day - pd.Timedelta(days=7)) & (inc["day"] < day)]
    top = last_week.groupby("zone_id").size().sort_values(ascending=False)
    idx = {z: i for i, z in enumerate(zones["zone_id"])}
    sites = [idx[z] for z in top.index if z in idx][:k]
    for z in zones["n"].to_numpy().argsort()[::-1]:
        if len(sites) >= k:
            break
        if int(z) not in sites:
            sites.append(int(z))
    return sites


def simulate(inc, zones, T, day, policy, forecaster, holdout_days=DEMO_DAYS, k=None, extra=None):
    """Returns (log, moves, truck_hours).

    log:   one row per incident  - time, lat, lon, truck, response_min
    moves: one row per action    - time, truck, action (move / activate / stand down), to_zone, reason
    truck_hours: on-duty truck-hours that day (the cost side)
    """
    k = K if k is None else k
    extra = EXTRA if extra is None else extra
    day = pd.Timestamp(day)
    todays = inc[inc["day"] == day].sort_values("start_dt")
    zlat, zlon = zones["lat"].to_numpy(), zones["lon"].to_numpy()
    n_max = k + (extra if policy == "stormstage" else 0)

    if policy == "yards":
        home = [_nearest_zone(zones, la, lo) for la, lo in YARDS[:k]]
    elif policy == "fixed":
        home = fixed_sites(inc, zones, T, holdout_days, k)
    elif policy == "hotspot":
        home = hotspot_sites(inc, zones, day, k)
    elif policy == "stormstage":
        f, _ = forecaster(day)
        home = place_trucks(f["expected_incidents"].to_numpy(), T, k)[0]
        home += [home[0]] * extra          # on-call trucks wait at the first site until activated
    else:
        raise ValueError(policy)

    active = np.array([True] * k + [False] * (n_max - k))
    on_since = np.zeros(n_max)
    duty_min = 0.0
    free_at = np.zeros(n_max)                                # minute of day when free
    last = [(zlat[h], zlon[h]) for h in home]                # where it finished its last job
    back_done = np.zeros(n_max)                              # when it is back at its staging zone
    log, moves = [], []

    def where(i, t):
        return (zlat[home[i]], zlon[home[i]]) if t >= back_done[i] else last[i]

    def replan(hour):
        nonlocal duty_min
        now = day + pd.Timedelta(hours=hour)
        f, sf = forecaster(now)
        want = k + (extra if sf >= SURGE_AT else 0)
        for i in range(k, n_max):                            # activate / stand down on-call trucks
            if i < want and not active[i]:
                active[i] = True
                on_since[i] = hour * 60.0
                moves.append({"time": now, "truck": i, "action": "activate", "to_zone": zones["zone_id"].iat[home[i]],
                              "reason": f"Unit {i + 1} called in: incidents forecast x{sf:.1f} normal"})
            elif i >= want and active[i] and free_at[i] <= hour * 60.0:
                active[i] = False
                duty_min += hour * 60.0 - on_since[i]
                moves.append({"time": now, "truck": i, "action": "stand down", "to_zone": zones["zone_id"].iat[home[i]],
                              "reason": f"Unit {i + 1} stood down: forecast back to x{sf:.1f} normal"})
        ids = [i for i in range(n_max) if active[i]]
        new, reasons = place_trucks(f["expected_incidents"].to_numpy(), T, len(ids),
                                    current=[home[i] for i in ids], move_penalty_min=MOVE_PENALTY_MIN)
        for r in reasons:
            i, to = ids[r["truck"]], r["to"]
            here = where(i, hour * 60.0)
            last[i] = here
            back_done[i] = max(free_at[i], hour * 60.0) + drive_min(here[0], here[1], zlat[to], zlon[to])
            moves.append({"time": now, "truck": i, "action": "move", "to_zone": zones["zone_id"].iat[to],
                          "reason": f"Unit {i + 1} -> zone {zones['zone_id'].iat[to]}: forecast "
                                    f"{r['demand_to']} incidents next 3 h, saves ~{r['saves_min']} "
                                    f"expected min (x{sf:.1f} normal)"})
        for j, i in enumerate(ids):
            home[i] = new[j]

    next_replan = 1
    for _, row in todays.iterrows():
        t = (row["start_dt"] - day).total_seconds() / 60.0
        while policy == "stormstage" and next_replan * 60 <= t:
            replan(next_replan)
            next_replan += 1
        best, best_arrive = None, np.inf
        for j in range(n_max):
            if not active[j]:
                continue
            ready = max(free_at[j], t)
            loc = where(j, ready)
            a = ready + drive_min(loc[0], loc[1], row["lat"], row["lon"])
            if a < best_arrive:
                best, best_arrive = j, a
        i = best
        free_at[i] = best_arrive + SCENE_MIN                 # free after the scene, heads back to staging
        last[i] = (row["lat"], row["lon"])
        back_done[i] = free_at[i] + drive_min(row["lat"], row["lon"], zlat[home[i]], zlon[home[i]])
        log.append({"incident_id": row["incident_id"], "time": row["start_dt"], "lat": row["lat"],
                    "lon": row["lon"], "truck": i, "response_min": round(best_arrive - t, 1)})

    for i in range(n_max):                                   # close out the day
        if active[i]:
            duty_min += 24 * 60.0 - on_since[i]
    return pd.DataFrame(log), pd.DataFrame(moves), round(duty_min / 60.0, 1)


def metrics(log):
    r = log["response_min"]
    return {"incidents": len(r), "avg_min": round(r.mean(), 1),
            "p90_min": round(r.quantile(0.9), 1),
            "pct_within_15": round(100 * (r <= 15).mean(), 1)}


def setup(zone_source="grid"):
    inc = load_incidents()
    zones = a_zones() if zone_source == "a" else grid_zones(inc)
    inc, zones = assign_zones(inc, zones)
    return inc, zones, zone_matrix(zones)


def main(forecast_source="standin", zone_source="grid", days=None):
    inc, zones, T = setup(zone_source)
    days = days or DEMO_DAYS
    forecaster = make_forecaster(forecast_source, inc, zones, holdout_days=DEMO_DAYS)
    near = (inc["dist_km"] <= 2.0).mean()
    print(f"{len(inc)} incidents, {len(zones)} zones ({zone_source}), forecast={forecast_source}, "
          f"{near:.0%} of incidents within 2 km of a zone centre, "
          f"{K} trucks on duty (+{EXTRA} on call for StormStage)\n")
    rows = []
    runs = [("yards", K), ("fixed", K), ("hotspot", K), ("stormstage", K), ("fixed", K + EXTRA)]
    for d in days:
        for p, k in runs:
            log, moves, th = simulate(inc, zones, T, d, p, forecaster, k=k)
            name = p if k == K else f"{p} x{k} all day"
            rows.append({"day": d, "policy": name, **metrics(log), "truck_hours": th, "actions": len(moves)})
            if p == "stormstage" and d == days[0] and len(moves):
                print("StormStage actions on", d)
                print(moves[["time", "reason"]].head(8).to_string(index=False), "\n")
    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    print("\nMean over days:")
    print(res.groupby("policy", sort=False)[["avg_min", "p90_min", "pct_within_15", "truck_hours"]]
          .mean().round(1).to_string())
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast", choices=["standin", "a"], default="standin")
    ap.add_argument("--zones", choices=["grid", "a"], default="grid")
    ap.add_argument("--days", nargs="*")
    a = ap.parse_args()
    main(a.forecast, a.zones, a.days)
