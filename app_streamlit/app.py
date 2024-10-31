import streamlit as st
import plotly.express as px
import pandas as pd
from functions.sql_function import extract_data



# Configuración de la página
st.set_page_config(
    page_title="PFB: Red Eléctrica Española",
    page_icon=":bulb:",
    layout="wide"
)

def main ():
    st.title("Red Eléctroca de España. Análisis de mercado, sostenibilidad y rendimiento")

    st.title("Red Eléctrica de España. Investigación de mercado, sostenibilidad y rendimiento")
    st.header("¿Qué es Redeia, S.A.?")
    st.markdown("Redeia Corporación, S.A. es un grupo empresarial mutinacional de origen español fundado el 29 de enero de"
            "1985 que actúa en el mercado energético internacional como operador de sistema eléctrico"
            "Cuenta con una financiación público privada, en la que el Gobierno de España cubre el 20% de las invesiones,"
            "mientras que el 80% lo cubre capital privado.")
    st.header("¿De dónde se obtiene la información?")
    st.markdown("La política de total transparencia de la corporación, sellada y garantizada por organismos públicos, se "
            "manifiesta a través de la creación de un API donde los consumidores y diversos usuarios pueden consultar"
            "libremente los datos que Redeia genera a tiempo real."
            "Para más consultas: https://www.ree.es/es/datos/apidatos")
    st.header("Objetivos")
    st.markdown("Con los daos obtenidos se pretende realizar un análisis integral de la corporación enfocándose a la "
            "estructura de negocio desta empresa desde cuatro pilares funamentales:"
            "\n- Generación de energía"
            "\n- Balance estructural energético"
            "\n- Demanda energética del mercado español"
            "\n- Transacciones Internacionales"
            "\nComo punto clave este estudio se situa sobre la sostenibilidad incidiendo en el precio y el impacto de la"
            "de la huella de carbono a través del crecimiento de la demanda y l ageneración de energía")
    choices=["Vista general", "Vista específica"]
    choice=st.sidebar.selectbox(label="Menú", options=choices,index=0)
    if choice == "Vista general":
        #### A PARTIR DE AQUÍ SE COLOCAN LAS VISUALIZACIONES GENERALES. ACORDAROS QUE COMO MÍNIMO SON 5. PODEMOS
        #### AÑADIR TABLAS DE SQL
        st.subheader("Demanda del mercado")
        #Filtros
        df_demanda=extract_data("SELECT fecha, valor_demanda_MW FROM demanda_energia")
        #Visualizaciones
        fig=px.line(df_demanda, x='fecha', y='valor_demanda_MW')
        st.plotly_chart(fig)
        st.subheader("Balance energético")
        #Filtros
        #Visualizaciones
        st.subheader("Transacciones energéticas")
        #Filtros
        #Visualizaciones
        st.subheader("Generación energética")
        #Filtros
        #Visualizaciones
    else:
        ### TEXTO EXPLICATIVO???
        st.subheader("Predicción de demanda")
        st.subheader("Predicción de balance")
        st.subheader("Predicción de generación energía")
        st.subheader("Predicción de importaciones")
        st.subheader("Predicción de exportaciones")
        st.subheader("Prediccion de saldo")

if  __name__ == "__main__":
    main()
