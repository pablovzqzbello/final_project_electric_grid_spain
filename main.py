import streamlit as st
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from functions.extraction_data import *

def main ():

    st.title("Red Eléctrica de España. Investigación de mercado, sostenibilidad y rendimiento")

    st.text("Este proyecto tiene como objetivo al consolidación de una aplicación innovadora en el mercado que nos"
            "permita obtener datos a tiempo real del mercado eléctrico español. En primer lugar, de la demanda energética." 
            "En segundo lugar, la generación de energía dispuesta entre energías renovables y no renovables. En tercer lugar,"
            "un balance de producción general, en el que podamos ver la evolución del consumo energético español."
            "En cuarto lugar, un estudio sobre la importación y exportación de energía entre España y sus partners."
            "Agradecemos a Redeia Corporación S.A. la disposición de un API accesible para la consulta de su base de datos")



    st.text ("Extractor de datos de la app")

    lang = st.selectbox("Select Language", ["es", "en"])
    category = st.text_input("Category", value="demanda")
    widget = st.text_input("Widget", value="evolucion")
    start_year = st.number_input("Start Year", min_value=2000, max_value=2024, value=2020)
    end_year = st.number_input("End Year", min_value=2000, max_value=2024, value=2023)

    if st.button("Extracción y guardado de los datos"):
        data = extract_data_demanda(lang, category, widget, start_year, end_year)
        filename = 'sources/extracted_data.csv'
        save_csv_demanda(data, filename)
        st.success("¡Extracción completada!")


if __name__ == "__main__":
    main()