# Actual StormStage demo captures

Captured October 4, 2026 (user client date, America/Edmonton) from the running local Streamlit app at UI commit **839c6a96f9390fbee4cee9f334c0baa0ccdfc8a7**, using an isolated headless Microsoft Edge session through Playwright. Evidence base: `03d52e6`. Forecast source: **`a`**. Selected replay: **Feb 4, 2025, 01:00 Calgary local time**, **Presentation Mode**, **StormStage + on-call**.

These are real app captures, with no compositing or fabricated map data. Road tiles are CARTO/OpenStreetMap context; truck coordinates, incidents, decisions, and results come from the tracked replay/results files. Multiple units at the same coordinate share a marker and ID label.

| File | Content |
| --- | --- |
| [01_stormstage_overview.png](01_stormstage_overview.png) | 1920×1080 presentation viewport: current cards, timeline, map, decision panel, selected-day results |
| [02_activation_evidence.png](02_activation_evidence.png) | Recorded 2.4× signal, six-to-ten fleet transition, four-unit activation, threshold and explanation |
| [03_demo_day_results.png](03_demo_day_results.png) | Feb 4 full-day response and capacity: 20.1 → 9.8 minutes; 144 → 228 truck-hours |
| [04_aggregate_results.png](04_aggregate_results.png) | Separate 12-day evidence: response, within-15 share, capacity, policy table and wins |
| [05_strategy_revision.png](05_strategy_revision.png) | Tested PLAN → SCORE → REVISE → RESCORE policy-development story |

All files are below 1 MB. [provenance.json](provenance.json) records dimensions, byte sizes, SHA-256 hashes, viewport, and source commit. Other required hour/day/mode and responsive checks were captured in ignored `.validation/screenshots/`; their results are recorded in [final handoff](../docs/final-handoff.md).

Result bands show completed simulated replay outcomes, independent of the hour slider. They are not field-deployment results. Feb 4 is a single demo day. The aggregate summarizes means of daily metrics across 12 designated storm test days using a causal forecast. Truck-hours measure capacity use, not monetary savings.

For manual recapture: launch the app, choose Presentation Mode / Feb 04, 2025 / Replay hour 01:00, use a 1920×1080 browser viewport, wait for the map to load, capture the top viewport, then capture each named evidence section while scrolling. Keep the response/capacity trade-off and simulation labels visible; update provenance after any UI change.
