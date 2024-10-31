import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import streamlit as st

@st.cache_data
def preprocess_data(df, target_column):
    """Preprocesa el DataFrame para el modelo de predicción."""
    df = df.copy()
    df['year'] = df['fecha'].dt.year
    df_agg = df.groupby('year')[target_column].mean().reset_index()
    return df_agg

@st.cache_data
def train_predictive_model(df, target_column):
    """Entrena un modelo de regresión lineal y realiza predicciones a futuro."""
    df_processed = preprocess_data(df, target_column)
    X = df_processed[['year']].values
    y = df_processed[target_column].values

    model = LinearRegression()
    model.fit(X, y)

    future_years = np.array([[year] for year in range(df_processed['year'].max() + 1, df_processed['year'].max() + 11)])
    future_predictions = model.predict(future_years)

    future_df = pd.DataFrame({
        'year': future_years.flatten(),
        f'predicted_{target_column}': future_predictions
    })
    return future_df, model

@st.cache_data
def generate_future_projection(df_demand, df_generation, df_co2):
    """Genera proyecciones a futuro para demanda, generación y CO2."""
    demand_projection, _ = train_predictive_model(df_demand, 'valor_demanda_MW')
    generation_projection, _ = train_predictive_model(df_generation, 'valor_generacion_GW')
    co2_projection, _ = train_predictive_model(df_co2, 'valor_co2')

    return demand_projection, generation_projection, co2_projection

