import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import pickle
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
import plotly.graph_objects as go
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping


df_demanda = pd.read_csv("df_demanda")

df_exchanges = pd.read_csv("df_exchanges")

df_generation = pd.read_csv("df_generation")


def preprocess_data(df_demanda, df_exchanges, df_generation):
    # Eliminar columnas innecesarias
    df_demanda = df_demanda.drop(columns=["fecha_extraccion"])
    df_exchanges = df_exchanges.drop(columns=["fecha_extraccion"])
    df_generation = df_generation.drop(columns=["fecha_extraccion"])


    # Filtrar y limpiar df_generation
    df_generation_filtered = df_generation[(df_generation['energia'] == 'Generación total') | (df_generation['tipo_tecnología'] == 'Generación total')]
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


df=preprocess_data(df_demanda, df_exchanges, df_generation)


def escalador(df, target_column="valor_demanda_MW",scaler_filename="models/scaler.pkl"):
    # Seleccionar las columnas a escalar, excluyendo la columna objetivo
    columnas_a_escalar = df.drop(columns=[target_column]).columns
    valores = df[columnas_a_escalar].values
    objetivo = df[target_column].values
    
    # Crear y ajustar el escalador
    scaler = StandardScaler()
    valores_escalados = scaler.fit_transform(valores)
    objetivo_escalado = scaler.fit_transform(objetivo.reshape(-1, 1))
    
    # Dar forma a los valores escalados
    valores_escalados = valores_escalados.reshape((valores_escalados.shape[0],valores_escalados.shape[1], 1))
    
    # Guardar el escalador en un archivo pickle
    with open(scaler_filename, "wb") as f:
        pickle.dump(scaler, f)
    
    return valores_escalados, objetivo_escalado


valores_escalados, objetivo_escalado=escalador(df)


def train_test_split_data(valores_escalados, objetivo_escalado, train_ratio=0.8):
    # Calcular el tamaño del conjunto de entrenamiento
    train_size = int(len(valores_escalados) * train_ratio)
    
    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test = valores_escalados[:train_size], valores_escalados[train_size:]
    y_train, y_test = objetivo_escalado[:train_size], objetivo_escalado[train_size:]
    
    return X_train, X_test, y_train, y_test


X_train, X_test, y_train, y_test=train_test_split_data(valores_escalados, objetivo_escalado)



def modelo_neuronal_RNN (X_train, y_train, X_test, y_test, scaler_filename="models/scaler.pkl", model_filename="models/rnn_model.pkl"):
    
    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)
    
    # Definición del modelo
    model = Sequential()
    model.add(Input(shape=(X_train.shape[1], X_train.shape[2])))
    model.add(SimpleRNN(units=50, activation='relu'))
    model.add(Dense(units=1))
    model.compile(optimizer="adam", loss="mse")

    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # Entrenamiento del modelo
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=200, batch_size=1,callbacks=[early_stopping])
    
    # Realizar predicciones
    predictions_scaled = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions_scaled)
    expected = scaler.inverse_transform(y_test)

    # Guardar el modelo en un archivo pickle
    with open(model_filename, "wb") as f:
        pickle.dump(model, f)

    plt.plot(history.history["val_loss"], label = "val_loss")
    plt.plot(history.history["loss"], label = "loss")
    plt.legend()
    plt.show()
    
    # Mostrar predicciones y graficar resultados
    for i in range(len(y_test)):
        print(f"Real: {expected[i]} | Predicción: {predictions[i]}")

    plt.plot(expected, color="blue", alpha=0.7, label="objetivo")
    plt.plot(predictions, color="green", alpha=0.7, label="prediccion")
    plt.legend()
    plt.show()

    return model, history


modelo_neuronal_RNN(X_train, y_train, X_test, y_test)



def predict_7_days(scaler_filename="models/scaler.pkl", model_filename="models/rnn_model.pkl", last_sequence=X_test[-1]):

    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)
    
    with open(model_filename, "rb") as f:
        model = pickle.load(f)
    
    predictions_scaled = []
    input_sequence = last_sequence.copy()

    for _ in range(7):  # Predecir 7 días
        # Redimensionar la secuencia para cumplir con el formato del modelo
        input_sequence_reshaped = input_sequence.reshape(1, input_sequence.shape[0], input_sequence.shape[1])

        # Realizar la predicción
        prediction_scaled = model.predict(input_sequence_reshaped)[0, 0]  # Extraer el valor escalar
        predictions_scaled.append(prediction_scaled)

        # Actualizar la secuencia de entrada
        input_sequence = np.append(input_sequence_reshaped[:,1,:], [[prediction_scaled]], axis=0)
    predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))
 
    return predictions



predictions_7 = predict_7_days()


predictions_7


def modelo_neuronal_lstm (X_train, y_train, X_test, y_test, scaler_filename="models/scaler.pkl", model_filename="models/lstm_model.pkl"):
    # Cargar el escalador preentrenado desde el archivo pickle
    with open(scaler_filename, "rb") as f:
        scaler = pickle.load(f)
    
    # Definición del modelo LSTM
    model_lstm = Sequential()
    model_lstm.add(Input(shape=(X_train.shape[1], X_train.shape[2])))
    model_lstm.add(LSTM(units=50, activation='relu'))
    model_lstm.add(Dense(units=1))
    model_lstm.compile(optimizer="adam", loss="mse")


    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # Entrenamiento del modelo
    history_lstm = model_lstm.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=200, batch_size=1,callbacks=[early_stopping])
    
    # Realizar predicciones
    predictions_scaled = model_lstm.predict(X_test)
    predictions = scaler.inverse_transform(predictions_scaled)
    expected = scaler.inverse_transform(y_test)

    # Guardar el modelo en un archivo pickle
    with open(model_filename, "wb") as f:
        pickle.dump(model_lstm, f)

    plt.plot(history_lstm.history["val_loss"], label = "val_loss")
    plt.plot(history_lstm.history["loss"], label = "loss")
    plt.legend()
    plt.show()
    
    # Mostrar predicciones y graficar resultados
    for i in range(len(y_test)):
        print(f"Real: {expected[i]} | Predicción: {predictions[i]}")

    plt.plot(expected, color="blue", alpha=0.7, label="objetivo")
    plt.plot(predictions, color="green", alpha=0.7, label="prediccion")
    plt.legend()
    plt.show()

    return model_lstm, history_lstm



modelo_neuronal_lstm(X_train, y_train, X_test, y_test)



predictions_7_lstm = predict_7_days(model_filename="models/lstm_model.pkl")


predictions_7_lstm

