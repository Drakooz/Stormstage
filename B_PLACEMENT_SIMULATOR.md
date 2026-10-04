# B: placement, simulator, results, replay exports

```
pip install -r requirements.txt
python simulate.py                 # quick table on the 3 demo days (~3 s)
python evaluate.py                 # tune on some days, test on others -> results/RESULTS.md (~75 s)
python export_replay.py            # precompute replays for the app -> data/processed/replay/ (~5 s)
python -m pytest -q                # 9 sanity tests
# add  --forecast a --zones a  to any of the first three to use A's forecast() and zones.csv
```

## Headline (stand-in forecast; rerun `evaluate.py` once A's forecast lands)

Data: the team raw file `data/raw/calgary_traffic_incidents_full.csv`, **converted from UTC to Calgary time**, filtered to 2025 (7,005 incidents).

Settings were tuned on 5 storm days and 8 normal days. The rule was fixed before testing: call in **4 on-call trucks when the forecast runs ×2.0 normal**. Tested on 12 other storm days (including the 3 demo days) and 8 other normal days:

| Test days | Plan | Avg response | 9 in 10 within | Within 15 min | Truck-hours/day |
|---|---|---|---|---|---|
| 12 storm days | Best fixed plan (6 trucks) | 13.7 min | 26.1 min | 71% | 144 |
| 12 storm days | **StormStage (6 + up to 4 on call)** | **9.8 min** | **17.2 min** | **85%** | **171** |
| 12 storm days | 10 trucks all day | 7.5 min | 13.0 min | 94% | 240 |
| 8 normal days | Best fixed plan | 8.8 min | 15.0 min | 91% | 144 |
| 8 normal days | StormStage | 9.2 min | 15.6 min | 87% | 147 |

- StormStage beat the best fixed plan on **10 of 12** test storm days. The 2 misses were mild days where the fixed plan was already fast: 28 Nov (8.7 vs 9.5 min) and 10 Dec (a tie at 9.6).
- On the heavy days the gap is large: 4 Feb 19.2 → 8.6 min, 24 Nov 24.2 → 10.2, 22 Apr 17.6 → 8.9.
- On storm days it gets about two-thirds of the benefit of putting 4 more trucks on all day, for about a quarter of the extra truck-hours (+27 vs +96).
- On normal days it adds about 3 truck-hours. Response is slightly slower than the best fixed plan (9.2 vs 8.8 min) because it occasionally relocates a truck it didn't need to; say this honestly if asked.
- **Demo days only (4 Feb, 14 Feb, 24 Nov 2025):** 19.5 → 10.0 min average response; 51% → 82% of incidents reached within 15 minutes.

**Why this design:** moving the same 6 trucks around hour by hour barely beats a good fixed plan, because storm-day crashes stay spread across the city. The forecast earns its keep by timing **when to add capacity**, then placing every truck where expected demand is.

## Time zones (team rule)

Raw data comes in UTC, and A keeps it in UTC. B converts to Calgary local time (`America/Edmonton`, which handles MST and MDT automatically) at the simulator boundary:

- **Incidents:** `common.load_incidents` converts `START_DT_UTC` to Calgary time before filtering to 2025.
- **Weather:** `weather.py` reads `data/processed/weather_hourly.csv` with **UTC** timestamps (`timestamp` or ECCC's `Date/Time (UTC)`) and converts to Calgary time on read.
- **A's forecast:** `forecast_adapter.py` converts the simulator's Calgary time to **UTC** before calling A's `forecast(day, hour, weather)` and `baseline_forecast(day, hour)`, so both take UTC day/hour.
- `tests/test_b.py::test_time_boundary` checks winter (UTC−7) and summer (UTC−6).

## Files

| File | What it does |
|---|---|
| `place.py` | `place_trucks(demand, T, k, current, move_penalty_min)`: greedy p-median + swap pass; one reason per move |
| `simulate.py` | Replay engine. Trucks follow a timeline (responding → on_scene → returning / relocating) with interpolated positions; nearest-arrival dispatch; 5 policies; `metrics()`, `truck_positions()` |
| `evaluate.py` | Tune/test split, writes `results/` (RESULTS.md, tuning.csv, test_by_day.csv, test_summary.csv) |
| `export_replay.py` | Precomputes every demo day × policy into `data/processed/replay/<day>/` |
| `replay_data.py` | **For C**: drop-in for `mock_data.py` with real numbers |
| `forecast_adapter.py`, `weather.py` | Plug A's `forecast(day, hour, weather)` in; storm factor = forecast ÷ `baseline_forecast` |
| `common.py` | Incidents, citywide ~2 km grid (179 zones, named with quadrant), drive times, B's stand-in forecast |
| `tests/test_b.py` | Placement beats random, move penalty works, every incident served, forecast never peeks at the future, storm day triggers call-ins |

## For C: swap mock_data → replay_data

```python
from replay_data import (STORM_DAYS, POLICIES, COMPARISON_POLICIES, get_zones,
                         get_truck_positions, get_metrics, get_decision_log, get_incidents)

get_truck_positions("2025-02-04", "StormStage", hour=15, minute=0)  # unit_id, zone_id, lat, lon, status (5-min steps)
get_metrics("2025-02-04", "Fixed staging")   # avg_response_min, p90_response_min, pct_within_15, relocation_count, activations, truck_hours
get_decision_log("2025-02-04", "StormStage", hour=9)   # ["07:00 — Unit 7 called in: incidents forecast x2.1 normal", ...]
get_incidents("2025-02-04", "StormStage", hour=9)      # time, lat, lon, unit_id, response_min
get_zones()                                            # the 179 grid zones the replays use
```

- Policy labels: `"Fixed staging"` (best fixed plan), `"Fixed yards (naive)"`, `"Historical hotspots"`, `"StormStage"`, plus key `"fixed_all"` (10 trucks all day) for the cost comparison.
- StormStage shows up to 10 units; on-call units appear only while on duty. Colour by `status`.
- Map centre: the grid covers all of Calgary, so zoom ~10, not 11.

## For A

- Keep incidents and weather in UTC (agreed). For the model, consider a **local-hour feature** (`ts.tz_convert("America/Edmonton").hour`): rush hour is fixed in Calgary time but moves an hour in UTC with daylight saving. Filter "2025" on local dates if you want the same storm days as B.
- **`forecast.py` crashes as committed**: `ZONES_PATH` points two folders up. Use `Path(__file__).resolve().parent / "zones.csv"`. The adapter works around it for now.
- **`zones.csv` covers only downtown** (20 zones; 27% of 2025 incidents fall inside). Consider adopting `data/processed/zones_grid.csv` (179 citywide zones) as `zones.csv`.
- Make `baseline_forecast()` the real "same hour last week". StormStage's call-in decision is `sum(forecast) / sum(baseline)`, and with the flat stub it never reaches ×2.0.
- Add `data/processed/weather_hourly.csv` (`timestamp, snowing, temp_c, snow_last_6h`). Never train on the 12 test storm days listed in `evaluate.py`.
- The upgrade worth showing: a weather-driven forecast that crosses ×2.0 **before** the surge. The stand-in only reacts to the last 3 hours of incidents.

## Q&A answers (B's area)

- **"Why not just keep 10 trucks on all day?"** It's faster, but it costs 96 extra truck-hours on every storm day *and* every normal day. StormStage adds about 27 on storm days and about 3 on normal days.
- **"Isn't StormStage just 'more trucks'?"** The extra trucks only come on when the forecast says so. On normal days it adds about 3 truck-hours, and on storm days it uses +27 truck-hours where putting all 10 trucks on all day takes +96.
- **"Did you tune on the test days?"** No. Settings were chosen on 5 other storm days + 8 normal days, using a rule set in advance (`evaluate.py`).
- **"Drive times?"** Straight-line km × 1.3 at 40 km/h, with 30 min on scene. Relocating and returning trucks can be re-dispatched from their real interpolated position.
- **"Why doesn't moving trucks help more?"** Storm-day crashes are spread citywide, so a good static spread is already close to optimal for a fixed fleet. Capacity timing is the lever, and we found it with the data.
