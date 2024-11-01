import requests
import pandas as pd
import unicodedata
import time


# Función de estandarización de texto
def estandarizar_texto(valor):
    if isinstance(valor, str):
        valor = valor.lower()
        valor = ''.join((c for c in unicodedata.normalize('NFD', valor) if unicodedata.category(c) != 'Mn'))
        valor = valor.strip()
        valor = valor.replace(" ", "_")
    return valor


# Función para extraer datos de demanda
def extract_demand(year, time_trunc='day'):
    all_data = []
    url = f"https://apidatos.ree.es/es/datos/demanda/evolucion"
    params = {
        'start_date': f'{year}-01-01T00:00',
        'end_date': f'{year}-12-31T23:59',
        'time_trunc': time_trunc
    }
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Host': 'apidatos.ree.es'}

    response = requests.get(url, params=params, headers=headers, timeout=60)
    if response.status_code == 200:
        data = response.json()
        included = data.get('included', [])
        for item in included:
            values = item.get('attributes', {}).get('values', [])
            for value in values:
                all_data.append({
                    'fecha': value.get('datetime', '').split('T')[0],
                    'valor_demanda_MW': value.get('value')
                })
    else:
        print(f"Error fetching data for year {year}: {response.status_code}")

    df_demanda = pd.DataFrame(all_data)
    df_demanda['fecha_extraccion'] = pd.Timestamp.now().floor("s")
    df_demanda['fecha'] = pd.to_datetime(df_demanda['fecha'], errors='coerce')
    return df_demanda


# Función para extraer datos de balance
def extract_balance(year, time_trunc='day'):
    all_data = []
    url = 'https://apidatos.ree.es/es/datos/balance/balance-electrico'
    params = {'start_date': f'{year}-01-01T00:00', 'end_date': f'{year}-12-31T23:59', 'time_trunc': time_trunc}

    response = requests.get(url, params=params, timeout=60)
    if response.status_code == 200:
        balance_data = response.json()
        content_data = balance_data.get('included', [])[0].get('attributes', {}).get('content', [])
        for item in content_data:
            type_name = item['type']
            values = item.get('attributes', {}).get('values', [])
            for value in values:
                all_data.append({
                    'fecha': value.get('datetime', '').split('T')[0],
                    'valor_balance_GW': value.get('value'),
                    'energia': type_name
                })
    else:
        print(f"Error fetching data for year {year}: {response.status_code}")

    df_balance = pd.DataFrame(all_data)
    df_balance['fecha_extraccion'] = pd.Timestamp.now().floor("s")
    df_balance['fecha'] = pd.to_datetime(df_balance['fecha'], errors='coerce')
    return df_balance


# Función para extraer datos de intercambios
def extract_exchange(year, time_trunc='day', widget='todas-fronteras-fisicos'):
    all_data = []
    url = f'https://apidatos.ree.es/es/datos/intercambios/{widget}'
    params = {'start_date': f'{year}-01-01T00:00', 'end_date': f'{year}-12-31T23:59', 'time_trunc': time_trunc}

    response = requests.get(url, params=params, timeout=60)
    if response.status_code == 200:
        exchange_data = response.json()
        for country in exchange_data.get('included', []):
            country_name = country.get('id')
            for content in country.get('attributes', {}).get('content', []):
                trade_type = content.get('attributes', {}).get('title')
                values = content.get('attributes', {}).get('values', [])
                for value in values:
                    all_data.append({
                        'pais': country_name,
                        'tipo_transaccion': trade_type,
                        'valor_GW': value.get('value'),
                        'fecha': value.get('datetime', '').split('T')[0]
                    })
    else:
        print(f"Error fetching data for year {year}: {response.status_code}")

    df_exchange = pd.DataFrame(all_data)
    df_exchange['fecha_extraccion'] = pd.Timestamp.now().floor("s")
    df_exchange['fecha'] = pd.to_datetime(df_exchange['fecha'], errors='coerce')
    return df_exchange


# Función para extraer datos de generación
def extract_generation(year, time_trunc='day'):
    all_data = []
    url = 'https://apidatos.ree.es/es/datos/generacion/estructura-generacion'
    params = {'start_date': f'{year}-01-01T00:00', 'end_date': f'{year}-12-31T23:59', 'time_trunc': time_trunc}

    response = requests.get(url, params=params, timeout=60)
    if response.status_code == 200:
        generation_data = response.json()
        for included_data in generation_data.get('included', []):
            values = included_data.get('attributes', {}).get('values', [])
            for value in values:
                all_data.append({
                    'fecha': value.get('datetime', '').split('T')[0],
                    'valor_generacion_GW': value.get('value'),
                    'energia': included_data.get('type')
                })
    else:
        print(f"Error fetching data for year {year}: {response.status_code}")

    df_generation = pd.DataFrame(all_data)
    df_generation['fecha_extraccion'] = pd.Timestamp.now().floor("s")
    df_generation['fecha'] = pd.to_datetime(df_generation['fecha'], errors='coerce')
    return df_generation


# Función para extraer datos de CO2
def extract_co2(year, time_trunc='day'):
    all_data = []
    url = 'https://apidatos.ree.es/es/datos/generacion/no-renovables-detalle-emisiones-CO2'
    params = {'start_date': f'{year}-01-01T00:00', 'end_date': f'{year}-12-31T23:59', 'time_trunc': time_trunc}

    response = requests.get(url, params=params, timeout=60)
    if response.status_code == 200:
        generation_data_co2 = response.json()
        for included_data in generation_data_co2.get('included', []):
            values = included_data.get('attributes', {}).get('values', [])
            for value in values:
                all_data.append({
                    'fecha': value.get('datetime', '').split('T')[0],
                    'valor_co2': value.get('value'),
                    'energia': included_data.get('type')
                })
    else:
        print(f"Error fetching data for year {year}: {response.status_code}")

    df_co2 = pd.DataFrame(all_data)
    df_co2['fecha_extraccion'] = pd.Timestamp.now().floor("s")
    df_co2['fecha'] = pd.to_datetime(df_co2['fecha'], errors='coerce')
    return df_co2

