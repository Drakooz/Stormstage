# B: placement + simulator

```
pip install -r requirements.txt
python simulate.py                          # B's stand-in forecast, citywide ~2 km grid (179 zones)
python simulate.py --forecast a --zones a   # A's forecast() + A's zones.csv
```

| File | What it does | Owner |
|---|---|---|
| `forecast.py`, `zones.csv` | A's forecast interface (stub) and zones | A |
| `common.py` | Load incidents, zones (A's or citywide grid), nearest-zone assignment, drive times, B's stand-in forecast | B |
| `weather.py` | `weather_for(ts)` → the dict A's `forecast()` takes; reads `data/processed/weather_hourly.csv` when A adds it, calm until then | B (A fills the CSV) |
| `forecast_adapter.py` | One call shape for the simulator: `fn(now) → (DataFrame[zone_id, expected_incidents], storm_factor)` | B |
| `place.py` | `place_trucks(demand, T, k, current, move_penalty_min)`: greedy p-median + swap pass, one reason per move | B |
| `simulate.py` | `simulate(...) → (log, moves, truck_hours)`, `metrics(log)`, 5 policies | B |
| `data/raw/calgary_traffic_incidents_2025.csv` | Open Calgary Traffic Incidents, 2025 subset (from the hackathon repo, Case 5) | — |

## For A

- Storm factor with your forecast = `sum(forecast) / sum(baseline_forecast)` for the same hour. Keep `baseline_forecast` as the real "same hour last week" so this ratio means something.
- `weather_hourly.csv` columns: `timestamp, snowing, temp_c, snow_last_6h` (local time, hourly).
- Your forecast should use only data before the hour it is called for, and never train on the 3 demo days.

## For C

- `log`: `time, lat, lon, truck, response_min` (incident dots + response counters)
- `moves`: `time, truck, action (move / activate / stand down), to_zone, reason` (truck animation + voice lines)
- `metrics(log)`: `avg_min, p90_min, pct_within_15` (results panel); `truck_hours` is the cost side

## Results so far (stand-in forecast, citywide grid, mean of 4 Feb / 14 Feb / 24 Nov 2025)

| Policy | Avg min | 90th pct min | % within 15 min | Truck-hours |
|---|---|---|---|---|
| Naive yards, 6 trucks | 19.4 | 40.4 | 53.7 | 144 |
| Best fixed plan, 6 trucks | 19.7 | 39.6 | 49.8 | 144 |
| Last week's hotspots, 6 trucks | 20.0 | 38.7 | 45.3 | 144 |
| **StormStage, 6 + up to 3 on call** | **10.8** | **19.4** | **75.0** | **190** |
| Fixed, 9 trucks all day | 10.5 | 19.1 | 81.3 | 216 |

Moving the same 6 trucks hour by hour barely beats a good fixed plan, because storm-day incidents stay spread across the city. The win comes from the forecast deciding **when to call in on-call trucks**. That halves response time and matches a 9-truck fleet with about 12% fewer truck-hours. On 6 normal days StormStage mostly stays at 6 trucks (about 152 truck-hours on average vs 144).

## Knobs

`simulate.py`: `K=6`, `EXTRA=3`, `SURGE_AT=1.5`, `MOVE_PENALTY_MIN=3`. `common.py`: 40 km/h, ×1.3 detour, 30 min on scene, grid size.
