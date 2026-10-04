"""B: select policy settings on tuning days, then report on separate evaluation days.

  TUNE  : 5 storm days (ranks 4-8 by incident count) + 8 normal days
  TEST  : the 3 demo storm days + 9 more storm days (>= 40 incidents) + 8 other normal days
  HOLDOUT (excluded from B's stand-in/nowcast history and fixed-plan training demand):
          all TEST storm days AND all TEST normal days

With forecast source "a", evaluation uses a causal rolling-origin forecast.
For each replay decision, A fits only on information before the requested UTC date.
Earlier evaluation dates may become historical training data for later replay dates;
therefore this is not a single frozen holdout set. A explicitly excludes Feb 4,
Feb 14, and Nov 24 plus each following UTC date, rather than B's full HOLDOUT set.

Two StormStage variants are reported side by side:
  - StormStage (same 6 trucks): hourly forecast-driven re-staging, no extra trucks (same-fleet comparison)
  - StormStage + on-call: same, plus up to EXTRA on-call trucks when the forecast runs xSURGE_AT normal

Baselines: Fixed yards (naive) = PRIMARY naive baseline; Best fixed plan = stronger SECONDARY baseline.

On-call selection rule (fixed before looking at TEST): lowest average response on TUNE storm days, subject to
  - storm-day truck-hours at least 10% below keeping K+EXTRA trucks on all day, and
  - at most 8 extra truck-hours per normal day (few false alarms).

Writes results/tuning.csv, results/test_by_day.csv, results/test_summary.csv, results/RESULTS.md
Run: python evaluate.py [--forecast standin|a] [--zones grid|a]
"""
import argparse
import itertools
from pathlib import Path

import pandas as pd

import simulate as S
from forecast_adapter import make_forecaster

OUT = Path(__file__).resolve().parent / "results"
TUNE_STORM = ["2025-02-05", "2025-12-03", "2025-12-17", "2025-02-03", "2025-12-13"]
TEST_STORM = S.DEMO_DAYS + ["2025-12-24", "2025-04-22", "2025-02-18", "2025-03-29", "2025-11-28",
                            "2025-02-19", "2025-11-26", "2025-07-15", "2025-12-10"]
GRID = {"surge_at": [1.3, 1.5, 2.0, 2.5], "extra": [2, 3, 4]}

# One set of names shared by B's results, C's app and the README.
NAIVE, BEST_FIXED = "Fixed yards (naive)", "Best fixed plan"
SS_SAME, SS_ONCALL = "StormStage (same 6 trucks)", "StormStage + on-call"
LABELS = {"yards": NAIVE, "fixed": BEST_FIXED, "hotspot": "Historical hotspots",
          "stormstage_same": SS_SAME, "stormstage": SS_ONCALL, "fixed_all": "Fixed, all trucks all day"}


def normal_days(inc, n, seed):
    daily = inc.groupby("day").size()
    pool = daily[(daily >= 15) & (daily <= 25)].index
    return [d.strftime("%Y-%m-%d") for d in pd.Series(pool).sample(n, random_state=seed)]


def split_days(inc):
    """Returns (tune_storm, tune_normal, test_storm, test_normal, holdout)."""
    tune_normal = normal_days(inc, 8, seed=1)
    test_normal = [d for d in normal_days(inc, 16, seed=2) if d not in tune_normal][:8]
    holdout = sorted(set(TEST_STORM) | set(test_normal))
    return TUNE_STORM, tune_normal, TEST_STORM, test_normal, holdout


def run(inc, zones, T, fc, days, policy, **kw):
    rows = []
    for d in days:
        log, moves, th = S.simulate(inc, zones, T, d, policy, fc, **kw)
        rows.append({"day": d, **S.metrics(log), "truck_hours": th,
                     "moves": int((moves["action"] == "move").sum()) if len(moves) else 0,
                     "activations": int((moves["action"] == "activate").sum()) if len(moves) else 0})
    return pd.DataFrame(rows)


