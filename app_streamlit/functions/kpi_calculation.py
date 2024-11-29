import pandas as pd

def calcular_crecimiento_5_anos(df_generation):
    # Asegurarse de que 'fecha' es de tipo datetime
    df_generation['fecha'] = pd.to_datetime(df_generation['fecha'])

    # Filtrar solo filas con 'Generación total'
    df_generacion_total = df_generation[df_generation['tipo_tecnología'] == 'Generación total']

    # Extraer el año y calcular el total anual de generación
    df_generacion_total['year'] = df_generacion_total['fecha'].dt.year
    generacion_anual = df_generacion_total.groupby('year')['valor_generacion_MW'].sum().reset_index()

    # Seleccionar los últimos 5 años
    ultimos_5_anios = generacion_anual.tail(5)

    # Calcular el crecimiento porcentual
    valor_inicial = ultimos_5_anios.iloc[0]['valor_generacion_MW']
    valor_reciente = ultimos_5_anios.iloc[-1]['valor_generacion_MW']
    crecimiento_porcentual = ((valor_reciente - valor_inicial) / valor_inicial) * 100

    return crecimiento_porcentual


def calcular_crecimiento_demanda(df_demanda):
# Asegurarse de que 'fecha' es de tipo datetime
    df_demanda['fecha'] = pd.to_datetime(df_demanda['fecha'])

    # Calcular la demanda máxima por año
    df_demanda['year'] = df_demanda['fecha'].dt.year
    demanda_maxima_anual = df_demanda.groupby('year')['valor_demanda_MW'].max().reset_index()

    # Seleccionar los últimos 5 años
    ultimos_5_anos = demanda_maxima_anual.tail(5)

    # Calcular el crecimiento porcentual
    valor_inicial = ultimos_5_anos.iloc[0]['valor_demanda_MW']
    valor_reciente = ultimos_5_anos.iloc[-1]['valor_demanda_MW']
    crecimiento_porcentual = ((valor_reciente - valor_inicial) / valor_inicial) * 100

    return crecimiento_porcentual


def calculo_crecimiento_co2(df_emisiones_co2):
    df_emisiones_co2 = df_emisiones_co2[~(df_emisiones_co2['energia'].isin(['tCO2 eq./MWh', 'Total tCO2 eq.']))]
    df_emisiones_co2 = df_emisiones_co2.groupby('fecha', as_index=False)['valor'].sum()

    df_emisiones_co2['fecha'] = pd.to_datetime(df_emisiones_co2['fecha'])
    df_emisiones_co2['year'] = df_emisiones_co2['fecha'].dt.year

    emisiones_maxima_anual = df_emisiones_co2.groupby('year')['valor'].max().reset_index()

    # Seleccionar los últimos 5 años
    ultimos_5_anos = emisiones_maxima_anual.tail(5)

    # Calcular el crecimiento porcentual
    valor_inicial = ultimos_5_anos.iloc[0]['valor']
    valor_reciente = ultimos_5_anos.iloc[-1]['valor']
    crecimiento_porcentual = ((valor_reciente - valor_inicial) / valor_inicial) * 100

    return crecimiento_porcentual
