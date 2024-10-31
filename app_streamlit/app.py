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

def main():
    # Mostrar la imagen de Redeia
    image_path = 'auxiliary/redeia_marca1_2.png'
    st.image(image_path, caption='Redeia S.A', use_column_width=True)

    # Encabezados y descripción
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
                'Para más consultas: https://www.ree.es/es/datos/apidatos')

    st.header("Objetivos")
    st.markdown(
        "Con los datos obtenidos se pretende realizar un análisis integral de la corporación enfocándose a la "
            "estructura de negocio desta empresa desde cuatro pilares funamentales:"
            "\n- Generación de energía"
            "\n- Balance estructural energético"
            "\n- Demanda energética del mercado español"
            "\n- Transacciones Internacionales"
            "\nComo punto clave este estudio se situa sobre la sostenibilidad incidiendo en el precio y el impacto de la"
            "de la huella de carbono a través del crecimiento de la demanda y l ageneración de energía")


    choices = ["Vista general", "Vista específica"]
    choice = st.sidebar.selectbox(label="Menú", options=choices, index=0)

    if choice == "Vista general":
        st.subheader("Demanda del mercado")
        df_demanda = extract_data("SELECT fecha, valor_demanda_MW FROM demanda_energia")

        # Filtro de Fecha para Demanda (encima de la visualización)

        start_date_demanda = st.date_input("Fecha de inicio (Demanda)", value=df_demanda['fecha'].min(),
                                           min_value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max())
        end_date_demanda = st.date_input("Fecha de fin (Demanda)", value=df_demanda['fecha'].max(),
                                         min_value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max())
        filtered_df_demanda = df_demanda[(df_demanda['fecha'] >= pd.to_datetime(start_date_demanda)) & (
                    df_demanda['fecha'] <= pd.to_datetime(end_date_demanda))]

        # Visualización de Demanda
        fig1 = px.line(filtered_df_demanda, x='fecha', y='valor_demanda_MW')
        st.plotly_chart(fig1)

        # Sección Balance Energético
        st.subheader("Balance energético")
        df_balance = extract_data("SELECT fecha, valor_balance_GW, energia FROM balance_energia")

        # Filtro Multiselect para Tipo de Energía en el Sidebar
        energia_type = st.sidebar.multiselect("Tipo de Energía (Balance)", options=df_balance['energia'].unique(),
                                              default=df_balance['energia'].unique())
        filtered_df_balance = df_balance[df_balance['energia'].isin(energia_type)]

        # Filtro de Fecha para Balance (encima de la visualización)
        start_date_balance = st.date_input("Fecha de inicio (Balance)", value=filtered_df_balance['fecha'].min(),
                                           min_value=filtered_df_balance['fecha'].min(),
                                           max_value=filtered_df_balance['fecha'].max())
        end_date_balance = st.date_input("Fecha de fin (Balance)", value=filtered_df_balance['fecha'].max(),
                                         min_value=filtered_df_balance['fecha'].min(),
                                         max_value=filtered_df_balance['fecha'].max())
        filtered_df_balance = filtered_df_balance[
            (filtered_df_balance['fecha'] >= pd.to_datetime(start_date_balance)) & (
                        filtered_df_balance['fecha'] <= pd.to_datetime(end_date_balance))]

        # Visualización de Balance
        fig2 = px.line(filtered_df_balance[~(filtered_df_balance['energia'] == 'Generación renovable')], x='fecha',
                       y='valor_balance_GW')
        st.plotly_chart(fig2)

        # Sección Transacciones Energéticas
        st.subheader("Transacciones energéticas")

        # Carga de datos para Transacciones
        df_exchanges = extract_data("SELECT fecha, valor_GW, tipo_transaccion, pais FROM transacciones_energia")

        # Filtro para excluir el valor 'saldo' en la columna 'tipo_transaccion'
        df_exchanges = df_exchanges[df_exchanges['tipo_transaccion'] != 'saldo']

        # Filtros Multiselect en el Sidebar para País y Tipo de Transacción
        pais_filter = st.sidebar.multiselect("País", options=df_exchanges['pais'].unique(),
                                             default=df_exchanges['pais'].unique())
        transaccion_type = st.sidebar.multiselect("Tipo de Transacción",
                                                  options=df_exchanges['tipo_transaccion'].unique(),
                                                  default=df_exchanges['tipo_transaccion'].unique())
        filtered_df_exchanges = df_exchanges[
            (df_exchanges['pais'].isin(pais_filter)) & (df_exchanges['tipo_transaccion'].isin(transaccion_type))]

        # Filtro de Fecha para Transacciones (encima de la visualización)
        start_date_exchanges = st.date_input("Fecha de inicio (Transacciones)",
                                             value=filtered_df_exchanges['fecha'].min(),
                                             min_value=filtered_df_exchanges['fecha'].min(),
                                             max_value=filtered_df_exchanges['fecha'].max())
        end_date_exchanges = st.date_input("Fecha de fin (Transacciones)", value=filtered_df_exchanges['fecha'].max(),
                                           min_value=filtered_df_exchanges['fecha'].min(),
                                           max_value=filtered_df_exchanges['fecha'].max())
        filtered_df_exchanges = filtered_df_exchanges[
            (filtered_df_exchanges['fecha'] >= pd.to_datetime(start_date_exchanges)) & (
                        filtered_df_exchanges['fecha'] <= pd.to_datetime(end_date_exchanges))]

        # Visualización de Transacciones
        fig3 = px.histogram(filtered_df_exchanges, x='fecha', y='valor_GW', color='pais')
        st.plotly_chart(fig3)

        # Sección Generación Energética
        st.subheader("Generación energética")
        df_generation = extract_data("SELECT fecha, valor_generacion_GW, energia FROM generacion_energia")

        # Filtro Multiselect en el Sidebar para Tipo de Energía en Generación
        energia_filter = st.sidebar.multiselect("Tipo de Energía (Generación)",
                                                options=df_generation['energia'].unique(),
                                                default=df_generation['energia'].unique())
        filtered_df_generation = df_generation[df_generation['energia'].isin(energia_filter)]

        # Filtro de Fecha para Generación (encima de la visualización)
        start_date_generation = st.date_input("Fecha de inicio (Generación)",
                                              value=filtered_df_generation['fecha'].min(),
                                              min_value=filtered_df_generation['fecha'].min(),
                                              max_value=filtered_df_generation['fecha'].max())
        end_date_generation = st.date_input("Fecha de fin (Generación)", value=filtered_df_generation['fecha'].max(),
                                            min_value=filtered_df_generation['fecha'].min(),
                                            max_value=filtered_df_generation['fecha'].max())
        filtered_df_generation = filtered_df_generation[
            (filtered_df_generation['fecha'] >= pd.to_datetime(start_date_generation)) & (
                        filtered_df_generation['fecha'] <= pd.to_datetime(end_date_generation))]

        # Visualización de Generación Energética
        fig4 = px.histogram(filtered_df_generation[~(filtered_df_generation['energia'] == 'Generación total')],
                            x='fecha', y='valor_generacion_GW', color='energia')
        st.plotly_chart(fig4)

        fig5 = px.pie(filtered_df_generation[~(filtered_df_generation['energia'] == 'Generación total')],
                      values='valor_generacion_GW', names='energia')
        st.plotly_chart(fig5)

    else:
        st.subheader("Predicción de demanda")
        st.subheader("Predicción de balance")
        st.subheader("Predicción de generación energía")
        st.subheader("Predicción de importaciones")
        st.subheader("Predicción de exportaciones")
        st.subheader("Predicción de saldo")


if __name__ == "__main__":
    main()