def md(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def main(forecast_source="standin", zone_source="grid"):
    OUT.mkdir(exist_ok=True)
    inc, zones, T = S.setup(zone_source)
    tune_storm, tune_normal, test_storm, test_normal, holdout = split_days(inc)
    fc = make_forecaster(forecast_source, inc, zones, holdout_days=holdout)
    base_th = 24.0 * S.K

    # ---- tune the on-call variant --------------------------------------------------------------
    rows = []
    for surge_at, extra in itertools.product(GRID["surge_at"], GRID["extra"]):
        kw = dict(surge_at=surge_at, extra=extra, holdout_days=holdout)
        st = run(inc, zones, T, fc, tune_storm, "stormstage", **kw)
        nm = run(inc, zones, T, fc, tune_normal, "stormstage", **kw)
        rows.append({"surge_at": surge_at, "extra": extra,
                     "storm_avg_min": st["avg_min"].mean(), "storm_p90_min": st["p90_min"].mean(),
                     "storm_truck_hours": st["truck_hours"].mean(),
                     "normal_avg_min": nm["avg_min"].mean(),
                     "normal_extra_truck_hours": nm["truck_hours"].mean() - base_th})
        print(f"tune surge_at={surge_at} extra={extra}: storm avg {rows[-1]['storm_avg_min']:.1f} min, "
              f"{rows[-1]['storm_truck_hours']:.0f} truck-h; normal +{rows[-1]['normal_extra_truck_hours']:.1f} truck-h")
    tune = pd.DataFrame(rows).round(2)
    tune["all_day_truck_hours"] = 24.0 * (S.K + tune["extra"])
    ok = tune[(tune["storm_truck_hours"] <= 0.9 * tune["all_day_truck_hours"]) &
              (tune["normal_extra_truck_hours"] <= 8)]
    best = (ok if len(ok) else tune).sort_values("storm_avg_min").iloc[0]
    surge_at, extra = float(best["surge_at"]), int(best["extra"])
    tune["chosen"] = (tune["surge_at"] == surge_at) & (tune["extra"] == extra)
    tune.to_csv(OUT / "tuning.csv", index=False)
    print(f"\nChosen: surge_at={surge_at}, extra={extra}\n")

    # ---- test ---------------------------------------------------------------------------------
    plans = [("yards", "yards", dict(k=S.K)), ("fixed", "fixed", dict(k=S.K)),
             ("hotspot", "hotspot", dict(k=S.K)),
             ("stormstage_same", "stormstage", dict(k=S.K, extra=0)),
             ("stormstage", "stormstage", dict(k=S.K, surge_at=surge_at, extra=extra)),
             ("fixed_all", "fixed", dict(k=S.K + extra))]
    by_day = []
    for kind, days in [("storm", test_storm), ("normal", test_normal)]:
        for name, pol, kw in plans:
            r = run(inc, zones, T, fc, days, pol, holdout_days=holdout, **kw)
            r.insert(0, "policy", LABELS[name])
            r.insert(0, "day_type", kind)
            by_day.append(r)
    by_day = pd.concat(by_day, ignore_index=True)
    by_day.to_csv(OUT / "test_by_day.csv", index=False)
    summ = (by_day.groupby(["day_type", "policy"], sort=False)
            [["avg_min", "p90_min", "pct_within_15", "truck_hours", "moves", "activations"]]
            .mean().round(1).reset_index())
    summ.to_csv(OUT / "test_summary.csv", index=False)

    storm = by_day[by_day.day_type == "storm"].pivot(index="day", columns="policy", values="avg_min")
    wins = {(ss, b): int((storm[ss] < storm[b]).sum()) for ss in (SS_SAME, SS_ONCALL) for b in (NAIVE, BEST_FIXED)}
    demo_s = (by_day[by_day["day"].isin(S.DEMO_DAYS)]
              .groupby("policy", sort=False)[["avg_min", "p90_min", "pct_within_15", "truck_hours"]].mean().round(1))
    nice = {"avg_min": "avg min", "p90_min": "90th pct min", "pct_within_15": "% within 15 min",
            "truck_hours": "truck-hours"}
    n = len(test_storm)

    report = f"""# StormStage results

Forecast: `{forecast_source}` · Zones: `{zone_source}` ({len(zones)} zones) · {S.K} trucks on duty · drive and scene model in `common.py`.

**Evaluation methodology:** With forecast source `a`, evaluation uses a causal rolling-origin / out-of-time forecast. For each replay decision, the forecast is fit only on information available before the requested UTC date. Earlier evaluation dates may become historical training data for later replay dates; therefore this is not a single frozen holdout set. `forecast.py` explicitly excludes Feb 4, Feb 14, and Nov 24 plus each following UTC date. B's full evaluation-day exclusions apply to the stand-in/nowcast history and fixed-plan training demand; A's `forecast()` does not receive that full set.

**Policy selection:** On-call settings were picked on 5 separate tuning storm days + 8 separate tuning normal days with a rule fixed in advance. Chosen: call in **{extra}** on-call trucks when the forecast runs **x{surge_at}** normal.

**Baselines:** {NAIVE} is the primary naive baseline; {BEST_FIXED} is a stronger secondary baseline.

## Test: {n} storm days (incl. 3 demo days) and {len(test_normal)} normal days

{md(summ.rename(columns=nice))}

| Storm days won (lower avg response) | vs {NAIVE} | vs {BEST_FIXED} |
|---|---|---|
| {SS_SAME} | {wins[(SS_SAME, NAIVE)]} of {n} | {wins[(SS_SAME, BEST_FIXED)]} of {n} |
| {SS_ONCALL} | {wins[(SS_ONCALL, NAIVE)]} of {n} | {wins[(SS_ONCALL, BEST_FIXED)]} of {n} |

## The 3 demo days only

{md(demo_s.reset_index().rename(columns=nice))}

## On-call tuning grid (tune days only)

{md(tune.drop(columns=['all_day_truck_hours']))}

Test days: storm {', '.join(test_storm)}; normal {', '.join(test_normal)}.
Files: `tuning.csv`, `test_by_day.csv`, `test_summary.csv`.
"""
    (OUT / "RESULTS.md").write_text(report)
    print(summ.to_string(index=False))
    print("\nWins:", wins)
    print("\nDemo days:\n", demo_s.to_string())
    return surge_at, extra


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast", choices=["standin", "a"], default="standin")
    ap.add_argument("--zones", choices=["grid", "a"], default="grid")
    a = ap.parse_args()
    main(a.forecast, a.zones)
