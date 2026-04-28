# data_loader.py
import pandas as pd

def load_csv(filepath, datetime_col, value_col):
    df = pd.read_csv(filepath)

    if datetime_col not in df.columns or value_col not in df.columns:
        raise ValueError("Columnas no encontradas en el CSV")

    df = df[[datetime_col, value_col]]
    df[datetime_col] = pd.to_datetime(df[datetime_col])

    df = df.set_index(datetime_col)
    df = df.sort_index()

    return df