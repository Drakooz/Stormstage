# B: placement, simulator, results, replay exports

```
pip install -r requirements.txt
python simulate.py                 # quick table on the 3 demo days (~3 s)
python evaluate.py                 # tune on some days, test on others -> results/RESULTS.md (~75 s)
python export_replay.py            # precompute replays for the app -> data/processed/replay/ (~5 s)
python -m pytest -q                # 12 B tests (incl. the A → B integration test)
# add  --forecast a --zones a  to any of the first three to use A's forecast() and zones.csv
```

## Headline: with A's real forecast (`--forecast a`)

Data: team raw incidents in Calgary time, 2025. **Evaluation methodology:** A's forecast uses causal rolling-origin / out-of-time evaluation: for each replay decision, it fits only on information available before the requested UTC date. Earlier evaluation dates may become historical training data for later replay dates; therefore this is not a single frozen holdout set. `forecast.py` explicitly excludes Feb 4, Feb 14, and Nov 24 plus each following UTC date. All 12 test storm days and all 8 test normal days are excluded from B's stand-in/nowcast history and fixed-plan training demand; A's `forecast()` does not receive that full set. On-call settings were selected on 5 separate tuning storm days + 8 separate tuning normal days, with a rule fixed in advance: call in **4 on-call trucks when the storm factor reaches ×2.0**.

**Storm factor** = the larger of two signals:

- **Weather lift:** A's forecast with real weather ÷ A's forecast with calm weather.
- **Nowcast:** reported incidents in the last 3 h vs normal for those hours.

Both signals are bounded. The earlier forecast ÷ `baseline_forecast()` divided by zero overnight, when last week's count was 0.

**Names used everywhere:** Fixed yards (naive) = primary naive baseline · Best fixed plan = stronger secondary baseline · StormStage (same 6 trucks) · StormStage + on-call.

| 12 test storm days | Avg response | 9 in 10 within | Within 15 min | Truck-hours/day | Days beating naive | Days beating best fixed |
|---|---|---|---|---|---|---|
| Fixed yards (naive) | 14.1 min | 27.1 min | 68% | 144 | — | — |
| Best fixed plan | 13.7 min | 26.1 min | 71% | 144 | — | — |
| StormStage (same 6 trucks) | 14.2 min | 27.1 min | 69% | 144 | 5 of 12 | 2 of 12 |
| **StormStage + on-call** | **10.6 min** | **18.9 min** | **79%** | **176.5** | **10 of 12** | **8 of 12** |
| Fixed, 10 trucks all day | 7.5 min | 13.1 min | 93% | 240 | — | — |

| 8 test normal days | Avg response | Truck-hours/day |
|---|---|---|
| Fixed yards (naive) | 9.6 min | 144 |
| Best fixed plan | 8.8 min | 144 |
| StormStage (same 6 trucks) | 9.2 min | 144 |
| StormStage + on-call | 9.2 min | 147.5 |

