import streamlit as st
from functions.extraction_data import *
from auxiliary.db_connection import *
from functions.sql_function import *
from config import configure_page
from PIL import Image
from dotenv import load_dotenv
import plotly as px
import os

configure_page()

load_dotenv()

estandarizar_texto()
extract_demand()
extract_exchange()
extract_generation()
extract_balance()

create_db()
create_tables()

df_demanda=extract_demand()
df_exchanges=extract_exchange()
df_generation=extract_generation()
df_balance=extract_balance()

get_engine()
insert_data()
extract_data()


def main():

    st.title("Red Eléctrica de España. Análisis de mercado, sostenibilidad y rendimiento")

    st.subheader("¿Qué es Redeia, S.A.?")
    st.markdown("Redeia Corporación, S.A. es un grupo empresarial mutinacional de origen español fundado el 29 de enero de"
            "1985 que actúa en el mercado energético internacional como operador de sistema eléctrico"
            "Cuenta con una financiación público privada, en la que el Gobierno de España cubre el 20% de las invesiones,"
            "mientras que el 80% lo cubre capital privado.")

    st.subheader("¿De dónde se obtiene la información?")
    st.markdown("La política de total transparencia de la corporación, sellada y garantizada por organismos públicos, se "
            "manifiesta a través de la creación de un API donde los consumidores y diversos usuarios pueden consultar"
            "libremente los datos que Redeia genera a tiempo real."
            "Para más consultas: https://www.ree.es/es/datos/apidatos")

    st.subheader("Objetivos")
    st.markdown("Con los datos obtenidos se pretende realizar un análisis integral de la corporación enfocándose a la "
                "estructura de nogocio desta empresa desde cuatro pilares funamentales:"
                "- Generación de energía"
                "- Balance estructural energético"
                "- Demanda energética del mercado español"
                "- Transacciones Internacionales"
                "Como punto clave este estudio se situa sobre la sostenibilidad incidiendo en el precio y el impacto de la"
                "de la huella de carbono a través del crecimiento de la demanda y la generación de energía")

    choices = ["Vista general", "Vista específica"]
    choice = st.sidebar.selectbox(label="Menú", options=choices, index=0)

    if choice == "Vista general":
            #### A PARTIR DE AQUÍ SE COLOCAN LAS VISUALIZACIONES GENERALES. ACORDAROS QUE COMO MÍNIMO SON 5. PODEMOS
            #### AÑADIR TABLAS DE SQL. VAMOS BIEN. PONER UN BOTÓN AQUÍ QUE ACTIVE LA EXTRACCIÓN O LIMPIE???

        st.subheader("Demanda del mercado")
            # Filtros
        df_demanda_app=extract_data("SELECT * FROM demanda_energia")
            # Visualizaciones
        px.line(df_demanda_app, x='fecha', y='valor_demanda_MW')
        st.subheader("Balance energético")
            # Filtros
        df_balance_app=extract_data("SELECT * FROM balance_energia")
            # Visualizaciones
        st.subheader("Transacciones energéticas")
            # Filtros
        df_transacciones_app=extract_data("SELECT * FROM transacciones_energia")
            # Visualizaciones
        st.subheader("Generación energética")
            # Filtros
        df_generacion_app=extract_data("SELECT * FROM generacion_energia")
            # Visualizaciones

    elif choice == "Vista específica":
            ### TEXTO EXPLICATIVO???
        st.subheader("Predicción de demanda")
        st.subheader("Predicción de balance")
        st.subheader("Predicción de generación energía")
        st.subheader("Predicción de importaciones")
        st.subheader("Predicción de exportaciones")
        st.subheader("Prediccion de saldo")

if __name__ == "__main__":
    main()
