# StormStage — live demo runbook

For Role C — App, Voice & Pitch Lead. Pair with the [5-minute pitch](pitch.md); steps 1–8 occupy 1:20–3:10 and step 9 occupies 3:10–3:40.

> StormStage decides where to stage trucks from weather and incident history, replans as conditions change, and is evaluated against fixed staging on the same incidents.

## Current state and ownership

The current [app](../app.py) is a Streamlit shell using [demo fixtures](../mock_data.py). It displays zone coordinates from [zones.csv](../zones.csv), side-by-side fixed/StormStage truck markers and assignment tables, static mock metrics, and mock decision messages. The day selector does not change the fixtures. Play/Pause does not advance time. No forecast visualization, simulator integration, or voice capability is implemented.

The project build plan assigns **A — Data & Forecast**, **B — Optimizer & Simulator**, and **C — App, Voice & Pitch Lead**. A supplies data/forecasts, B supplies optimized staging and replay outputs, and C connects them to the app and presents them. A/B output alone does not make the current UI integrated. Main/current-app status statements below do not establish the status of teammate branches.

There are two delivery modes:

- **Integrated replay:** use only after real outputs are connected and the selected storm day, truck moves, reasons, and metrics have been validated.
- **Current shell walkthrough:** disclose “MOCK / DEMO,” advance the hour slider manually, and describe the intended workflow. It cannot satisfy a measured-results ending today.

## Preparation before presenting

1. From the repository folder, launch `streamlit run app.py` in an environment with `requirements.txt` installed. If using the repository virtual environment, the Windows command is `.\.venv\Scripts\python.exe -m streamlit run app.py`. Open the local URL printed by Streamlit. No new app functionality is needed for this walkthrough.
2. Confirm the zone map loads and both comparison tables show six units. Check that the mock banner and metric warnings remain visible. Use tables if overlapping markers obscure individual trucks.
3. Select `StormStage` in the `Policy` dropdown and set `Current hour` to 14. The default hour is 15, already after the fixture move. Leave Play/Pause on Pause for the shell walkthrough.
4. **BLOCKED — A/B:** obtain [FINAL DEMO DAY], the validated incident/weather data, and [BEFORE CHANGE HOUR] / [AFTER CHANGE HOUR]. The fixture’s 14:00–15:00 transition is not a validated snow-onset time. Although the README names 2025-02-04, do not treat it as validated from the date selector alone.
5. **BLOCKED — A:** obtain the real next-three-hour forecast output (`zone_id`, `expected_incidents`) and evidence of the demand change. **BLOCKED — C integration:** no forecast/demand visualization currently exists. The app deliberately does not call the forecast stub.
6. **BLOCKED — B:** obtain both policies’ replay positions, a recorded reason for at least one actual move, per-incident response logs, and measured summaries. Ensure matching incidents and simulation assumptions. **BLOCKED — C integration:** replace fixture displays only in a separate authorized implementation task.
7. If validated outputs exist, record their source, run identifier, assumptions, and selected day in the demo evidence. Confirm no future incidents are used to make earlier decisions. Obtain held-out-day results or keep their status pending.
8. Prepare screenshots or a short recording of the verified demo, clearly labeled with its day and run identifier. If only the shell is available, label the capture “MOCK / DEMO.” These backup assets are preparation items; none are currently supplied by this repository. Test the local launch and network-dependent map rendering before the event.

**Option A verification gate:** before claiming compliance, verify real public Open Calgary reported traffic incident records and ECCC hourly weather (A); **Fixed staging** as the primary named naive baseline; at least one coded **plan → score → change-plan** cycle, followed by rescoring through the intended hourly replan (B, with C integration); and **AMA roadside**, represented by a dispatcher, as the named intended real user. User engagement still needs evidence and does not imply a customer or partner. Keep reported traffic incidents distinct from all collisions; the public records do not establish a complete collision count. The mock shell does not verify these requirements.

## Step-by-step sequence

### 1. Open StormStage — 1:20–1:25

**Action:** Show the app title and tagline, then the sidebar controls.

**Say:** “StormStage is a staging decision tool for a small Calgary tow and roadside fleet.” In shell mode add: “This interface currently uses labeled demo fixtures.”

**Check:** The banner is visible. Do not describe the shell as a connected forecasting system.

### 2. Select the validated storm day — 1:25–1:35

**Integrated action:** Select [FINAL DEMO DAY] and [BEFORE CHANGE HOUR] using the verified integrated controls.

**BLOCKED — A/B:** a validated storm-day replay is not currently present on main / not yet integrated into the current app. C must also connect the day selector to the real replay.

