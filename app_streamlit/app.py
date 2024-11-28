import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime
from functions.sql_function import extract_data
from functions.processing_predictions_functions import preprocess_data, escalador, train_test_split_data, modelo_neuronal_rnn, modelo_neuronal_lstm, predict_7_days_rnn, predict_7_days_lstm, modelo_neuronal_gru, predict_7_days_gru, model_prophet, visual_loss_rnn, visual_loss_lstm, visual_loss_gru
from functions.vocabulary import obtener_vocabulario
from streamlit_lottie import st_lottie
import json
import pydeck as pdk
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="PFB: Red Eléctrica Española",
    page_icon="🔋",
    layout="wide")

# Función para cargar datos con caché
@st.cache_data
def load_data(query):
    return extract_data(query)

######################

def load_exchanges_data():
    query = """
    SELECT pais, tipo_transaccion, SUM(valor_MW) AS valor_MW
    FROM transacciones_energia
    GROUP BY pais, tipo_transaccion
    """
    return extract_data(query)

def mostrar_mapa_coro():
    st.title("Intercambio de Energía de Redeia S.A. con Otros Países")

    df_exchanges = load_exchanges_data()
    st.write("Datos Cargados:", df_exchanges)


    tipo_transaccion = st.selectbox("Seleccionar tipo de transacción", options=["Importación", "Exportación"])

    filtered_df = df_exchanges[df_exchanges['tipo_transaccion'] == tipo_transaccion]
    country_mapping = {
        'Francia': 'France',
        'Portugal': 'Portugal',
        'Marruecos': 'Morocco',
        'Andorra': 'Andorra',}

    st.write('Datos Filtrados:', filtered_df)

    # Filtrar los datos por tipo de transacción seleccionado

    filtered_df['pais'] = filtered_df['pais'].replace(country_mapping)

    if not filtered_df.empty:
        color_scale = px.colors.sequential.YlGnBu
        max_value = filtered_df['valor_MW'].max()

        fig = px.choropleth(
            filtered_df,
            locations="pais",
            locationmode="country names",
            color="valor_MW",
            projection="mercator",
            color_continuous_scale=color_scale,
            range_color = (0, max_value),
            title=f"Intercambio de energía ({tipo_transaccion}) de España con otros países",
            labels={'valor_MW': 'MWh'},
            width=1900,
            height=1600,)

        fig.update_geos(
            showcoastlines=True, coastlinecolor='Black',
            showland=True, landcolor='white',
            showocean=True, oceancolor='lightblue',
            projection_type='natural earth',
            lonaxis_range=[-25, 55],
            lataxis_range=[-35, 70],)

        fig.update_layout(
            margin={'r':0,'t':50,'l':0,'b':0},
            title_x=0.5,
            coloraxis_colorbar=dict(
                title='Mwh',
                tickvals=[0, max_value / 2, max_value],
                ticks='outside'))
        for index, row in filtered_df.iterrows():
            if row['valor_MW'] == max_value or row['valor_MW'] == filtered_df['valor_MW'].min():
                fig.add_annotation(
                    x=row['pais'],
                    y=row['valor_MW'],
                    text=f'{row['pais']}: {row['valor_MW']:,} MhW',
                    showarrow=False,
                    yshift=10)

        st.plotly_chart(fig)
    else:
        st.warning("No hay datos para mostrar en el mapa con la selección actual.")

#######################

