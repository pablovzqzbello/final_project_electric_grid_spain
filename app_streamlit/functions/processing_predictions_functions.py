import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pickle
import plotly.express as px

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


def escalador(df, target_column="valor_demanda_MW", scaler_filename="models/scaler.pkl"):

    # Seleccionar las columnas a escalar, excluyendo la columna objetivo
    columnas_a_escalar = df.drop(columns=[target_column]).columns
    valores = df[columnas_a_escalar].values
    objetivo = df[target_column].values

    # Cargar el escalador desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Aplicar el escalador a los valores y al objetivo
    valores_escalados = scaler.fit_transform(valores)
    objetivo_escalado = scaler.fit_transform(objetivo.reshape(-1, 1))

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


def modelo_neuronal_rnn(X_test, y_test, scaler_filename="models/scaler.pkl", model_filename="models/rnn_model.pkl"):
    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Cargar el modelo LSTM preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model_rnn = pickle.load(f)

    # Realizar predicciones
    predictions_scaled = model_rnn.predict(X_test)

    # Asegurar que el escalador reciba datos en el formato correcto para la transformación inversa
    predictions = scaler.inverse_transform(predictions_scaled.reshape(-1, 1))
    expected = scaler.inverse_transform(y_test.reshape(-1, 1))

    # Mostrar predicciones
    for i in range(len(y_test)):
        print(f"Real: {expected[i]} | Predicción: {predictions[i]}")

    # Crear un DataFrame para las gráficas
    df = pd.DataFrame({
        'Fecha': range(len(expected)),  # Asumiendo que cada índice es una fecha secuencial
        'Real': expected.flatten(),
        'Predicción': predictions.flatten()
    })

    # Graficar con plotly
    fig_rnn = px.line(df, x='Fecha', y=['Real', 'Predicción'], labels={'Fecha': 'Tiempo', 'value': 'Valor'},
                       title="Predicciones vs Valores Reales")
    return st.plotly_chart(fig_rnn)


def modelo_neuronal_lstm(X_test, y_test, scaler_filename="models/scaler.pkl", model_filename="models/lstm_model.pkl"):
    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Cargar el modelo LSTM preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model_lstm = pickle.load(f)

    # Realizar predicciones
    predictions_scaled = model_lstm.predict(X_test)

    # Asegurar que el escalador reciba datos en el formato correcto para la transformación inversa
    predictions = scaler.inverse_transform(predictions_scaled.reshape(-1, 1))
    expected = scaler.inverse_transform(y_test.reshape(-1, 1))

    # Mostrar predicciones
    for i in range(len(y_test)):
        print(f"Real: {expected[i]} | Predicción: {predictions[i]}")

    # Crear un DataFrame para las gráficas
    df = pd.DataFrame({
        'Fecha': range(len(expected)),  # Asumiendo que cada índice es una fecha secuencial
        'Real': expected.flatten(),
        'Predicción': predictions.flatten()
    })

    # Graficar con plotly
    fig_lstm = px.line(df, x='Fecha', y=['Real', 'Predicción'], labels={'Fecha': 'Tiempo', 'value': 'Valor'},
                  title="Predicciones vs Valores Reales")
    return st.plotly_chart(fig_lstm)


def modelo_neuronal_rnn_seven_days(X_test, scaler_filename="models/scaler.pkl", model_filename="models/rnn_model.pkl"):
    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Cargar el modelo LSTM preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model_rnn = pickle.load(f)

    # Predecir los próximos 7 días basándonos en las últimas observaciones
    predictions_scaled = []
    input_sequence = X_test[-1]  # Tomamos el último valor de entrada para empezar la predicción

    for _ in range(7):  # Predecir 7 días
        # Redimensionar la entrada para cumplir con el formato esperado por el modelo (1, 1, 7)
        input_sequence_reshaped = input_sequence.reshape(1, 1, -1)  # (batch_size, time_steps, features)

        # Realizar la predicción para el siguiente día
        prediction_scaled = model_rnn.predict(input_sequence_reshaped)
        predictions_scaled.append(prediction_scaled[0])

        # Actualizamos la secuencia de entrada para incluir la predicción del día
        input_sequence = np.roll(input_sequence, -1)  # Mover todos los valores una posición
        input_sequence[-1] = prediction_scaled  # Asignar la predicción al último valor de la secuencia

    # Convertir las predicciones escaladas a los valores originales
    predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))

    # Mostrar predicciones
    print("Predicciones para los próximos 7 días:")
    for i, pred in enumerate(predictions):
        print(f"Día {i + 1}: {pred[0]} MW")

    # Crear un DataFrame para las gráficas
    df = pd.DataFrame({
        'Fecha': pd.date_range(start="2024-11-09", periods=7, freq='D'),  # Asegúrate de ajustar la fecha inicial
        'Predicción': predictions.flatten()
    })

    # Graficar con plotly
    fig_rnn_7 = px.line(df, x='Fecha', y='Predicción', labels={'Fecha': 'Fecha', 'Predicción': 'Valor Predicho'},
                        title="Predicción de Demanda de Energía para los Próximos 7 Días")
    return st.plotly_chart(fig_rnn_7)

def modelo_neuronal_lstm_seven_days(X_test, scaler_filename="models/scaler.pkl", model_filename="models/lstm_model.pkl"):
    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Cargar el modelo LSTM preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model_lstm = pickle.load(f)

    # Predecir los próximos 7 días basándonos en las últimas observaciones
    predictions_scaled = []
    input_sequence = X_test[-1]  # Tomamos el último valor de entrada para empezar la predicción

    for _ in range(7):  # Predecir 7 días
        # Redimensionar la entrada para cumplir con el formato esperado por el modelo (1, 1, 7)
        input_sequence_reshaped = input_sequence.reshape(1, 1, -1)  # (batch_size, time_steps, features)

        # Realizar la predicción para el siguiente día
        prediction_scaled = model_lstm.predict(input_sequence_reshaped)
        predictions_scaled.append(prediction_scaled[0])

        # Actualizamos la secuencia de entrada para incluir la predicción del día
        input_sequence = np.roll(input_sequence, -1)  # Mover todos los valores una posición
        input_sequence[-1] = prediction_scaled  # Asignar la predicción al último valor de la secuencia

    # Convertir las predicciones escaladas a los valores originales
    predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))

    # Mostrar predicciones
    print("Predicciones para los próximos 7 días:")
    for i, pred in enumerate(predictions):
        print(f"Día {i + 1}: {pred[0]} MW")

    # Crear un DataFrame para las gráficas
    df = pd.DataFrame({
        'Fecha': pd.date_range(start="2024-11-09", periods=7, freq='D'),  # Asegúrate de ajustar la fecha inicial
        'Predicción': predictions.flatten()
    })

    # Graficar con plotly
    fig_lstm_7 = px.line(df, x='Fecha', y='Predicción', labels={'Fecha': 'Fecha', 'Predicción': 'Valor Predicho'},
                        title="Predicción de Demanda de Energía para los Próximos 7 Días")
    return st.plotly_chart(fig_lstm_7)