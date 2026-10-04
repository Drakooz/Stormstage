import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
import pandas as pd
import forecast as model
from src.prepare_data import clean_weather


class PartATests(unittest.TestCase):
    def tearDown(self):
        model.clear_cache()

    def test_weather_utc_and_causal_snow(self):
        weather = clean_weather(Path(__file__).resolve().parents[1] / 'data/raw/weather')
        self.assertEqual(len(weather), 8760)
        self.assertEqual(str(weather.timestamp.dt.tz), 'UTC')
        expected = weather.snowing.shift(1, fill_value=False).rolling(6, min_periods=1).max().astype(bool)
        pd.testing.assert_series_equal(weather.snow_last_6h, expected, check_names=False)
        self.assertFalse(weather.snow_last_6h.iloc[0])
        self.assertEqual(weather.temp_c.isna().sum(), 8)

    def test_join_conserves_incidents_and_counts(self):
        root = Path(__file__).resolve().parents[1] / 'data/processed'
        inc = pd.read_csv(root / 'incidents_weather.csv')
        hourly = pd.read_csv(root / 'zone_hourly.csv')
        self.assertEqual(len(inc), len(pd.read_csv(root / 'incidents_clean.csv')))
        self.assertEqual(hourly.incident_count.sum(), len(inc))
        self.assertFalse(hourly.duplicated(['timestamp', 'zone_id']).any())
        self.assertEqual(len(hourly), 8760 * len(model._zones()))
        starts = pd.to_datetime(inc.START_DT_UTC, utc=True)
        pd.testing.assert_series_equal(starts.dt.floor('h'), pd.to_datetime(inc.timestamp, utc=True), check_names=False)

    def test_midnight_horizon_and_contract(self):
        f = model.forecast('2025-02-04', 23, {'snowing': True, 'temp_c': -8., 'snow_last_6h': True})
        self.assertEqual(list(f.columns), ['zone_id', 'expected_incidents'])
        self.assertEqual(list(f.zone_id), list(model._zones().zone_id))
        self.assertTrue(np.isfinite(f.expected_incidents).all())
        self.assertTrue(f.expected_incidents.ge(0).all())
        with patch.object(model, '_trained', return_value=(np.r_[0., np.zeros(170)], 0., np.ones(len(f))/len(f))), \
             patch.object(model, '_features', wraps=model._features) as features:
            constant = model.forecast('2025-12-31', 23, {'snowing': False, 'temp_c': 5., 'snow_last_6h': False})
        self.assertAlmostEqual(constant.expected_incidents.sum(), 3.)
        self.assertEqual(features.call_args.args[0][-1], pd.Timestamp('2026-01-01 01:00', tz='UTC'))

    def test_prior_week_baseline_exact_window(self):
        zones = pd.DataFrame({'zone_id': ['A', 'B']})
        weather = pd.DataFrame({'timestamp': pd.date_range('2025-01-01', periods=500, freq='h', tz='UTC')})
        inc = pd.DataFrame({'zone_id': ['A', 'A', 'B', 'B'], 'START_DT_UTC': pd.to_datetime(
            ['2025-01-01 22:59Z', '2025-01-01 23:00Z', '2025-01-02 01:59Z', '2025-01-02 02:00Z'])})
        with patch.object(model, '_zones', return_value=zones), patch.object(model, '_data', return_value=(weather, inc)):
            actual = model.baseline_forecast('2025-01-08', 23)
        self.assertEqual(actual.expected_incidents.tolist(), [1., 1.])

    def test_future_and_reserved_outcomes_do_not_change_fit(self):
        weather, incidents = model._data()
        cutoff = pd.Timestamp('2025-03-01', tz='UTC')
        zone_ids = tuple(model._zones().zone_id)
        original = model._trained(cutoff.isoformat(), zone_ids)
        altered = incidents.copy()
        withheld = (altered.START_DT_UTC >= cutoff) | altered.START_DT_UTC.dt.strftime('%Y-%m-%d').isin(model.EXCLUDED_DAYS)
        # Keep non-withheld history identical; inflate only inaccessible outcomes.
        altered = pd.concat([incidents[~withheld], incidents[withheld], incidents[withheld]], ignore_index=True)
        altered_weather = weather.copy()
        excluded = (weather.timestamp >= cutoff) | weather.timestamp.dt.strftime('%Y-%m-%d').isin(model.EXCLUDED_DAYS)
        altered_weather.loc[excluded, 'temp_c'] = 1000.
        model._trained.cache_clear()
        with patch.object(model, '_data', return_value=(altered_weather, altered)):
            changed = model._trained(cutoff.isoformat(), zone_ids)
        for a, b in zip(original, changed):
            np.testing.assert_allclose(a, b)

    def test_bad_hour_rejected(self):
        for hour in [-1, 24, True, 2.5]:
            with self.assertRaises(ValueError):
                model._start('2025-02-04', hour)


if __name__ == '__main__':
    unittest.main()
