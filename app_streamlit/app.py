import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import timedelta
from functions.sql_function import extract_data

# Configuración de la página
st.set_page_config(
    page_title="PFB: Red Eléctrica Española",
    page_icon="🔋",
    layout="wide"
)

# Función para cargar datos con caché
@st.cache_data
def load_data(query):
    return extract_data(query)

######################

def load_exchanges_data():
    query = """
    SELECT pais, tipo_transaccion, SUM(valor_GW) AS valor_GW
    FROM transacciones_energia
    GROUP BY pais, tipo_transaccion
    """
    return extract_data(query)

def mostrar_mapa_coro():
    st.title("Intercambio de Energía de España con Otros Países")

    df_exchanges = load_exchanges_data()
    st.write("Datos Cargados:", df_exchanges)



    tipo_transaccion = st.selectbox("Seleccionar tipo de transacción", options=["Importación", "Exportación"])

    filtered_df = df_exchanges[df_exchanges['tipo_transaccion'] == tipo_transaccion]
    country_mapping = {
        'Francia': 'France',
        'Portugal': 'Portugal',
        'Marruecos': 'Morocco',
        'Andorra': 'Andorra',
    }

    st.write('Datos Filtrados:', filtered_df)

    # Filtrar los datos por tipo de transacción seleccionado

    filtered_df['pais'] = filtered_df['pais'].replace(country_mapping)



    if not filtered_df.empty:
        color_scale = px.colors.sequential.YlGnBu
        max_value = filtered_df['valor_GW'].max()

        fig = px.choropleth(
            filtered_df,
            locations="pais",
            locationmode="country names",
            color="valor_GW",
            color_continuous_scale=color_scale,
            range_color = (0, max_value),
            title=f"Intercambio de energía ({tipo_transaccion}) de España con otros países",
            labels={'valor_GW': 'GWh'},
            width=1900,
            height=1600,
        )

        fig.update_geos(
            showcoastlines=True, coastlinecolor='Black',
            showland=True, landcolor='white',
            showocean=True, oceancolor='lightblue',
            projection_type='natural earth',
            lonaxis_range=[-25, 55],
            lataxis_range=[-35, 70],
        )

        fig.update_layout(
            margin={'r':0,'t':50,'l':0,'b':0},
            title_x=0.5,
            coloraxis_colorbar=dict(
                title='Gwh',
                tickvals=[0, max_value / 2, max_value],
                ticks='outside')
        )
        for index, row in filtered_df.iterrows():
            if row['valor_GW'] == max_value or row['valor_GW'] == filtered_df['valor_GW'].min():
                fig.add_annotation(
                    x=row['pais'],
                    y=row['valor_GW'],
                    text=f'{row['pais']}: {row['valor_GW']:,} GhW',
                    showarrow=False,
                    yshift=10
                    )

        st.plotly_chart(fig)
    else:
        st.warning("No hay datos para mostrar en el mapa con la selección actual.")



#######################

# Función para aplicar filtro de fecha con periodos predefinidos
def date_filter(df, period, start_date=None, end_date=None):
    if period == "Personalizado" and start_date and end_date:
        return df[(df['fecha'] >= pd.to_datetime(start_date)) & (df['fecha'] <= pd.to_datetime(end_date))]
    else:
        end_date = df['fecha'].max()
        if period == "Última semana":
            start_date = end_date - timedelta(weeks=1)
        elif period == "Último mes":
            start_date = end_date - timedelta(days=30)
        elif period == "Último año":
            start_date = end_date - timedelta(days=365)
        else:  # Histórico
            start_date = df['fecha'].min()
        return df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]

def show_help():
    with st.expander("ℹ️ Ayuda de la Aplicación", expanded=True):
        st.markdown("""
            ### Ayuda de la Aplicación
            Esta aplicación permite realizar un análisis interactivo de datos energéticos de la red eléctrica de España.

            **Secciones principales**:
            - 🔌 **Demanda del mercado**: Visualización y análisis de la demanda energética en MW.
            - ⚡ **Balance energético**: Información sobre el balance de distintos tipos de energía generada.
            - 🌍 **Transacciones energéticas**: Análisis de las transacciones de energía entre países.

            **Filtros disponibles**:
            - Selección de periodos específicos: "Última semana", "Último mes", "Último año".
            - Filtro personalizado de fecha para un análisis más detallado.
        """)

