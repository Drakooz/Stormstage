"""B: replay a real day of incidents under a staging policy and score response times.

Policies (same simulator, same incidents, same drive-time model)
  yards      - NAIVE baseline: K trucks parked all day at 6 hand-picked yards around the city
  fixed      - STRONG baseline: K trucks placed once on whole-year demand (best static plan)
  hotspot    - K trucks placed once on LAST WEEK's busiest zones
  stormstage - K base trucks re-placed hourly from the forecast, PLUS up to EXTRA on-call trucks
               activated when the storm factor (forecast vs normal) reaches SURGE_AT

Every truck keeps a timeline of segments (responding, on_scene, returning, relocating). Its position
at any minute is interpolated along that timeline, so dispatch decisions and the map use the same
positions.

Run:
  python simulate.py                              # stand-in forecast, citywide grid zones
  python simulate.py --forecast a --zones a       # A's forecast() and A's zones.csv
"""
import argparse
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from common import (SCENE_MIN, a_zones, assign_zones, drive_min, grid_zones, load_incidents,
                    zone_matrix)
from forecast_adapter import make_forecaster
from place import place_trucks

K = 6                    # trucks on duty all day
EXTRA = 4                # on-call trucks StormStage may activate (tuned in evaluate.py)
SURGE_AT = 2.0           # storm factor that triggers on-call trucks (tuned in evaluate.py)
MOVE_PENALTY_MIN = 3.0   # a relocation must save at least this many expected minutes
DEMO_DAYS = ["2025-02-04", "2025-02-14", "2025-11-24"]
YARDS = [(51.045, -114.070), (51.100, -114.150), (51.090, -113.980),
         (50.980, -114.120), (50.950, -114.030), (51.150, -114.070)]


@dataclass
class Truck:
    home: int                                   # staging zone index
    active: bool
    free_at: float = 0.0                        # minute of day it can take a new call
    segs: list = field(default_factory=list)    # (t0, t1, (lat,lon) from, (lat,lon) to, status)
    duty: list = field(default_factory=list)    # [on_minute, off_minute or None]

    def where(self, t):
        """Position at minute t, interpolated along the timeline."""
        for t0, t1, a, b, _ in reversed(self.segs):
            if t >= t0:
                if t >= t1 or t1 == t0:
                    return b
                f = (t - t0) / (t1 - t0)
                return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))
        return self.segs[0][2]

    def status(self, t):
        for t0, t1, _, _, s in reversed(self.segs):
            if t0 <= t < t1:
                return s
            if t >= t1:
                return "staged"
        return "staged"

    def cut(self, t):
        """Drop plans after minute t (truncating the segment in progress at t)."""
        here = self.where(t)
        kept = []
        for t0, t1, a, b, s in self.segs:
            if t0 >= t and kept:
                continue
            if t0 < t < t1:
                kept.append((t0, t, a, here, s))
            else:
                kept.append((t0, t1, a, b, s))
        self.segs = kept
        return here

    def on_duty(self, t):
        return any(on <= t and (off is None or t < off) for on, off in self.duty)


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


