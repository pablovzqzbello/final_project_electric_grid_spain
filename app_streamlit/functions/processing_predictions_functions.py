import pandas as pd
import numpy as np
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


def escalador(df, T=7, target_column="valor_demanda_MW", scaler_filename="models/scaler.pkl"):

    # Seleccionar las columnas a escalar, excluyendo la columna objetivo
    columnas_a_escalar = df.drop(columns=[target_column]).columns
    valores = df[columnas_a_escalar].values
    objetivo = df[target_column].values

    # Seleccionar las columnas a escalar, excluyendo la columna objetivo
    valores = valores
    objetivo = objetivo

    # Cargar el escalador desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    # Aplicar el escalador a los valores y al objetivo
    valores_escalados = scaler.fit_transform(valores)
    objetivo_escalado = scaler.fit_transform(objetivo.reshape(-1, 1))

    # Crear listas para las secuencias de entrada y salida
    X = []
    y = []
    
    # Generar ventanas deslizantes
    for t in range(len(df) - T):
        # Toma valores de X de t en t con stride de 1
        x = valores_escalados[t : t + T]
        X.append(x)
        
        # Toma los valores de t en t
        y_ = objetivo_escalado[t + T]
        y.append(y_)
    
    # Convertir listas a arrays de numpy
    X = np.array(X)  # Dimensión: (samples, timesteps, features)
    y = np.array(y)  # Dimensión: (samples, 1)
    
    return X, y

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

    # Cargar el modelo RNN preentrenado desde el archivo pickle
    with open(model_filename, "rb") as f:
        model_rnn = pickle.load(f)

    # Realizar predicciones
    predictions_scaled = model_rnn.predict(X_test)

    # Asegurar que el escalador reciba datos en el formato correcto para la transformación inversa
    predictions = scaler.inverse_transform(predictions_scaled)
    expected = scaler.inverse_transform(y_test)

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
    predictions = scaler.inverse_transform(predictions_scaled)
    expected = scaler.inverse_transform(y_test)

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


def predict_7_days_rnn(
        scaler_filename="models/scaler.pkl",
        model_filename="models/rnn_model.pkl",
        last_sequence=None):

    # Cargar el scaler y el modelo
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    with open(model_filename, "rb") as f:
        model = pickle.load(f)

    #return predictions
    if last_sequence.ndim == 3:
        last_sequence = last_sequence[0]  

    if last_sequence is None or last_sequence.ndim != 2:
        raise ValueError("`last_sequence` debe ser un array 2D con forma (T, n_features).")
    
    predictions_scaled = []
    input_sequence = last_sequence.reshape(7,7)

    for _ in range(7):  # Predecir 7 días
        # Redimensionar la secuencia para cumplir con el formato del modelo
        input_sequence_reshaped = input_sequence.reshape(1, input_sequence.shape[0], input_sequence.shape[1])

        # Realizar la predicción
        prediction_scaled = model.predict(input_sequence_reshaped)[0, 0]  # Extraer el valor escalar
        predictions_scaled.append(prediction_scaled)

        # Actualizar la secuencia de entrada
        # Desplazar los timesteps anteriores y añadir la nueva predicción como una característica adicional
        new_timestep = np.zeros(input_sequence.shape[1])
        new_timestep[0] = prediction_scaled  # Suponiendo que la predicción corresponde a la primera característica
        input_sequence = np.vstack((input_sequence[1:], new_timestep))
    
    # Invertir la escala de las predicciones
    predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))

    # Crear un DataFrame para las predicciones
    days = list(range(1, 8))  # Días 1 al 7
    predictions_df = pd.DataFrame({
        "Día": days,
        "Demanda (MW)": predictions.flatten()
    })

    # Crear el gráfico con plotly.express
    fig_rnn = px.line(
        predictions_df,
        x="Día",
        y="Demanda (MW)",
        title="Predicción de 7 días de energía",
        markers=True,
        template="plotly_white"
    )

    return st.plotly_chart(fig_rnn)


def predict_7_days_lstm(
        scaler_filename="models/scaler.pkl",
        model_filename="models/lstm_model.pkl",
        last_sequence=None):

    # Cargar el scaler y el modelo
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)

    with open(model_filename, "rb") as f:
        model = pickle.load(f)

    #return predictions
    if last_sequence.ndim == 3:
        last_sequence = last_sequence[0]  

    if last_sequence is None or last_sequence.ndim != 2:
        raise ValueError("`last_sequence` debe ser un array 2D con forma (T, n_features).")
    
    predictions_scaled = []
    input_sequence = last_sequence.reshape(7,7)

    for _ in range(7):  # Predecir 7 días
        # Redimensionar la secuencia para cumplir con el formato del modelo
        input_sequence_reshaped = input_sequence.reshape(1, input_sequence.shape[0], input_sequence.shape[1])

        # Realizar la predicción
        prediction_scaled = model.predict(input_sequence_reshaped)[0, 0]  # Extraer el valor escalar
        predictions_scaled.append(prediction_scaled)

        # Actualizar la secuencia de entrada
        # Desplazar los timesteps anteriores y añadir la nueva predicción como una característica adicional
        new_timestep = np.zeros(input_sequence.shape[1])
        new_timestep[0] = prediction_scaled  # Suponiendo que la predicción corresponde a la primera característica
        input_sequence = np.vstack((input_sequence[1:], new_timestep))
    
    # Invertir la escala de las predicciones
    predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))

    # Crear un DataFrame para las predicciones
    days = list(range(1, 8))  # Días 1 al 7
    predictions_df = pd.DataFrame({
        "Día": days,
        "Demanda (MW)": predictions.flatten()
    })

    # Crear el gráfico con plotly.express
    fig_lstm = px.line(
        predictions_df,
        x="Día",
        y="Demanda (MW)",
        title="Predicción de 7 días de energía",
        markers=True,
        template="plotly_white"
    )

    return st.plotly_chart(fig_lstm)