# Función para aplicar filtro de fecha con periodos predefinidos
def date_filter(df, period, start_date=None, end_date=None):
    df['fecha'] = pd.to_datetime(df['fecha'])
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
            Esta aplicación permite realizar un análisis interactivo y detallado de los datos energéticos de la red eléctrica de España, abarcando varios aspectos fundamentales del sistema energético nacional. A continuación, se describen las principales secciones y funcionalidades para que puedas navegar y aprovechar al máximo la aplicación.

            **Secciones principales**:
            - 🔌 **Demanda del Mercado**: Visualización y análisis de la evolución de la demanda energética en MW. Podrás observar tendencias históricas y realizar comparativas entre diferentes periodos.
            - ⚡ **Balance Energético**: Información sobre el balance de distintos tipos de energía, incluyendo energía renovable y no renovable. Aquí puedes explorar cómo se genera y consume la energía en distintos momentos.
            - ✨ **Estructura de Generación**: Análisis detallado de la generación energética, desglosada por las diferentes tecnologías utilizadas por Redeia S.A., como energía eólica, solar, hidroeléctrica, entre otras.
            - 🌍 **Transacciones Energéticas**: Análisis de las transacciones de energía entre España y otros países. Podrás visualizar las importaciones y exportaciones de energía, así como los principales socios comerciales de España en este ámbito.
            - 📊 **Emisiones de CO2**: Monitorización de las emisiones de CO2 asociadas a la generación de energía, desglosada por tipo de fuente. Esta sección permite evaluar el impacto ambiental del consumo energético y los avances hacia la sostenibilidad.
            - 📖 **Vocabulario Energético**: Glosario interactivo de términos clave en el ámbito energético. Podrás seleccionar una letra para explorar definiciones y aclarar conceptos importantes.

            **Filtros disponibles**:
            - **Filtro de Fechas**: Puedes filtrar los datos por periodos específicos como "Última semana", "Último mes", "Último año" o realizar una selección personalizada de fecha para un análisis más detallado. Este filtro está disponible en todas las secciones y permite ajustar el rango temporal de los gráficos y análisis presentados.
            - **Filtros Específicos por Sección**: Además del filtro de fechas general, cada sección cuenta con filtros específicos para ajustar la visualización según los parámetros de interés (por ejemplo, tipo de energía, país, tipo de transacción, etc.).

            **Cómo Navegar la Aplicación**:
            - Utiliza el menú lateral para seleccionar la sección que deseas explorar.
            - Aplica los filtros personalizados en el sidebar para refinar los resultados mostrados en los gráficos.
            - Haz clic en "Mostrar Ayuda" para acceder a esta guía en cualquier momento.

            Esta herramienta está diseñada para ofrecer una visión integral del sector energético español, permitiendo a los usuarios realizar análisis personalizados y obtener información útil sobre la producción, consumo, y sostenibilidad energética en España.
        """)

# Botón en el sidebar para mostrar la ayuda
if st.sidebar.button("ℹ️ Mostrar Ayuda"):
    show_help()

# Función principal
def main():

    # Menú de selección en el sidebar
    choices = ['Página Principal', "Vista general", "Vista específica", "Mapa Coroplético de Intercambio Energético", '¡Costes promedios!']

    choice = st.sidebar.selectbox(label="Menú", options=choices, index=0)

    if choice == "Vista general":

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
            "mientras que el 80% lo cubre capital privado.")

        st.header("¿De dónde se obtiene la información?")
        st.markdown(
            "La política de total transparencia de la corporación, sellada y garantizada por organismos públicos, se "
            "manifiesta a través de la creación de un API donde los consumidores y diversos usuarios pueden consultar "
            "libremente los datos que Redeia genera a tiempo real. "
            "[Para más consultas, visite el API de datos de Redeia.](https://www.ree.es/es/datos/apidatos)")

        st.header("Objetivos")
        st.markdown(
            "Con los datos obtenidos se pretende realizar un análisis integral de la corporación enfocándose en la "
            "estructura de negocio de esta empresa desde cuatro pilares fundamentales:"
            "\n- Generación de energía"
            "\n- Balance estructural energético"
            "\n- Demanda energética del mercado español"
            "\n- Transacciones Internacionales"
            "\n\nComo punto clave, este estudio se centra en la sostenibilidad, con especial atención al precio y al "
            "impacto de la huella de carbono en función del crecimiento de la demanda y la generación de energía.")

        # Llamada general de datos

        df_demanda = load_data("SELECT fecha, valor_demanda_MW FROM demanda_energia")
        df_demanda['fecha'] = pd.to_datetime(df_demanda['fecha'])
        df_demanda['year'] = df_demanda['fecha'].dt.year
        df_balance = load_data("SELECT fecha, valor_balance_MW, energia FROM balance_energia")
        df_balance['fecha'] = pd.to_datetime(df_balance['fecha'])
        df_balance['year'] =df_balance['fecha'].dt.year
        df_generation = load_data("SELECT fecha, valor_generacion_MW, energia, tipo_tecnología FROM generacion_energia")
        df_generation['fecha'] = pd.to_datetime(df_generation['fecha'])
        df_generation['year'] = df_generation['fecha'].dt.year
        df_exchanges = load_data("SELECT fecha, valor_MW, tipo_transaccion, pais FROM transacciones_energia")
        df_exchanges['fecha'] = pd.to_datetime(df_exchanges['fecha'])
        df_exchanges['year']=df_exchanges['fecha'].dt.year
        df_co2 = load_data("SELECT fecha, valor, energia FROM emisiones_co2")
        df_co2['fecha']=pd.to_datetime(df_co2['fecha'])
        df_co2['year']=df_co2['fecha'].dt.year

        # Filtros generales personalizados en el Sidebar

        with st.sidebar.expander("Filtrado por fecha"):
            st.markdown("#### Filtro por Fecha")

            # Selección del rango de fechas usando la tabla de demanda como referencia
            start_date_demanda = st.date_input(
                "Fecha de inicio", value=df_demanda['fecha'].min(),
                min_value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max())
            end_date_demanda = st.date_input(
                "Fecha de fin", value=df_demanda['fecha'].max(),
                min_value=df_demanda['fecha'].min(), max_value=df_demanda['fecha'].max())

            start_date_demanda = datetime.combine(start_date_demanda, datetime.min.time())
            end_date_demanda = datetime.combine(end_date_demanda, datetime.min.time())

            # Aplicar el filtro de fechas a todas las tablas
            df_demanda = df_demanda[(df_demanda['fecha'] >= start_date_demanda) & (df_demanda['fecha'] <= end_date_demanda)]
            df_balance = df_balance[(df_balance['fecha'] >= start_date_demanda) & (df_balance['fecha'] <= end_date_demanda)]
            df_exchanges = df_exchanges[(df_exchanges['fecha'] >= start_date_demanda) & (df_exchanges['fecha'] <= end_date_demanda)]
            df_generation = df_generation[(df_generation['fecha'] >= start_date_demanda) & (df_generation['fecha'] <= end_date_demanda)]
            df_co2 = df_co2[(df_co2['fecha'] >= start_date_demanda) & (df_co2['fecha'] <= end_date_demanda)]

        # SECCIÓN DE DEMANDA
        st.subheader("Demanda del mercado")
        # Filtro de periodo predefinido para Demanda (encima de la visualización)
        period_demanda = st.selectbox(
            "Seleccionar periodo",
            ["Personalizado", "Última semana", "Último mes", "Último año", "Histórico"])

        if period_demanda == "Personalizado":
            filtered_df_demanda = date_filter(
                df_demanda, period_demanda, start_date_demanda, end_date_demanda)
        else:
            filtered_df_demanda = date_filter(df_demanda, period_demanda)

        # Gráfico de línea de Demanda
        fig1 = px.line(filtered_df_demanda, x='fecha', y='valor_demanda_MW', title="Demanda Energética en MW")
        st.plotly_chart(fig1)

        st.markdown("""
            **Evolución de la Demanda Energética en España (2011-2024)**

            La gráfica muestra la **evolución de la demanda energética** en España desde 2011 hasta 2024.

            Se observa una marcada **reducción** en la demanda durante el periodo de **confinamiento** por la pandemia de **COVID-19**, comenzando el 14 de marzo de 2020. El punto más bajo ocurre en esta fase, y la **recuperación** gradual inicia en junio del mismo año con la **reapertura económica** y la flexibilización de las restricciones.

            Aunque podría esperarse un aumento en la demanda debido al incremento del **consumo doméstico**, esta disminución refleja el impacto del cierre temporal de muchas actividades industriales y comerciales, que son los principales **consumidores de energía**.

            Las variaciones en la demanda a lo largo del año responden a **patrones diarios**, **semanales** y **estacionales**: el consumo es mayor durante el **día** que en la **noche**, más alto entre semana que los fines de semana, y tiende a incrementarse en **invierno** y en **verano**, especialmente durante los **picos de frío** y **calor**.
        """)

        # Gráfico de barras mensual de demanda promedio
        filtered_df_demanda['mes'] = filtered_df_demanda['fecha'].dt.to_period('M').dt.to_timestamp()
        demanda_mensual = filtered_df_demanda.groupby('mes')['valor_demanda_MW'].mean().reset_index()
        fig_demanda_mensual = px.bar(demanda_mensual, x='mes', y='valor_demanda_MW',
                                     title="Demanda Promedio Mensual en MW")
        st.plotly_chart(fig_demanda_mensual)
        st.markdown("""
            **Demanda Promedio Mensual de Energía en MW (2011-2024)**

            La gráfica muestra la **demanda promedio mensual de energía** en MW durante un período prolongado, cubriendo aproximadamente desde 2011 hasta 2024. 

            A lo largo del tiempo, la demanda promedio mensual parece mantenerse relativamente estable, aunque con algunas fluctuaciones. Se observan ciertos **picos de demanda** en distintos años, especialmente alrededor de **2012** y **2017-2018**, que podrían estar relacionados con **factores estacionales**, **cambios en el consumo**, o **eventos específicos** que incrementaron la demanda.

            Asimismo, hay momentos con **disminuciones**, que podrían deberse a **condiciones económicas**, **climáticas** o cambios en la **eficiencia energética**. Aunque el gráfico no especifica los meses exactos, es posible que haya **patrones de demanda estacionales**, como aumentos durante **periodos de clima extremo**, en los que se usa más energía para **calefacción** o **refrigeración**.

            En los últimos años (aproximadamente desde **2023**), parece haber una leve **disminución** en la demanda promedio mensual, lo cual podría indicar un cambio en el **consumo de energía**, posiblemente debido a **iniciativas de eficiencia energética**, cambios en el **comportamiento de consumo**, un aumento de los **precios de la energía** o una **desaceleración económica**.
        """)

        # Filtros en el Sidebar para la comparación de años de Pablo

        st.sidebar.subheader("Comparación de Años")
        available_years = df_demanda['year'].unique()
        selected_years = st.sidebar.multiselect(
            "Selecciona los años a comparar",
            options=sorted(available_years),
            default=[2022, 2023])

        if selected_years:
            df_demanda_comparador = df_demanda[df_demanda['year'].isin(selected_years)].copy()

            # Ajustar la fecha para que todos los años tengan el mismo año de referencia
            df_demanda_comparador['fecha_ajustada'] = df_demanda_comparador['fecha'].apply(
                lambda x: x.replace(year=2020))

            # Crear la gráfica de comparación con la fecha ajustada
            fig_comparador = px.line(
                df_demanda_comparador, x='fecha_ajustada', y='valor_demanda_MW', color='year',
                title=f"Comparador de Demanda en MW, años {', '.join(map(str, selected_years))}")

            # Calcular métricas para líneas de referencia
            metricas = df_demanda_comparador.groupby('year')['valor_demanda_MW'].agg(['mean', 'median', 'min', 'max'])

            # Añadir líneas de referencia a la gráfica
            for year, row in metricas.iterrows():
                fig_comparador.add_hline(
                    y=row['mean'], line_color='yellow', line_dash="dash",
                    annotation_text=f"Media {year}", annotation_position="top left")
                fig_comparador.add_hline(
                    y=row['median'], line_color='blue', line_dash="dot",
                    annotation_text=f"Mediana {year}", annotation_position="top left")
                fig_comparador.add_hline(
                    y=row['min'], line_color='red', line_dash="dot",
                    annotation_text=f"Mínimo {year}", annotation_position="top left")
                fig_comparador.add_hline(
                    y=row['max'], line_color='green', line_dash="dot",
                    annotation_text=f"Máximo {year}", annotation_position="top left")

            # Mostrar la gráfica comparativa
            st.plotly_chart(fig_comparador)
        st.markdown("""
            **Comparación de Demanda Anual**

            Este gráfico dinámico permite comparar la **demanda anual** de manera visual e intuitiva. A través de él, podemos observar las diferencias en la demanda entre los distintos años registrados en nuestra base de datos, con indicadores claros del **máximo**, **mediana**, **media** y **mínimo** de demanda para cada año.
        """)

        ################ BALANCE

        # Sección Balance Energético

        st.subheader("Balance energético")

        # Filtros en el Sidebar para Balance
        with st.sidebar.expander("Filtros para Balance Energético"):
            st.markdown("#### Filtro por Tipo de Energía")
            energia_type = st.multiselect(
                "Tipo de Energía (Balance)", options=df_balance['energia'].unique(),
                default=df_balance['energia'].unique())

        filtered_df_balance = df_balance[df_balance['energia'].isin(energia_type)]
        filtered_df_balance = date_filter(filtered_df_balance, period_demanda)

        # Visualización de Balance Energético
        fig2 = px.line(filtered_df_balance[filtered_df_balance['energia']=='Generación renovable'], x='fecha', y='valor_balance_MW', color='energia',
                       title="Balance Generación Energías Renovables en MW")
        st.plotly_chart(fig2)

        st.markdown("""
            **Balance de Generación de Energías Renovables en GW (2011-2024)**

            La gráfica muestra el **balance de generación de energías renovables** en GW a lo largo del tiempo, desde aproximadamente 2011 hasta 2024.

            A lo largo del período, se observan fuertes **fluctuaciones** en la generación de energía renovable, lo cual es característico de este tipo de fuentes debido a su dependencia de **condiciones naturales** como el **viento**, la **luz solar** y la **lluvia** para la energía **hidroeléctrica**. La generación no es constante y muestra **picos** y **caídas** de forma regular.

            Aunque la **variabilidad** es alta, se nota una tendencia general al alza en la **capacidad de generación renovable**. Desde 2020 en adelante, parece que los **picos máximos** son más altos que en años anteriores, lo que podría indicar un aumento en la **capacidad instalada** o una mayor **integración de energías renovables** en el sistema eléctrico.

            Es probable que existan **patrones estacionales** en la generación, ya que el gráfico muestra ciclos repetitivos. Esto puede deberse a estaciones del año donde ciertas fuentes renovables, como la **eólica** y la **hidroeléctrica**, tienen una mayor o menor disponibilidad.

            En los últimos años (desde 2022), parece que la generación ha alcanzado **picos más altos** y también presenta una mayor **estabilidad** en algunos períodos. Esto puede estar relacionado con **avances tecnológicos** o mejoras en la **eficiencia de generación renovable**, así como un mejor manejo de la **variabilidad** a través de **almacenamiento de energía** o estrategias de **gestión de la red**.

            La gráfica muestra una dependencia significativa de **factores naturales** que influyen en la generación renovable, pero con una tendencia general positiva en cuanto a la **capacidad** y **contribución de las energías renovables** en el sistema eléctrico. Esto sugiere que se están logrando avances en la **integración de estas energías**, aunque aún existen desafíos en la gestión de su **variabilidad**.
        """)

        # Saldo de Balance

        # Filtrado del df
        df_generation = df_generation[(df_generation['energia'] == 'Generación total') | (df_generation['tipo_tecnología'] == 'Generación total')]
        df_generation = df_generation.drop(columns=['energia', 'tipo_tecnología'])
        df_generation = df_generation.reset_index(drop=True)

        # Creación de un nuevo df
        df_saldo_balance = pd.merge(df_demanda, df_generation, on='fecha', how='inner')
        df_saldo_balance = df_saldo_balance[['fecha', 'valor_demanda_MW', 'valor_generacion_MW']]
        df_saldo_balance['balance'] = df_saldo_balance['valor_generacion_MW'] - df_saldo_balance['valor_demanda_MW']
        df_saldo_balance=date_filter(df_saldo_balance, period_demanda)

        # Visualización de generación y demanda
        fig_demanda_generacion = px.line(df_saldo_balance,
                      x='fecha',
                      y=['valor_demanda_MW', 'valor_generacion_MW'],
                      labels={'fecha': 'Fecha', 'value': 'Valores (MW)', 'variable': 'Categoría'},
                      title='Balance entre demanda y generación')

        #Visualización del saldo restante entre generación y demanda
        fig_saldo = px.line(df_saldo_balance,
                       x='fecha',
                       y='balance',
                       labels={'fecha': 'Fecha', 'value': 'Valores (MW)'},
                       title='Balance energético')

        # Mostrar la gráfica
        st.plotly_chart(fig_demanda_generacion)
        st.plotly_chart(fig_saldo)

        # Gráfico de área apilado para balance energético
        fig_balance_energia = px.area(filtered_df_balance[~(filtered_df_balance['energia']=='Generación renovable')], x='fecha', y='valor_balance_MW', color='energia',
                                      title="Balance Energético por Tipo de Energía en MW")
        st.plotly_chart(fig_balance_energia)

        st.markdown("""
            **Evolución de la Generación de Energía Eléctrica Renovable (2011-2024)**

            El gráfico que se presenta muestra la **evolución temporal de la generación de energía eléctrica** a partir de diversas fuentes renovables entre 2011 y 2024. 

            Cada línea representa una fuente específica (**eólica**, **hidráulica**, **solar fotovoltaica**, etc.) y su altura en un punto dado indica la cantidad de **energía generada** en ese momento.

            Revela una transformación profunda en el **sector energético**, con un claro protagonismo de las **energías renovables**. El auge de las **energías renovables** abre nuevas oportunidades en el sector de los **servicios energéticos**, como la **gestión de la energía**, la **eficiencia energética** y la **comercialización de electricidad**.

            Este hecho ha incentivado la construcción de **parques eólicos**, **plantas solares** y otras **infraestructuras** relacionadas con las **energías renovables**, especialmente a partir del año 2020 fruto de una fuerte **transición energética** que cumple con los objetivos de la **agenda climática de Horizon 2020 y Horizon 2030**.
        """)

        # Sección Transacciones Energéticas
        st.subheader("Transacciones energéticas")

        # Filtros en el Sidebar para Transacciones
        with st.sidebar.expander("Filtros para Transacciones Energéticas"):
            st.markdown("#### Filtro por País")
            pais_filter = st.multiselect("País", options=df_exchanges['pais'].unique(), default=df_exchanges['pais'].unique())
            st.markdown("#### Filtro por Tipo de Transacción")
            transaccion_type = st.multiselect("Tipo de Transacción", options=df_exchanges['tipo_transaccion'].unique(), default=df_exchanges['tipo_transaccion'].unique())

        filtered_df_exchanges = df_exchanges[(df_exchanges['pais'].isin(pais_filter)) & (df_exchanges['tipo_transaccion'].isin(transaccion_type))]
        filtered_df_exchanges = date_filter(filtered_df_exchanges, period_demanda)

        # Gráfico de evolución de transacciones energéticas general
        fig_evolucion_transacciones=px.histogram(filtered_df_exchanges[~(filtered_df_exchanges['tipo_transaccion']=='saldo')],
                                                 x='fecha', y='valor_MW', color='tipo_transaccion',
                                                 title="Evolución General de Transacciones Energéticas en MW")
        st.plotly_chart(fig_evolucion_transacciones)
        st.markdown("""
            La **evolución de las transacciones comerciales** entre **Redeia S.A.** y sus socios internacionales muestra una notable **reducción** en la dependencia de las **importaciones** hacia el año **2022**. 

            Este cambio responde, en gran medida, al impulso en la **generación de energías renovables**, especialmente en el sector **solar fotovoltaico**, que ha permitido a España aumentar gradualmente su capacidad de **exportación**. 

            La **transición energética** y el crecimiento sostenido del sector **renovable** han favorecido un modelo más **autosuficiente**, donde las importaciones se utilizan de manera estratégica para cubrir **picos de demanda**, pero ya no constituyen el eje central del abastecimiento.

            Además, una ligera **reducción en el consumo energético** ha permitido un mayor margen para las **exportaciones**, consolidando a **España** como un **exportador neto** en el contexto europeo.

            Así, la combinación de una menor **dependencia de combustibles fósiles** y el incremento de la **capacidad renovable** posiciona a **Redeia S.A.** en una posición de **liderazgo** en el **comercio energético**, apuntalando el camino hacia un sistema más **sostenible** y **eficiente**.
        """)

        # Gráfico de evolución de transacciones energéticas por país

        fig_evolucion_transacciones_pais = px.histogram(
            filtered_df_exchanges[~(filtered_df_exchanges['tipo_transaccion'] == 'saldo')],
            x='fecha', y='valor_MW', color='pais',
            title="Evolución por país de Transacciones Energéticas en MW")
        st.plotly_chart(fig_evolucion_transacciones_pais)
        st.markdown("""
            Esta gráfica muestra la **evolución histórica** de las **importaciones y exportaciones de energía** de España, desglosada por **países clave** (**Francia**, **Portugal**, **Marruecos** y **Andorra**). 

            Los valores **positivos** representan **exportaciones**, mientras que los valores **negativos** corresponden a **importaciones**. Al interactuar con los filtros, se observa que **Francia** ha sido tradicionalmente el principal proveedor energético de España. 

            Sin embargo, a partir de **2020-2021**, se nota una tendencia hacia un aumento de las **exportaciones**, lo que podría estar vinculado al crecimiento en la **producción de energía renovable** en el país. Esta **transición** resalta el cambio de España de **importador a exportador energético**, reflejando una mayor **autosuficiencia** y un compromiso con **fuentes de energía sostenibles**.
        """)

        # Gráfico de flujo de transacciones energéticas por país
        transacciones_pais = filtered_df_exchanges.groupby(['pais', 'tipo_transaccion'])['valor_MW'].sum().reset_index()
        fig_transacciones = px.bar(transacciones_pais, x='pais', y='valor_MW', color='tipo_transaccion',
                                   title="Transacciones Energéticas por País en MW", barmode='group')
        st.plotly_chart(fig_transacciones)

        # Sección Generación Energética
        st.subheader("Generación energética")


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
        fig_generacion_energia = px.area(filtered_df_generation, x='fecha', y='valor_generacion_MW', color='energia',
                                         title="Estructura de generación energética en MW")
        st.plotly_chart(fig_generacion_energia)

        # Visualización de Generación Energética
        fig4 = px.histogram(filtered_df_generation, x='fecha', y='valor_generacion_MW', color='energia',
                            title="Generación en MW")
        st.plotly_chart(fig4)
        st.markdown("""
            Este gráfico ilustra la **evolución de la generación de energía** en **Redeia S.A.**, mostrando tanto **fuentes renovables** como **no renovables** entre 2012 y 2024. 

            En tan solo 12 años, se observan dos fenómenos clave que reflejan una **transición energética** en España. En primer lugar, destaca la **reducción de la dependencia de los combustibles fósiles**, especialmente el **carbón**, que muestra una caída drástica en 2019 como fuente principal de energía. Este cambio es un paso importante hacia la **descarbonización** del sector energético.

            En segundo lugar, se observa un notable **crecimiento en las energías renovables**, con la **energía eólica** y la **solar fotovoltaica** liderando este cambio, especialmente a partir de 2020. También destacan el incremento de la **energía solar térmica** y la **generación hidroeléctrica** mediante **turbinación de bombeo**, cuyo crecimiento ha sido evidente desde 2012.

            Respecto a las **energías no renovables**, la **energía nuclear** ha mantenido una presencia constante como fuente complementaria, necesaria para cubrir la **demanda energética** actual. Sin embargo, se observa una tendencia general a la **reducción** de otras fuentes no renovables, como los **motores diésel**, **turbinas de gas**, **turbinas de vapor**, **cogeneración** (energía eléctrica y térmica) y **residuos no renovables**.

            Esta **transición hacia fuentes de energía más limpias** subraya el compromiso de **Redeia S.A.** con la **sostenibilidad** y la adaptación al cambio en el panorama energético.
        """)

        # Distribución de Generación Energética
        fig5 = px.pie(
            filtered_df_generation,
            values='valor_generacion_MW',
            names='energia',
            title="Distribución de Generación Energética",
            width=900,
            height=700)
        st.plotly_chart(fig5)
        st.markdown("""
            La **estructura de generación energética** de esta empresa española se apoya en cinco fuentes principales. 

            La **energía nuclear** constituye el **20.6%** del total, subrayando su importancia como fuente constante en el **mix energético**. La **energía eólica** ocupa el segundo lugar con un **19.9%**, reflejando el impulso hacia **fuentes limpias**. La **generación mediante ciclo combinado** representa un **15.1%**, seguida de la **energía hidráulica** con un **10.9%**, que continúa siendo una fuente relevante.

            Aunque el **carbón**, con un **10.5%**, aún forma parte de la producción, se encuentra en clara disminución. Esta distribución muestra la **transición hacia un modelo energético más sostenible**, con un incremento notable en **fuentes renovables** y una **reducción gradual de los combustibles fósiles**.
        """)

        # Seccion de CO2

        st.subheader("Emisiones de CO2")

        #Filtros

        with st.sidebar.expander("Filtros para Emisión CO2"):
            st.markdown("#### Filtro por Tipo de Energía")
            energia_co2_filter = st.multiselect("Tipo de Energía (Generación)", options=df_co2['energia'].unique(), default=df_co2['energia'].unique())

        filtered_df_co2 = df_co2[df_co2['energia'].isin(energia_co2_filter)]

        filtered_df_co2 = filtered_df_co2[~(filtered_df_co2['energia'].isin(['tCO2 eq./MWh', 'Total tCO2 eq.']))]

        filtered_df_co2 = date_filter(filtered_df_co2, period_demanda)

        filtered_df_co2_grouped = filtered_df_co2.groupby('fecha', as_index=False)['valor'].sum()

        #Gráfico de la evolución de las emisiones de co2

        fig_co2_evolucion=px.line(filtered_df_co2_grouped, x='fecha', y='valor', title="Evolución de las emisiones CO2")
        st.plotly_chart(fig_co2_evolucion)
        st.markdown("""
            La **evolución de las emisiones de CO2** desde 2010 hasta 2024 muestra una tendencia marcada por fluctuaciones que reflejan la volatilidad inherente a los datos y la **estacionalidad de las emisiones**, más frecuentes en **invierno** y **verano** debido al mayor **consumo** y **demanda estacional**. 

            Esta serie de **picos y valles** sugiere períodos de incrementos y disminuciones abruptas en las emisiones, relacionados principalmente con la **estacionalidad** y la constante relación entre **generación** y **demanda de energía**.

            A partir de enero de **2019**, se observa una **disminución en las emisiones** que no está relacionada directamente con la **pandemia de la COVID-19**, salvo durante el período de **confinamiento**, en el que se registraron bajas emisiones. Esta **reducción** es atribuible a la efectividad de las **normativas europeas** impulsadas por la **Comisión Europea**, como la norma **EURO** para transportes, y el **Plan Nacional de Calidad del Aire** (2017-2019), que implementa diversas medidas para reducir las emisiones en varios sectores, especialmente el **industrial**.

            Además, se alinean con los **objetivos climáticos** establecidos en las agendas **HORIZON 2020 y 2030**.
        """)

        #Gráfico por generación de las emisiones de co2

        fig_co2_energia=px.histogram(filtered_df_co2, x='fecha', y='valor', color='energia', title="Emisiones de CO2 según su generación")
        st.plotly_chart(fig_co2_energia)
        st.markdown("""
            La **evolución de las emisiones de CO2**, desglosadas por **tipo de energía**, muestra una **tendencia a la baja**, especialmente a partir de **2019**, gracias a la **reducción en el uso del carbón**. Este cambio refleja una **transición clara hacia fuentes de energía más limpias y sostenibles**, alineadas con los esfuerzos por mitigar el impacto ambiental. 

            Sin embargo, a pesar de estos avances, el **ciclo combinado** sigue siendo la fuente de energía con mayor impacto en términos de emisiones, dominando ampliamente el espacio de las emisiones frente a otras fuentes como la **cogeneración**, las **turbinas de gas**, las **turbinas de vapor**, el **diésel** y el **fuel-gas**. 

            Esto subraya la necesidad de seguir impulsando la **eficiencia energética** y la **transición hacia energías renovables**, para reducir aún más las emisiones de CO2 y avanzar hacia un **modelo energético verdaderamente sostenible**.
        """)

        #Filtro personalizado lateral

        # Glosario
        st.header('Vocabulario energético')

        # Lista de letras
        letras = ['C', 'E', 'F', 'H', 'M', 'N', 'R', 'S', 'T']

        # Multiselect para que el usuario seleccione múltiples letras
        letras_seleccionadas = st.multiselect('Selecciona una o más letras', letras)

        # Si se han seleccionado letras, mostramos sus definiciones
        if letras_seleccionadas:
            for letra in letras_seleccionadas:
                st.write(f'**{letra}:**')
                resultados = obtener_vocabulario(letra)
                if isinstance(resultados, list):
                    for definicion in resultados:
                        st.write(f'- {definicion}')  # Mostrar cada definición por separado
                else:
                    st.write(resultados)
        else:
            st.write("Seleccione la inicial de la palabra que desee consultar.")


        #Relaciones de variables

        #Scatter



        #Heatmap



    elif choice == "¡Costes promedios!":

        st.title("💡 Calculadora de Costos de Electrodomésticos")
        def load_lottie_file(filepath):
            try:
                with open(filepath, "r") as file:
                    return json.load(file)
            except FileNotFoundError:
                st.error(f"Error: No se encontró el archivo {filepath}. Verifica la ruta.")
                return None


        tarifas = {

            "Endesa": 0.157,  # €/kWh

            "Iberdrola": 0.153,

            "Naturgy": 0.160,

            "Repsol": 0.159,}

        st.sidebar.header("📊 Selección de Tarifa Eléctrica")
        tarifa_seleccionada = st.sidebar.selectbox("Selecciona tu compañía eléctrica", options=list(tarifas.keys()))
        precio_tarifa = tarifas[tarifa_seleccionada]
        st.sidebar.header("⏱️ Tiempo de Uso")
        tiempo_uso = st.sidebar.slider("Selecciona el tiempo de uso (en horas)", min_value=1, max_value=24, value=2)


        electrodomesticos = {

            "Lavadora": {"consumo": 0.9, "lottie": "auxiliary/Animation - 1731783434718.json"},
            "Aire Acondicionado": {"consumo": 1.5, "lottie": "auxiliary/Animation - 1731783350461.json"},
            "Horno": {"consumo": 2.0, "lottie": "auxiliary/Animation - 1731783259030.json"},
            "Frigorífico": {"consumo": 0.8, "lottie": "auxiliary/Animation - 1731783226494.json"},}


        st.info(f"**Tarifa Seleccionada:** {tarifa_seleccionada} - {precio_tarifa:.3f} €/kWh")
        for electro, datos in electrodomesticos.items():


            consumo = datos["consumo"]
            costo_total = consumo * tiempo_uso * precio_tarifa

            # Visualización del electrodoméstico
            st.subheader(f"🔌 {electro}")
            col1, col2 = st.columns([1, 2])

            with col1:

                # Cargar y mostrar la animación Lottie
                animation_data = load_lottie_file(datos["lottie"])
                if animation_data:
                    st_lottie(animation_data, height=150, width=150, key=electro)

            with col2:

                st.markdown(f"**Consumo:** {consumo} kWh/h")
                st.markdown(f"**Tiempo de Uso:** {tiempo_uso} horas")
                st.markdown(f"**Costo Total Estimado:** {costo_total:.2f} €")
                st.divider()  # Línea divisoria entre electrodomésticos


    elif choice == "Vista específica":

        st.title("Predicciones de Demanda Energética")

        model_choice = st.radio("Selecciona el modelo de predicción", ["Demanda (RNN)", "Demanda (LSTM)", "Demanda (GRU)", "Demanda (Prophet)"])

        if st.button("Realizar Predicción"):

            if model_choice == "Demanda (RNN)":

                df_demanda = load_data("SELECT * FROM demanda_energia")
                df_generation = load_data("SELECT * FROM generacion_energia")
                df_exchanges = load_data("SELECT * FROM transacciones_energia")
                df = preprocess_data(df_demanda, df_exchanges, df_generation)
                valores_escalados, objetivo_escalado = escalador(df)
                X_train, X_test, y_train, y_test = train_test_split_data(valores_escalados, objetivo_escalado,
                                                                         train_ratio=0.8)
                modelo_neuronal_rnn(X_test, y_test)
                predict_7_days_rnn(last_sequence=X_test)
                visual_loss_rnn()

            elif model_choice == "Demanda (LSTM)":
                df_demanda = load_data("SELECT * FROM demanda_energia")
                df_generation = load_data("SELECT * FROM generacion_energia")
                df_exchanges = load_data("SELECT * FROM transacciones_energia")
                df = preprocess_data(df_demanda, df_exchanges, df_generation)
                valores_escalados, objetivo_escalado = escalador(df)
                X_train, X_test, y_train, y_test = train_test_split_data(valores_escalados, objetivo_escalado,
                                                                         train_ratio=0.8)

                modelo_neuronal_lstm(X_test, y_test)
                predict_7_days_lstm(last_sequence=X_test)
                visual_loss_lstm()

            elif model_choice == "Demanda (Prophet)":

                df_demanda = load_data("SELECT * FROM demanda_energia")
                df_generation = load_data("SELECT * FROM generacion_energia")
                df_exchanges = load_data("SELECT * FROM transacciones_energia")
                df = preprocess_data(df_demanda, df_exchanges, df_generation)

                model_prophet(df)

            else:

                df_demanda = load_data("SELECT * FROM demanda_energia")
                df_generation = load_data("SELECT * FROM generacion_energia")
                df_exchanges = load_data("SELECT * FROM transacciones_energia")
                df = preprocess_data(df_demanda, df_exchanges, df_generation)
                valores_escalados, objetivo_escalado = escalador(df)
                X_train, X_test, y_train, y_test = train_test_split_data(valores_escalados, objetivo_escalado,
                                                                         train_ratio=0.8)

                modelo_neuronal_gru(X_test, y_test)
                predict_7_days_gru(last_sequence=X_test)
                visual_loss_gru()


    elif choice == "Mapa Coroplético de Intercambio Energético":
        mostrar_mapa_coro()




    elif choice == "Página Principal":

        # Función para cargar animaciones Lottie

        def load_lottie_file(filepath):

            try:

                with open(filepath, "r") as file:

                    return json.load(file)

            except FileNotFoundError:

                st.error(f"Error: No se encontró el archivo {filepath}. Verifica la ruta.")

                return None

        # Animación de bienvenida

        lottie_intro = load_lottie_file("auxiliary/Animation - 1732401006815.json")

        if lottie_intro:
            st_lottie(lottie_intro, height=250, key="welcome_animation")

        # Título principal

        st.title("🔋 **Bienvenido a la Plataforma de Análisis Energético de Redeia S.A.**")

        st.markdown("""

            ---

            ### 🚀 **Explora y analiza el futuro del sector energético español**

            Esta aplicación interactiva combina datos históricos, análisis científico y herramientas predictivas para ayudarte

            a comprender y tomar decisiones informadas sobre el sistema energético.

            ---

        """)

        # Tarjetas de métricas clave

        st.header("📊 **Indicadores Energéticos Clave**")

        #Cálculo métricas Kpis

        #Extracción de la información

        df_demanda = load_data("SELECT fecha, valor_demanda_MW FROM demanda_energia")
        df_demanda['fecha'] = pd.to_datetime(df_demanda['fecha'])
        df_demanda['year'] = df_demanda['fecha'].dt.year
        df_generation = load_data("SELECT fecha, valor_generacion_MW, energia, tipo_tecnología FROM generacion_energia")
        df_generation['fecha'] = pd.to_datetime(df_generation['fecha'])
        df_generation['year'] = df_generation['fecha'].dt.year
        df_generation = df_generation[(df_generation['energia'] == 'Generación total') | (df_generation['tipo_tecnología'] == 'Generación total')]
        df_generation = df_generation.drop(columns=['energia', 'tipo_tecnología'])
        df_generation = df_generation.reset_index(drop=True)
        df_co2 = load_data("SELECT fecha, valor, energia FROM emisiones_co2")
        df_co2['fecha'] = pd.to_datetime(df_co2['fecha'])
        df_co2['year'] = df_co2['fecha'].dt.year
        df_co2 = df_co2[~(df_co2['energia'].isin(['tCO2 eq./MWh', 'Total tCO2 eq.']))]
        df_co2 = df_co2.groupby('fecha', as_index=False)['valor'].sum()

        generacion_total = df_generation['valor_generacion_MW'].sum()
        maxima_demanda = df_demanda['valor_demanda_MW'].max()
        emisiones_totales = df_co2['valor'].sum()

        #Cálculos porcentuales




        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric("⚡ Generación Total (MW)", f"{generacion_total}", "⬆︎ 2.5%")

            st.caption("Progreso basado en los últimos 5 años.")

        with col2:

            st.metric("📈 Máxima Demanda Registrada (MW)", f"{maxima_demanda}", "⬆︎ 1.8%")

            st.caption("Histórico actualizado a 2024.")

        with col3:

            st.metric("🌱 Emisiones Totales (tCO2)", f"{emisiones_totales}", "⬇︎ 4.2%")

            st.caption("Reducción anual promedio desde 2020.")

        # Sección "Aprende y Optimiza"

        st.header("💡 **Aprende y Optimiza**")

        st.subheader("🌍 **Impacto de las Energías Renovables**")

        st.markdown("""

            Las energías renovables han transformado el panorama energético global.  

            En España, la transición hacia fuentes limpias como la eólica y la solar está reduciendo la dependencia de combustibles fósiles.

        """)

        st.info("💡 **Dato clave:** La energía eólica representa el 19.9% del mix energético español en 2024.")

        # Recomendaciones interactivas

        st.subheader("🧠 **Recomendaciones Personalizadas**")

        st.write("Selecciona tus prioridades para obtener sugerencias adaptadas:")

        prioridades = st.multiselect(

            "¿Cuáles son tus objetivos?",

            ["Reducir emisiones", "Ahorrar costos", "Aumentar eficiencia energética"]

        )

        if "Reducir emisiones" in prioridades:
            st.success("🌱 Cambia a proveedores de energía renovable y minimiza el uso de combustibles fósiles.")

        if "Ahorrar costos" in prioridades:
            st.success("💡 Ajusta tus consumos a las horas valle y revisa los electrodomésticos de mayor consumo.")

        if "Aumentar eficiencia energética" in prioridades:
            st.success("⚡ Opta por dispositivos inteligentes y sistemas de monitoreo energético.")

        if "Reducir emisiones" in prioridades and "Ahorrar costos" in prioridades:
            st.success("🌱💡 Implementa paneles solares y ajusta tus consumos a las horas valle.")

        if "Reducir emisiones" in prioridades and "Aumentar eficiencia energética" in prioridades:
            st.success("🌱⚡ Considera electrodomésticos eficientes y fuentes renovables.")

        if "Ahorrar costos" in prioridades and "Aumentar eficiencia energética" in prioridades:
            st.success("💡⚡ Aprovecha la tecnología de bajo consumo y revisa tus hábitos energéticos.")

        # Tendencias Globales y Comparativas

        st.header("🌐 **Tendencias Globales y Comparativas**")

        st.markdown("""

            El sector energético mundial está en constante evolución. Aquí te mostramos cómo España se compara con otros países:

            - **Generación renovable**: España ocupa el **4º lugar en Europa** en capacidad instalada de energía solar.

            - **Demanda energética**: Crecimiento moderado del **1.3% anual** desde 2019.

            - **Emisiones de CO2**: Reducción del **35% desde 2010**, en línea con los objetivos de la UE.

        """)

        st.info(
            "🔎 **Nota:** Los datos provienen de informes internacionales de la Agencia Internacional de Energía (IEA).")

        # Aprendizaje interactivo: Glosario energético

        st.header("📖 **Glosario Energético**")

        st.markdown("Selecciona una letra para explorar términos clave del sector energético:")

        letras = ['C', 'E', 'F', 'H', 'M', 'N', 'R', 'S', 'T']

        letra_seleccionada = st.selectbox("Selecciona una letra", letras)

        if letra_seleccionada:

            st.write(f"**Términos que empiezan con la letra {letra_seleccionada}:**")

            definiciones = obtener_vocabulario(letra_seleccionada)

            if isinstance(definiciones, list):

                for definicion in definiciones:
                    st.write(f"- {definicion}")

            else:

                st.write(definiciones)

        # Información adicional sobre Redeia

        st.header("📖 **Sobre Redeia S.A.**")

        st.markdown("""

            Redeia Corporación, S.A. es líder en innovación y sostenibilidad energética.  

            Como operador del sistema eléctrico español, impulsa la transición hacia un modelo limpio y eficiente.

            ---

        """)

        st.image("auxiliary/redeia_marca1_2.png", width=150)

        # Animación final y despedida

        lottie_thanks = load_lottie_file("auxiliary/thanks_animation.json")

        if lottie_thanks:
            st_lottie(lottie_thanks, height=200, key="thanks_animation")

        st.markdown("""

            ---

            🤝 **Gracias por explorar nuestra aplicación**  

            Esperamos que esta herramienta te inspire a tomar decisiones energéticas informadas.

        """)

        st.snow()


if __name__ == "__main__":
    main()