def simulate(inc, zones, T, day, policy, forecaster, holdout_days=DEMO_DAYS, k=None, extra=None,
             surge_at=None, move_penalty=None, return_trucks=False):
    """Returns (log, moves, truck_hours) [+ trucks if return_trucks].

    log:   one row per incident  - incident_id, time, lat, lon, truck, response_min
    moves: one row per action    - time, truck, action (move / activate / stand down), to_zone, reason
    truck_hours: on-duty truck-hours that day (the cost side)
    """
    k = K if k is None else k
    extra = EXTRA if extra is None else extra
    surge_at = SURGE_AT if surge_at is None else surge_at
    move_penalty = MOVE_PENALTY_MIN if move_penalty is None else move_penalty
    day = pd.Timestamp(day)
    todays = inc[inc["day"] == day].sort_values("start_dt")
    zlat, zlon = zones["lat"].to_numpy(), zones["lon"].to_numpy()
    zxy = lambda z: (float(zlat[z]), float(zlon[z]))
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

    trucks = []
    for i in range(n_max):
        tr = Truck(home=home[i], active=i < k)
        tr.segs.append((0.0, 0.0, zxy(home[i]), zxy(home[i]), "staged"))
        if tr.active:
            tr.duty.append([0.0, None])
        trucks.append(tr)
    log, moves = [], []

    def send_home(tr, start):
        """From minute `start`, drive back to the staging zone (replacing any later plans)."""
        here = tr.cut(start)
        dest = zxy(tr.home)
        tr.segs.append((start, start + drive_min(here[0], here[1], dest[0], dest[1]), here, dest,
                        "returning"))

    def replan(hour):
        now = day + pd.Timedelta(hours=hour)
        t = hour * 60.0
        f, sf = forecaster(now)
        want = k + (extra if sf >= surge_at else 0)
        for i in range(k, n_max):                            # activate / stand down on-call trucks
            tr = trucks[i]
            if i < want and not tr.active:
                tr.active = True
                tr.duty.append([t, None])
                tr.cut(t)
                moves.append({"time": now, "truck": i, "action": "activate",
                              "to_zone": zones["zone_id"].iat[tr.home],
                              "reason": f"Unit {i + 1} called in: incidents forecast x{sf:.1f} normal"})
            elif i >= want and tr.active and tr.free_at <= t:
                tr.active = False
                tr.duty[-1][1] = t
                moves.append({"time": now, "truck": i, "action": "stand down",
                              "to_zone": zones["zone_id"].iat[tr.home],
                              "reason": f"Unit {i + 1} stood down: forecast back to x{sf:.1f} normal"})
        ids = [i for i in range(n_max) if trucks[i].active]
        new, reasons = place_trucks(f["expected_incidents"].to_numpy(), T, len(ids),
                                    current=[trucks[i].home for i in ids], move_penalty_min=move_penalty)
        for r in reasons:
            i, to = ids[r["truck"]], r["to"]
            tr = trucks[i]
            tr.home = to
            start = max(tr.free_at, t)
            send_home(tr, start)
            s = list(tr.segs[-1])
            s[4] = "relocating" if start == t else "returning"
            tr.segs[-1] = tuple(s)
            moves.append({"time": now, "truck": i, "action": "move", "to_zone": zones["zone_id"].iat[to],
                          "reason": f"Unit {i + 1} -> zone {zones['name'].iat[to]}: forecast "
                                    f"{r['demand_to']} incidents next 3 h, saves ~{r['saves_min']} "
                                    f"expected min (x{sf:.1f} normal)"})

    next_replan = 1
    for _, row in todays.iterrows():
        t = (row["start_dt"] - day).total_seconds() / 60.0
        while policy == "stormstage" and next_replan * 60 <= t:
            replan(next_replan)
            next_replan += 1
        best, best_arrive, best_ready = None, np.inf, 0.0
        for j, tr in enumerate(trucks):
            if not tr.active:
                continue
            ready = max(tr.free_at, t)
            loc = tr.where(ready)
            a = ready + drive_min(loc[0], loc[1], row["lat"], row["lon"])
            if a < best_arrive:
                best, best_arrive, best_ready = j, a, ready
        tr = trucks[best]
        start = tr.cut(best_ready)
        inc_xy = (float(row["lat"]), float(row["lon"]))
        tr.segs.append((best_ready, best_arrive, start, inc_xy, "responding"))
        tr.segs.append((best_arrive, best_arrive + SCENE_MIN, inc_xy, inc_xy, "on_scene"))
        tr.free_at = best_arrive + SCENE_MIN
        send_home(tr, tr.free_at)
        log.append({"incident_id": int(row["incident_id"]), "time": row["start_dt"],
                    "lat": row["lat"], "lon": row["lon"], "truck": best,
                    "response_min": round(best_arrive - t, 1)})

    while policy == "stormstage" and next_replan < 24:      # finish the day's re-plans
        replan(next_replan)
        next_replan += 1
    duty_min = sum(((off if off is not None else 1440.0) - on) for tr in trucks for on, off in tr.duty)
    out = (pd.DataFrame(log), pd.DataFrame(moves, columns=["time", "truck", "action", "to_zone", "reason"]),
           round(duty_min / 60.0, 1))
    return out + (trucks,) if return_trucks else out


def truck_positions(trucks, zones, day, every_min=15):
    """Snapshot of every on-duty truck every `every_min` minutes: time, unit_id, lat, lon, zone_id, status."""
    day = pd.Timestamp(day)
    zl, zo = zones["lat"].to_numpy(), zones["lon"].to_numpy()
    rows = []
    for t in np.arange(0, 1440, every_min):
        for i, tr in enumerate(trucks):
            if not tr.on_duty(t):
                continue
            la, lo = tr.where(t)
            z = int(drive_min(zl, zo, la, lo).argmin())
            rows.append({"time": day + pd.Timedelta(minutes=float(t)), "unit_id": i + 1,
                         "lat": round(la, 5), "lon": round(lo, 5), "zone_id": zones["zone_id"].iat[z],
                         "status": tr.status(t)})
    return pd.DataFrame(rows)


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
