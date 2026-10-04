# StormStage — timed 5-minute pitch

Prepared for Role C — App, Voice & Pitch Lead. Based on the current [README](../README.md), [app shell](../app.py), [demo fixtures](../mock_data.py), [forecast stub](../forecast.py), and [zone file](../zones.csv). No slides are part of this deliverable.

> StormStage decides where to stage trucks from weather and incident history, replans as conditions change, and is evaluated against fixed staging on the same incidents.

This is the project message and intended evaluation, not a claim that the current shell runs that loop. Today, the dashboard uses mock storm days, truck positions, decision messages, and static metrics. No forecast or simulator is connected. Use the integrated-demo wording below only after the corresponding backend outputs and app integration are verified; otherwise use the explicit shell wording.

**Official hackathon rubric:**

- Autonomous Reasoning + Data-Driven Decisions — 30%
- Real Industrial Problem & Relevance — 20%
- Execution & Software Architecture — 20%
- Commercialization in Industry — 15%
- Presentation & Demo Quality — 15%

**Option A compliance:** demonstrate real public data, a named naive baseline (**Fixed staging**, primary), at least one **plan → score → change-plan** cycle in code, and a named real user (**AMA roadside**, represented by a dispatcher, as the intended user). The hourly replan is the intended revise-and-rescore loop. Public-data integration, the coded cycle, and user engagement remain to be verified; naming a target user does not establish a customer relationship. Open Calgary records are **reported traffic incidents**, not a count of all collisions.

## 0:00–0:10 — Introduction

**Presenter says:** “We’re StormStage. We help a small Calgary tow and roadside fleet decide where to wait as winter conditions change.”

**On screen:** StormStage title and tagline in the app. Keep the current MOCK / DEMO banner visible when presenting the shell.

**Rubric area supported:** Presentation & Demo Quality; Real Industrial Problem & Relevance.

## 0:10–1:00 — Problem

**Presenter says:** “During winter weather, reported traffic incidents can cluster in parts of Calgary while trucks wait elsewhere. Our question is practical: where should six trucks wait, hour by hour, to be closer to expected demand? We use incident history and weather to estimate demand over the next three hours, then choose staging locations. We are solving a fleet-location decision, not building a full traffic model. Faster response is the goal. We will test that goal by replaying real reported incidents and comparing both policies on exactly the same incidents.”

**On screen:** The app’s Calgary zones map. Describe the gray points as zone locations from `zones.csv`, not current incidents, observed hotspots, or forecast demand. The numerical snow-day examples in the README are not needed for this pitch; validate their data provenance before quoting them.

**Rubric area supported:** Real Industrial Problem & Relevance; Autonomous Reasoning + Data-Driven Decisions.

## 1:00–1:20 — User / industry relevance

**Presenter says:** “Our named intended user is an AMA roadside dispatcher; Calgary tow operators and the City’s Traffic Management Centre are also potential users. The operational question is whether better staging can improve coverage with the same fleet. A dispatcher’s feedback is still pending: [INDUSTRY QUOTE].”

**Delivery rule:** If a verified, attributable quote is unavailable, omit the last sentence and say, “We still need dispatcher feedback.” Do not imply any named organization is a customer or partner.

**On screen:** Keep the comparison view visible; point to the six-unit assignment tables as the fleet decision the user would review.

**Rubric area supported:** Real Industrial Problem & Relevance; Commercialization in Industry.

## 1:20–3:10 — Live demo

Use the detailed [demo runbook](demo-runbook.md). Reserve time for clicking and observing; do not fill the entire segment with speech.

| Time | What the presenter says | What should be on screen |
| --- | --- | --- |
| 1:20–1:35 | Integrated: “This is [FINAL DEMO DAY], our validated storm-day replay.” Shell: “This is the current interface walkthrough. The dates and truck behavior are fixtures.” | Selected storm day and hour. A validated day is blocked on A/B; the current control is `Storm day (mock)`. |
| 1:35–1:55 | “The left panel represents fixed staging. We begin before the change in conditions.” | Fixed staging and StormStage panels at the same hour. For the shell, set `Current hour` to 14 and select `StormStage`. |
| 1:55–2:15 | Integrated: “We advance to the change in conditions and inspect the updated demand.” Shell: “The hour slider advances the fixture display. Play is a placeholder.” | Replay controls. Show forecast changes only if A’s real output has been integrated by C. There is no demand visualization today. |
| 2:15–2:40 | Integrated: “StormStage changes staging where the expected saving justifies the move cost.” Shell: “At 15:00, the fixture changes Unit 3 from Z13 to Z14. This is illustrative, not an optimizer result.” | Hour 15; right-panel assignment table and truck markers. Actual replay positions and move decisions are blocked on B and C integration. |
| 2:40–2:55 | Integrated: “Here is the recorded reason for this move: [VALIDATED MOVE REASON].” Shell: “The decision log demonstrates a one-line explanation. Its snow and demand statements are mock messages.” | `Decision log — mock / demo` today, or a verified backend move reason after integration. |
| 2:55–3:10 | Integrated: “Both policies are scored by the same replay on the same incidents.” Shell: “These panels show the intended comparison; the displayed metrics are static placeholders.” | Side-by-side staging comparison, then results area. Keep all mock warnings visible. |

