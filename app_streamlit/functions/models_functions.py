import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, LSTM, Dense, Input
import pickle

def prepare_data_for_model(df, feature="valor_demanda_MW", time_step=50):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[[feature]])

    X, y = [], []
    for i in range(time_step, len(scaled_data)):
        X.append(scaled_data[i - time_step:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # (samples, time_steps, features)

    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    # Dividir en entrenamiento y prueba
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    return X_train, X_test, y_train, y_test, scaler


def build_rnn_model(input_shape):
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(SimpleRNN(units=50, activation='relu'))
    model.add(Dense(units=1))
    model.compile(optimizer="adam", loss="mse")
    return model


def build_lstm_model(input_shape):
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(units=50, activation='relu'))
    model.add(Dense(units=1))
    model.compile(optimizer="adam", loss="mse")
    return model


def generate_predictions


