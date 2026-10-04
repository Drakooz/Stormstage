"""Reproducible Part A preparation. Run python -m src.prepare_data."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / 'data' / 'processed'


def clean_weather(raw_dir):
    files = sorted(Path(raw_dir).glob('calgary_weather_2025_*_utc.csv'))
    expected = {f'calgary_weather_2025_{m:02d}_utc.csv' for m in range(1, 13)}
    if {f.name for f in files} != expected:
        raise ValueError('Expected exactly the twelve 2025 UTC monthly weather files')
    raw = pd.concat([pd.read_csv(f, encoding='utf-8-sig') for f in files], ignore_index=True)
    if raw['Climate ID'].nunique() != 1 or str(raw['Climate ID'].iloc[0]) != '3031092':
        raise ValueError('Expected Calgary International A, climate ID 3031092')
    timestamps = pd.to_datetime(raw['Date/Time (UTC)'], utc=True, errors='raise')
    if timestamps.duplicated().any() or not timestamps.equals(timestamps.dt.floor('h')):
        raise ValueError('Duplicate or non-hourly UTC weather timestamps')
    temp_column = next(c for c in raw if c.startswith('Temp ('))
    weather = pd.DataFrame({'timestamp': timestamps,
                            'temp_c': pd.to_numeric(raw[temp_column], errors='coerce'),
                            'precip_mm': pd.to_numeric(raw['Precip. Amount (mm)'], errors='coerce'),
                            'wind_kmh': pd.to_numeric(raw['Wind Spd (km/h)'], errors='coerce'),
                            'visibility_km': pd.to_numeric(raw['Visibility (km)'], errors='coerce'),
                            'weather_description': raw['Weather'].fillna(''),
                            'weather_description_missing': raw['Weather'].isna(),
                            'climate_id': raw['Climate ID']}).sort_values('timestamp').reset_index(drop=True)
    expected_hours = pd.date_range('2025-01-01', '2026-01-01', freq='h', inclusive='left', tz='UTC')
    if not pd.DatetimeIndex(weather.timestamp).equals(expected_hours):
        raise ValueError('Weather must cover every UTC hour of 2025')
    weather['snowing'] = weather.weather_description.str.contains('snow|ice pellets', case=False, regex=True)
    # Previous six observed hours, excluding the current hour; no future observations.
    weather['snow_last_6h'] = weather.snowing.shift(1, fill_value=False).rolling(6, min_periods=1).max().astype(bool)
    weather['snow_history_hours'] = np.minimum(np.arange(len(weather)), 6)
    weather['below_zero'] = weather.temp_c.lt(0).astype('boolean').mask(weather.temp_c.isna())
    return weather


def build_zones(incidents):
    """Same ~2 km grid constants as B; existing grids are preserved by prepare()."""
    rows = np.floor((incidents.Latitude - 50.84) / .018).astype(int)
    cols = np.floor((incidents.Longitude + 114.32) / .028).astype(int)
    cells = pd.DataFrame({'row': rows, 'col': cols}).value_counts().rename('n').reset_index()
    cells = cells[cells.n >= 5].sort_values(['row', 'col'])
    return pd.DataFrame({'zone_id': [f'G{r:02d}_{c:02d}' for r, c in zip(cells.row, cells.col)],
                         'lat': 50.84 + (cells.row + .5) * .018,
                         'lon': -114.32 + (cells.col + .5) * .028}).reset_index(drop=True)


def assign_zones(incidents, zones):
    if zones.empty or zones.zone_id.isna().any() or zones.zone_id.duplicated().any():
        raise ValueError('Zone IDs must be unique and nonempty')
    if not np.isfinite(zones[['lat', 'lon']].to_numpy(dtype=float)).all():
        raise ValueError('Zone coordinates must be finite')
    lat = np.radians(incidents.Latitude.to_numpy()[:, None])
    lon = np.radians(incidents.Longitude.to_numpy()[:, None])
    zlat = np.radians(zones.lat.to_numpy()[None, :])
    zlon = np.radians(zones.lon.to_numpy()[None, :])
    distance = np.sin((lat-zlat)/2)**2 + np.cos(lat)*np.cos(zlat)*np.sin((lon-zlon)/2)**2
    result = incidents.copy()
    result['zone_id'] = zones.zone_id.to_numpy()[distance.argmin(axis=1)]
    return result


def prepare():
    weather = clean_weather(ROOT / 'data' / 'raw' / 'weather')
    incidents = pd.read_csv(PROCESSED / 'incidents_clean.csv')
    incidents['START_DT_UTC'] = pd.to_datetime(incidents.START_DT_UTC, utc=True, errors='raise')
    if incidents.id.duplicated().any():
        raise ValueError('Duplicate incident IDs')
    for col in ['Latitude', 'Longitude']:
        incidents[col] = pd.to_numeric(incidents[col], errors='raise')
    if not np.isfinite(incidents[['Latitude', 'Longitude']].to_numpy()).all():
        raise ValueError('Invalid incident coordinates')
    zones_path = PROCESSED / 'zones_grid.csv'
    zones = pd.read_csv(zones_path) if zones_path.exists() else build_zones(incidents)
    incidents = assign_zones(incidents, zones)
    incidents['timestamp'] = incidents.START_DT_UTC.dt.floor('h')
    joined = incidents.merge(weather, on='timestamp', how='left', validate='many_to_one', indicator=True)
    if not joined['_merge'].eq('both').all():
        raise ValueError('Some incident hours have no weather coverage')
    joined = joined.drop(columns='_merge')
    counts = joined.groupby(['timestamp', 'zone_id']).size()
    grid = pd.MultiIndex.from_product([weather.timestamp, zones.zone_id], names=['timestamp', 'zone_id'])
    hourly = counts.reindex(grid, fill_value=0).rename('incident_count').reset_index()
    days = weather.assign(day=weather.timestamp.dt.strftime('%Y-%m-%d')).groupby('day').agg(
        snow_hours=('snowing', 'sum'), min_temp_c=('temp_c', 'min'),
        missing_temperature_hours=('temp_c', lambda x: int(x.isna().sum())))
    days['storm_day'] = days.snow_hours.ge(1)
    days['incident_count'] = joined.groupby(joined.timestamp.dt.strftime('%Y-%m-%d')).size().reindex(days.index, fill_value=0)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    weather.to_csv(PROCESSED / 'weather_hourly.csv', index=False)
    joined.to_csv(PROCESSED / 'incidents_weather.csv', index=False)
    hourly.to_csv(PROCESSED / 'zone_hourly.csv', index=False)
    days.reset_index().to_csv(PROCESSED / 'storm_days.csv', index=False)
    days.sort_values('incident_count', ascending=False).head(10).reset_index().to_csv(
        PROCESSED / 'top_incident_days.csv', index=False)
    if not zones_path.exists():
        zones.to_csv(zones_path, index=False)
    report = {'weather_hours': len(weather), 'missing_temperatures': int(weather.temp_c.isna().sum()),
              'incidents': len(joined), 'zones': len(zones), 'zone_hours': len(hourly),
              'storm_days': int(days.storm_day.sum()),
              'zero_incident_utc_dates': int(days.incident_count.eq(0).sum()),
              'median_incidents_per_utc_day': float(days.incident_count.median()), 'timestamp_timezone': 'UTC',
              'storm_rule': 'at least one reported snow/ice-pellet hour per UTC date'}
    (PROCESSED / 'part_a_validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    prepare()
