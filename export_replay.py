"""B -> C: precompute replays so the app never runs the simulator live (fast, works offline).

Writes data/processed/replay/<day>/<policy_key>_{incidents,trucks,actions}.csv, metrics.json,
and data/processed/zones_grid.csv.

Run: python export_replay.py [--forecast standin|a] [--zones grid|a] [--days ...]
"""
import argparse
import json
from pathlib import Path

import simulate as S
from evaluate import BEST_FIXED, NAIVE, SS_ONCALL, SS_SAME, split_days
from forecast_adapter import make_forecaster

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "processed" / "replay"
STEP_MIN = 5

# key -> (simulate policy, trucks on duty, on-call trucks, label shown in the app)
POLICIES = {
    "yards":           ("yards", S.K, 0, NAIVE),                   # primary naive baseline
    "fixed":           ("fixed", S.K, 0, BEST_FIXED),              # stronger secondary baseline
    "hotspot":         ("hotspot", S.K, 0, "Historical hotspots"),
    "stormstage_same": ("stormstage", S.K, 0, SS_SAME),            # same-fleet StormStage
    "stormstage":      ("stormstage", S.K, S.EXTRA, SS_ONCALL),    # 6 + up to EXTRA on call
    "fixed_all":       ("fixed", S.K + S.EXTRA, 0, f"Fixed, {S.K + S.EXTRA} trucks all day"),
}


def main(forecast_source="standin", zone_source="grid", days=None):
    days = days or S.DEMO_DAYS
    inc, zones, T = S.setup(zone_source)
    holdout = split_days(inc)[-1]          # same held-out days as evaluate.py
    fc = make_forecaster(forecast_source, inc, zones, holdout_days=holdout)
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    zones[["zone_id", "name", "quadrant", "lat", "lon", "n"]].to_csv(ROOT / "data" / "processed" / "zones_grid.csv", index=False)
    for d in days:
        out = OUT / d
        out.mkdir(parents=True, exist_ok=True)
        metrics = {}
        for key, (pol, k, extra, label) in POLICIES.items():
            log, moves, th, trucks = S.simulate(inc, zones, T, d, pol, fc, k=k, extra=extra,
                                                holdout_days=holdout, return_trucks=True)
            log["unit_id"] = log["truck"] + 1
            log.drop(columns="truck").to_csv(out / f"{key}_incidents.csv", index=False)
            S.truck_positions(trucks, zones, d, every_min=STEP_MIN).to_csv(out / f"{key}_trucks.csv", index=False)
            if len(moves):
                moves["unit_id"] = moves["truck"] + 1
                moves = moves.drop(columns="truck")
            moves.to_csv(out / f"{key}_actions.csv", index=False)
            m = S.metrics(log)
            metrics[key] = {"label": label, "avg_response_min": m["avg_min"], "p90_response_min": m["p90_min"],
                            "pct_within_15": m["pct_within_15"], "incidents": m["incidents"],
                            "relocation_count": int((moves["action"] == "move").sum()) if len(moves) else 0,
                            "activations": int((moves["action"] == "activate").sum()) if len(moves) else 0,
                            "truck_hours": th}
        meta = {"forecast": forecast_source, "zones": zone_source, "k": S.K, "extra": S.EXTRA,
                "surge_at": S.SURGE_AT, "step_min": STEP_MIN, "policies": metrics}
        (out / "metrics.json").write_text(json.dumps(meta, indent=2))
        print(d, {k: (v["avg_response_min"], v["truck_hours"]) for k, v in metrics.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast", choices=["standin", "a"], default="standin")
    ap.add_argument("--zones", choices=["grid", "a"], default="grid")
    ap.add_argument("--days", nargs="*")
    a = ap.parse_args()
    main(a.forecast, a.zones, a.days)
