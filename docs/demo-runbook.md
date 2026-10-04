# StormStage — demo runbook

For Role C — App, Voice & Pitch Lead. Pair with the [5-minute pitch](pitch.md): steps 1–8 occupy 1:20–3:10 and step 9 occupies 3:10–3:40.

> **WEATHER-DRIVEN PRECOMPUTED REPLAY.** A's causal forecast is integrated; exports use source `a`. Metrics are simulated replay outcomes, not field-deployment results. Fixed yards (naive) is primary; Best fixed plan is secondary. StormStage uses 6 base trucks plus up to 4 on-call trucks.

## Current evidence and preparation

Local main (`ccdcae8`) includes the integrated forecast, backend evaluation, and weather-driven replay exports. The dashboard uses `replay_data.py` for saved positions, decisions, incidents, and full-day scores on the citywide grid. Hours are **Calgary local time (America/Edmonton)**. Play/Pause remains a placeholder; demand visualization and voice are absent.

1. Launch `streamlit run app.py` with dependencies installed. On Windows with the repository environment: `.\.venv\Scripts\python.exe -m streamlit run app.py`. Check maps, active-unit tables, and the weather-driven banner.
2. Select `2025-02-04`, `StormStage + on-call`, **hour 0**; leave Pause selected. Advance to **hour 1** to show the actual recorded activation.
3. Check [Feb 4 actions](../data/processed/replay/2025-02-04/stormstage_actions.csv): units 7–10 activate at 01:00 with `incidents forecast x2.4 normal`. This exceeds the 2.0 policy threshold. The signal is the larger of weather lift and a recent-incident nowcast; the log does not identify which dominated at that hour.
4. Check [Feb 4 metrics](../data/processed/replay/2025-02-04/metrics.json): no recorded relocations. Demonstrate **capacity revision**, not an invented move. The full-day average response is 20.1 minutes for Fixed yards versus 9.8 for on-call.
5. Prepare the [aggregate table](../README.md) separately: it summarizes 12 designated storm test days, not Feb 4 alone. Sources are [test_summary.csv](../results/test_summary.csv) and [RESULTS.md](../results/RESULTS.md); per-day values are in [test_by_day.csv](../results/test_by_day.csv).
6. Prepare screenshots/recording labeled with day, inspected commit, forecast source `a`, and WEATHER-DRIVEN PRECOMPUTED REPLAY. Backup assets and clean-clone verification still need completion.

**PLAN → SCORE → REVISE → RESCORE:** the tested same-six-truck policy did not improve fixed baselines' aggregate average response; the policy was revised to on-call capacity and rescored. Within each replay the backend also refreshes demand and revises capacity/staging hourly. The slider navigates saved output; full-day cards do not compute a score for each selected hour.

## Step-by-step sequence

### 1. Open StormStage — 1:20–1:25

**Action:** show title, controls, and WEATHER-DRIVEN PRECOMPUTED REPLAY banner.

**Say:** “StormStage explores when to add on-call capacity and where active trucks should wait. This is a saved weather-driven replay, with simulated outcomes.”

### 2. Select Feb 4 — 1:25–1:35

**Action:** choose `2025-02-04`, `StormStage + on-call`, hour 0. The selector reads exports; it does not run a forecast or simulator.

### 3. Show the initial capacity and staging — 1:35–1:55

**Action:** show `Staging comparison — precomputed truck positions` and the unit tables at 00:00. Fixed yards is left; on-call is right.

**Say:** “Fixed yards keeps six fixed waiting locations. StormStage starts with six base trucks and can call in four more. Fixed waiting locations do not mean trucks stay still during incident response.”

Do not describe full-day metric cards as a score for this initial hour.

### 4. Advance the recorded replay — 1:55–2:05

**Action:** move `Current hour` from 0 to 1.

**Say:** “The slider selects recorded positions. Play/Pause is a placeholder; neither control runs a new optimization.”

### 5. Read the capacity trigger — 2:05–2:15

**Action:** show the 01:00 activation reason in `Decision log — precomputed replay`.

**Say:** “Unit 7 is called in at a recorded surge signal of x2.4 normal. The policy compares weather lift and recent incidents, then uses the larger signal. This log alone does not prove advance warning from weather.”

Gray grid dots are zone locations, not a forecast heatmap.

