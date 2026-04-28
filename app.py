import streamlit as st
import pandas as pd
import numpy as np

from forecast_methods import (
    naive,
    mean_method,
    moving_average,
    drift
)

# ----------------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------------
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
        # VISUALIZACIÓN PRINCIPAL (UNA SOLA)
        # ----------------------------------------
        st.subheader("📊 Serie de tiempo histórica")

        chart_data = pd.DataFrame({
            "Histórico": series
        })

        # ----------------------------------------
        # CONFIGURACIÓN DEL PRONÓSTICO
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

        run = st.button("🚀 Ejecutar pronóstico", use_container_width=True)

        # ----------------------------------------
        # EJECUCIÓN
        # ----------------------------------------
        if run:

            # -------- CÁLCULO --------
            if method == "Ingenuo":
                forecast = naive(series, horizon)

            elif method == "Media":
                forecast = mean_method(series, horizon)

            elif method == "Media Móvil":
                forecast = moving_average(series, horizon, window)

            elif method == "Deriva":
                forecast = drift(series, horizon)

            elif method == "Ingenuo Estacional":
                season_length = st.number_input("Tamaño de la temporada", min_value=2, value=7)
                forecast = list(series.values[-season_length:])[:horizon]

            forecast = np.array(forecast)

            # ----------------------------------------
            # FECHAS FUTURAS
            # ----------------------------------------
            freq = pd.infer_freq(series.index)
            if freq is None:
                freq = "D"

            forecast_index = pd.date_range(
                start=series.index[-1],
                periods=horizon + 1,
                freq=freq
            )[1:]

            forecast_series = pd.Series(forecast, index=forecast_index)

            # 🔥 SUAVIZAR TRANSICIÓN (PRO)
            forecast_series.iloc[0] = series.iloc[-1]

            # ----------------------------------------
            # UNIR HISTÓRICO + PRONÓSTICO
            # ----------------------------------------
            chart_data = pd.DataFrame({
                "Histórico": series,
                "Pronóstico": forecast_series
            })

            # Evitar problemas visuales
            chart_data["Pronóstico"] = chart_data["Pronóstico"].astype(float)

            # Mostrar inicio del forecast
            st.caption(f"📍 El pronóstico inicia en: {forecast_index[0].date()}")

        # ----------------------------------------
        # GRÁFICA FINAL (SIEMPRE UNA SOLA)
        # ----------------------------------------
        st.line_chart(chart_data)

        # ----------------------------------------
        # SI HAY PRONÓSTICO → MOSTRAR RESULTADOS
        # ----------------------------------------
        if run:

            st.subheader("📌 Resumen del Pronóstico")

            col1, col2, col3 = st.columns(3)
            col1.metric("Último valor real", f"{series.iloc[-1]:.2f}")
            col2.metric("Primer valor pronosticado", f"{forecast[0]:.2f}")
            col3.metric("Promedio pronosticado", f"{np.mean(forecast):.2f}")

            # ----------------------------------------
            # MÉTRICAS
            # ----------------------------------------
            st.subheader("📊 Métricas de Evaluación")

            y_true = np.array([series.iloc[-1]] * horizon)

            mae = np.mean(np.abs(y_true - forecast))
            rmse = np.sqrt(np.mean((y_true - forecast) ** 2))

            st.write(f"- **MAE (Error Absoluto Medio):** {mae:.2f}")
            st.write(f"- **RMSE (Raíz del Error Cuadrático Medio):** {rmse:.2f}")

            # ----------------------------------------
            # TABLA DE RESULTADOS
            # ----------------------------------------
            forecast_df = pd.DataFrame({
                "Fecha": forecast_index,
                "Valor Pronosticado": forecast
            })

            st.subheader("📊 Valores Pronosticados")
            st.dataframe(forecast_df.style.format({"Valor Pronosticado": "{:.2f}"}))

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")