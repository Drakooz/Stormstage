# StormStage — timed 5-minute pitch

For Role C — App, Voice & Pitch Lead. Reviewed against local main (`ccdcae8`), [test_summary.csv](../results/test_summary.csv), [RESULTS.md](../results/RESULTS.md), [forecast.py](../forecast.py), and the weather-driven replay exports. No slides are part of this deliverable.

> StormStage uses 6 base trucks plus up to 4 forecast-triggered on-call trucks. Fixed yards (naive) is the primary baseline; Best fixed plan is the stronger secondary comparator. A's causal weather-driven forecast is integrated, and the dashboard displays WEATHER-DRIVEN PRECOMPUTED REPLAY.

**Option A — own problem using public data:** show public-data evidence and **PLAN → SCORE → REVISE → RESCORE**. The intended user is a roadside-assistance dispatcher / Calgary tow operator. Open Calgary reported incidents are **not all collisions or all tow calls**. All response results are **simulated replay outcomes, not field-deployment results**.

Rubric mapping carried from the [submission checklist](submission-checklist.md): Autonomous Reasoning + Data-Driven Decisions (30%); Real Industrial Problem & Relevance (20%); Execution & Software Architecture (20%); Commercialization in Industry (15%); Presentation & Demo Quality (15%).

## 0:00–0:10 — Introduction

**Say:** “We're StormStage. We help a small Calgary tow and roadside fleet explore when to add on-call capacity and where active trucks should wait during winter conditions.”

**Screen:** title, tagline, and WEATHER-DRIVEN PRECOMPUTED REPLAY banner.

## 0:10–1:00 — Problem and policy revision

**Say:** “Our original hypothesis was to re-stage the same six trucks. We tested it, and it did not improve average storm-day response over the fixed baselines. We revised the policy: six base trucks plus up to four on-call trucks, activated when the forecast and recent incidents indicate a surge. The current pipeline combines incident history and weather. Our story is plan, score, revise, rescore; the measured revision is capacity timing, not a claimed same-fleet staging win.”

**Screen:** the citywide zone map, then the architecture visual. Gray dots are zone locations, not forecast intensity. Do not use unsupported incident-count anecdotes.

## 1:00–1:20 — Intended user

**Say:** “Our intended user is a roadside-assistance dispatcher or Calgary tow operator. We report response time alongside truck-hours to make the capacity trade-off visible. We still need dispatcher feedback; no customer, partner, or deployment is established.”

**Screen:** active-unit tables and truck-hour metrics. Naming an organization as a potential user does not establish engagement.

## 1:20–3:10 — Demonstration of the saved replay

Follow the [demo runbook](demo-runbook.md); reserve time for clicking and observing. All shown hours are Calgary local time (`America/Edmonton`). Present the saved replay with its source and simulation caveat visible.

| Time | Say | Screen / action |
| --- | --- | --- |
| 1:20–1:35 | “This is a weather-driven precomputed replay for February 4.” | Select `2025-02-04`, `StormStage + on-call`, hour 0; leave Play/Pause on Pause. |
| 1:35–1:55 | “Both start with six base trucks; Fixed yards is our primary baseline.” | Main comparison and active-unit tables at 00:00. Full-day score cards are not scores for this hour. |
| 1:55–2:15 | “The slider selects saved positions. It does not rerun the optimizer.” | Advance from hour 0 to hour 1; Play/Pause does not advance time. |
| 2:15–2:40 | “The recorded surge activates four on-call units.” | Show units 7–10 and the 01:00 activation reason: `incidents forecast x2.4 normal`. The signal combines weather lift and recent incidents; the log does not isolate which caused this event. |
| 2:40–2:55 | “The demonstrated revision here is extra capacity; this day has no recorded relocations.” | Decision log and status tables. Do not describe dispatch/return movement as re-staging. |
| 2:55–3:10 | “On this demo day, average simulated response was 20.1 minutes for Fixed yards and 9.8 for on-call.” | Full-day Feb 4 cards. Select `Best fixed plan` and open the selected-policy expander for the secondary comparator; main panels stay unchanged. |