**Demo days (A's forecast):**

| Day | Fixed yards (naive) | StormStage (same 6 trucks) | StormStage + on-call | Truck-hours |
|---|---|---|---|---|
| 4 Feb | 20.1 min | 19.6 min | 9.8 min | 228 |
| 14 Feb | 14.2 min | 15.6 min | 12.3 min | 196 |
| 24 Nov | 24.3 min | 24.8 min | 11.8 min | 196 |

- **Same fleet:** re-staging the same 6 trucks ties fixed staging. A's forecast is citywide total × fixed historical zone shares, so where demand is expected doesn't change within a day, and B's hourly re-planning makes no relocations.
- **On-call:** calling in capacity when the storm factor fires is what wins. It costs +32.5 truck-hours on storm days vs +96 for keeping all 10 trucks on all day, and +3.5 on normal days.
- **With B's stand-in forecast** (`python evaluate.py`): on-call 9.8 min, same-fleet 13.8 min. The conclusions are the same.
- **Fallback:** if A's forecast can't run for an hour (no training history before ~2 Jan), the adapter uses B's stand-in for that hour. 0 hours on all test days.

## Design decision for the team

The original README promises a **same-fleet** comparison (6 trucks, "same number of trucks"). The designated evaluation-day results say that design does not beat fixed staging, while **adaptive on-call capacity** does, clearly. Options:

1. **Adopt on-call as the final design** (B's recommendation). Pitch it honestly: "We tested re-staging the same 6 trucks; it ties fixed staging. The data showed the lever is *when to add capacity*, so StormStage calls in on-call trucks before the surge." Update the README challenge and value lines to "6 trucks plus up to 4 on call".
2. **Keep same-fleet as the headline.** It is honest, but the result is a tie.

Either way both variants stay in the results and the app. `replay_data.STORMSTAGE_PRIMARY` picks which one the label "StormStage" and the main comparison use. It currently defaults to on-call; set it to `"stormstage_same"` if the team chooses option 2.

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
get_metrics("2025-02-04", "Fixed yards (naive)")   # avg_response_min, p90_response_min, pct_within_15, relocation_count, activations, truck_hours
get_decision_log("2025-02-04", "StormStage", hour=9)   # ["07:00 — Unit 7 called in: incidents forecast x2.1 normal", ...]
get_incidents("2025-02-04", "StormStage", hour=9)      # time, lat, lon, unit_id, response_min
get_zones()                                            # the 179 grid zones the replays use
```

- Policy labels: `"Fixed yards (naive)"` (primary naive baseline), `"Best fixed plan"` (secondary), `"Historical hotspots"`, `"StormStage (same 6 trucks)"`, `"StormStage + on-call"`, plus key `"fixed_all"` (10 trucks all day) for the cost comparison. Old names still work: `"Fixed staging"` → Fixed yards (naive), `"StormStage"` → `STORMSTAGE_PRIMARY`.
- `COMPARISON_POLICIES` = (Fixed yards (naive), the primary StormStage variant).
- StormStage shows up to 10 units; on-call units appear only while on duty. Colour by `status`.
- Map centre: the grid covers all of Calgary, so zoom ~10, not 11.

## For A

- Keep incidents and weather in UTC (agreed). For the model, consider a **local-hour feature** (`ts.tz_convert("America/Edmonton").hour`): rush hour is fixed in Calgary time but moves an hour in UTC with daylight saving. Filter "2025" on local dates if you want the same storm days as B.
- **`forecast.py` crashes as committed**: `ZONES_PATH` points two folders up. Use `Path(__file__).resolve().parent / "zones.csv"`. The adapter works around it for now.
- **`zones.csv` covers only downtown** (20 zones; 27% of 2025 incidents fall inside). Consider adopting `data/processed/zones_grid.csv` (179 citywide zones) as `zones.csv`.
- Make `baseline_forecast()` the real "same hour last week". StormStage's call-in decision is `sum(forecast) / sum(baseline)`, and with the flat stub it never reaches ×2.0.
- Add `data/processed/weather_hourly.csv` (`timestamp, snowing, temp_c, snow_last_6h`). For causal rolling-origin evaluation, train only on information before the requested UTC date and retain the explicit demo-date exclusions in `forecast.py`.
- The upgrade worth showing: a weather-driven forecast that crosses ×2.0 **before** the surge. The stand-in only reacts to the last 3 hours of incidents.

## Q&A answers (B's area)

- **"Why not just keep 10 trucks on all day?"** It's faster, but it costs 96 extra truck-hours on every storm day *and* every normal day. StormStage + on-call adds about 26 on storm days and about 3.5 on normal days.
- **"Isn't StormStage just 'more trucks'?"** The extra trucks only come on when the forecast says so: +26 truck-hours on storm days against +96 for keeping all 10 trucks on all day, and +3.5 on normal days. We also report the same-fleet variant, and it ties fixed staging, which is exactly why we added capacity timing.
- **"Did you tune on the test days?"** No. Policy settings were chosen on 5 separate tuning storm days + 8 separate tuning normal days, using a rule set in advance. `evaluate.split_days` supplies all designated evaluation days as exclusions for B's stand-in/nowcast history and fixed-plan training demand. A's forecast instead fits causally before each requested UTC date, with the explicit demo-date exclusions; earlier evaluation dates may enter training for later replay dates.
- **"Drive times?"** Straight-line km × 1.3 at 40 km/h, with 30 min on scene. Relocating and returning trucks can be re-dispatched from their real interpolated position.
- **"Why doesn't moving trucks help more?"** Storm-day crashes are spread citywide, so a good static spread is already close to optimal for a fixed fleet. Capacity timing is the lever, and we found it with the data.
