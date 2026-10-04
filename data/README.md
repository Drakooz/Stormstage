# Part A data and forecast

Run `python -m src.prepare_data` from the repository root. All Part A timestamps,
weather joins, date boundaries, hour-of-week features, and forecast inputs are UTC.
Source of truth: StormStage ? Hackathon Build Plan (1).pdf, supplied by the user.
The task's locked UTC contract and zones_grid.csv path supersede the PDF's
earlier paths. The PDF does not specify a snow-day threshold or exact horizon
boundaries; those implementation choices are documented below.

Input: the twelve 2025 UTC ECCC CSVs for CALGARY INTL A (climate ID 3031092),
and the existing `processed/incidents_clean.csv`. ECCC confirms the station
identifiers at https://climate.weather.gc.ca/climate_data/almanac_e.html?StationID=50430&Year=2024&day=18&month=1&timeframe=4 ;
Climate ID 3031092 is distinct from bulk-download StationID 50430. Preparation requires all 8,760
unique hourly observations. It preserves missing temperatures and blank weather
text; blank descriptions mean no *reported* snow, not verified clear conditions.
Snow includes descriptions containing snow or ice pellets. `snow_last_6h` uses
only the preceding six hours, excluding the current hour. The first six records
have partial history, recorded in `snow_history_hours`.

Outputs under `data/processed/`:

- `weather_hourly.csv`: hourly UTC weather and causal snow indicators.
- `incidents_weather.csv`: every cleaned incident joined to its UTC hour and zone.
- `zone_hourly.csv`: every hour for every zone, including zero incident counts.
- `storm_days.csv`: all UTC dates, snow hours, minimum temperature, incident count,
  and a provisional storm label (at least one reported snow/ice-pellet hour).
- `top_incident_days.csv`: top ten UTC dates, counts and weather checks.
- `part_a_validation.json`: coverage and conservation counts.

The existing `zones_grid.csv` is preserved so B/C replay IDs stay stable. If it is
absent, preparation builds B's approximate 2 km grid (origin 50.84, -114.32;
steps .018 latitude, .028 longitude; cells with at least five incidents).
Incidents are assigned to the nearest centre using spherical distance, matching
B's convention. The zone geometry was selected using full-year locations and is
an agreed fixed map, not a held-out spatial validation result.

`forecast(day, hour, weather)` returns exactly `zone_id, expected_incidents` for
`[day hour, day hour + 3 hours)` in UTC, including midnight rollover. The model
fits ridge Poisson regression to citywide hourly counts, with categorical UTC
hour of week, reported snow, below-zero temperature, and preceding-six-hour snow.
It allocates city demand to smoothed historical zone shares. This is a pooled
Poisson model; it does not learn zone-specific weather effects. Ridge strength
is 2; each zone gets a one-incident share prior. Zero-count hours enter training.

Training ends before the requested UTC date: neither that day's observations nor
future incidents/weather enter fitting. Missing temperature uses the historical
training median. The supplied current weather is held constant over the three
forecast hours, rather than reading future observed weather. Fits are cached by
UTC date. Rebuild outputs before importing forecast, or call `clear_cache()`.
Calls without earlier incident history fail explicitly.

`baseline_forecast(day, hour)` sums actual counts in the same three hourly buckets
seven days earlier, with zeros for zones without incidents. An unavailable
prior-week window fails explicitly. No synthetic fallback is used.

Incident records represent reported traffic incidents (including traffic-signal
issues), not all collisions or tow demand. Held-out forecast errors are generated separately; this does not establish
a placement improvement. No evaluation dates were selected based on model performance. The plan's candidate dates are reserved: February 4 (demo), February 14 and
November 24 (holdouts). None enters model training, even for later forecasts.
The following UTC date for each is also excluded to cover B's Calgary local-day
replay intervals conservatively. These exclusions apply to both weather fit and
zone shares. Dates without incidents remain zero-count hours; the feed cannot
distinguish no events from missing reporting, so the 41 empty UTC dates are a
coverage limitation, not established days with no incidents.

Run `python -m src.evaluate_forecast` for the model/baseline error comparison on
24 overlapping three-hour windows per reserved UTC day. Weather at the start of
each window is observed and then persisted. Outcomes are used only for scoring.
Results are forecast errors, not simulated response-time gains. February 4 has
77 incidents in UTC in this cleaned full-feed extraction, rather than the PDF's
85; the plan uses a different sample and does not specify its time basis. Use generated counts in the pitch.

The complete zero-filled zone-hour CSV is approximately 56 MB and can be
regenerated; it stores counts without repeating weather on every zone row.
For checks, install pytest (`python -m pip install pytest`) and run
`python -m pytest -q`. Production preparation/forecast needs only the existing
pandas and numpy dependencies.
