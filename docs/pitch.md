# StormStage — five-minute pitch

Use Presentation Mode, Feb 4, 2025. Keep technical details collapsed. Rehearse the script aloud; the timings include clicks and pauses. Pair with the [demo runbook](demo-runbook.md) and [judge Q&A](judge-qa.md).

## 0:00–0:40 — Introduce the problem

**Say:** “We’re Admest FC, and this is StormStage. It helps a small Calgary tow and roadside fleet explore when to add capacity and where active trucks should wait during winter conditions. Winter incident demand changes, while fixed waiting locations and a fixed fleet do not automatically adapt. Our intended user is a roadside-assistance dispatcher or Calgary tow operator.”

**Screen:** StormStage title, weather-driven precomputed simulation badge, Presentation Mode. Move Replay hour to 00:00.

## 0:40–1:20 — Explain what the evidence changed

**Say:** “Our original hypothesis was to re-stage the same six trucks. We scored it, and it did not improve aggregate average response over the fixed baselines: 14.2 minutes versus 14.1 for Fixed yards and 13.7 for Best fixed plan. We revised the policy to forecast-triggered on-call capacity: six base trucks, plus up to four when the surge signal crosses the threshold. That is our plan, score, revise, rescore story.”

**Screen:** six base trucks at 00:00. Mention that the strategy strip below records the tested policy revision.

## 1:20–2:40 — Demonstrate the recorded decision

**Say:** “This is a saved weather-driven replay for February 4, in Calgary local time. The map uses actual exported truck coordinates and reported incidents. The slider selects saved positions; it does not run the optimizer.”

**Action:** move Replay hour from 00:00 to 01:00. Pause for the cards and map to update.

**Say:** “At 01:00 the recorded signal is 2.4 times normal, above the 2.0 threshold. Four on-call trucks activate, taking the fleet from six to ten. The signal combines weather lift and recent incident activity; the log does not show weather alone caused it. The decision panel explains that event. Truck colors distinguish availability, response, time on scene, and return travel. Units sharing a position share a labeled marker; hover shows their individual statuses. This day has no recorded relocations, so the demonstrated revision is capacity.”

**Screen:** activation cards, operations map, and decision explanation. Do not open raw tables during the pitch.

## 2:40–3:20 — Show the selected-day trade-off

**Action:** scroll to “Did the decision help?”

**Say:** “For February 4 alone, simulated average response fell from 20.1 to 9.8 minutes, a 51.2 percent reduction. Capacity rose from 144 to 228 truck-hours. Faster simulated response required additional on-call capacity. These are completed full-day outcomes; they do not change when we move the slider.”

## 3:20–4:10 — Show the broader evidence and rescore

**Action:** show “Across 12 storm test days,” then “The evidence changed our strategy.”

**Say:** “Across 12 designated storm test days using a causal forecast, average simulated response fell from 14.1 to 10.6 minutes. The mean daily share reached within 15 minutes rose from 68.2 to 79.3 percent. On-call beat Fixed yards on ten of twelve days and Best fixed plan on eight of twelve. It used 176.5 truck-hours per day. Keeping all ten trucks active all day was faster at 7.5 minutes, but used 240 truck-hours. We expose that trade-off. The strategy strip connects our original six-truck hypothesis to the 14.2-minute score, the on-call revision, and the 10.6-minute rescore.”

## 4:10–4:40 — Explain the architecture and limits

**Say:** “Open Calgary reported incidents and ECCC hourly weather feed a causal next-three-hour forecast, capacity and staging plans, and replay scoring. Streamlit reads the precomputed output. These are simulated replay outcomes, not field-deployment results. Reported incidents are not all crashes or all tow calls. Truck-hours measure capacity use, not proven monetary cost.”

**Screen:** use the [architecture visual](architecture-visual.md) if needed; otherwise keep the evidence strip visible. Scores inform the tested policy revision, not an online optimizer feedback input.

## 4:40–5:00 — Next step

**Say:** “Our next step is dispatcher review of the assumptions and suggested capacity timing, followed by a possible operational pilot. No customer, partner, deployment, pricing, or savings validation exists yet. The evidence helped us revise the problem from moving the same fleet to deciding when to add capacity.”

**Q&A boundary:** evaluation uses a causal rolling-origin / out-of-time forecast fitted only on information available before each requested UTC date. Earlier evaluation dates may become historical training data for later replay dates, so this is not a single frozen holdout set. `forecast.py` explicitly excludes Feb 4, Feb 14, and Nov 24 plus each following UTC date; policy settings were selected on separate tuning days. Do not claim all 12 storm and 8 normal evaluation dates were excluded from A's training. Daily aggregate p90 values are means of daily percentiles, not pooled incident percentiles. See [judge Q&A](judge-qa.md).

Before filing, the team must confirm member handles, registration/attestations, firsthand reflections, source usage, and any demo link. The final submission is a team action.
