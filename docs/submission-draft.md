## 1. Team Name

Admest FC

## 2. Team Member Names and GitHub Handles

- Thamer Elsadek — [GITHUB HANDLE: confirm with Thamer]
- Salif Sylla — [GITHUB HANDLE: confirm with Salif]
- Adam Bensidi — [GITHUB HANDLE: confirm with Adam]

## 3. Project Stream

Software and Computational Math

Option A — own problem using public data.

## 4. Project Title

StormStage

## 5. Project Short Description

Forecast-triggered on-call capacity and adaptive tow-truck staging for Calgary winter incidents.

## 6. About the Project

### Inspiration

When should a small Calgary tow and roadside fleet add capacity, and where should active trucks wait as winter conditions change? StormStage targets a **roadside-assistance dispatcher / Calgary tow operator**. Its final design uses **6 base trucks + up to 4 additional on-call trucks**, activated when forecasted demand indicates a surge, with active trucks staged/re-staged near expected demand. Open Calgary records describe **reported traffic incidents**, not all collisions or every tow request. No customer, partner, deployment, or industry validation is established.

### What we learned

Testing re-staging with the same six trucks showed little advantage over fixed staging in B's stand-in evaluation. That finding led the team to revise the policy to forecast-triggered on-call capacity. Fair evaluation uses the same incidents, dispatch, travel, and service assumptions, while exposing the capacity difference through truck-hours. Traceable replay logs and separate forecast, placement, replay, and scoring components make the evidence easier to inspect.

[TEAM-CONFIRMED LEARNINGS: add a brief firsthand learning from the build; personal team reflections remain pending.]

### How we built it

Our Python dashboard uses Streamlit, Pandas, and Pydeck to show precomputed truck positions, incident responses, decision reasons, and full-day metrics. Raw/cleaned incident CSVs, monthly UTC weather files, B's placement/replay/scoring backend, and replay exports are on main. Dataset documentation and final weather-driven validation remain pending.

The final architecture combines Open Calgary incidents with ECCC hourly weather to forecast next-three-hour zonal demand, activate on-call capacity during a surge, and stage active trucks through **plan → score → revise → rescore**. **Fixed yards (naive)** is the primary naive baseline; **Best fixed plan** is the stronger secondary comparator. Current B results/replays use the **stand-in forecast**; A's real weather-driven forecast is **not yet integrated**. Final weather-driven metrics remain placeholders.

### Challenges

The remaining integration challenges are documenting source coverage/time zones, aligning A's forecast with B's citywide zones and interface, supplying processed weather, and regenerating verified weather-driven evaluation/replays.

## 7. Screenshots

[FINAL SCREENSHOTS: attach 2–5 captioned PNG/JPG/GIF images, each ≤10 MB. Include staging, on-call decisions, and results; identify commit/day/run ID and forecast source. Label current captures PRECOMPUTED / INTERIM — stand-in forecast. No final screenshots are supplied yet.]

## 8. Demo Video / Live Site

[DEMO URL: add a judge-accessible video and/or live-site link, preferably ≤5 minutes. State whether it shows the current stand-in replay or a verified final weather-driven replay; no final URL is supplied yet.]

## 9. Additional Info

**Repository:** [Drakooz/Stormstage](https://github.com/Drakooz/Stormstage)

**Architecture:** [Specification and component status](https://github.com/Drakooz/Stormstage/blob/main/docs/architecture-spec.md). [FINAL ARCHITECTURE IMAGE/LINK: add the reviewed judge-facing diagram, distinguishing implemented, stub, and pending components.]

**Public data:** Open Calgary reported incidents and raw ECCC hourly UTC weather files are tracked. The real weather-driven forecast is not yet integrated. [FINAL DATASET CITATIONS: supply exact source URLs, incident coverage, weather station ID/coverage, download instructions, usage terms, cleaning and time-zone rules, and validation evidence.]

**Evaluation:** Compare StormStage + on-call against **Fixed yards (naive)** (primary) and **Best fixed plan** (stronger secondary) on the same incidents, dispatch, travel, and service assumptions, using only information available at decision time. Both static comparators use 6 trucks; StormStage uses 6 base + up to 4 on-call. Report truck-hours alongside response metrics. B's stand-in evaluation covers 12 held-out storm days and 8 normal days; final weather-driven evaluation remains pending.

**Final fleet design:** 6 base trucks + up to 4 forecast-triggered on-call trucks; stage/re-stage active trucks near expected demand. [FINAL RUN CONFIGURATION: document the real-forecast trigger, initial staging, and dispatch/travel/service/relocation assumptions after integration.]

**Final weather-driven results: [PENDING].** Current [B results](../results/RESULTS.md) and dashboard metrics are simulated stand-in outcomes, not final weather-driven performance or field deployment gains. Do not fill the final table from interim exports.

[FINAL WEATHER-DRIVEN RESULTS EVIDENCE: add validated demo/held-out days, run IDs, evaluated commit, forecast source, response logs, capacity costs, assumptions, and coded plan → score → revise → rescore evidence.]

| Final weather-driven replay metric | Fixed yards (naive) | Best fixed plan | StormStage + on-call |
| --- | --- | --- | --- |
| Average response time (minutes) | [FINAL NAIVE AVG] | [FINAL BEST FIXED AVG] | [FINAL STORMSTAGE AVG] |
| 90th-percentile response time (minutes) | [FINAL NAIVE P90] | [FINAL BEST FIXED P90] | [FINAL STORMSTAGE P90] |
| Incidents reached within 15 minutes (%) | [FINAL NAIVE WITHIN-15] | [FINAL BEST FIXED WITHIN-15] | [FINAL STORMSTAGE WITHIN-15] |
| Truck-hours | [FINAL NAIVE TRUCK-HOURS] | [FINAL BEST FIXED TRUCK-HOURS] | [FINAL STORMSTAGE TRUCK-HOURS] |
| Relocations / on-call activations | [FINAL NAIVE COUNTS] | [FINAL BEST FIXED COUNTS] | [FINAL STORMSTAGE COUNTS] |

Report zero or negative differences honestly. Replay results describe simulated outcomes under documented assumptions, not field deployment gains or forecast accuracy.

**Local setup:** Python 3.10+, `pip install -r requirements.txt`, then `streamlit run app.py`. Clean-clone verification remains pending. [FINAL DEMO STATUS: update after integration and clean-clone verification.]
