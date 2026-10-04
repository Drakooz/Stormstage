# StormStage results

Forecast: `a` · Zones: `grid` (179 zones) · 6 trucks on duty · drive and scene model in `common.py`.

**Evaluation methodology:** With forecast source `a`, evaluation uses a causal rolling-origin / out-of-time forecast. For each replay decision, the forecast is fit only on information available before the requested UTC date. Earlier evaluation dates may become historical training data for later replay dates; therefore this is not a single frozen holdout set. `forecast.py` explicitly excludes Feb 4, Feb 14, and Nov 24 plus each following UTC date. B's full evaluation-day exclusions apply to the stand-in/nowcast history and fixed-plan training demand; A's `forecast()` does not receive that full set.

**Policy selection:** On-call settings were picked on 5 separate tuning storm days + 8 separate tuning normal days with a rule fixed in advance. Chosen: call in **4** on-call trucks when the forecast runs **x2.0** normal.

**Baselines:** Fixed yards (naive) is the primary naive baseline; Best fixed plan is a stronger secondary baseline.

## Test: 12 storm days (incl. 3 demo days) and 8 normal days

| day_type | policy | avg min | 90th pct min | % within 15 min | truck-hours | moves | activations |
|---|---|---|---|---|---|---|---|
| storm | Fixed yards (naive) | 14.1 | 27.1 | 68.2 | 144.0 | 0.0 | 0.0 |
| storm | Best fixed plan | 13.7 | 26.1 | 70.9 | 144.0 | 0.0 | 0.0 |
| storm | Historical hotspots | 15.0 | 28.5 | 59.1 | 144.0 | 0.0 | 0.0 |
| storm | StormStage (same 6 trucks) | 14.2 | 27.1 | 68.8 | 144.0 | 0.0 | 0.0 |
| storm | StormStage + on-call | 10.6 | 18.9 | 79.3 | 176.5 | 0.6 | 6.2 |
| storm | Fixed, all trucks all day | 7.5 | 13.1 | 93.3 | 240.0 | 0.0 | 0.0 |
| normal | Fixed yards (naive) | 9.6 | 17.1 | 84.0 | 144.0 | 0.0 | 0.0 |
| normal | Best fixed plan | 8.8 | 15.0 | 90.9 | 144.0 | 0.0 | 0.0 |
| normal | Historical hotspots | 10.8 | 21.6 | 70.3 | 144.0 | 0.0 | 0.0 |
| normal | StormStage (same 6 trucks) | 9.2 | 16.4 | 86.2 | 144.0 | 0.0 | 0.0 |
| normal | StormStage + on-call | 9.2 | 16.4 | 86.2 | 147.5 | 0.0 | 3.5 |
| normal | Fixed, all trucks all day | 6.2 | 10.7 | 99.0 | 240.0 | 0.0 | 0.0 |

| Storm days won (lower avg response) | vs Fixed yards (naive) | vs Best fixed plan |
|---|---|---|
| StormStage (same 6 trucks) | 5 of 12 | 2 of 12 |
| StormStage + on-call | 10 of 12 | 8 of 12 |

## The 3 demo days only

| policy | avg min | 90th pct min | % within 15 min | truck-hours |
|---|---|---|---|---|
| Fixed yards (naive) | 19.5 | 40.1 | 51.7 | 144.0 |
| Best fixed plan | 19.5 | 40.0 | 50.7 | 144.0 |
| Historical hotspots | 20.2 | 40.9 | 45.8 | 144.0 |
| StormStage (same 6 trucks) | 20.0 | 42.5 | 50.1 | 144.0 |
| StormStage + on-call | 11.3 | 21.3 | 75.3 | 206.7 |
| Fixed, all trucks all day | 8.9 | 16.0 | 87.7 | 240.0 |

## On-call tuning grid (tune days only)

| surge_at | extra | storm_avg_min | storm_p90_min | storm_truck_hours | normal_avg_min | normal_extra_truck_hours | chosen |
|---|---|---|---|---|---|---|---|
| 1.3 | 2 | 9.88 | 16.78 | 184.8 | 8.25 | 16.0 | False |
| 1.3 | 3 | 9.44 | 15.9 | 205.2 | 8.25 | 24.0 | False |
| 1.3 | 4 | 9.1 | 14.1 | 225.6 | 8.25 | 32.0 | False |
| 1.5 | 2 | 9.98 | 16.78 | 176.4 | 8.25 | 8.75 | False |
| 1.5 | 3 | 9.52 | 15.9 | 192.6 | 8.25 | 13.12 | False |
| 1.5 | 4 | 9.18 | 14.1 | 208.8 | 8.25 | 17.5 | False |
| 2.0 | 2 | 10.36 | 17.36 | 166.2 | 8.26 | 3.0 | False |
| 2.0 | 3 | 9.94 | 16.46 | 177.2 | 8.26 | 4.5 | False |
| 2.0 | 4 | 9.64 | 16.02 | 188.2 | 8.26 | 6.0 | True |
| 2.5 | 2 | 11.04 | 20.64 | 158.4 | 8.29 | 1.25 | False |
| 2.5 | 3 | 10.88 | 20.48 | 165.4 | 8.29 | 1.88 | False |
| 2.5 | 4 | 10.74 | 20.48 | 172.4 | 8.29 | 2.5 | False |

Test days: storm 2025-02-04, 2025-02-14, 2025-11-24, 2025-12-24, 2025-04-22, 2025-02-18, 2025-03-29, 2025-11-28, 2025-02-19, 2025-11-26, 2025-07-15, 2025-12-10; normal 2025-08-20, 2025-09-29, 2025-01-08, 2025-10-27, 2025-01-18, 2025-02-08, 2025-11-10, 2025-09-18.
Files: `tuning.csv`, `test_by_day.csv`, `test_summary.csv`.
