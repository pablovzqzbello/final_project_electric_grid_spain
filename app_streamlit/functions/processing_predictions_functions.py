import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

def preprocess_data(df_demanda, df_exchanges, df_generation):
    # Eliminar columnas innecesarias
    df_demanda = df_demanda.drop(columns=["fecha_extraccion"])
    df_exchanges = df_exchanges.drop(columns=["fecha_extraccion"])
    df_generation = df_generation.drop(columns=["fecha_extraccion"])

    # Filtrar y limpiar df_generation
    df_generation_filtered = df_generation[
        (df_generation['energia'] == 'Generación total') | (df_generation['tipo_tecnología'] == 'Generación total')]
    df_generation_filtered = df_generation_filtered.drop(columns=['energia', 'tipo_tecnología'])
    df_generation_filtered = df_generation_filtered.reset_index(drop=True)

    # Filtrar df_exchanges
    df_exchanges_filtered = df_exchanges[(df_exchanges['tipo_transaccion'] == 'saldo')]
    df_exchanges_agg = df_exchanges_filtered.groupby("fecha", as_index=False)["valor_GW"].sum()

    # Merge de los DataFrames
    df_merge_test = df_demanda.merge(df_exchanges_agg, on="fecha", how="left")
    df_merge_test = df_merge_test.rename(columns={"valor_GW": "saldo_intercambios"})
    df_merge_test = df_merge_test.merge(df_generation_filtered, on="fecha", how="left")

    # Interpolación de valores NaN'S en 'saldo_intercambios'
    df_merge_test['saldo_intercambios'] = df_merge_test['saldo_intercambios'].interpolate(method='linear')

    # Crear nuevas columnas basadas en la fecha
    df_merge_test['fecha'] = pd.to_datetime(df_merge_test['fecha'], format='%Y-%m-%d')
    df_merge_test['año'] = df_merge_test['fecha'].dt.year
    df_merge_test['mes'] = df_merge_test['fecha'].dt.month
    df_merge_test['dia'] = df_merge_test['fecha'].dt.day
    df_merge_test['dia_semana'] = df_merge_test['fecha'].dt.weekday
    df_merge_test['es_fin_de_semana'] = df_merge_test['dia_semana'].apply(lambda x: 1 if x >= 5 else 0)
    df_merge_test = df_merge_test.drop(columns=["fecha"])

    return df_merge_test


def escalador(df, target_column="valor_demanda_MW", scaler_filename="scaler.pkl"):

    # Seleccionar las columnas a escalar, excluyendo la columna objetivo
    columnas_a_escalar = df.drop(columns=[target_column]).columns
    valores = df[columnas_a_escalar].values
    objetivo = df[target_column].values

    # Cargar el escalador desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Aplicar el escalador a los valores y al objetivo
    valores_escalados = scaler.transform(valores)
    objetivo_escalado = scaler.transform(objetivo.reshape(-1, 1))

    # Dar forma a los valores escalados
    valores_escalados = valores_escalados.reshape((valores_escalados.shape[0], 1, valores_escalados.shape[1]))

    return valores_escalados, objetivo_escalado


def train_test_split_data(valores_escalados, objetivo_escalado, train_ratio=0.8):
    # Calcular el tamaño del conjunto de entrenamiento
    train_size = int(len(valores_escalados) * train_ratio)

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test = valores_escalados[:train_size], valores_escalados[train_size:]
    y_train, y_test = objetivo_escalado[:train_size], objetivo_escalado[train_size:]

    return X_train, X_test, y_train, y_test


def modelo_neuronal_RNN(X_test, y_test, scaler_filename, model_filename="rnn_model.pkl"):

    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Cargar el modelo preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model = pickle.load(f)

    # Realizar predicciones
    predictions_scaled = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions_scaled)
    expected = scaler.inverse_transform(y_test)

    # Mostrar predicciones y graficar resultados
    for i in range(len(y_test)):
        print(f"Real: {expected[i]} | Predicción: {predictions[i]}")

    plt.plot(expected, color="blue", alpha=0.7, label="Objetivo")
    plt.plot(predictions, color="green", alpha=0.7, label="Predicción")
    plt.legend()
    plt.show()

    return predictions


def modelo_neuronal_lstm(X_test, y_test, scaler_filename, model_filename="lstm_model.pkl"):

    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Cargar el modelo preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model_lstm = pickle.load(f)

    # Realizar predicciones
    predictions_scaled = model_lstm.predict(X_test)
    predictions = scaler.inverse_transform(predictions_scaled)
    expected = scaler.inverse_transform(y_test)

    # Mostrar predicciones y graficar resultados
    for i in range(len(y_test)):
        print(f"Real: {expected[i]} | Predicción: {predictions[i]}")

    plt.plot(expected, color="blue", alpha=0.7, label="Objetivo")
    plt.plot(predictions, color="green", alpha=0.7, label="Predicción")
    plt.legend()
    plt.show()

    return predictions