**Shell action:** Choose `2025-02-04` under `Storm day (mock)` for a reproducible walkthrough and set `Current hour` to 14. Say: “This date is a fixture selection; all listed days share the same mock behavior.” This does not fill [FINAL DEMO DAY].

### 3. Show fixed staging before conditions change — 1:35–1:55

**Action:** Scroll to `Staging comparison — mock truck positions` today, or the verified comparison view after integration. Point to Fixed staging on the left and StormStage on the right; both panels use the same selected hour.

**Say:** “Fixed staging is our primary named naive baseline: its waiting locations stay unchanged. StormStage’s intended policy places six trucks near expected demand.” In shell mode add: “Both sets of assignments here are fixtures.”

**Integrated cycle evidence:** record the initial plan and its score before advancing, using B’s verified output. The later hourly replan must show a changed plan and revised score; the current shell cannot provide this evidence.

**Check:** Show the unit/zone tables. Before hour 15, mock StormStage Unit 3 is at Z13. The shell starts with different assignments for the two policies; this is not a measured improvement or evidence of an optimized initial placement.

### 4. Start or advance the replay — 1:55–2:05

**Integrated action:** Use the rehearsed replay control to advance from [BEFORE CHANGE HOUR] to [AFTER CHANGE HOUR]. Automatic playback is usable only if subsequently implemented and verified.

**BLOCKED — B and C integration:** the real replay is not yet integrated into the current app; its Play/Pause control does not advance time.

**Shell action:** Move `Current hour` from 14 to 15. Say: “I’m advancing the fixture manually; Play is a placeholder.” Do not press Play and imply that it runs a simulator.

### 5. Show forecast/demand changes when available — 2:05–2:15

**Integrated action:** Inspect the connected forecast output at the two selected hours, showing where expected incident demand changes over the next three hours. Narrate only what the real output supports.

**BLOCKED — A and C integration:** the current app has no demand layer or forecast view. The gray zone dots are location markers, not forecast intensity. `forecast.py` produces explicitly fake values and is not connected.

**Shell action:** Keep the comparison visible and say: “The demand view is pending forecast integration; we cannot demonstrate a measured forecast change today.” Skip the visualization rather than pretending the zone map is a forecast.

### 6. Show StormStage truck repositioning — 2:15–2:40

**Integrated action:** Show the verified changed assignment and its matching replay-hour position, while fixed staging retains its staging locations. Distinguish waiting-location changes from truck dispatch to an incident.

**Integrated cycle evidence:** identify the hourly replan as the change-plan step and show its revised score alongside the initial score from step 3. Verify this plan → score → change-plan → rescore cycle ran in code; do not infer it from changed markers alone.

**BLOCKED — B and C integration:** actual relocation behavior and positions are not connected.

**Shell action:** At hour 15, show mock Unit 3 at Z14 in the right-hand table, compared with Z13 at hour 14. Toggle back to 14 and forward to 15 once if needed. Fixed staging assignments stay unchanged.

**Say:** “This fixture illustrates a staging change. It does not establish that weather caused a real optimization or that response times improved.”

### 7. Show a one-line reason for at least one move — 2:40–2:55

**Action:** Keep `Policy` set to `StormStage` and scroll to the decision log. Selecting Fixed staging changes the log, while the two comparison panels always remain Fixed staging and StormStage.

**Integrated say:** “This move’s recorded reason is: [VALIDATED MOVE REASON].” Use B’s actual explanation; do not invent a saving or move-cost number.

**BLOCKED — B and C integration:** no actual backend decision reason is available here.

**Shell say:** “The mock log explains Unit 3’s move with a forecast-demand message. This is example wording; no reforecast or relocation calculation executed.” The fixture’s “southeast Calgary” claim is not validated geographic or demand evidence; avoid asserting it independently.

### 8. Compare StormStage with fixed staging — 2:55–3:10

**Action:** Return to both panels, then scroll to the results area.

**Integrated say:** “These policies were evaluated on the same real reported incidents, with the same six-truck fleet, dispatch rules, travel-time model, and service assumptions.” Say this only after B confirms the comparison. State material simulation assumptions when interpreting it.

**BLOCKED — B:** same-incident replay logs and computed comparison results are not currently present on main / not yet integrated into the current app.

**Shell say:** “The layout demonstrates the comparison we intend to make. The numerical cards below are static mock values and do not prove a benefit.” Do not calculate an improvement from `MOCK_METRICS`.

### 9. End on measured metrics — 3:10–3:40

**Integrated action:** Show the verified results for [FINAL DEMO DAY], including their evidence source. Use the following handoff fields; every result remains a placeholder until B supplies it and C verifies the display.

