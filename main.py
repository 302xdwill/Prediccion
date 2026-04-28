# main.py
from data_loader import load_csv
from forecast_methods import (
    naive_forecast,
    mean_forecast,
    moving_average_forecast,
    drift_forecast
)
from plotter import plot_forecast

def main():
    filepath = input("Ruta del archivo CSV: ")
    date_col = input("Nombre columna fecha: ")
    value_col = input("Nombre columna valor: ")

    data = load_csv(filepath, date_col, value_col)
    series = data[value_col]

    horizon = int(input("Horizonte de pronóstico: "))

    print("""
    Seleccione método:
    1 - Ingenuo
    2 - Media
    3 - Media Móvil
    4 - Deriva
    """)

    option = int(input("Opción: "))

    if option == 1:
        forecast = naive_forecast(series, horizon)
        title = "Método Ingenuo"

    elif option == 2:
        forecast = mean_forecast(series, horizon)
        title = "Método de la Media"

    elif option == 3:
        window = int(input("Tamaño de ventana: "))
        forecast = moving_average_forecast(series, horizon, window)
        title = "Media Móvil Simple"

    elif option == 4:
        forecast = drift_forecast(series, horizon)
        title = "Método de la Deriva"

    else:
        print("Opción inválida")
        return

    plot_forecast(series, forecast, horizon, title)


if __name__ == "__main__":
    main()