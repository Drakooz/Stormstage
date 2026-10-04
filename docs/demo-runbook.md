# StormStage — live demo runbook

For Role C — App, Voice & Pitch Lead. Pair with the [5-minute pitch](pitch.md); steps 1–8 occupy 1:20–3:10 and step 9 occupies 3:10–3:40.

> StormStage uses 6 base trucks plus up to 4 forecast-triggered on-call trucks, staging/re-staging active trucks near expected demand. Fixed yards (naive) is the primary baseline; Best fixed plan is the stronger secondary comparator.

## Current state and ownership

Current main (`1081dfa`) includes B's backend and precomputed replay integration. The [app](../app.py) reads [replay_data.py](../replay_data.py) for day/hour-specific positions, incident responses, decisions, and full-day metrics on a 179-zone citywide grid. Play/Pause remains a placeholder; use the hour slider. Forecast visualization and voice are absent.

All current B results/replays use the **stand-in forecast**. A's real weather-driven forecast is **not yet integrated**. Keep **PRECOMPUTED / INTERIM** labels visible; current simulated outcomes are not final weather-driven performance. Testing same-six-truck re-staging showed little advantage, leading the team to revise the policy to forecast-triggered on-call capacity.

**A — Data & Forecast** supplies the real forecast and data documentation; **B — Optimizer & Simulator** integrates it and regenerates evaluation/replays; **C — App, Voice & Pitch Lead** verifies the display and presents evidence. Final weather-driven fields remain placeholders until verified.

## Preparation before presenting

1. Launch `streamlit run app.py` from the repository folder with `requirements.txt` installed. With the repository virtual environment on Windows, use `.\.venv\Scripts\python.exe -m streamlit run app.py`. Open Streamlit's local URL and test map rendering.
2. Confirm comparison panels and active-unit tables load. Fixed yards (naive) has 6 trucks; StormStage + on-call can show up to 10 on-duty trucks. Keep interim labels and metric warnings visible.
3. For a reproducible **stand-in** walkthrough, select `2025-02-04`, `StormStage + on-call`, and hour 6. Leave Play/Pause on Pause. The recorded 07:00 surge activation is an interim event, not verified weather anticipation.
4. **Pending A/B:** confirm [FINAL DEMO DAY], [BEFORE CHANGE HOUR], [AFTER CHANGE HOUR], and real weather-driven demand evidence. Do not reuse stand-in event times as final forecast evidence.
5. **Pending A:** next-three-hour output (`zone_id`, `expected_incidents`) aligned to B's zones. The app has no demand layer; use a labeled backend capture if a verified forecast table is available.
6. Check activation/move reasons and responses against the selected replay. Match incidents, dispatch, travel, and service assumptions; disclose the capacity difference and report truck-hours.
7. Prepare backend evidence of **plan → score → revise → rescore**. Full-day cards do not recompute with the slider or supply per-step scores. Final weather-driven cycle/results evidence remains [PENDING].
8. Prepare screenshots/recording with day, evaluated commit/run ID, and forecast source. Label current captures **PRECOMPUTED / INTERIM — stand-in forecast**. Test offline table/capture fallbacks; final backup assets remain pending.

**Option A — own problem using public data:** present public-data evidence, Fixed yards (naive) as primary naive baseline, Best fixed plan as stronger secondary comparator, and the coded revision/rescore cycle. The intended user is a roadside-assistance dispatcher / Calgary tow operator; AMA roadside is a potential example, not a verified customer. Feedback is pending. Reported incidents are not all collisions or tow requests.

## Step-by-step sequence

### 1. Open StormStage — 1:20–1:25

**Action:** Show title, tagline, controls, and interim banner.

**Say:** “StormStage decides when to activate on-call capacity and where to stage active trucks. Today's demonstration is a precomputed stand-in replay; final weather-driven results are pending.”

### 2. Select the storm day — 1:25–1:35

**Current action:** Select `2025-02-04`, `StormStage + on-call`, and hour 6. The selector changes the replay day; it does not run a forecast or simulator.

**Final handoff:** [FINAL DEMO DAY] and [BEFORE CHANGE HOUR] remain pending A/B verification after real-forecast integration and regenerated exports.

### 3. Show the initial plan — 1:35–1:55

**Action:** Show `Staging comparison — precomputed truck positions`: Fixed yards (naive) on the left, StormStage + on-call on the right, at the same hour. Use tables if markers overlap.

**Say:** “Our primary naive baseline keeps six trucks at fixed waiting locations. StormStage starts with six base trucks and can activate up to four on-call trucks when forecasted demand indicates a surge.”

**Cycle evidence:** identify the initial plan and score from verified backend evidence. Dashboard cards summarize the full day, not this initial hour.

### 4. Advance the recorded replay — 1:55–2:05

**Action:** Move `Current hour` from 6 to 7 for the stand-in walkthrough. Play/Pause does not advance time.

**Say:** “The slider selects recorded positions. It does not execute a new optimization.” Final event hours remain [BEFORE CHANGE HOUR] / [AFTER CHANGE HOUR].

### 5. Explain the forecast trigger — 2:05–2:15

**Action:** Inspect the activation reason. The 07:00 log on this stand-in day reports demand at x2.2 normal, crossing the current x2.0 trigger.

**Say:** “The stand-in forecast triggers extra capacity here. A's real weather-driven forecast is not yet integrated, so this event does not demonstrate advance warning from weather.”

