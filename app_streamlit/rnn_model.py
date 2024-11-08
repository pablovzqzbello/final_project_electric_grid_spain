import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
from functions.sql_function import extract_data

def load_data_from_sql():
    query = 'SELECT valor_demanda_MW FROM demanda_energia'
    df = extract_data(query)
    return df['valor_demanda_MW'].values

def create_sequences(data, sequence_length=30):
    X = []
    y = []
    for i in range(len(data) - sequence_length):
        X.append(data[i:i + sequence_length])
        y.append(data[i + sequence_length])
    return np.array(X), np.array(y)

def build_rnn_model(sequence_length=30):
    model = Sequential()
    model.add(SimpleRNN(units=50, activation='relu', input_shape=(sequence_length, 1)))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mae')  # Configuración de la pérdida en MAE

    return model

def train_rnn_model(model, X, y, epochs=20):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    history = model.fit(X_train, y_train, epochs=epochs, validation_data=(X_test, y_test))
    return history

def load_and_prepare_data(sequence_length=30):
    demanda_values = load_data_from_sql()
    X, y = create_sequences(demanda_values, sequence_length)
    return X, y
