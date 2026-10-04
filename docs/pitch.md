# StormStage — timed 5-minute pitch

Prepared for Role C — App, Voice & Pitch Lead. Based on current main (`1081dfa`), the [README](../README.md), [dashboard](../app.py), [B implementation notes](../B_PLACEMENT_SIMULATOR.md), and [interim results](../results/RESULTS.md). No slides are part of this deliverable.

> StormStage uses 6 base trucks plus up to 4 forecast-triggered on-call trucks, staging/re-staging active trucks near expected demand. Fixed yards (naive) is the primary baseline; Best fixed plan is the stronger secondary comparator.

The dashboard reads precomputed B replay positions, decisions, incident responses, and full-day metrics. These use the **stand-in forecast**; A's real weather-driven forecast is **not yet integrated**. Keep **PRECOMPUTED / INTERIM** labels visible. Final weather-driven results remain **[PENDING]**.

**Official hackathon rubric:**

- Autonomous Reasoning + Data-Driven Decisions — 30%
- Real Industrial Problem & Relevance — 20%
- Execution & Software Architecture — 20%
- Commercialization in Industry — 15%
- Presentation & Demo Quality — 15%

**Option A — own problem using public data:** demonstrate public-data evidence, **Fixed yards (naive)** as the primary naive baseline, and a coded **plan → score → revise → rescore** cycle. Use **Best fixed plan** as the stronger secondary comparator. The intended user is a **roadside-assistance dispatcher / Calgary tow operator**. Naming AMA roadside as an example does not establish engagement or a customer relationship. Open Calgary records describe **reported traffic incidents**, not all collisions.

## 0:00–0:10 — Introduction

**Presenter says:** “We’re StormStage. We help a small Calgary tow and roadside fleet decide where to wait as winter conditions change.”

**On screen:** StormStage title, tagline, and **PRECOMPUTED / INTERIM** banner.

**Rubric area supported:** Presentation & Demo Quality; Real Industrial Problem & Relevance.

## 0:10–1:00 — Problem

**Presenter says:** “During winter weather, demand can outgrow a small fleet's capacity. We first tested re-staging the same six trucks; the stand-in evaluation showed little advantage over fixed staging. That led us to revise the policy: six base trucks, plus up to four on-call trucks activated when forecasted demand indicates a surge. We stage and re-stage active trucks near expected demand over the next three hours. The final design uses weather and incident history; today's replay uses a stand-in forecast, with the real weather-driven evaluation still pending.”

**On screen:** The app's 179-zone citywide grid. Gray points are zone locations, not forecast demand. Skip numerical snow-day anecdotes unless their provenance has been checked.

**Rubric area supported:** Real Industrial Problem & Relevance; Autonomous Reasoning + Data-Driven Decisions.

## 1:00–1:20 — User / industry relevance

**Presenter says:** “Our intended user is a roadside-assistance dispatcher or Calgary tow operator. The decision is when to call in extra capacity and where to stage active trucks. We report truck-hours alongside response times so the cost of that capacity is visible. Dispatcher feedback is pending: [INDUSTRY QUOTE].”

**Delivery rule:** If a verified, attributable quote is unavailable, omit the last sentence and say, “We still need dispatcher feedback.” Do not imply any named organization is a customer or partner.

**On screen:** Keep the comparison view visible; point to active-unit tables and truck-hours.

**Rubric area supported:** Real Industrial Problem & Relevance; Commercialization in Industry.

## 1:20–3:10 — Live demo

Use the detailed [demo runbook](demo-runbook.md). Reserve time for clicking and observing; do not fill the entire segment with speech.

| Time | What the presenter says | What should be on screen |
| --- | --- | --- |
| 1:20–1:35 | “This is a precomputed stand-in replay, not final weather-driven performance.” | Select `2025-02-04`, `StormStage + on-call`, and hour 6. Final day remains [FINAL DEMO DAY]. |
| 1:35–1:55 | “Fixed yards (naive) uses six trucks; StormStage starts with six base trucks.” | Main comparison at the same hour; show active-unit tables. |
| 1:55–2:15 | “The hour slider advances the recorded replay. Play is a placeholder.” | Advance from 6 to 7. Explain the stand-in forecast trigger from the log; no demand layer is available. |
| 2:15–2:40 | “The recorded surge activates on-call capacity, then active trucks are re-staged.” | Show added units and recorded moves. This event does not prove weather anticipation. |
| 2:40–2:55 | “Here is the recorded reason for an activation and a move.” | `Decision log — precomputed replay`; read actual reasons. Final weather-driven reason remains [VALIDATED MOVE REASON]. |
| 2:55–3:10 | “Both policies use the same incidents and shared simulation assumptions; StormStage can use extra capacity.” | Main comparison and full-day metrics; choose `Best fixed plan` in the Policy dropdown and open the selected-policy expander for the secondary comparator. |