| Metric | Fixed staging | StormStage | Comparison |
| --- | --- | --- | --- |
| Average response minutes | [FIXED AVG RESPONSE MIN] | [STORMSTAGE AVG RESPONSE MIN] | [AVG RESPONSE IMPROVEMENT] minutes |
| 90th-percentile response minutes | [FIXED P90 RESPONSE MIN] | [STORMSTAGE P90 RESPONSE MIN] | [P90 IMPROVEMENT] minutes |
| Percent reached within 15 minutes | [FIXED % WITHIN 15 MIN] | [% WITHIN 15 MIN] | [WITHIN 15 DIFFERENCE PP] percentage points |
| Truck relocations | [FIXED RELOCATION COUNT] | [STORMSTAGE RELOCATION COUNT] | Report counts as context for move cost. |

Average and p90 differences mean fixed minus StormStage in minutes. The within-15 difference means StormStage minus fixed in percentage points. Report zero or negative differences honestly. These are simulated response outcomes, not forecast-accuracy scores or proven operational response-time gains.

**BLOCKED — B and C integration:** measured metrics are not yet integrated into the current app; the present cards never change with day or hour. In shell mode end with: “Measured results are pending. The current numbers are illustrative. We will evaluate both policies on the same incidents.” Do not claim the intended measured-results step was completed.

**Next:** Continue to the architecture and proposed pilot portions of the pitch. Keep [HELD-OUT VALIDATION STATUS] pending until the demo-day and two held-out-day checks specified in the README have evidence.

## Fallbacks

### If live replay breaks

- Use the hour slider only if verified per-hour output still works. In the current shell, this is fixture navigation, not a replay recovery.
- Otherwise show the prepared screenshot/recording of the same validated run, labeling it as a capture. Keep its day and run identifier visible.
- If no validated capture exists, walk through the mock comparison and log with the disclaimer, then state that measured results are pending. A mock capture cannot substitute for replay evidence.

### If forecast visualization is unavailable

- This is the current state. Explain the planned forecast-to-staging handoff using the README loop and proceed to the position comparison.
- If A has supplied verified output, a separately prepared table of `zone_id` and `expected_incidents` can support the explanation; label it as a captured backend output, not a feature of the current app.
- If no verified output exists, say it is pending. Do not call the stub’s values real demand predictions or colorless zone dots a heatmap.

### If voice fails

- Present the pitch aloud and operate the existing controls manually. Read a verified move reason, or explicitly describe the mock message as an example.
- No voice control or narration feature is integrated into the current app. This fallback applies only if voice is added later or an external rehearsal aid is used; do not promise it in the live demo.

### If Wi-Fi fails

- Continue with the already running local Streamlit app if possible. Rehearse beforehand with dependencies available locally; do not depend on installing packages during the presentation.
- Map backgrounds may need network access. Use the existing unit/zone tables and decision log, plus prepared offline captures if maps fail to render.
- Use locally saved, validated metric evidence if available. Otherwise state that metrics remain pending; offline fixtures do not become measured results.

## Handoff assumptions, pending items, and project conflicts

**Assigned roles and assumptions:** the build plan assigns A — Data & Forecast, B — Optimizer & Simulator, and C — App, Voice & Pitch Lead. The six-truck design and three-hour forecast horizon come from the README, and 14:00–15:00 is only a reproducible fixture walkthrough. The pitch uses the official hackathon rubric. A verified industry quote was not supplied. Screenshot/recording backups must still be prepared. The proposed pilot and commercial model in the pitch are hypotheses, not shipped features or customer commitments.

**Waiting on teammates:** A/B must validate [FINAL DEMO DAY] and event hours; A must provide real public-data/forecast outputs; B must supply move reasons, response logs, all measured metric fields above, evidence of the coded hourly revise-and-rescore loop against Fixed staging, and [HELD-OUT VALIDATION STATUS]. C integration is also required for the full live sequence. [INDUSTRY QUOTE] needs sourced user feedback rather than a backend number; naming AMA roadside as the intended user does not establish engagement.

**Conflicts to surface:** the README promises a Play-based real-day comparison and describes showing response-time reduction, but the current app is a mock shell. The simulator and real public incident/weather dataset are not currently present on main / not yet integrated into the current app; teammate branch work is not assessed here. The linked `data/README.md` is absent on main. On main, the forecast stub expects an unavailable zone file outside this checkout, unlike the app’s root `zones.csv`. Mock relocation counts are static and are not derived from the one displayed fixture move. Option A’s real-data and coded-cycle evidence, and engagement with the named intended user, remain to be verified. Resolve these in later teammate work; this documentation task changes none of them.