**Pending:** verified final forecast comparison. Gray zone dots show locations, not demand intensity; do not call them a forecast heatmap.

### 6. Show capacity and staging revision — 2:15–2:40

**Action:** Show on-call units 7–10 and recorded relocations. Distinguish staging changes from dispatch, on-scene work, and returning trucks using status colors/columns. Fixed waiting locations do not mean fixed truck positions during incident response.

**Say:** “StormStage activates on-call capacity and re-stages active trucks near expected demand. Moves use an expected saving and a move penalty.”

**Cycle evidence:** pair a recorded revision with its verified backend rescore. Changed markers alone do not supply **plan → score → revise → rescore** evidence. Keep [FINAL WEATHER-DRIVEN CYCLE EVIDENCE] pending.

### 7. Show a one-line decision reason — 2:40–2:55

**Action:** Keep `Policy` on `StormStage + on-call`; show `Decision log — precomputed replay`. Read an actual activation and move reason; do not invent savings or weather causes.

The log is cumulative through the selected hour; positions are snapshots at its start. [VALIDATED MOVE REASON] remains pending for the final weather-driven run.

### 8. Compare policies — 2:55–3:10

**Action:** Show main panels and results. Select `Best fixed plan` and open the selected-policy expander for the stronger secondary comparator; main panels remain Fixed yards (naive) versus StormStage + on-call.

**Say:** “These policies use the same reported incidents and shared simulation assumptions. Both static comparators use six trucks; StormStage can use up to ten. Truck-hours show the cost of extra capacity.”

State model limits: straight-line distance × 1.3 at 40 km/h, with 30 minutes on scene. These are simulated outcomes, not field measurements.

### 9. End on metrics and pending final results — 3:10–3:40

**Current action:** Show `Results — precomputed / interim replay` and its warning. Cards are full-day simulated metrics for the selected day, independent of the slider. Supporting [B results](../results/RESULTS.md) cover 12 held-out storm days and 8 normal days using the stand-in forecast.

**Say today:** “Same-six-truck re-staging showed little advantage, which led us to revise the policy to forecast-triggered on-call capacity. These numbers use the stand-in forecast. Final weather-driven response and truck-hour results remain pending.”

**Final handoff — fill only after real-forecast integration and verification:**

| Metric | Fixed yards (naive) | Best fixed plan | StormStage + on-call |
| --- | --- | --- | --- |
| Average response minutes | [FINAL NAIVE AVG] | [FINAL BEST FIXED AVG] | [FINAL STORMSTAGE AVG] |
| 90th-percentile response minutes | [FINAL NAIVE P90] | [FINAL BEST FIXED P90] | [FINAL STORMSTAGE P90] |
| Percent reached within 15 minutes | [FINAL NAIVE WITHIN-15] | [FINAL BEST FIXED WITHIN-15] | [FINAL STORMSTAGE WITHIN-15] |
| Truck-hours | [FINAL NAIVE TRUCK-HOURS] | [FINAL BEST FIXED TRUCK-HOURS] | [FINAL STORMSTAGE TRUCK-HOURS] |
| Relocations / on-call activations | [FINAL NAIVE COUNTS] | [FINAL BEST FIXED COUNTS] | [FINAL STORMSTAGE COUNTS] |

Response differences mean comparator minus StormStage in minutes; within-15 differences mean StormStage minus comparator in percentage points. Report zero/negative outcomes honestly. Keep [HELD-OUT VALIDATION STATUS], [AVG RESPONSE IMPROVEMENT], and [P90 IMPROVEMENT] pending for final weather-driven results. No forecast accuracy or operational deployment benefit is established.

**Next:** Continue to architecture and the proposed pilot in the pitch.

## Fallbacks

### If replay display breaks

- Use the hour slider if verified snapshots still load; it navigates recorded output.
- Otherwise show a prepared capture of the same run with day/run ID and forecast source visible. Stand-in captures retain interim labels.
- Without verified captures, explain the workflow and pending final results; do not substitute old mock metrics for replay evidence.

### If forecast visualization is unavailable

- This is the current state. Explain the forecast-to-capacity/staging handoff from the README loop and recorded log.
- Use a verified forecast table if available, labeled as backend output rather than a current app feature.
- Otherwise state that the real forecast is pending; neither A's stub nor gray zone dots demonstrate real demand predictions.

### If voice fails

- Present aloud, use existing controls manually, and read a recorded reason.
- Voice is not integrated; this fallback applies to external rehearsal aids or future voice work.

### If Wi-Fi fails

- Continue with the running local app and installed dependencies.
- Map backgrounds may need network access. Use unit/zone tables, decision logs, and offline captures.
- Locally saved stand-in results remain interim; offline availability does not make them final weather-driven evidence.

## Handoff assumptions and pending items

A/B must align citywide zones, source UTC and Calgary replay time, processed weather, and the real forecast. B then reruns held-out evaluation/replays; C checks the display and final cycle evidence. `data/README.md` remains absent, and A's forecast stub has a path/coverage mismatch. See [architecture-spec.md](architecture-spec.md) for status and [submission-checklist.md](submission-checklist.md) for owners.

The final design is **6 base trucks + up to 4 forecast-triggered on-call trucks**, with active trucks staged/re-staged from expected demand. [FINAL DEMO DAY], final results, [HELD-OUT VALIDATION STATUS], [INDUSTRY QUOTE], and screenshot/recording backups remain pending. A proposed pilot or subscription is a hypothesis; no customer, partner, or deployment is verified. This documentation task changes no implementation.
