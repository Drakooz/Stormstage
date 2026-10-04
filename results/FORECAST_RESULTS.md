# Part A forecast evaluation

Source: the user-supplied StormStage Hackathon Build Plan. The locked UTC
contract determines date boundaries. February 4 is the demo; February 14 and
November 24 are holdouts. Model training excludes these and their following UTC
dates, protecting the corresponding Calgary local replay windows as well.

`python -m src.evaluate_forecast` reproduces `forecast_accuracy.csv` and
`forecast_windows.csv`. Each day has 24 forecasts of the three-hour interval
starting at the requested UTC hour. These windows overlap and may cross
midnight; totals across windows must not be interpreted as daily incident counts.
Weather at the decision hour is observed and persisted for three hours. Actual
future incident counts are read only to score predictions. Training uses only
earlier dates, with reserved days removed. No hyperparameter tuning used these
scores. MAE and RMSE are in incidents per three-hour window.

| UTC date | Last-week zone MAE | Poisson zone MAE | Last-week zone RMSE | Poisson zone RMSE | Last-week city MAE | Poisson city MAE |
|---|---:|---:|---:|---:|---:|---:|
| 2025-02-04 | 0.0617 | 0.0735 | 0.2850 | 0.2645 | 8.7917 | 7.2166 |
| 2025-02-14 | 0.0556 | 0.0609 | 0.2759 | 0.2246 | 4.3750 | 4.8852 |
| 2025-11-24 | 0.0694 | 0.0642 | 0.2755 | 0.2264 | 5.5833 | 5.7827 |

Poisson improves zone RMSE on all three dates; baseline improves zone MAE on two.
Citywide absolute error also has mixed results. Sparse per-zone counts make these
metrics answer different questions. This comparison does not establish a
uniformly better demand model or any truck response-time improvement.

Data validation: 8,760 unique UTC weather hours; 8 missing temperatures; 7,015
cleaned reported incidents, all joined; 179 existing zone IDs; 1,568,040
zero-filled zone-hour counts. There are 75 dates with at least one reported
snow/ice-pellet hour, and 41 UTC dates without incident records. The median is
19 incident records per UTC date, including empty dates. February 4 has 77
records in UTC; the plan's 85 is not reproduced using this extraction/time basis.
