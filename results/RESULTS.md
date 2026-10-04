# StormStage results

Forecast: `standin` · Zones: `grid` (179 zones) · 6 trucks on duty · scene time and drive model in `common.py`.

**Tuned on different days than tested.** Settings were picked on 5 storm days + 8 normal days, using a rule fixed in advance. Chosen: call in **4** on-call trucks when the forecast runs **x2.0** normal.

## Test: 12 storm days (incl. 3 demo days) and 8 normal days

| day_type | policy | avg min | 90th pct min | % within 15 min | truck-hours | moves | activations |
|---|---|---|---|---|---|---|---|
| storm | Fixed yards (naive) | 15.0 | 30.0 | 64.9 | 144.0 | 0.0 | 0.0 |
| storm | Best fixed plan | 15.1 | 30.4 | 65.9 | 144.0 | 0.0 | 0.0 |
| storm | Last week's hotspots | 16.6 | 32.7 | 55.2 | 144.0 | 0.0 | 0.0 |
| storm | StormStage | 10.8 | 21.0 | 79.8 | 176.5 | 5.3 | 7.5 |
| storm | Fixed, all trucks all day | 8.0 | 13.8 | 91.6 | 240.0 | 0.0 | 0.0 |
| normal | Fixed yards (naive) | 9.4 | 15.0 | 87.6 | 144.0 | 0.0 | 0.0 |
| normal | Best fixed plan | 9.3 | 16.2 | 87.4 | 144.0 | 0.0 | 0.0 |
| normal | Last week's hotspots | 11.6 | 20.4 | 68.0 | 144.0 | 0.0 | 0.0 |
| normal | StormStage | 9.2 | 16.0 | 89.0 | 149.8 | 1.1 | 3.0 |
| normal | Fixed, all trucks all day | 6.4 | 10.7 | 97.9 | 240.0 | 0.0 | 0.0 |

StormStage beat the best fixed plan on **12 of 12** test storm days.

## The 3 demo days only

| policy | avg min | 90th pct min | % within 15 min | truck-hours |
|---|---|---|---|---|
| Fixed yards (naive) | 19.7 | 39.8 | 50.9 | 144.0 |
| Best fixed plan | 19.9 | 40.1 | 50.1 | 144.0 |
| Last week's hotspots | 22.4 | 42.9 | 43.1 | 144.0 |
| StormStage | 10.4 | 18.4 | 81.7 | 198.0 |
| Fixed, all trucks all day | 8.9 | 15.2 | 87.7 | 240.0 |

## Tuning grid

| surge_at | extra | storm_avg_min | storm_p90_min | storm_truck_hours | normal_avg_min | normal_extra_truck_hours | chosen |
|---|---|---|---|---|---|---|---|
| 1.3 | 2 | 10.94 | 20.0 | 170.0 | 8.34 | 9.5 | False |
| 1.3 | 3 | 10.16 | 18.42 | 182.8 | 8.29 | 14.38 | False |
| 1.3 | 4 | 9.62 | 17.8 | 195.8 | 8.4 | 19.12 | False |
| 1.5 | 2 | 11.0 | 20.46 | 167.6 | 8.26 | 5.5 | False |
| 1.5 | 3 | 10.36 | 18.86 | 179.2 | 8.26 | 8.12 | False |
| 1.5 | 4 | 9.7 | 17.84 | 191.0 | 8.26 | 10.75 | False |
| 2.0 | 2 | 11.42 | 20.82 | 164.2 | 8.27 | 2.0 | False |
| 2.0 | 3 | 11.1 | 20.58 | 174.0 | 8.27 | 3.0 | False |
| 2.0 | 4 | 10.82 | 20.44 | 184.0 | 8.27 | 4.0 | True |
| 2.5 | 2 | 11.38 | 20.82 | 160.4 | 8.11 | 0.75 | False |
| 2.5 | 3 | 11.12 | 20.54 | 168.4 | 8.11 | 1.12 | False |
| 2.5 | 4 | 10.96 | 20.48 | 176.6 | 8.11 | 1.5 | False |

Files: `tuning.csv`, `test_by_day.csv`, `test_summary.csv`.
