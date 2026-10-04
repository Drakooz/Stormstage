# StormStage submission checklist

Reviewed October 3, 2026 against current main (`1081dfa`), matching this checkout. Incident/weather artifacts, B's backend/results, and precomputed app replay integration are on main. Current B results/replays use the **stand-in forecast**; A's real weather-driven forecast is **not yet integrated**. Checked items indicate repository evidence, not submission approval or final performance validation. A = Data & Forecast; B = Optimizer & Simulator; C = App, Voice & Pitch Lead.

Official sources: organizer [README](https://github.com/nagusubra/industry-hackathon-lab/blob/main/README.md), [submission guide](https://github.com/nagusubra/industry-hackathon-lab/blob/main/SUBMISSIONS.md), [issue form](https://github.com/nagusubra/industry-hackathon-lab/blob/main/.github/ISSUE_TEMPLATE/submission.yml), [rules](https://github.com/nagusubra/industry-hackathon-lab/blob/main/RULES.md), and [rubric](https://github.com/nagusubra/industry-hackathon-lab/blob/main/JUDGING_RUBRIC.md), inspected at organizer commit `fe3d53c`.

**Deadline: Sunday, October 4, 2026, 12:00 PM MDT (America/Edmonton).** Submit one **Hackathon Submission** issue before close. The form/guide make demo links and additional info optional despite the organizer README's required-package list; include both. Setup verification, results, and backups are team preparation checks beyond the form fields.

## READY

- [x] **Team name:** Admest FC — recorded in [README](../README.md).
- [x] **Member names:** Thamer Elsadek, Salif Sylla, Adam Bensidi — recorded in README; handles remain pending below.
- [x] **Project stream:** Software and Computational Math; **path:** Option A — own problem using public data.
- [x] **Project title:** StormStage.
- [x] **Tagline, one line:** “Adaptive tow-truck staging for Calgary winter incidents.” — app text describing the goal.
- [x] **Public repository:** [Drakooz/Stormstage](https://github.com/Drakooz/Stormstage) — matches `origin`; GitHub reports `isPrivate: false`.
- [x] **Architecture specification / Mermaid data-flow exists:** [architecture-spec.md](architecture-spec.md) documents the intended flow/statuses. The final judge-facing architecture visual still needs C verification/polish before presentation; a finished presentation asset is not established.
- [x] **Pitch and walkthrough:** [pitch.md](pitch.md) and [demo-runbook.md](demo-runbook.md) distinguish stand-in replay evidence from pending final weather-driven results.
- [x] **Final design decision:** 6 base trucks + up to 4 additional on-call trucks, activated when forecasted demand indicates a surge; stage/re-stage active trucks near expected demand. Same-six-truck testing showed little advantage and led to this revision.
- [x] **Comparator names:** Fixed yards (naive) is the primary naive baseline; Best fixed plan is the stronger secondary comparator.
- [x] **B backend and interim evidence:** placement, hourly replanning, response logs, positions, reasons, scoring, and [stand-in results](../results/RESULTS.md) are tracked. The app consumes precomputed exports, not a live optimizer.
- [x] **Raw weather artifacts:** monthly 2025 ECCC UTC CSVs are tracked; this does not establish real weather-forecast integration.

- [x] **Open Calgary incident artifacts:** raw/cleaned CSVs and `src/load.py` are tracked. B uses raw incidents via `common.py`; the app displays exported incident responses. Final provenance/reproducibility documentation remains pending.

## WAITING ON A

- [ ] **Option A / datasets:** supply exact Open Calgary/ECCC citations, coverage, station ID, download steps, usage terms, and cleaning/time-zone/zone rules. Validate outputs and document reproducibility/limitations. `data/README.md` remains absent.
- [ ] Deliver processed hourly weather and real `forecast(day, hour, weather)` → `zone_id, expected_incidents`; fix the stub path and align coverage with B's 179-zone grid. Current replays use B's stand-in demand.
- [ ] With B, validate [FINAL DEMO DAY], event hours, and [HELD-OUT VALIDATION STATUS] after real-forecast integration. Current stand-in evaluation covers 12 held-out storm days and 8 normal days; it is not final weather-driven evidence.

## WAITING ON B

- [ ] Integrate A's real weather-driven forecast, rerun evaluation, and regenerate replay exports. Preserve stand-in evidence labels until replaced by verified final output.
- [ ] Verify final **plan → score → revise → rescore** evidence: initial score, hourly capacity/staging revision and reason, revised score. Slider snapshots/full-day cards alone do not establish per-step scores.
- [ ] **Final weather-driven results table [PENDING]:** Fixed yards (naive), Best fixed plan, and StormStage + on-call for response mean, p90, within-15 share, relocations, activations, and truck-hours. Attach evaluated commit/day/run IDs, logs, forecast source, and assumptions.
- [ ] Use the **same incidents**, dispatch, travel, and service assumptions. Disclose 6 trucks for both static comparators versus 6 base + up to 4 on-call for StormStage; report truck-hours. Report zero/negative differences honestly.

## WAITING ON C

- [ ] **All members + GitHub handles:** confirm mappings, then format one per line; contributor usernames do not establish identity.

  | Member from README | Confirmed GitHub handle |
  | --- | --- |
  | Thamer Elsadek | Pending confirmation |
  | Salif Sylla | Pending confirmation |
  | Adam Bensidi | Pending confirmation |

- [ ] **About — inspiration:** winter fleet-staging problem and dispatcher user; avoid unsupported counts.
- [ ] **About — what we learned:** confirm firsthand reflections; include the measured same-six-truck limitation and policy revision without presenting stand-in numbers as final.
- [ ] **About — how we built it:** distinguish shipped code from planned pipeline.
- [ ] **About — challenges:** real forecast, zone coverage, weather/time alignment, demo limitations, and teammate-confirmed challenges. Final team review remains pending.
- [ ] **Final judge-facing architecture visual:** verify/polish the specification's Mermaid data-flow and component-status labels before presentation; the final visual is not complete.
- [ ] Verify regenerated weather-driven exports in the dashboard; Play/Pause remains a placeholder. Keep interim labels on current stand-in displays.
- [ ] **2–5 screenshots:** PNG/JPG/GIF, ≤10 MB each, captioned with run evidence and forecast source. None tracked; current captures must say `PRECOMPUTED / INTERIM — stand-in forecast`.
- [ ] **Demo video or live-site link:** judge-accessible URL, video preferably ≤5 minutes. None supplied.
- [ ] **Setup verified from a clean clone:** fresh directory/environment, Python 3.10+, `pip install -r requirements.txt`, `streamlit run app.py`. Record commit/Python/commands/outcome; existing `.venv` is insufficient. Verify the real pipeline once integrated.
- [ ] **Live demo verification:** rehearse day selection, forecast trigger, on-call activation, staging revision/reason, and scores via runbook; distinguish interim stand-in evidence from final weather-driven evidence.
- [ ] **Backup demo recording:** capture the validated run with day/run IDs. None tracked.
- [ ] **Local backup assets:** screenshots, recording, diagram, verified logs/results, data, working environment; test offline/table map fallbacks. No package exists.

## FINAL TEAM CHECK

- [ ] Confirm names/handles, registration, original work, one submission, and rules/Code of Conduct agreement. Registration is unverified.
- [ ] Confirm Option A stream fit, cited public data, named intended user (**roadside-assistance dispatcher / Calgary tow operator**), baseline result, and coded revision. Industry feedback is encouraged, not mandatory; no actual user engagement, customer, partner, or quote is verified.
- [ ] Review all form fields, ≤3-line/~280-character tagline, setup, architecture, final metric placeholders, and judge access; preserve interim labels.
- [ ] Rehearse **5-minute pitch + 3-minute Q&A**, test backups; distinguish reported incidents from all collisions and stand-in outcomes from final weather-driven results.
- [ ] Resolve the [remaining integration blockers](architecture-spec.md) with A/B/C; this task changes documentation only.
- [ ] **Submission issue filed before deadline:** designate author; use [Hackathon Submission](https://github.com/nagusubra/industry-hackathon-lab/issues/new?template=submission.yml). Record URL/timestamp and resolve validator `needs-fix` feedback before lock. Only the author edits the body. Filing remains pending, outside this task.
