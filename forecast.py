"""Part A: causal Poisson city demand allocated to historical zone shares (UTC)."""
from functools import lru_cache
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
ZONES_PATH = ROOT / 'data' / 'processed' / 'zones_grid.csv'
WEATHER_PATH = ROOT / 'data' / 'processed' / 'weather_hourly.csv'
INCIDENTS_PATH = ROOT / 'data' / 'processed' / 'incidents_weather.csv'
# Reserve the plan's demo and holdouts, plus the following UTC date so
# each Calgary local replay day is also completely excluded. All bounds are UTC.
EVALUATION_DAYS = ('2025-02-04', '2025-02-14', '2025-11-24')
EXCLUDED_DAYS = frozenset(d for day in EVALUATION_DAYS for d in
    (day, (pd.Timestamp(day) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')))


def _zones():
    zones = pd.read_csv(ZONES_PATH)
    if zones.zone_id.isna().any() or zones.zone_id.duplicated().any() or zones.empty:
        raise ValueError('Zone IDs must be unique and nonempty')
    return zones


def _start(day, hour):
    if isinstance(hour, bool) or not isinstance(hour, (int, np.integer)) or not 0 <= hour <= 23:
        raise ValueError('hour must be a UTC integer from 0 to 23')
    ts = pd.Timestamp(day)
    if ts.tzinfo is None:
        ts = ts.tz_localize('UTC')
    else:
        ts = ts.tz_convert('UTC')
    return ts.normalize() + pd.Timedelta(hours=int(hour))


@lru_cache(maxsize=1)
def _data():
    weather = pd.read_csv(WEATHER_PATH)
    weather['timestamp'] = pd.to_datetime(weather.timestamp, utc=True)
    incidents = pd.read_csv(INCIDENTS_PATH, usecols=['START_DT_UTC', 'zone_id'])
    incidents['START_DT_UTC'] = pd.to_datetime(incidents.START_DT_UTC, utc=True)
    return weather, incidents


def _features(times, snow, temp, recent, median):
    times = pd.DatetimeIndex(times)
    how = times.dayofweek * 24 + times.hour
    hour_week = np.eye(168)[how][:, 1:]
    temp = np.asarray(temp, dtype=float)
    temp = np.where(np.isfinite(temp), temp, median)
    return np.column_stack([np.ones(len(times)), hour_week, np.asarray(snow, dtype=float),
                            (temp < 0).astype(float), np.asarray(recent, dtype=float)])


def _fit_poisson(x, y, ridge=2.0):
    """Ridge Poisson IRLS, including zero-incident hours; intercept unpenalized."""
    beta = np.zeros(x.shape[1])
    beta[0] = np.log(max(float(y.mean()), 1e-6))
    penalty = np.eye(x.shape[1]) * ridge
    penalty[0, 0] = 0
    def objective(b):
        eta = np.clip(x @ b, -25, 25)
        return float(np.sum(np.exp(eta) - y * eta) + .5 * b @ penalty @ b)
    for _ in range(60):
        eta = np.clip(x @ beta, -25, 25)
        mu = np.exp(eta)
        gradient = x.T @ (mu - y) + penalty @ beta
        hessian = x.T @ (mu[:, None] * x) + penalty
        step = np.linalg.solve(hessian, gradient)
        scale = 1.0
        score = objective(beta)
        while scale > 1e-8 and objective(beta - scale * step) > score:
            scale *= .5
        updated = beta - scale * step
        if np.max(np.abs(updated - beta)) < 1e-7:
            return updated
        beta = updated
    raise RuntimeError('Poisson fit did not converge')


@lru_cache(maxsize=32)
def _trained(cutoff_text, zone_ids):
    weather, incidents = _data()
    cutoff = pd.Timestamp(cutoff_text)
    w = weather[(weather.timestamp < cutoff) &
                ~weather.timestamp.dt.strftime('%Y-%m-%d').isin(EXCLUDED_DAYS)].copy()
    history = incidents[(incidents.START_DT_UTC < cutoff) &
                        ~incidents.START_DT_UTC.dt.strftime('%Y-%m-%d').isin(EXCLUDED_DAYS)]
    if w.empty or history.empty:
        raise ValueError('No pre-decision training history; choose a later UTC date')
    counts = history.groupby(history.START_DT_UTC.dt.floor('h')).size()
    y = counts.reindex(pd.DatetimeIndex(w.timestamp), fill_value=0).to_numpy(dtype=float)
    median = float(w.temp_c.median())
    if not np.isfinite(median):
        raise ValueError('No historical temperature observations')
    x = _features(w.timestamp, w.snowing, w.temp_c, w.snow_last_6h, median)
    beta = _fit_poisson(x, y)
    shares = history.zone_id.value_counts().reindex(zone_ids, fill_value=0).to_numpy(dtype=float)
    shares = (shares + 1) / (shares.sum() + len(shares))
    return beta, median, shares


def forecast(day, hour: int, weather: dict) -> pd.DataFrame:
    """Zone demand for [day hour UTC, +3h), using current weather persisted 3h.

    Fit only on dates before the decision UTC date. Missing temperature is imputed
    from training history. Required weather keys: snowing, temp_c, snow_last_6h.
    """
    start = _start(day, hour)
    zones = _zones()
    beta, median, shares = _trained(start.normalize().isoformat(), tuple(zones.zone_id))
    times = pd.date_range(start, periods=3, freq='h')
    for key in ('snowing', 'snow_last_6h'):
        if not isinstance(weather[key], (bool, np.bool_)):
            raise ValueError(f'{key} must be boolean')
    x = _features(times, [weather['snowing']]*3, [weather['temp_c']]*3,
                  [weather['snow_last_6h']]*3, median)
    total = float(np.exp(np.clip(x @ beta, -25, 25)).sum())
    return pd.DataFrame({'zone_id': zones.zone_id, 'expected_incidents': total * shares})


def baseline_forecast(day, hour: int) -> pd.DataFrame:
    """Observed per-zone counts in the same three UTC hours seven days earlier."""
    start = _start(day, hour) - pd.Timedelta(days=7)
    end = start + pd.Timedelta(hours=3)
    zones = _zones()
    w, incidents = _data()
    if start < w.timestamp.min() or end > w.timestamp.max() + pd.Timedelta(hours=1):
        raise ValueError('Same-week baseline window is outside the available data')
    history = incidents[(incidents.START_DT_UTC >= start) & (incidents.START_DT_UTC < end)]
    counts = history.zone_id.value_counts().reindex(zones.zone_id, fill_value=0)
    return pd.DataFrame({'zone_id': zones.zone_id.to_numpy(), 'expected_incidents': counts.to_numpy(dtype=float)})


def clear_cache():
    """Call after rebuilding source CSVs in a running process."""
    _data.cache_clear()
    _trained.cache_clear()
