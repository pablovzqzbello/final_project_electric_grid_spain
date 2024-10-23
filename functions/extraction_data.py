import streamlit as st
import requests
import os

def extract_data_demanda(start_year=2020, end_year=2023, lang="es", category="demanda", wodget="evolucion"):
    all_data = []

    for year in range(start_year, end_year + 1):
        url = f"https://apidatos.ree.es/{lang}/datos/{category}/{widget}"

        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': 'month'}

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Host': 'apidatos.ree.es'}

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            all_data.append(data)
        else:
            print(f"Error fetching data for year {year}: {response.status_code}")

    return all_data

demanda_json=extract_data_demanda()

def proccess_demanda(demanda_json):

    demanda = []

    for entry in all_data:
        included = entry.get('included', [])
        for item in included:
            values = item.get('attributes', {}).get('values', [])
            for value in values:
                # Extraer información relevante
                relevant = {'datetime': value.get('datetime'),
                            'demand_value': value.get('value'),
                            'percentage': value.get('percentage')}
                demanda.append(relevant)

    df_demanda = pd.DataFrame(demanda)

    return df_demanda

df_demanda=proccess_demanda()

def save_csv_demanda(df_demanda, filename="sources/demanda_data.csv"):

    os.makedirs("sources", exist_ok=True)

    df_demanda.to_csv(filename, index=False)