**Rubric area supported:** Autonomous Reasoning + Data-Driven Decisions; Execution & Software Architecture; Presentation & Demo Quality, to the extent actually demonstrated.

**Option A demo evidence:** show initial plan/score, a recorded hourly capacity/staging revision, then its rescore using verified backend evidence. B implements the replay loop, but the slider only selects snapshots and the metric cards are full-day summaries. Keep **[FINAL WEATHER-DRIVEN CYCLE EVIDENCE]** pending until A/B rerun and verify it.

## 3:10–3:40 — Results

**Presenter says, only after final weather-driven validation:** “On [FINAL DEMO DAY], the average-response difference against Fixed yards (naive) is [AVG RESPONSE IMPROVEMENT] minutes and the 90th-percentile difference is [P90 IMPROVEMENT] minutes. StormStage reaches [% WITHIN 15 MIN] percent within 15 minutes, compared with [FIXED % WITHIN 15 MIN]. Truck-hours are [FINAL TRUCK-HOURS COMPARISON]; the Best fixed plan comparison is [FINAL SECONDARY COMPARISON]. Held-out evaluation is [HELD-OUT VALIDATION STATUS]. These are simulated outcomes, not field deployment gains.”

**Presenter says today:** “The current results are simulated stand-in outcomes. Same-six-truck re-staging showed little advantage, which led us to add forecast-triggered on-call capacity. Final weather-driven metrics are pending. We compare response times and the share reached within 15 minutes against Fixed yards (naive) and Best fixed plan, while reporting truck-hours.”

**On screen:** Interim full-day cards and their warning, with [B results](../results/RESULTS.md) as supporting stand-in evidence. Never present these numbers as final weather-driven performance.

**Rubric area supported:** Autonomous Reasoning + Data-Driven Decisions; Real Industrial Problem & Relevance.

**Measurement rules:** Define response-time differences as comparator minus StormStage, in minutes; report zero/negative outcomes honestly. Report within-15 differences in percentage points. Match incidents, dispatch, travel, and service assumptions; disclose 6 baseline trucks versus 6 base + up to 4 on-call and report truck-hours. B's current stand-in evaluation covers 12 held-out storm days and 8 normal days. Final weather-driven evaluation and forecast-accuracy evidence remain pending.

## 3:40–4:20 — Architecture

**Presenter says:** “The final pipeline uses Open Calgary reported incidents and ECCC hourly weather to forecast next-three-hour zonal demand. It activates on-call capacity during a forecast surge and stages active trucks with greedy placement, swaps, and a move penalty. Replay uses nearest-arrival dispatch. Our loop is plan, score, revise, rescore. The backend and exported replays are on main; the current forecast is a stand-in. A's real weather-driven model still needs integration.”

**On screen:** Open the README loop or [architecture specification](architecture-spec.md). Identify the implemented stand-in path and pending real-forecast handoff.

**Rubric area supported:** Execution & Software Architecture; Autonomous Reasoning + Data-Driven Decisions.

## 4:20–5:00 — Pilot and commercialization

**Presenter says:** “Our proposed next step is to validate the weather-driven replay and review capacity and staging suggestions with a dispatcher, then explore a pilot with one Calgary operator. A fleet subscription is a commercial hypothesis; pricing and willingness to pay are untested. No customer or deployment is established. StormStage's final design is six base trucks plus up to four forecast-triggered on-call trucks, staged near expected demand.”

**On screen:** Return to the StormStage comparison view. Describe the pilot as a proposal; no pilot management, billing, or subscription feature exists in the current app.

**Rubric area supported:** Commercialization in Industry; Real Industrial Problem & Relevance; Presentation & Demo Quality.

## Dependencies and claims to resolve before delivery

- **A — Data & Forecast (assigned by the project build plan):** validated public incident/weather inputs, zone compatibility, storm-day evidence, and real `zone_id, expected_incidents` forecasts. [FINAL DEMO DAY] remains pending A/B validation; no forecast accuracy result is available.
- **B — Optimizer & Simulator:** integrate A's real forecast, rerun held-out evaluation and exports, and verify final cycle/results evidence. All final metric placeholders above remain pending; current stand-in logs/results are available on main.
- **C — App, Voice & Pitch Lead:** verify regenerated exports and rehearse the demo; prepare screenshots/recording. Voice is absent. [INDUSTRY QUOTE] needs source and attribution.
- **Remaining integration limits:** `data/README.md` and processed hourly weather are absent; A's stub path/zone coverage differs from B's grid. Play is inert, and the dashboard has no forecast view or per-step rescoring. Resolve these through teammate implementation; this task edits documentation only.