# Botón en el sidebar para mostrar la ayuda
if st.sidebar.button("ℹ️ Mostrar Ayuda"):
    show_help()

# Función principal
def main():
    # Mostrar la imagen de Redeia con un tamaño controlado
    image_path = 'auxiliary/redeia_marca1_2.png'
    st.image(image_path, caption='Redeia S.A', width=400)  # Tamaño ajustado de la imagen

    # Encabezados y descripción
    st.title("Red Eléctrica de España. Análisis de mercado, sostenibilidad y rendimiento")

    st.header("¿Qué es Redeia, S.A.?")
    st.markdown(
        "Redeia Corporación, S.A. es un grupo empresarial multinacional de origen español fundado el 29 de enero de "
        "1985 que actúa en el mercado energético internacional como operador de sistema eléctrico. "
        "Cuenta con una financiación público-privada, en la que el Gobierno de España cubre el 20% de las inversiones, "
        "mientras que el 80% lo cubre capital privado."
    )

    st.header("¿De dónde se obtiene la información?")
    st.markdown(
        "La política de total transparencia de la corporación, sellada y garantizada por organismos públicos, se "
        "manifiesta a través de la creación de un API donde los consumidores y diversos usuarios pueden consultar "
        "libremente los datos que Redeia genera a tiempo real. "
        "[Para más consultas, visite el API de datos de Redeia.](https://www.ree.es/es/datos/apidatos)"
    )

    st.header("Objetivos")
    st.markdown(
        "Con los datos obtenidos se pretende realizar un análisis integral de la corporación enfocándose en la "
        "estructura de negocio de esta empresa desde cuatro pilares fundamentales:"
        "\n- Generación de energía"
        "\n- Balance estructural energético"
        "\n- Demanda energética del mercado español"
        "\n- Transacciones Internacionales"
        "\n\nComo punto clave, este estudio se centra en la sostenibilidad, con especial atención al precio y al "
        "impacto de la huella de carbono en función del crecimiento de la demanda y la generación de energía."
    )

    # Menú de selección en el sidebar
    choices = ["Vista general", "Vista específica", "Mapa Coroplético de Intercambio Energético"]

    choice = st.sidebar.selectbox(label="Menú", options=choices, index=0)

    if choice == "Vista general":
        # Sección Demanda del mercado
        st.subheader("Demanda del mercado")
        df_demanda = load_data("SELECT fecha, valor_demanda_MW FROM demanda_energia")

        # Filtros en el Sidebar para Demanda
        with st.sidebar.expander("¡Filtros Personalizados!"):
            st.markdown("#### Filtro por Fecha")
            start_date_demanda = st.date_input(
                "Fecha de inicio", value=df_demanda['fecha'].min(),
                min_value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max()
            )
            end_date_demanda = st.date_input(
                "Fecha de fin", value=df_demanda['fecha'].max(),
                min_value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max()
            )

        # Filtro de periodo predefinido para Demanda (encima de la visualización)
        period_demanda = st.selectbox(
            "Seleccionar periodo",
            ["Personalizado", "Última semana", "Último mes", "Último año", "Histórico"]
        )

        if period_demanda == "Personalizado":
            filtered_df_demanda = date_filter(
                df_demanda, period_demanda, start_date_demanda, end_date_demanda
            )
        else:
            filtered_df_demanda = date_filter(df_demanda, period_demanda)

        # Gráfico de línea de Demanda
        fig1 = px.line(filtered_df_demanda, x='fecha', y='valor_demanda_MW', title="Demanda Energética en MW")
        st.plotly_chart(fig1)

        # Gráfico de barras mensual de demanda promedio
        filtered_df_demanda['mes'] = filtered_df_demanda['fecha'].dt.to_period('M').dt.to_timestamp()
        demanda_mensual = filtered_df_demanda.groupby('mes')['valor_demanda_MW'].mean().reset_index()
        fig_demanda_mensual = px.bar(demanda_mensual, x='mes', y='valor_demanda_MW',
                                     title="Demanda Promedio Mensual en MW")
        st.plotly_chart(fig_demanda_mensual)

        # Sección Balance Energético
        st.subheader("Balance energético")
        df_balance = load_data("SELECT fecha, valor_balance_GW, energia FROM balance_energia")

        # Filtros en el Sidebar para Balance
        with st.sidebar.expander("Filtros para Balance Energético"):
            st.markdown("#### Filtro por Tipo de Energía")
            energia_type = st.multiselect(
                "Tipo de Energía (Balance)", options=df_balance['energia'].unique(),
                default=df_balance['energia'].unique()
            )

        filtered_df_balance = df_balance[df_balance['energia'].isin(energia_type)]
        filtered_df_balance = date_filter(filtered_df_balance, period_demanda)

        # Visualización de Balance Energético
        fig2 = px.line(filtered_df_balance, x='fecha', y='valor_balance_GW', color='energia',
                       title="Balance Energético en GW")
        st.plotly_chart(fig2)

        # Gráfico de área apilado para balance energético
        fig_balance_energia = px.area(filtered_df_balance, x='fecha', y='valor_balance_GW', color='energia',
                                      title="Balance Energético por Tipo de Energía en GW")
        st.plotly_chart(fig_balance_energia)

        # Sección Transacciones Energéticas
        st.subheader("Transacciones energéticas")
        df_exchanges = load_data("SELECT fecha, valor_GW, tipo_transaccion, pais FROM transacciones_energia")

        # Filtros en el Sidebar para Transacciones
        with st.sidebar.expander("Filtros para Transacciones Energéticas"):
            st.markdown("#### Filtro por País")
            pais_filter = st.multiselect("País", options=df_exchanges['pais'].unique(), default=df_exchanges['pais'].unique())
            st.markdown("#### Filtro por Tipo de Transacción")
            transaccion_type = st.multiselect("Tipo de Transacción", options=df_exchanges['tipo_transaccion'].unique(), default=df_exchanges['tipo_transaccion'].unique())

        filtered_df_exchanges = df_exchanges[(df_exchanges['pais'].isin(pais_filter)) & (df_exchanges['tipo_transaccion'].isin(transaccion_type))]
        filtered_df_exchanges = date_filter(filtered_df_exchanges, period_demanda)

        # Gráfico de flujo de transacciones energéticas por país
        transacciones_pais = filtered_df_exchanges.groupby(['pais', 'tipo_transaccion'])['valor_GW'].sum().reset_index()
        fig_transacciones = px.bar(transacciones_pais, x='pais', y='valor_GW', color='tipo_transaccion',
                                   title="Transacciones Energéticas por País en GW", barmode='group')
        st.plotly_chart(fig_transacciones)

        # Sección Generación Energética
        st.subheader("Generación energética")
        df_generation = load_data("SELECT fecha, valor_generacion_GW, energia FROM generacion_energia")

        # Filtros en el Sidebar para Generación
        with st.sidebar.expander("Filtros para Generación Energética"):
            st.markdown("#### Filtro por Tipo de Energía")
            energia_filter = st.multiselect("Tipo de Energía (Generación)", options=df_generation['energia'].unique(), default=df_generation['energia'].unique())

        filtered_df_generation = df_generation[df_generation['energia'].isin(energia_filter)]

    #####
        # Filtro para la Generación total
        filtered_df_generation = filtered_df_generation[filtered_df_generation['energia'] != 'Generación total']

    #########

        filtered_df_generation = date_filter(filtered_df_generation, period_demanda)

        # Gráfico de líneas para generación de energía
        fig_generacion_energia = px.line(filtered_df_generation, x='fecha', y='valor_generacion_GW', color='energia',
                                         title="Generación de Energía por Tipo en GW")
        st.plotly_chart(fig_generacion_energia)

        # Visualización de Generación Energética
        fig4 = px.histogram(filtered_df_generation, x='fecha', y='valor_generacion_GW', color='energia',
                            title="Generación en GW")
        st.plotly_chart(fig4)

        # Distribución de Generación Energética
        fig5 = px.pie(
            filtered_df_generation,
            values='valor_generacion_GW',
            names='energia',
            title="Distribución de Generación Energética",
            width=900,
            height=700
        )
        st.plotly_chart(fig5)

    elif choice == "Mapa Coroplético de Intercambio Energético":
        mostrar_mapa_coro()

if __name__ == "__main__":
    main()
