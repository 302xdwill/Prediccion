# plotter.py
import matplotlib.pyplot as plt
import numpy as np

def plot_forecast(series, forecast, horizon, title):
    x_train = np.arange(len(series))
    x_forecast = np.arange(len(series), len(series) + horizon)

    plt.figure(figsize=(14, 5))
    plt.plot(x_train, series.values, marker='o', label="Datos históricos")
    plt.plot(x_forecast, forecast, marker='D', label="Pronóstico")

    plt.title(title)
    plt.xlabel("Tiempo")
    plt.ylabel("Valor")
    plt.grid(True)
    plt.legend()
    plt.show()