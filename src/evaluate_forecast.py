"""Score the plan's reserved storm dates without training on their outcomes."""
import numpy as np
import pandas as pd
import forecast as model


def evaluate():
    weather, incidents = model._data()
    weather = weather.set_index('timestamp')
    rows = []
    for day in model.EVALUATION_DAYS:
        for hour in range(24):
            start = model._start(day, hour)
            w = weather.loc[start]
            f = model.forecast(day, hour, {'snowing': bool(w.snowing), 'temp_c': float(w.temp_c),
                                          'snow_last_6h': bool(w.snow_last_6h)})
            b = model.baseline_forecast(day, hour)
            observed = incidents[(incidents.START_DT_UTC >= start) &
                                 (incidents.START_DT_UTC < start + pd.Timedelta(hours=3))]
            actual = observed.zone_id.value_counts().reindex(f.zone_id, fill_value=0).to_numpy(dtype=float)
            for label, prediction in [('poisson', f), ('last_week', b)]:
                expected = prediction.expected_incidents.to_numpy()
                rows.append({'day': day, 'hour_utc': hour, 'model': label,
                             'zone_mae': float(np.abs(expected-actual).mean()),
                             'zone_mse': float(np.square(expected-actual).mean()),
                             'city_absolute_error': float(abs(expected.sum()-actual.sum())),
                             'predicted_total': float(expected.sum()), 'actual_total': float(actual.sum())})
    scores = pd.DataFrame(rows)
    summary = scores.groupby(['day', 'model'], as_index=False).agg(
        zone_mae=('zone_mae', 'mean'), zone_mse=('zone_mse', 'mean'),
        city_mae=('city_absolute_error', 'mean'))
    summary['zone_rmse'] = np.sqrt(summary.pop('zone_mse'))
    (model.ROOT / 'results').mkdir(parents=True, exist_ok=True)
    scores.to_csv(model.ROOT / 'results' / 'forecast_windows.csv', index=False)
    summary.to_csv(model.ROOT / 'results' / 'forecast_accuracy.csv', index=False)
    print(summary.to_string(index=False))
    return summary


if __name__ == '__main__':
    evaluate()