**Cycle evidence:** connect the recorded capacity revision to the completed replay outcome, then explain the tested policy revision from same-six-truck staging to on-call in the aggregate results. The slider does not provide an initial-hour score or a per-step rescore. No relocation reason should be invented for Feb 4.

## 3:10–3:40 — Measured results

**Say:** “Across 12 designated storm test days using a causal forecast, average simulated response fell from 14.1 minutes for Fixed yards to 10.6 for StormStage plus on-call. It beat Fixed yards on 10 of 12 days and Best fixed plan on 8 of 12. On-call used 176.5 truck-hours per day. Keeping all ten trucks active all day was faster, but used 240. These are simulated replay outcomes, not field-deployment results.”

**Screen:** the aggregate table in [README](../README.md) or [submission draft](submission-draft.md), clearly labeled **12 designated storm test days**. Feb 4's 20.1 versus 9.8-minute cards are a single-day example, not that aggregate.

**Supporting values for Q&A:** mean daily p90 was 27.1 minutes for Fixed yards versus 18.9 for on-call; mean daily within-15 share was 68.2% versus 79.3%. Best fixed plan averaged 13.7 minutes. Same-six-truck StormStage averaged 14.2 minutes. Fixed ten trucks all day averaged 7.5 minutes. Sources: [test_summary.csv](../results/test_summary.csv) and [day-win counts](../results/RESULTS.md).

## 3:40–4:20 — Architecture and evidence limits

**Say:** “Open Calgary reported incidents and ECCC hourly weather feed a causal next-three-hour forecast. It fits only on data before the requested UTC decision date and allocates citywide demand to historical zone shares. The backend refreshes demand hourly, chooses capacity and staging, and replays shared dispatch assumptions. Streamlit reads saved positions, reasons, and scores in Calgary local time. We have an exclusion-scope discrepancy to resolve: A explicitly reserves the three demo dates and following UTC dates, while the result report claims broader exclusions. We do not claim every evaluation day was fully excluded from A's training.”

**Screen:** [architecture visual](architecture-visual.md), then the evidence-boundary note in [architecture specification](architecture-spec.md). Scores inform our policy experiment; they are not an online optimizer feedback input.

## 4:20–5:00 — Next step and close

**Say:** “The next step is dispatcher review of the assumptions and suggested capacity timing, followed by a proposed pilot if that review supports it. Customer validation, pricing, and field benefits remain untested. We started with re-staging the same six trucks, scored it, revised to forecast-triggered on-call capacity, and rescored. The evidence supports a response-versus-capacity trade-off under simulation assumptions.”

**Screen:** return to the comparison. Describe the pilot as a proposal, without a customer commitment or monetary-savings claim.

## Delivery checks and Q&A boundaries

- **Results:** report daily-metric averages across designated dates, not pooled incident statistics. Use Fixed yards as primary and Best fixed plan as secondary. On-call has extra capacity; do not call its gain a same-fleet improvement.
- **Forecast exclusions:** `forecast.py` reserves Feb 4, Feb 14, and Nov 24 (+ following UTC dates). Causality does not establish exclusion of all 12 storm and 8 normal evaluation days; A/B must reconcile the broader wording in `results/RESULTS.md`.
- **Simulation:** shared nearest-arrival dispatch, straight-line distance × 1.3 at 40 km/h, 30 minutes on scene. Truck-hours do not establish monetary costs or savings.
- **Presentation:** Play/Pause remains a placeholder; demand visualization and voice are absent. Use the slider and status tables. Prepare screenshots/recording and rehearse offline map fallbacks.
- **Unresolved submission items:** confirmed GitHub handles, screenshots, demo URL, clean-clone verification, and team review remain in the [checklist](submission-checklist.md). No attributable industry quote is established.
