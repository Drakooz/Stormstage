# StormStage Final Handoff

## Release status

**READY — presentation release candidate.** The dashboard, tests, reproducible startup, documents, and actual screenshot package are complete. This does not mean the organizer submission has been filed or that team identity, registration, source usage, or field validation is confirmed. Remaining team actions are listed below.

Reviewed October 4, 2026 using the user's America/Edmonton date context.

## Branch

`ui-presentation-redesign`. Development stayed on this branch.

## Current main

`03d52e620e8398a174074cee44e9a97be797b61b` — fetched from origin before development and again before pushing. No new teammate commits appeared. Main was left unchanged.

## Final feature commits

- `839c6a96f9390fbee4cee9f334c0baa0ccdfc8a7` — Redesign presentation dashboard with time-correct replay evidence.
- `324e73ca07102202fe4f1c1eaf01f971796dc621` — Align demo, architecture, and submission docs with the final dashboard.
- `da7c33870fdd8e60b306d3bc0e27a027daa36a40` — Add verified running-app demo captures and provenance.
- The final handoff/audit commit contains this document. Its identifier is available with `git log -1 --format="%H %s"`; a commit cannot embed its own final SHA in its contents.

## Files changed

- UI: `app.py`, `dashboard.css`, `dashboard_data.py`, `.streamlit/config.toml`.
- Setup/verification: `.gitignore`, `requirements.txt`, `tests/test_dashboard.py`.
- Documents: `README.md`, `docs/pitch.md`, `docs/demo-runbook.md`, `docs/judge-qa.md`, `docs/submission-draft.md`, `docs/submission-checklist.md`, `docs/architecture-spec.md`, `docs/architecture-visual.md`, `docs/architecture-diagram.mmd`, this file.
- Assets: `final_demo_assets/README.md`, `final_demo_assets/provenance.json`, and five PNGs listed below.

No forecast, placement, simulation, evaluation, replay-interface semantics, datasets, replay exports, or result numbers changed. A final path-limited diff against the evidence base confirmed that boundary.

## What was completed

- Dark industrial dashboard using approximately 94% of desktop width, with a full-width header, four status cards, manual timeline, one primary operations map, and decision explanation.
- Presentation Mode defaults to Feb 4, 2025, 01:00, StormStage + on-call. No placeholder playback control remains.
- Current fleet state is separated from exact-hour transitions and historical trigger evidence. Stand-down restores six trucks.
- Actual truck coordinates, readable grouped unit IDs, status colors, incident points, geographic map background, tooltips, and legend. No fabricated heatmap, truck positions, or decorative operational photograph.
- Full-day selected-day response/capacity band, separate 12-day aggregate KPIs/table, and visible PLAN → SCORE → REVISE → RESCORE strip.
- Technical logs, coordinate tables, assumptions, and additional policies collapsed by default. Explorer retains all three exported dates and all six policies, detailed data, optional side-by-side maps, and zone inspection.
- Read-only calculations and styles separated from rendering. Aggregate evidence is cached; restart the app after replacing result files.
- Five-minute pitch, exact demo procedure, judge Q&A, submission draft/checklist, and synchronized architecture diagram.
- Five real running-app screenshots with hashes and source-commit provenance.
- Fresh clone/environment installation, data preparation, all tests, imports, Streamlit/browser startup, responsive checks, and external-request-blocked fallback verification.

## Final evidence

**Feb 4 demo day only — full-day simulated outcomes:**

| Policy | Average response | P90 | Within 15 min | Truck-hours |
| --- | --- | --- | --- | --- |
| Fixed yards | 20.1 min | 37.7 min | 44.7% | 144 |
| StormStage + on-call | 9.8 min | 17.9 min | 83.5% | 228 |

The computed average-response reduction is **51.2%**. Four on-call units activate at **01:00**, with a recorded **2.4× normal** signal and **2.0×** threshold. All four stand down at **22:00**. This replay records **no relocations**. Faster simulated response required additional on-call capacity.

**Across 12 designated storm test days using a causal forecast — means of daily metrics:**

| Policy | Average response | Mean daily p90 | Mean within-15 share | Truck-hours/day |
| --- | --- | --- | --- | --- |
| Fixed yards — primary | 14.1 min | 27.1 min | 68.2% | 144 |
| Best fixed plan — secondary | 13.7 min | 26.1 min | 70.9% | 144 |
| StormStage same six | 14.2 min | 27.1 min | 68.8% | 144 |
| StormStage + on-call | 10.6 min | 18.9 min | 79.3% | 176.5 |
| Ten trucks active all day | 7.5 min | 13.1 min | 93.3% | 240 |

On-call beat Fixed yards on **10 of 12** storm days and Best fixed plan on **8 of 12**. All ten trucks all day was faster; on-call used less capacity. Daily p90 means are not pooled incident percentiles.

