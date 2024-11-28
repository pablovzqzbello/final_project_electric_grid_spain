import numpy as np
import pandas as pd
from functions.sql_function import extract_data
import streamlit as st
import plotly.express as px

def saldo_balance ():

    # Extracción datos
    df_demanda = extract_data("SELECT fecha, valor_demanda_MW FROM demanda_energia")
    df_generation = extract_data ("SELECT fecha, valor_generacion_MW, energia, tipo_tecnología FROM generacion_energia")

    #Filtrado del df
    df_generation = df_generation[(df_generation['energia'] == 'Generación total')|(df_generation['tipo_tecnología'] == 'Generación total')]
    df_generation = df_generation.drop(columns=['energia', 'tipo_tecnología'])
    df_generation = df_generation.reset_index(drop=True)

    #Creación de un nuevo df
    df_saldo_balance=pd.concat([df_demanda, df_generation], axis=1)
    df_saldo_balance=df_saldo_balance[['fecha', 'valor_demanda_MW', 'valor_generacion_MW']]
    df_saldo_balance.columns = ['fecha', 'fecha2', 'valor_demanda_MW', 'valor_generacion_MW']
    df_saldo_balance.drop('fecha2', axis=1, inplace=True)
    df_saldo_balance['balance']=df_saldo_balance['valor_generacion_MW'] - df_saldo_balance['valor_demanda_MW']

    #Visualización de los datos
    fig = px.line(df_saldo_balance,
                  x='fecha',
                  y=['valor_demanda_MW', 'valor_generacion_MW'],
                  labels={'fecha': 'Fecha', 'value': 'Valores (MW)', 'variable': 'Categoría'},
                  title='Balance entre demanda y generación')

    fig1 = px.line(df_saldo_balance,
                   x='fecha',
                   y='balance',
                   labels={'fecha': 'Fecha', 'value': 'Valores (MW)'},
                   title='Saldo balance energético')

    # Mostrar la gráfica
    st.plotly_chart(fig)
    st.plotly_chart(fig1)
