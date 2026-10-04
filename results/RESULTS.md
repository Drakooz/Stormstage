# StormStage results

Forecast: `standin` · Zones: `grid` (179 zones) · 6 trucks on duty · scene time and drive model in `common.py`.

**Tuned on different days than tested.** Settings were picked on 5 storm days + 8 normal days, using a rule fixed in advance. Chosen: call in **4** on-call trucks when the forecast runs **x2.0** normal.

## Test: 12 storm days (incl. 3 demo days) and 8 normal days

| day_type | policy | avg min | 90th pct min | % within 15 min | truck-hours | moves | activations |
|---|---|---|---|---|---|---|---|
| storm | Fixed yards (naive) | 14.1 | 27.1 | 68.2 | 144.0 | 0.0 | 0.0 |
| storm | Best fixed plan | 13.7 | 26.1 | 70.9 | 144.0 | 0.0 | 0.0 |
| storm | Last week's hotspots | 15.0 | 28.5 | 59.1 | 144.0 | 0.0 | 0.0 |
| storm | StormStage | 9.8 | 17.2 | 84.7 | 171.3 | 5.8 | 6.3 |
| storm | Fixed, all trucks all day | 7.5 | 13.0 | 93.8 | 240.0 | 0.0 | 0.0 |
| normal | Fixed yards (naive) | 9.6 | 17.1 | 84.0 | 144.0 | 0.0 | 0.0 |
| normal | Best fixed plan | 8.8 | 15.0 | 90.9 | 144.0 | 0.0 | 0.0 |
| normal | Last week's hotspots | 10.8 | 21.6 | 70.3 | 144.0 | 0.0 | 0.0 |
| normal | StormStage | 9.2 | 15.6 | 86.6 | 147.0 | 0.6 | 3.0 |
| normal | Fixed, all trucks all day | 6.2 | 10.1 | 98.5 | 240.0 | 0.0 | 0.0 |

StormStage beat the best fixed plan on **10 of 12** test storm days.

## The 3 demo days only

| policy | avg min | 90th pct min | % within 15 min | truck-hours |
|---|---|---|---|---|
| Fixed yards (naive) | 19.5 | 40.1 | 51.7 | 144.0 |
| Best fixed plan | 19.5 | 40.0 | 50.7 | 144.0 |
| Last week's hotspots | 20.2 | 40.9 | 45.8 | 144.0 |
| StormStage | 10.0 | 18.4 | 81.7 | 200.0 |
| Fixed, all trucks all day | 8.7 | 15.3 | 88.9 | 240.0 |

## Tuning grid

| surge_at | extra | storm_avg_min | storm_p90_min | storm_truck_hours | normal_avg_min | normal_extra_truck_hours | chosen |
|---|---|---|---|---|---|---|---|
| 1.3 | 2 | 10.48 | 19.02 | 171.6 | 8.07 | 11.25 | False |
| 1.3 | 3 | 9.44 | 17.82 | 185.2 | 8.06 | 16.88 | False |
| 1.3 | 4 | 9.02 | 16.72 | 198.8 | 8.06 | 22.5 | False |
| 1.5 | 2 | 10.16 | 19.06 | 166.8 | 8.2 | 6.75 | False |
| 1.5 | 3 | 9.54 | 17.76 | 178.2 | 8.19 | 10.12 | False |
| 1.5 | 4 | 8.98 | 17.0 | 189.6 | 8.19 | 13.5 | False |
| 2.0 | 2 | 10.74 | 20.2 | 162.2 | 8.26 | 3.0 | False |
| 2.0 | 3 | 10.28 | 18.86 | 171.2 | 8.25 | 4.5 | False |
| 2.0 | 4 | 9.76 | 18.4 | 180.2 | 8.25 | 6.0 | True |
| 2.5 | 2 | 11.42 | 21.68 | 158.2 | 8.3 | 1.25 | False |
| 2.5 | 3 | 11.12 | 21.28 | 165.2 | 8.29 | 1.88 | False |
| 2.5 | 4 | 10.76 | 20.04 | 172.2 | 8.29 | 2.5 | False |

Files: `tuning.csv`, `test_by_day.csv`, `test_summary.csv`.