**Policy revision:** re-stage the same six → score **14.2 min**, no aggregate average improvement → revise to forecast-triggered on-call → rescore **10.6 min**. This is policy development, not online replay-score feedback to the hourly optimizer.

Sources: [aggregate CSV](../results/test_summary.csv), [daily CSV](../results/test_by_day.csv), [Feb 4 replay metrics](../data/processed/replay/2025-02-04/metrics.json), and [recorded actions](../data/processed/replay/2025-02-04/stormstage_actions.csv).

## Validation performed

Project environment: **Python 3.14.3**, Streamlit **1.65.0**, pandas **3.0.6**, NumPy **2.5.3**, Pydeck **0.9.3**, pytest **9.1.1**.

- Initial suite: **18 passed**. The sandbox blocked the default pytest temporary/cache path; rerunning with `-p no:cacheprovider --basetemp=.validation/pytest-baseline` passed. No backend failure was found.
- Final suite: **25 passed**. Seven new regressions cover five replay-hour boundaries, aggregate capacity/win comparisons, and end-to-end mode/day/policy access. Original 18 tests remain intact.
- `git diff --check`: **passed**, including the complete committed diff against the evidence base.
- `import app, dashboard_data, replay_data`: **passed**. Bare imports can print Streamlit's benign “No runtime found” cache notice.
- Streamlit local launch at `127.0.0.1:8501`: **passed**. Real browser interaction and visual review used an isolated headless Microsoft Edge session via Playwright, without personal browser profiles.
- Feb 4 **00:00, 01:00, 04:00, 22:00, 23:00**, Feb 14 **01:00**, and Explorer: **passed**. Cards, recorded events, current/historical wording, maps, mode switching, and day selection were checked.
- **1920×1080**, **1440×1080**, and **1100×1080** layouts: **passed**; no horizontal overflow or browser page errors. Readable cards/tables and map labels were visually reviewed. Vertical scrolling remains available for lower evidence sections.
- AppTest exercised all **three exported dates × six policies**, plus hour/mode reruns: **passed**.
- External HTTPS requests blocked in a fresh browser page: local replay cards, selected-day results, aggregate results, and expanded truck table **passed**. Map backgrounds require internet.
- Source-boundary audit: backend, `replay_data.py`, `data/`, and `results/` diffs against `03d52e6` were **empty**.

Local verification captures/scripts are retained in ignored `.validation/`. Only the five final PNGs and their provenance are release assets.

## Clean-clone result

**PASS.** A local Git clone using `--no-hardlinks` and a new environment was created in `.validation/clean-clone`, at UI commit **839c6a9**. It used no packages from the original environment. Later feature commits only add documents/assets/handoff.

From the project root:

```powershell
git clone --no-hardlinks --branch ui-presentation-redesign . .validation/clean-clone
py -3.14 -m venv .validation/clean-clone/.venv
```