**Rubric area supported:** Autonomous Reasoning + Data-Driven Decisions; Execution & Software Architecture; Presentation & Demo Quality, to the extent actually demonstrated.

**Option A demo evidence:** after integration, show at least one coded plan → score → change-plan cycle: initial staging and its score, the hourly replan, and the revised plan’s score. The fixture slider change alone does not demonstrate this cycle. Evidence is pending B’s optimizer/simulator output and C’s app integration.

## 3:10–3:40 — Results

**Presenter says, only with validated results:** “On [FINAL DEMO DAY], the measured average-response difference is [AVG RESPONSE IMPROVEMENT] minutes, and the 90th-percentile difference is [P90 IMPROVEMENT] minutes. StormStage reaches [% WITHIN 15 MIN] percent of incidents within 15 minutes, compared with [FIXED % WITHIN 15 MIN] percent for fixed staging. These are replay results under the recorded assumptions, not field deployment results. Checks on two held-out storm days are [HELD-OUT VALIDATION STATUS].”

**Presenter says if results remain pending:** “Measured replay results are pending. The current dashboard numbers are illustrative and establish no benefit. Our evaluation will compare average response time, the 90th percentile, and the share reached within 15 minutes against fixed staging on the same incidents.”

**On screen:** Verified comparison outputs after B supplies replay logs and metrics and C connects them. Otherwise show the app’s mock warning and do not read its numeric cards as results. The measured-results ending is currently blocked.

**Rubric area supported:** Autonomous Reasoning + Data-Driven Decisions; Real Industrial Problem & Relevance.

**Measurement rules:** Define each response-time difference as fixed staging minus StormStage, in minutes; zero or negative results must be reported honestly. Report within-15 shares separately, or their difference in percentage points. Match the day, incidents, fleet size, dispatch rules, travel-time model, and service assumptions across policies. Do not claim forecast accuracy without a separate measured evaluation. The README calls for the demo day plus two held-out storm days; do not imply these checks have happened.

## 3:40–4:20 — Architecture

**Presenter says:** “The planned pipeline joins Open Calgary reported traffic incidents with ECCC hourly weather and forecasts zonal demand for the next three hours. Placement uses greedy selection and a swap pass; replay dispatches the nearest free truck. The hourly replan is our intended revise-and-rescore loop, with a move penalty. Fixed staging is the primary naive baseline; last week’s hotspots are secondary. On main, forecasting is a stub; the replay backend is not currently present on main / not yet integrated into the current app.”

**On screen:** Open the README’s “Picture of the loop” and “Steps” sections. Identify which parts are planned. Do not present the diagram as proof of a working end-to-end pipeline.

**Rubric area supported:** Execution & Software Architecture; Autonomous Reasoning + Data-Driven Decisions.

## 4:20–5:00 — Pilot and commercialization

**Presenter says:** “Our proposed next step is a pilot with one Calgary tow or roadside operator. First, validate the historical replay and review staging suggestions with a dispatcher. Then assess coverage and response outcomes before considering operational use. The commercial hypothesis is a dispatcher-facing staging tool, potentially sold as a fleet subscription. Pricing and willingness to pay remain untested. We are seeking an operator to validate the workflow, not claiming a signed customer. StormStage decides where to stage trucks from weather and incident history, replans as conditions change, and is evaluated against fixed staging on the same incidents.”

**On screen:** Return to the StormStage comparison view. Describe the pilot as a proposal; no pilot management, billing, or subscription feature exists in the current app.

**Rubric area supported:** Commercialization in Industry; Real Industrial Problem & Relevance; Presentation & Demo Quality.

## Dependencies and claims to resolve before delivery

- **A — Data & Forecast (assigned by the project build plan):** validated public incident/weather inputs, zone compatibility, storm-day evidence, and real `zone_id, expected_incidents` forecasts. [FINAL DEMO DAY] remains pending A/B validation; no forecast accuracy result is available.
- **B — Optimizer & Simulator (assigned by the project build plan):** actual positions, per-incident response logs, move reasons, measured metrics, and evidence of the coded plan → score → change-plan → rescore loop. [AVG RESPONSE IMPROVEMENT], [P90 IMPROVEMENT], [% WITHIN 15 MIN], [FIXED % WITHIN 15 MIN], [VALIDATED MOVE REASON], and [HELD-OUT VALIDATION STATUS] remain pending.
- **C — App, Voice & Pitch Lead (assigned by the project build plan):** connect verified outputs in a later implementation task. This documentation task does not implement integration or voice. [INDUSTRY QUOTE] needs a real source and attribution; it is an outreach dependency, not a backend result.
- **Existing-project conflicts:** the README tells users to press Play and describes a real replay with response-time reduction, but Play is inert and all current app metrics are mock. Its data-note link points to `data/README.md`, absent on main; on main, `forecast.py` expects an unavailable `data/processed/zones.csv` outside this checkout, while the app reads root `zones.csv`. Real incident/weather data, the real data pipeline, and a simulator are not currently present on main / not yet integrated into the current app; this does not establish the status of teammate branches. Treat the README’s performance language as an objective until validated. Current fixture dates are not evidence of validated storm days.
