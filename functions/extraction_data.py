import streamlit as st
import requests
import os

def extract_data_demanda(start_year=2020, end_year=2023, lang="es", category="demanda", wodget="evolucion"):
    all_data = []

    for year in range(start_year, end_year + 1):
        # Construir la URL
        url = f"https://apidatos.ree.es/{lang}/datos/{category}/{widget}"

        # Ajustar los parámetros para cada año
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


