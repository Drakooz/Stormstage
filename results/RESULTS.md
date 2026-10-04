# StormStage results

Forecast: `standin` · Zones: `grid` (179 zones) · 6 trucks on duty · drive and scene model in `common.py`.

**Held out properly.** All 12 test storm days **and** all 8 test normal days are excluded from every forecast history and from the fixed-plan training demand. On-call settings were picked on 5 other storm days + 8 other normal days with a rule fixed in advance. Chosen: call in **4** on-call trucks when the forecast runs **x2.0** normal.

**Baselines:** Fixed yards (naive) is the primary naive baseline; Best fixed plan is a stronger secondary baseline.

## Test: 12 storm days (incl. 3 demo days) and 8 normal days

| day_type | policy | avg min | 90th pct min | % within 15 min | truck-hours | moves | activations |
|---|---|---|---|---|---|---|---|
| storm | Fixed yards (naive) | 14.1 | 27.1 | 68.2 | 144.0 | 0.0 | 0.0 |
| storm | Best fixed plan | 13.7 | 26.1 | 70.9 | 144.0 | 0.0 | 0.0 |
| storm | Historical hotspots | 15.0 | 28.5 | 59.1 | 144.0 | 0.0 | 0.0 |
| storm | StormStage (same 6 trucks) | 13.8 | 26.0 | 71.0 | 144.0 | 1.2 | 0.0 |
| storm | StormStage + on-call | 9.8 | 17.2 | 84.8 | 170.3 | 5.8 | 6.0 |
| storm | Fixed, all trucks all day | 7.5 | 13.1 | 93.3 | 240.0 | 0.0 | 0.0 |
| normal | Fixed yards (naive) | 9.6 | 17.1 | 84.0 | 144.0 | 0.0 | 0.0 |
| normal | Best fixed plan | 8.8 | 15.0 | 90.9 | 144.0 | 0.0 | 0.0 |
| normal | Historical hotspots | 10.8 | 21.6 | 70.3 | 144.0 | 0.0 | 0.0 |
| normal | StormStage (same 6 trucks) | 8.8 | 15.1 | 90.2 | 144.0 | 0.1 | 0.0 |
| normal | StormStage + on-call | 8.9 | 15.1 | 90.2 | 147.5 | 1.0 | 3.5 |
| normal | Fixed, all trucks all day | 6.2 | 10.7 | 99.0 | 240.0 | 0.0 | 0.0 |

| Storm days won (lower avg response) | vs Fixed yards (naive) | vs Best fixed plan |
|---|---|---|
| StormStage (same 6 trucks) | 5 of 12 | 2 of 12 |
| StormStage + on-call | 10 of 12 | 10 of 12 |

## The 3 demo days only

| policy | avg min | 90th pct min | % within 15 min | truck-hours |
|---|---|---|---|---|
| Fixed yards (naive) | 19.5 | 40.1 | 51.7 | 144.0 |
| Best fixed plan | 19.5 | 40.0 | 50.7 | 144.0 |
| Historical hotspots | 20.2 | 40.9 | 45.8 | 144.0 |
| StormStage (same 6 trucks) | 19.9 | 39.4 | 49.5 | 144.0 |
| StormStage + on-call | 10.1 | 18.6 | 82.2 | 198.7 |
| Fixed, all trucks all day | 8.9 | 16.0 | 87.7 | 240.0 |

## On-call tuning grid (tune days only)

| surge_at | extra | storm_avg_min | storm_p90_min | storm_truck_hours | normal_avg_min | normal_extra_truck_hours | chosen |
|---|---|---|---|---|---|---|---|
| 1.3 | 2 | 10.56 | 19.04 | 171.6 | 8.07 | 11.0 | False |
| 1.3 | 3 | 9.48 | 17.66 | 185.2 | 8.06 | 16.5 | False |
| 1.3 | 4 | 9.0 | 16.12 | 198.8 | 8.06 | 22.0 | False |
| 1.5 | 2 | 10.32 | 19.24 | 167.4 | 8.2 | 6.75 | False |
| 1.5 | 3 | 9.6 | 17.86 | 178.8 | 8.19 | 10.12 | False |
| 1.5 | 4 | 8.84 | 16.4 | 190.6 | 8.19 | 13.5 | False |
| 2.0 | 2 | 10.78 | 19.76 | 162.6 | 8.26 | 3.0 | False |
| 2.0 | 3 | 10.1 | 18.44 | 171.8 | 8.25 | 4.5 | False |
| 2.0 | 4 | 9.56 | 17.72 | 181.0 | 8.25 | 6.0 | True |
| 2.5 | 2 | 11.48 | 21.24 | 158.0 | 8.3 | 1.25 | False |
| 2.5 | 3 | 11.06 | 20.92 | 165.2 | 8.29 | 1.88 | False |
| 2.5 | 4 | 10.68 | 19.72 | 172.2 | 8.29 | 2.5 | False |

Test days: storm 2025-02-04, 2025-02-14, 2025-11-24, 2025-12-24, 2025-04-22, 2025-02-18, 2025-03-29, 2025-11-28, 2025-02-19, 2025-11-26, 2025-07-15, 2025-12-10; normal 2025-08-20, 2025-09-29, 2025-01-08, 2025-10-27, 2025-01-18, 2025-02-08, 2025-11-10, 2025-09-18.
Files: `tuning.csv`, `test_by_day.csv`, `test_summary.csv`.
