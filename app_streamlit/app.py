import streamlit as st
import plotly.express as px
import pandas as pd
from functions.extraction_data import (
    extract_balance,
    extract_demand,
    extract_exchange,
    extract_generation,
    extract_co2
)
from sklearn.linear_model import LinearRegression
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="PFB: Red Eléctrica Española",
    page_icon=":bulb:",
    layout="wide"
)

st.title("Red Eléctrica de España. Análisis de mercado, sostenibilidad y rendimiento")

# Sección de selección de vistas
section = st.sidebar.selectbox("Seleccione la sección", ["Datos por Año", "Visualizaciones Destacadas", "Proyecciones Futuras"])

# Selección de año si se está en la sección "Datos por Año"
if section == "Datos por Año":
    year = st.selectbox("Selecciona el año para la extracción de datos:", list(range(2011, 2025)))

    # Extracción y visualización de datos por año
    with st.spinner(f"Extrayendo datos de demanda para el año {year}..."):
        try:
            df_demanda = extract_demand(year)
            st.write("Demanda Energética", df_demanda)
            st.plotly_chart(px.line(df_demanda, x='fecha', y='valor_demanda_MW', title="Demanda Energética"))
            st.plotly_chart(px.histogram(df_demanda, x='valor_demanda_MW', title="Distribución de Demanda"))
        except Exception as e:
            st.error(f"Error al extraer datos de demanda: {e}")

    with st.spinner(f"Extrayendo datos de balance para el año {year}..."):
        try:
            df_balance = extract_balance(year)
            st.write("Balance Energético", df_balance)
            st.plotly_chart(px.line(df_balance, x='fecha', y='valor_balance_GW', title="Balance Energético"))
        except Exception as e:
            st.error(f"Error al extraer datos de balance: {e}")

    with st.spinner(f"Extrayendo datos de intercambios para el año {year}..."):
        try:
            df_exchange = extract_exchange(year)
            st.write("Intercambios Energéticos", df_exchange)
            st.plotly_chart(
                px.histogram(df_exchange[~(df_exchange['tipo_transaccion'] == 'saldo')], x='fecha', y='valor_GW',
                             color='pais', title="Intercambios por País"))
        except Exception as e:
            st.error(f"Error al extraer datos de intercambios: {e}")

    with st.spinner(f"Extrayendo datos de generación para el año {year}..."):
        try:
            df_generation = extract_generation(year)
            st.write("Generación Energética", df_generation)
            st.plotly_chart(px.histogram(df_generation[~(df_generation['energia'] == 'Generación total')], x='fecha',
                                         y='valor_generacion_GW', color='energia', title="Generación por Tipo"))
        except Exception as e:
            st.error(f"Error al extraer datos de generación: {e}")

    with st.spinner(f"Extrayendo datos de emisiones de CO2 para el año {year}..."):
        try:
            df_co2 = extract_co2(year)
            st.write("Emisiones de CO2", df_co2)
            st.plotly_chart(px.line(df_co2, x='fecha', y='valor_co2', title="Emisiones de CO2"))
        except Exception as e:
            st.error(f"Error al extraer datos de CO2: {e}")

# Visualizaciones destacadas
elif section == "Visualizaciones Destacadas":
    st.subheader("Visualizaciones Destacadas y Análisis Comparativo")

    # Comparación de generación de energía por tipo
    st.markdown("### Comparación de Generación de Energía por Tipo")
    try:
        df_all_generation = pd.concat([extract_generation(y) for y in range(2011, 2025)])
        st.plotly_chart(px.line(df_all_generation[~(df_all_generation['energia'] == 'Generación total')], x='fecha',
                                y='valor_generacion_GW', color='energia',
                                title="Evolución de Generación de Energía por Tipo"))
    except Exception as e:
        st.error(f"Error al cargar datos de generación: {e}")

    # Comparación de intercambios de energía entre países
    st.markdown("### Comparación de Intercambios de Energía entre Países")
    try:
        df_all_exchange = pd.concat([extract_exchange(y) for y in range(2011, 2025)])
        st.plotly_chart(px.bar(df_all_exchange, x='fecha', y='valor_GW', color='pais',
                               title="Intercambios Energéticos por País a lo Largo de los Años"))
    except Exception as e:
        st.error(f"Error al cargar datos de intercambios: {e}")

    # Evolución de la demanda energética
    st.markdown("### Evolución de la Demanda Energética")
    try:
        df_all_demand = pd.concat([extract_demand(y) for y in range(2011, 2025)])
        st.plotly_chart(px.line(df_all_demand, x='fecha', y='valor_demanda_MW',
                                title="Evolución de la Demanda Energética (2011-2024)"))
    except Exception as e:
        st.error(f"Error al cargar datos de demanda: {e}")

    # Análisis de emisiones de CO2
    st.markdown("### Evolución de Emisiones de CO2")
    try:
        df_all_co2 = pd.concat([extract_co2(y) for y in range(2011, 2025)])
        st.plotly_chart(px.area(df_all_co2, x='fecha', y='valor_co2', color='energia',
                                title="Emisiones de CO2 por Fuente de Energía (2011-2024)"))
    except Exception as e:
        st.error(f"Error al cargar datos de CO2: {e}")

    # Correlación entre generación y demanda
    st.markdown("### Correlación entre Generación y Demanda Energética")
    try:
        df_all_generation = df_all_generation[~df_all_generation['energia'].isin(['Generación total'])]
        df_correlation = pd.merge(df_all_demand, df_all_generation, on="fecha", suffixes=("_demanda", "_generacion"))
        st.plotly_chart(px.scatter(df_correlation, x='valor_demanda_MW', y='valor_generacion_GW', color='energia',
                                   title="Correlación entre Demanda y Generación Energética por Tipo"))
    except Exception as e:
        st.error(f"Error al cargar datos para correlación: {e}")

# Proyecciones Futuras
elif section == "Proyecciones Futuras":
    st.subheader("Proyecciones Futuras de Consumo y Emisiones")

    try:
        # Cargar todos los datos históricos
        df_all_generation = pd.concat([extract_generation(y) for y in range(2011, 2025)])
        df_all_co2 = pd.concat([extract_co2(y) for y in range(2011, 2025)])

        # Generar proyección futura
        fig_projection = generate_future_projection(df_all_generation, df_all_co2)
        st.plotly_chart(fig_projection)
    except Exception as e:
        st.error(f"Error al generar proyección futura: {e}")

