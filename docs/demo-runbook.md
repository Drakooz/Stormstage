# StormStage — demo runbook

The dashboard reads weather-driven **precomputed simulation** exports (forecast source `a`). Every shown hour is **Calgary local time (America/Edmonton)**. Fixed yards is the primary baseline; Best fixed plan is secondary. Results are simulated replay outcomes, not field-deployment results.

## Start and rehearse

Run `python -m streamlit run app.py` in an activated environment. On this Windows checkout, use `.\.venv\Scripts\python.exe -m streamlit run app.py`. Presentation Mode defaults to Feb 4, 2025 at 01:00 with StormStage + on-call. The manual slider is the replay control.

1. Select **Presentation Mode** and **Feb 04, 2025** in the header.
2. Move **Replay hour** to **00:00**. Show **6 active trucks**, **Base fleet**, and **No activation yet**. The timeline previews recorded later events; those are not current decisions.
3. Move to **01:00**. Show **6 → 10 active trucks**, **+4 on-call activated**, and **2.4× normal** recorded at 01:00. The policy threshold is 2.0×.
4. Show the **Calgary operations map**. Truck icons and T-number labels use exported coordinates. Available is icy blue, responding red, on scene amber, returning teal; relocating is purple when present. Shared positions have grouped unit labels and tooltips. Muted zone dots do not encode forecast intensity.
5. Read **Why StormStage changed the plan**. Weather lift and recent incidents both contribute to the surge signal; the log does not isolate the dominant component. Feb 4 records no relocations. Do not confuse dispatch or return travel with re-staging.
6. Scroll to **Did the decision help?** Show **20.1 → 9.8 min**, **51.2% lower** simulated average response, and **144 → 228 truck-hours**. These are completed Feb 4 full-day outcomes, independent of the slider.
7. Show **Across 12 storm test days** on the same page: **14.1 → 10.6 min**, **68.2% → 79.3%**, and **176.5 vs 240 truck-hours/day**. On-call beat Fixed yards on **10 of 12** and Best fixed plan on **8 of 12**. Ten trucks all day was faster at 7.5 minutes.
8. Show **The evidence changed our strategy**: PLAN (same six) → SCORE (14.2 min, no aggregate improvement) → REVISE (on-call) → RESCORE (10.6 min). This is tested policy development, not live score feedback to the optimizer.
9. Leave **Technical details & evidence** collapsed unless asked. Decision log, Truck table, Incident table, Assumptions & limitations, and Additional policies contain the supporting detail.

The pitch fits approximately five minutes using [pitch.md](pitch.md). Raw tables are unnecessary during that flow.

## Optional time-state checks

- **04:00:** 10 active trucks, 6 base + 4 on-call, “On-call active,” and the historical 01:00 activation signal. The six-to-ten transition should not repeat.
- **22:00:** the recorded four-unit stand-down changes the fleet to six. The earlier activation signal remains explicitly historical.
- **23:00:** six active trucks; “On-call stood down,” last change at 22:00.
- Change the day to **Feb 14, 2025**; use that day's actual logged events and metrics.

## Explorer and Q&A

Choose **Explorer Mode**. The Policy selector includes Fixed yards, Best fixed plan, Historical hotspots, same-six StormStage, StormStage + on-call, and Fixed 10 trucks all day. Every exported date remains available. Open detailed tables/logs, optional side-by-side primary-policy maps, or the Calgary zone grid. Return to Presentation Mode for the pitch.

Truck snapshots are at the selected hour's start; incidents and decision-log entries extend through that hour's end. Incident tables contain completed response outcomes, including later arrivals. Full-day scores are not per-hour scores.

See [judge Q&A](judge-qa.md) for fairness, causality, capacity, and validation questions. Aggregate metrics are means of daily metrics. Evaluation uses a causal rolling-origin forecast fitted only on information available before each requested UTC date. Earlier evaluation dates may become historical training data for later replay dates, so this is not a single frozen holdout set. Policy settings were selected on separate tuning days.

## Emergency fallback and assets

Actual app captures are in [final_demo_assets](../final_demo_assets/README.md). If Wi-Fi or map tiles fail, use the overview and activation capture, then the selected-day, aggregate, and strategy images. Local results/logs/tables work without map backgrounds. The basemap is geographic context; travel simulation uses straight-line distance × 1.3 at 40 km/h, with 30 minutes on scene.

If the app fails entirely, show the captured results and [architecture visual](architecture-visual.md), explicitly describing them as saved simulation output. Do not use mock values or claim live optimization. No customer, partner, field deployment, pricing, or savings validation exists.

Remaining team actions: confirmed handles and registration/attestations, firsthand reflections, source/usage review, optional video/live URL, pitch rehearsal, and filing the organizer issue. See [final handoff](final-handoff.md) and [submission checklist](submission-checklist.md).