From that clone, using its fresh environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pytest
.\.venv\Scripts\python.exe -m src.prepare_data
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -c "import app, dashboard_data, replay_data"
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8502
git status --short
git diff --check
```

Installation succeeded; preparation reported **8,760 weather hours, 7,015 incidents, 179 zones, 1,568,040 zone-hours, 75 provisionally labeled storm dates, and 41 empty incident UTC dates**. The 75 weather-labeled dates are separate from the 12 designated evaluation dates. The ignored, regenerable `data/processed/zone_hourly.csv` was created (about 56 MB); tracked outputs remained unchanged. Tests: **25 passed**. Imports and browser/default-replay launch: **passed**. Clone Git status and diff check were clean.

Tracked replay exports suffice for the dashboard. Run preparation before tests/backend forecast work when the ignored zone-hour intermediate is absent. Do not regenerate replay exports or evaluation results merely to run the UI. Older Python/dependency combinations were not tested in this release; Python 3.14.3 is the verified setup.

## Demo procedure

1. Launch the app; choose Presentation Mode and Feb 04, 2025.
2. Set Replay hour to **00:00**: show six base trucks and no activation yet.
3. Set it to **01:00**: show 2.4× normal, four activations, six-to-ten fleet change, map, and decision panel.
4. Scroll to **Did the decision help?**: 20.1 → 9.8 minutes alongside 144 → 228 truck-hours.
5. Show **Across 12 storm test days**: 14.1 → 10.6, 68.2% → 79.3%, and 176.5 versus 240 truck-hours/day.
6. Show **The evidence changed our strategy**: PLAN → SCORE → REVISE → RESCORE.
7. Keep technical details collapsed unless asked. Use Explorer for all policies and deeper inspection.

At 04:00 the transition does not repeat; at 22:00 the fleet stands down; at 23:00 six trucks remain active. Truck positions use the hour's start; incidents/logs extend through the hour's end. Full-day scores do not change with the slider.

## Final pitch flow

Problem and intended dispatcher user → original same-six hypothesis and negative result → forecast-triggered on-call revision → Feb 4 activation demo → selected-day response/capacity trade-off → separate aggregate evidence → strategy rescore → simulation limits → proposed dispatcher review/pilot. [Timed script](pitch.md) and [judge Q&A](judge-qa.md) are ready; human rehearsal remains a team action.

## Known limitations

- Results are simulated replay outcomes, not field-deployment results. Dispatch/travel/scene assumptions are shared but not calibrated field operations.
- Reported traffic incidents are not all collisions or all tow calls. Blank weather descriptions and empty incident dates have reporting/coverage limitations.
- Truck-hours are capacity use, not proven monetary cost or savings. No customer, partner, deployment, pricing, or savings validation exists.
- A's forecast is causal, fits before the requested UTC decision date, and persists current weather over the horizon. It explicitly reserves Feb 4, Feb 14, and Nov 24 plus following UTC dates. The broader all-evaluation-days exclusion assertion in `results/RESULTS.md` is not established by `forecast.py`. Owner review remains; teammate evidence was preserved.
- Historical zone shares and full-year grid geometry do not establish held-out spatial validation or zone-specific weather effects.
- Basemap tiles need internet. No autoplay, voice control, or forecast-intensity heatmap is claimed. Exported replays cover three dates; the evaluation spans 12 designated storm and eight normal dates.
- Source/download/usage-term checks and separate evaluation-run provenance still need owners. Existing source-a exports and the evidence-base commit are documented.

## Submission items still requiring Adam/team

1. Confirm Thamer, Salif, and Adam's GitHub handles; placeholders remain in the draft.
2. Confirm registration, identities, original-work/rules/Code of Conduct attestations, and submission author. No agreement was accepted on the team's behalf.
3. Confirm firsthand learning/challenge reflections; retain or fill the draft's personal-reflection placeholder with team-confirmed text.
4. Review data source usage and the documented forecast-exclusion discrepancy with A/B owners.
5. Add a judge-accessible demo/video/live URL if available. No external deployment or invented link was created.
6. Rehearse the five-minute pitch and Q&A; confirm judge access and the current organizer deadline/form.
7. Copy [submission-draft.md](submission-draft.md) into the organizer form, attach the five actual PNGs, fill the genuine unknowns, and **file the organizer submission personally**. Relative repository image links may need uploaded attachments or absolute raw links when copied into another repository's issue.

The previously recorded deadline is October 4, 2026 at noon MDT; organizer state was not re-verified during this release task. The organizer submission issue has **not** been filed.

## Git state

Feature branch pushed using existing authentication. Reviewable PR: [#17](https://github.com/Drakooz/Stormstage/pull/17). **Not merged**; main remains the SHA above. The optional merge was left for team/evidence-owner review because the preserved backend report contains the documented training-exclusion discrepancy. The UI uses the supported causal-forecast wording and has no known technical release blocker.

No force-push, history rewrite, destructive branch change, or new credential configuration occurred. The final audit/handoff commit is pushed on the same feature branch; the working tree is clean after it. Verify current state with `git status --short`, `git log -4 --oneline`, and `gh pr view 17 --repo Drakooz/Stormstage`.

## Startup

Recommended portable command in an activated environment:

```text
python -m streamlit run app.py
```

Exact command for this Windows checkout (the system `python` alias did not resolve, but the project environment works):

```powershell
cd C:\Users\adamb\Stormstage
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Emergency fallback

If map tiles/internet fail, keep presenting local cards and results, or use the five actual captures below. Local data, metrics, tables, and decision logs need no external API. If the app cannot launch, show the screenshots and [architecture visual](architecture-visual.md), explicitly labeling the material as saved simulation output. Do not substitute mock data.

## Screenshots/assets

- [Overview](../final_demo_assets/01_stormstage_overview.png)
- [Activation evidence](../final_demo_assets/02_activation_evidence.png)
- [Feb 4 response and capacity](../final_demo_assets/03_demo_day_results.png)
- [12-day aggregate](../final_demo_assets/04_aggregate_results.png)
- [Strategy revision](../final_demo_assets/05_strategy_revision.png)
- [Provenance and hashes](../final_demo_assets/provenance.json)
- [Standalone architecture source](architecture-diagram.mmd) and [renderable Mermaid visual](architecture-visual.md)

## Anything that must NOT be claimed

Field-deployed benefits; all collisions/tow calls; a same-fleet on-call improvement; monetary savings; validated customers/partners/pricing; weather alone causing the activation; full exclusion of every evaluation date from forecast training; Feb 4 results as the 12-day aggregate; live optimization or online replay-score feedback; relocations on Feb 4; completed organizer submission or confirmed team attestations.
