# StormStage submission checklist

Reviewed October 3, 2026 against merged `origin/main` (`1668de9`), included in the current checkout. The 2025 incident-cleaning work is now on main; PR #3 is no longer open. Checked items have repository/GitHub evidence, not submission approval. A = Data & Forecast; B = Optimizer & Simulator; C = App, Voice & Pitch Lead. No other teammate work is verified here.

Official sources: organizer [README](https://github.com/nagusubra/industry-hackathon-lab/blob/main/README.md), [submission guide](https://github.com/nagusubra/industry-hackathon-lab/blob/main/SUBMISSIONS.md), [issue form](https://github.com/nagusubra/industry-hackathon-lab/blob/main/.github/ISSUE_TEMPLATE/submission.yml), [rules](https://github.com/nagusubra/industry-hackathon-lab/blob/main/RULES.md), and [rubric](https://github.com/nagusubra/industry-hackathon-lab/blob/main/JUDGING_RUBRIC.md), inspected at organizer commit `fe3d53c`.

**Deadline: Sunday, October 4, 2026, 12:00 PM MDT (America/Edmonton).** Submit one **Hackathon Submission** issue before close. The form/guide make demo links and additional info optional despite the organizer README's required-package list; include both. Setup verification, results, and backups are team preparation checks beyond the form fields.

## READY

- [x] **Team name:** Admest FC — recorded in [README](../README.md).
- [x] **Member names:** Thamer Elsadek, Salif Sylla, Adam Bensidi — recorded in README; handles remain pending below.
- [x] **Project stream:** Software and Computational Math; **path:** Option A — own problem, public data.
- [x] **Project title:** StormStage — app title; README uses `Stormstage`.
- [x] **Tagline, one line:** “Adaptive tow-truck staging for Calgary winter incidents.” — app text describing the goal.
- [x] **Public repository:** [Drakooz/Stormstage](https://github.com/Drakooz/Stormstage) — matches `origin`; GitHub reports `isPrivate: false`.
- [x] **Architecture specification / Mermaid data-flow exists:** [architecture-spec.md](architecture-spec.md) documents the intended flow/statuses. The final judge-facing architecture visual still needs C verification/polish before presentation; a finished presentation asset is not established.
- [x] **Pitch and walkthrough:** [pitch.md](pitch.md) and [demo-runbook.md](demo-runbook.md) exist and distinguish the mock shell from an integrated replay.

- [x] **Open Calgary incident artifacts on main:** `data/raw/calgary_traffic_incidents_full.csv`, the 2025 cleaning script `src/load.py`, and its output `data/processed/incidents_clean.csv` are tracked on merged main. This establishes artifact presence, not validated provenance, reproducibility, or app integration.

## WAITING ON A

- [ ] **Option A / datasets:** supply Open Calgary reported-incident and ECCC citations, coverage, station ID, download steps, usage terms, and cleaning/time-zone/zone rules. Validate the cleaning output and document reproducibility and limitations. `data/README.md` remains absent on inspected main; root zones alone are insufficient. The merged incident artifacts do not establish completed weather/forecast work.
- [ ] **Incident integration:** connect the cleaned incident output to the real pipeline and Streamlit app; the current app still uses fixtures.
- [ ] Deliver real `forecast(day, hour, weather)` → `zone_id, expected_incidents`; fix the stub's zone path. Current demand is fake.
- [ ] With B, validate the demo day/change hours and README's two held-out days. Fixture dates and README counts lack evidence.

## WAITING ON B

- [ ] Deliver placement/re-plan, response logs, hourly positions, and move reasons; backend modules are absent on main.
- [ ] Prove a coded **plan → score → change-plan → rescore** cycle via hourly re-plan; fixture changes do not qualify.
- [ ] **Measured results table:** Fixed staging vs StormStage for `avg_response_min`, `p90_response_min`, `pct_within_15`, plus relocations if available. Attach day/run IDs, logs, and assumptions; results are pending.
- [ ] Use the **same incidents** and fleet/dispatch/travel/service assumptions. **Fixed staging** is primary; Historical hotspots is optional. Verify Option A's baseline-beating requirement; report zero/negative differences honestly.

## WAITING ON C

- [ ] **All members + GitHub handles:** confirm mappings, then format one per line; contributor usernames do not establish identity.

  | Member from README | Confirmed GitHub handle |
  | --- | --- |
  | Thamer Elsadek | Pending confirmation |
  | Salif Sylla | Pending confirmation |
  | Adam Bensidi | Pending confirmation |

- [ ] **About — inspiration:** winter fleet-staging problem and dispatcher user; avoid unsupported counts.
- [ ] **About — what we learned:** collect actual team learnings.
- [ ] **About — how we built it:** distinguish shipped code from planned pipeline.
- [ ] **About — challenges:** data paths, integration, demo limitations, and teammate-confirmed challenges. Final About copy is pending.
- [ ] **Final judge-facing architecture visual:** verify/polish the specification's Mermaid data-flow and component-status labels before presentation; the final visual is not complete.
- [ ] Integrate A/B outputs in a later task; today's shell has mock data/static metrics and inert Play/Pause.
- [ ] **2–5 screenshots:** PNG/JPG/GIF, ≤10 MB each, captioned with run evidence. None tracked; label shell captures `MOCK / DEMO`.
- [ ] **Demo video or live-site link:** judge-accessible URL, video preferably ≤5 minutes. None supplied.
- [ ] **Setup verified from a clean clone:** fresh directory/environment, Python 3.10+, `pip install -r requirements.txt`, `streamlit run app.py`. Record commit/Python/commands/outcome; existing `.venv` is insufficient. Verify the real pipeline once integrated.
- [ ] **Live demo verification:** rehearse real day, demand change, move/reason, and computed results via runbook; shell rehearsal is insufficient.
- [ ] **Backup demo recording:** capture the validated run with day/run IDs. None tracked.
- [ ] **Local backup assets:** screenshots, recording, diagram, verified logs/results, data, working environment; test offline/table map fallbacks. No package exists.

## FINAL TEAM CHECK

- [ ] Confirm names/handles, registration, original work, one submission, and rules/Code of Conduct agreement. Registration is unverified.
- [ ] Confirm Option A stream fit, cited public data, named intended user (**roadside-assistance dispatcher / Calgary tow operator**), baseline result, and coded revision. Industry feedback is encouraged, not mandatory; no actual user engagement, customer, partner, or quote is verified.
- [ ] Review all form fields, ≤3-line/~280-character tagline, setup, architecture, measured table, and judge access; preserve mock labels.
- [ ] Rehearse **5-minute pitch + 3-minute Q&A**, test backups; distinguish reported incidents from all collisions and mock metrics from results.
- [ ] Assign owners for [README/demo discrepancies](architecture-spec.md); unchanged by this task.
- [ ] **Submission issue filed before deadline:** designate author; use [Hackathon Submission](https://github.com/nagusubra/industry-hackathon-lab/issues/new?template=submission.yml). Record URL/timestamp and resolve validator `needs-fix` feedback before lock. Only the author edits the body. Filing remains pending, outside this task.
