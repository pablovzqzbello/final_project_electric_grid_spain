import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
from functions.sql_function import extract_data

def load_data_from_sql():
    query = 'SELECT valor_demanda_MWW FROM demanda_energia'
    df = extract(query)
    return df['valor']