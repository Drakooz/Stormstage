# StormStage — judge Q&A

**Why is the comparison fair when on-call uses more trucks?** We replay the same reported incidents with shared dispatch, travel, and scene assumptions, and expose capacity alongside response. Fixed yards is the primary six-truck baseline. The ten-trucks-all-day comparator shows what additional capacity achieves.

**Why not keep ten trucks active all day?** That policy is faster: 7.5 versus 10.6 simulated average minutes across the 12 storm days. It uses 240 truck-hours/day versus 176.5 for on-call. We show a response-versus-capacity trade-off, without monetary savings claims.

**Did smarter re-staging alone work?** No aggregate average improvement: same-six averaged 14.2 minutes versus 14.1 for Fixed yards and 13.7 for Best fixed plan. That evidence caused the team to revise to forecast-triggered on-call capacity and rescore.

**Are these real response times?** They are simulated replay outcomes. The shared model uses nearest-arrival dispatch, straight-line distance × 1.3 at 40 km/h, and 30 minutes on scene. Field response times have not been calibrated or validated.

**Are the incidents all crashes or tow calls?** No. Open Calgary's reported traffic incidents include other events, including traffic-signal issues. This is an imperfect proxy for roadside demand.

**Did weather alone cause the Feb 4 activation?** No such claim is established. The signal is the larger of weather lift and recent incident activity. The log records 2.4× normal at 01:00 and four on-call activations, but does not identify which component dominated. Feb 4 records no relocations.

**Is every test day fully held out from forecast training?** The forecast is causal: fitting stops before the requested UTC decision date and future observed weather is not read into the horizon. `forecast.py` explicitly reserves Feb 4, Feb 14, and Nov 24 plus the following UTC dates. The broader all-evaluation-days exclusion assertion in `results/RESULTS.md` is not established by that implementation. We use “12 designated storm test days using a causal forecast.”

**Does moving the slider run AI or optimize live?** It reads precomputed positions, decisions, and full-day scores. The backend refreshes demand hourly during replay generation. Replay scores inform the tested policy-development revision, not an online optimizer feedback input.

**What does 51.2% refer to?** The Feb 4 single-day average response reduction from 20.1 to 9.8 minutes, computed from saved metrics. Capacity rose from 144 to 228 truck-hours. It is separate from the 12-day result of 14.1 to 10.6 minutes.

**Do you have a customer or savings estimate?** No customer, partner, field deployment, pricing, or savings validation exists. The intended user is a roadside/tow dispatcher. Dispatcher review and a possible operational pilot are proposed next steps.

Sources: [aggregate results](../results/test_summary.csv), [daily results](../results/test_by_day.csv), [Feb 4 replay](../data/processed/replay/2025-02-04/metrics.json), [architecture and limitations](architecture-spec.md).