### 6. Show the revised capacity — 2:15–2:40

**Action:** show on-call units 7–10. Explain status colors and use tables when markers overlap.

**Say:** “Four on-call units are active after the recorded revision. This Feb 4 replay has no relocations. Other marker movement represents dispatch and return travel, not evidence of re-staging.”

The backend supports relocation when savings justify the move penalty; do not invent a move for this day.

### 7. Show the recorded decision reason — 2:40–2:55

**Action:** keep `Policy` on `StormStage + on-call`, read an actual activation reason. The log is cumulative through the selected hour; map positions are snapshots at the hour's start.

**Say:** “These are recorded decisions from the integrated run. We can inspect why capacity changed and then compare the completed replay outcomes.”

### 8. Compare policies and the demo-day outcome — 2:55–3:10

**Action:** show results; select `Best fixed plan` and open the selected-policy expander to inspect the secondary comparator. The two main panels remain Fixed yards versus on-call.

**Say:** “The policies replay the same reported incidents under shared assumptions. On February 4 alone, average simulated response was 20.1 minutes for Fixed yards versus 9.8 for on-call. This is one day, not our 12-day aggregate.”

Cards are full-day simulated metrics from `replay_data`, independent of the hour slider. Reported incidents are **not all collisions or all tow calls**.

### 9. Present the 12-day aggregate — 3:10–3:40

**Action:** switch to the following table in the runbook or README. Do not describe the Feb 4 cards as aggregate results.

**Across 12 designated storm test days using a causal forecast**; daily-metric means from [test_summary.csv](../results/test_summary.csv):

| Policy | Average response (min) | Mean daily p90 (min) | Mean within-15 share (%) | Truck-hours/day |
| --- | --- | --- | --- | --- |
| Fixed yards (naive) — primary | 14.1 | 27.1 | 68.2 | 144 |
| Best fixed plan — secondary | 13.7 | 26.1 | 70.9 | 144 |
| StormStage (same 6 trucks) | 14.2 | 27.1 | 68.8 | 144 |
| StormStage + on-call | 10.6 | 18.9 | 79.3 | 176.5 |
| Fixed 10 trucks all day | 7.5 | 13.1 | 93.3 | 240 |

**Say:** “Same-six-truck staging did not improve the baselines' aggregate average response. We revised to on-call capacity and rescored: 10.6 minutes versus 14.1 for Fixed yards. On-call beat Fixed yards on 10 of 12 days and Best fixed plan on 8 of 12. It used 176.5 truck-hours per day versus 240 for ten trucks all day; that all-day policy was faster. These are simulated replay outcomes, not field-deployment results.”

Wins are from [RESULTS.md](../results/RESULTS.md). Daily p90 averages are not a pooled percentile. Do not claim monetary savings, forecast accuracy, or field benefits from these scores.

**Training boundary:** A fits before the requested UTC decision date and explicitly reserves Feb 4, Feb 14, and Nov 24 (+ following UTC dates). The broader all-evaluation-days exclusion wording in `results/RESULTS.md` does not match A's implementation. Do not claim all 12 storm and 8 normal days were fully excluded from A's forecast training. A/B own that discrepancy; no result file is changed here.

**Next:** architecture and the proposed dispatcher review/pilot in the pitch.

## Fallbacks and remaining preparation

- **Display failure:** use a verified capture of source `a` with day/commit labels; otherwise show the checked results and explain the saved replay workflow. Do not substitute mock metrics.
- **No forecast view:** this is the current app. Explain the handoff using the architecture diagram and recorded reason; gray zone dots do not visualize demand.
- **Voice:** present aloud and use controls manually; voice is not integrated.
- **Wi-Fi:** a local app can show tables and logs; map backgrounds may need network access. Rehearse offline captures and table fallbacks.
- **Simulation assumptions:** nearest-arrival dispatch, straight-line distance × 1.3 at 40 km/h, 30 minutes on scene. These are not calibrated field operating times.
- **Submission work:** screenshots/recording, demo URL, clean-clone verification, confirmed GitHub handles, and team review remain unresolved. Source/usage-term checks and the training-exclusion discrepancy need owner review. See [submission checklist](submission-checklist.md).

No customer, partner, deployment, attributable industry quote, pricing, or monetary-savings claim is established. The proposed pilot is a next step, not an existing commitment.
