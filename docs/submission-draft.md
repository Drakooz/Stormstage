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

Adaptive tow-truck staging for Calgary winter incidents.

## 6. About the Project

### Inspiration

Where should a small Calgary tow and roadside fleet wait as winter conditions change? StormStage targets a **roadside-assistance dispatcher / Calgary tow operator**, with the goal of placing trucks closer to expected demand using incident history and weather. Open Calgary records describe **reported traffic incidents**, not all collisions or every tow request. No customer, partner, or industry validation is established.

### What we learned

We learned that fair evaluation requires the same incidents and fleet, dispatch, travel, and service assumptions across policies. Traceable replay logs matter more than illustrative UI metrics, and separating forecasting, placement, replay, and scoring makes each component easier to validate.

[TEAM-CONFIRMED LEARNINGS: add a brief firsthand learning from the build; personal team reflections remain pending.]

### How we built it

Our Python dashboard uses Streamlit, Pandas, and Pydeck to show zone maps, side-by-side staging tables, and labeled mock metrics and decision messages. Raw and cleaned incident CSVs and a 2025 filtering script are present; provenance, output validation, and app integration remain pending.

The intended architecture combines Open Calgary incidents with ECCC hourly weather to forecast next-three-hour zonal demand and run **forecast → place/re-plan → replay/score → revise → rescore** as conditions change. **Fixed staging is the primary naive baseline.** The autonomous backend is not yet verified as integrated: forecasting remains a stub, and placement, replay, and scoring are not connected to the app.

### Challenges

The integration challenges are documenting time zones and data coverage, aligning the forecast's zone path and interface, agreeing backend/UI schemas, and replacing fixtures with verified outputs.

## 7. Screenshots

[FINAL SCREENSHOTS: attach 2–5 captioned PNG/JPG/GIF images, each ≤10 MB. Include the staging comparison and decision/results evidence; identify the commit and, for a verified replay, its day/run ID. Label shell captures MOCK / DEMO and keep their warnings visible. No final screenshots are supplied yet.]

## 8. Demo Video / Live Site

[DEMO URL: add a judge-accessible video and/or live-site link. Video preferably ≤5 minutes. State whether it shows the current mock shell or a verified integrated replay; no final demo URL is supplied yet.]

## 9. Additional Info

**Repository:** [Drakooz/Stormstage](https://github.com/Drakooz/Stormstage)

**Architecture:** [Specification and component status](https://github.com/Drakooz/Stormstage/blob/main/docs/architecture-spec.md). [FINAL ARCHITECTURE IMAGE/LINK: add the reviewed judge-facing diagram, distinguishing implemented, stub, and pending components.]

**Public data:** Open Calgary reported incidents; planned ECCC hourly weather for Calgary International is not integrated. [FINAL DATASET CITATIONS: supply exact source URLs, incident coverage, weather station ID/coverage, download instructions, usage terms, cleaning and time-zone rules, and validation evidence.]

**Evaluation:** Compare Fixed staging with StormStage on the same incidents and simulation assumptions, using only information available at each decision time. Historical hotspots is optional. Validation on a demo day and two held-out storm days is planned and remains pending.

[FINAL FLEET CONFIGURATION: confirm fleet size, any on-call capacity, initial staging, and dispatch/travel/service/relocation assumptions. The README and shell use six trucks; neither that configuration nor a six-plus-on-call design is established as final.]

**Final measured results: pending; no benefit is established.** Mock values and unmerged/unfinalized B branch or patch metrics are excluded.

[FINAL MEASURED RESULTS EVIDENCE: add validated demo/held-out days, run IDs, evaluated commit, response logs, simulation assumptions, and evidence of a coded revision followed by rescoring.]

| Replay metric | Fixed staging | StormStage |
| --- | --- | --- |
| Average response time (minutes) | [FINAL MEASURED FIXED AVG] | [FINAL MEASURED STORMSTAGE AVG] |
| 90th-percentile response time (minutes) | [FINAL MEASURED FIXED P90] | [FINAL MEASURED STORMSTAGE P90] |
| Incidents reached within 15 minutes (%) | [FINAL MEASURED FIXED WITHIN-15] | [FINAL MEASURED STORMSTAGE WITHIN-15] |
| Truck relocations, if measured | [FINAL MEASURED FIXED RELOCATIONS] | [FINAL MEASURED STORMSTAGE RELOCATIONS] |

Report zero or negative differences honestly. Replay results describe simulated outcomes under documented assumptions, not field deployment gains or forecast accuracy.

**Local setup:** Python 3.10+, `pip install -r requirements.txt`, then `streamlit run app.py`. Clean-clone verification remains pending. [FINAL DEMO STATUS: update after integration and clean-clone verification.]
