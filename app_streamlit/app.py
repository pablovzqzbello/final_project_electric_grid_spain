import streamlit as st
import plotly.express as px
import pandas as pd
from functions.sql_function import extract_data



# Configuración de la página
st.set_page_config(
    page_title="PFB: Red Eléctrica Española",
    page_icon=":bulb:",
    layout="wide")

def main ():
    st.title("Red Eléctrica de España. Análisis de mercado, sostenibilidad y rendimiento")

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
        #start_date=st.date_input("Fecha de inicio", value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max())
        #end_date = st.date_input("Fecha de fin", value=df_demanda["fecha"].max(), min_value=df_demanda["fecha"].min(),
                                 #max_value=df_demanda["fecha"].max())
        #start_date=pd.Timestamp(start_date)
        #end_date=pd.Timestamp(end_date)
        #filtered_df_demanda=df_demanda[(df_demanda['fecha']>=pd.to_datetime(start_date)) & (df_demanda['fecha']<=pd.to_datetime(end_date))]
        fig1=px.line(df_demanda, x='fecha', y='valor_demanda_MW')
        st.plotly_chart(fig1)
        st.subheader("Balance energético")
        #Filtros
        df_balance=extract_data("SELECT fecha, valor_balance_GW FROM balance_energia")
        fig2 = px.pie(df_balance[~(df_balance['energia']=='Generación renovable')],x='fecha', y='valor_balance_GW')
        st.plotly_chart(fig2)
        #Visualizaciones
        st.subheader("Transacciones energéticas")
        #Filtros
        df_exchanges=extract_data("SELECT * FROM transacciones_energia")
        fig3=px.histogram(df_exchanges[~(df_exchanges['tipo_transaccion'] == 'saldo')], x='fecha', y='valor_GW',
                     color='pais')
        st.plotly_chart(fig3)
        #Visualizaciones
        st.subheader("Generación energética")
        df_generation=extract_data("SELECT * FROM generacion_energia")
        fig4=px.histogram(df_generation[~(df_generation['energia']=='Generación total')], x='fecha', y='valor_generacion_GW', color='energia')
        st.plotly_chart(fig4)
        fig5=px.pie(df_generation[~(df_generation['energia']=='Generación total')], values='valor_generacion_GW', names='energia')
        st.plotly_chart(fig5)
    else:
        st.subheader("Predicción de demanda")
        st.subheader("Predicción de balance")
        st.subheader("Predicción de generación energía")
        st.subheader("Predicción de importaciones")
        st.subheader("Predicción de exportaciones")
        st.subheader("Prediccion de saldo")

if  __name__ == "__main__":
    main()
