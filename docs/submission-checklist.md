# StormStage submission checklist

Reviewed October 4, 2026 against evidence base `03d52e6`; UI release validation is recorded in [final handoff](final-handoff.md). A's causal weather-driven forecast, B's measured evaluation/replays, and C's dashboard are integrated. Evaluation and replay exports identify forecast source `a`. Checked items mean repository evidence or recorded verification exists; they do not mean submission approval or field validation. A = Data & Forecast; B = Optimizer & Simulator; C = App, Voice & Pitch Lead.

Organizer references carried from the earlier review at organizer commit `fe3d53c`: [README](https://github.com/nagusubra/industry-hackathon-lab/blob/main/README.md), [submission guide](https://github.com/nagusubra/industry-hackathon-lab/blob/main/SUBMISSIONS.md), [issue form](https://github.com/nagusubra/industry-hackathon-lab/blob/main/.github/ISSUE_TEMPLATE/submission.yml), [rules](https://github.com/nagusubra/industry-hackathon-lab/blob/main/RULES.md), and [rubric](https://github.com/nagusubra/industry-hackathon-lab/blob/main/JUDGING_RUBRIC.md).

**Recorded deadline: Sunday, October 4, 2026, 12:00 PM MDT (America/Edmonton).** The recorded submission path is one Hackathon Submission issue. The earlier form/guide review treated demo links and additional info as optional despite the README's package list; include both. This cleanup does not file a submission or re-verify organizer/account state.

## READY — repository evidence

- [x] **Team:** Admest FC — Thamer Elsadek, Salif Sylla, Adam Bensidi, as recorded in [README](../README.md). Confirmed handles remain unresolved below.
- [x] **Stream / path:** Software and Computational Math; Option A — own problem using public data.
- [x] **Title / description:** StormStage — forecast-triggered on-call capacity and adaptive tow-truck staging for Calgary winter incidents.
- [x] **Repository link:** [Drakooz/Stormstage](https://github.com/Drakooz/Stormstage). Judge-access verification remains a final check.
- [x] **Architecture:** [specification](architecture-spec.md) and [inline judge-facing visual](architecture-visual.md) describe the integrated pipeline and evidence boundaries.
- [x] **Pitch / walkthrough:** [pitch](pitch.md) and [demo runbook](demo-runbook.md) contain measured source-`a` results and separate the Feb 4 demo from the storm-test aggregate.
- [x] **Policy revision:** same-six-truck staging did not improve aggregate average response over fixed baselines; the team revised to 6 base trucks + up to 4 forecast-triggered on-call trucks and rescored.
- [x] **Comparator order:** Fixed yards (naive) is primary; Best fixed plan is the stronger secondary comparator. Both use six trucks; disclose extra capacity for on-call.
- [x] **Integrated data / forecast:** processed hourly weather, joined incidents, citywide zones, and `forecast.py` are present; [data/README.md](../data/README.md) documents UTC preparation, causal fitting, and limitations.
- [x] **Backend / exports / dashboard:** placement, hourly revision, dispatch, reasons, scoring, and regenerated replay exports are tracked. Dashboard metrics come from the selected day's replay; it is not a live optimizer.
- [x] **Measured storm results:** [test_summary.csv](../results/test_summary.csv) covers 12 designated storm test days: Fixed yards average 14.1 minutes; Best fixed plan 13.7; same-six-truck StormStage 14.2; on-call 10.6. On-call uses 176.5 truck-hours/day; fixed ten trucks all day uses 240 and averages 7.5 minutes.
- [x] **Day wins:** on-call beats Fixed yards on 10 of 12 storm days and Best fixed plan on 8 of 12 ([RESULTS.md](../results/RESULTS.md)).
- [x] **Demo evidence:** Feb 4 full-day average is 20.1 minutes for Fixed yards versus 9.8 for on-call; activation is recorded at 01:00 Calgary local time, with no relocations. This is not the 12-day aggregate.
- [x] **PLAN → SCORE → REVISE → RESCORE:** tested policy revision is supported by same-fleet and on-call results; hourly revisions are logged. Slider snapshots and full-day cards do not establish per-step scores.

## OWNER REVIEW — evidence limitations

- [x] **Evaluation methodology documented:** causal rolling-origin / out-of-time evaluation fits A only on information available before each requested UTC date. Earlier evaluation dates may become historical training data for later replay dates; this is not a single frozen holdout set. `forecast.py` explicitly excludes Feb 4, Feb 14, and Nov 24 plus each following UTC date. Policy settings were selected on separate tuning days. The 12 storm and 8 normal evaluation dates were not all excluded from A's training. [RESULTS.md](../results/RESULTS.md) and the release documents describe this limitation consistently.
- [ ] **A — source/usage review:** `data/README.md` is present and documents ECCC station identifiers, coverage, preparation, time zones, and limitations. Confirm the exact Open Calgary source/download citation and usage terms for both sources before filing; do not claim this review is complete.
- [ ] **A/B — traceability review:** confirm evaluated commit/run provenance and shared replay assumptions. Current files identify forecast `a`; documentation cites inspected local main, not a separately recorded evaluation run ID.
- [ ] **Team — limits:** maintain “simulated replay outcomes, not field-deployment results” and “reported incidents are not all collisions or all tow calls.” Do not imply forecast accuracy, customer validation, pricing, monetary savings, or deployment from response scores.

## WAITING ON C / TEAM — submission assets

- [ ] **Confirmed member handles:** contributor usernames do not establish identity. Keep unresolved placeholders in the submission draft.

  | Member | Confirmed GitHub handle |
  | --- | --- |
  | Thamer Elsadek | Pending confirmation |
  | Salif Sylla | Pending confirmation |
  | Adam Bensidi | Pending confirmation |

- [x] **About text / results draft:** [submission-draft.md](submission-draft.md) reflects integrated code, the measured limitation and revision, and the response/capacity trade-off.
- [ ] **Team review:** confirm firsthand learnings and challenges; fill the remaining personal-reflection placeholder only with team-confirmed content.
- [ ] **2–5 screenshots:** PNG/JPG/GIF, ≤10 MB each per the recorded submission requirements. No final assets supplied. Capture maps/tables, activation reason, and results; label day, source `a`, commit, and WEATHER-DRIVEN PRECOMPUTED REPLAY.
- [ ] **Demo video / live-site URL:** judge-accessible link, video preferably ≤5 minutes. No URL supplied; do not imply a deployed operational system.
- [x] **Clean-clone verification:** fresh clone of `839c6a9`, fresh Python 3.14.3 environment, dependency install, data preparation, all 25 tests, import check, and Streamlit/browser launch. Tracked evidence remained unchanged. Exact commands/results are in [final handoff](final-handoff.md).
- [ ] **Demo rehearsal:** Feb 4, hour 0→1, recorded on-call reason, capacity change, selected-day scores, secondary comparator, then separately labeled 12-day aggregate. No Feb 4 relocation should be invented.
- [x] **Local backup package:** actual screenshots, synchronized architecture diagram, verified results/logs, tracked local replay data, and startup/fallback instructions. A browser check blocking external requests verified local cards, result bands, and the truck table. Map backgrounds still require internet; no recording is supplied.
- [x] **Presentation limits:** the manual replay slider is functional; no placeholder playback control remains. No forecast heatmap or voice control is claimed. Weather-driven simulation labels and evidence caveats remain visible.

## FINAL TEAM CHECK

- [ ] Confirm names/handles, registration, original work, one submission, rules, and Code of Conduct agreement. Registration is unverified.
- [ ] Confirm Option A fit, cited public data, intended dispatcher/tow-operator user, primary/secondary baselines, measured results, and coded policy revision. No customer, partner, industry quote, or deployment is established.
- [ ] Review all form fields, recorded ≤3-line/~280-character tagline constraint, setup, architecture, evidence caveats, and judge access. Preserve genuine unknown handles/assets; final response metrics are filled.
- [ ] Rehearse the 5-minute pitch and 3-minute Q&A. Distinguish aggregate daily-metric means from the Feb 4 score, capacity use from monetary cost, and simulated results from field gains.
- [ ] Assign owners for the source/usage checks and retain the documented rolling-origin evaluation limitation in the submission.
- [ ] **File before the recorded deadline:** designate author; use [Hackathon Submission](https://github.com/nagusubra/industry-hackathon-lab/issues/new?template=submission.yml). Record URL/timestamp and resolve validator feedback before lock. Only the author edits the body. Filing remains outside this task.
