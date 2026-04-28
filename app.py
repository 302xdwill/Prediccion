import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from forecast_methods import (
    naive,
    mean_method,
    moving_average,
    drift
)

# ----------------------------------------
# CONFIGURACIÓN GLOBAL DE ESTILO
# ----------------------------------------
plt.rcParams["figure.figsize"] = [16, 5]
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["lines.linewidth"] = 3
plt.rcParams["lines.markersize"] = 8
plt.rcParams["xtick.color"] = "gray"
plt.rcParams["ytick.color"] = "gray"
plt.grid(color="#F3F2F2", linestyle=":", linewidth=2)

st.set_page_config(page_title="Pronóstico de Series de Tiempo", layout="wide")
st.title("📈 Aplicación Web de Pronóstico de Series de Tiempo")
st.write("Carga un archivo CSV y selecciona el método de pronóstico.")

# ----------------------------------------
# CARGA DE ARCHIVO
# ----------------------------------------
file = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if file is not None:
    try:
        df = pd.read_csv(file)
        st.success("Archivo cargado correctamente ✅")

        st.subheader("📄 Vista previa de los datos")
        st.dataframe(df.head())

        # ----------------------------------------
        # SELECCIÓN DE COLUMNAS
        # ----------------------------------------
        date_col = st.selectbox("Columna de fecha", df.columns)
        value_col = st.selectbox("Columna de valores", df.columns)

        # ----------------------------------------
        # PREPROCESAMIENTO
        # ----------------------------------------
        data = df[[date_col, value_col]].copy()
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        data[value_col] = (
            data[value_col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

        data = data.dropna().set_index(date_col).sort_index()
        series = data[value_col]

        # ----------------------------------------
        # VISUALIZACIÓN HISTÓRICA
        # ----------------------------------------
        st.subheader("📊 Serie de tiempo histórica")
        st.line_chart(series)

        # ----------------------------------------
        # PARÁMETROS DEL PRONÓSTICO
        # ----------------------------------------
        st.subheader("⚙️ Configuración del pronóstico")

        horizon = st.number_input("Horizonte de pronóstico", min_value=1, value=7)

        method = st.selectbox(
            "Método de pronóstico",
            ["Ingenuo", "Media", "Media Móvil", "Deriva", "Ingenuo Estacional"]
        )

        window = None
        if method == "Media Móvil":
            window = st.number_input("Ventana de la media móvil", min_value=2, value=5)

        # ----------------------------------------
        # EJECUCIÓN
        # ----------------------------------------
        if st.button("🚀 Ejecutar pronóstico"):

            # -------- CÁLCULO --------
            if method == "Ingenuo":
                forecast = naive(series, horizon)
                color, marker = "turquoise", "D"

            elif method == "Media":
                forecast = mean_method(series, horizon)
                color, marker = "gold", "X"

            elif method == "Media Móvil":
                forecast = moving_average(series, horizon, window)
                color, marker = "silver", "*"

            elif method == "Deriva":
                forecast = drift(series, horizon)
                color, marker = "deeppink", "o"

            elif method == "Ingenuo Estacional":
                # Repite los últimos valores de una temporada
                season_length = st.number_input("Tamaño de la temporada", min_value=2, value=7)
                forecast = list(series.values[-season_length:])[:horizon]
                color, marker = "turquoise", "D"

            forecast = np.array(forecast)

            # -------- GRÁFICA AVANZADA --------
            x_train = np.arange(len(series))
            x_forecast = np.arange(len(series), len(series) + horizon)

            fig, ax = plt.subplots()

            # Histórico
            ax.plot(x_train, series, color="pink", marker="o", label="Datos Históricos")

            # Pronóstico
            ax.plot(x_forecast, forecast, color=color, linestyle="--", marker=marker, label=f"Método {method}")

            # Personalización
            ax.tick_params(axis="x", labelrotation=90)
            if "electricidad" in file.name.lower():
                ax.set_ylabel("Demanda de Electricidad (MW)")
            else:
                ax.set_ylabel("Dólares Estadounidenses")
            ax.set_xlabel("Día de Cotización")
            ax.grid(color="#F3F2F2", linestyle=":", linewidth=2)
            ax.legend()

            st.pyplot(fig)

            # ----------------------------------------
            # RESUMEN VISUAL
            # ----------------------------------------
            st.subheader("📌 Resumen del Pronóstico")

            col1, col2, col3 = st.columns(3)
            col1.metric("Último valor real", f"{series.iloc[-1]:.2f}")
            col2.metric("Primer valor pronosticado", f"{forecast[0]:.2f}")
            col3.metric("Promedio pronosticado", f"{np.mean(forecast):.2f}")

            # ----------------------------------------
            # MÉTRICAS DE ERROR (VALOR AGREGADO)
            # ----------------------------------------
            st.subheader("📊 Métricas de Evaluación")

            y_true = np.array([series.iloc[-1]] * horizon)
            mae = np.mean(np.abs(y_true - forecast))
            rmse = np.sqrt(np.mean((y_true - forecast) ** 2))

            st.write(f"- **MAE (Error Absoluto Medio):** {mae:.2f}")
            st.write(f"- **RMSE (Raíz del Error Cuadrático Medio):** {rmse:.2f}")

            # ----------------------------------------
            # TABLA DE PRONÓSTICO
            # ----------------------------------------
            forecast_df = pd.DataFrame({
                "Periodo Futuro": range(1, horizon + 1),
                "Valor Pronosticado": forecast
            })

            st.subheader("📊 Valores Pronosticados")
            st.dataframe(forecast_df.style.format({"Valor Pronosticado": "{:.2f}"}))

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
