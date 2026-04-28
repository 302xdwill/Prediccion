import numpy as np

def naive(series, h):
    return [series.iloc[-1]] * h

def mean_method(series, h):
    return [series.mean()] * h

def moving_average(series, h, window):
    values = series.values[-window:].tolist()
    forecasts = []

    for _ in range(h):
        avg = np.mean(values)
        forecasts.append(avg)
        values.pop(0)
        values.append(avg)

    return forecasts

def drift(series, h):
    first = series.iloc[0]
    last = series.iloc[-1]
    n = len(series)

    return [last + i * ((last - first) / (n - 1)) for i in range(1, h + 1)]