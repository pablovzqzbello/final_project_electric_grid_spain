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
    st.title("Intercambio de Energía de Redeia S.A. con Otros Países")

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
            projection="mercator",
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
            - ⚡ **Balance energético**: Información sobre el balance de distintos tipos de energía renovable generada.
            - ✨ **Estructura de generación**: Información sobre la generación energética según cada tecnología utilizada por Redeia S.A.
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

        df_demanda['fecha'] = pd.to_datetime(df_demanda['fecha'])
        df_demanda['year'] = df_demanda['fecha'].dt.year

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

        st.markdown("La gráfica muestra la evolución de la demanda energética en España desde 2011 hasta 2024. "
                    "Se observa una marcada reducción en la demanda durante el periodo de confinamiento por la pandemia de COVID-19, comenzando el 14 de marzo de 2020. "
                    "El punto más bajo ocurre en esta fase y la recuperación gradual inicia en junio del mismo año con la reapertura económica y la flexibilización de las restricciones."
                    "Aunque podría esperarse un aumento en la demanda debido al incremento del consumo doméstico, esta disminución refleja el impacto del cierre temporal de muchas actividades industriales y comerciales, que son los principales consumidores de energía. "
                    "Las variaciones en la demanda a lo largo del año responden a patrones diarios, semanales y estacionales: el consumo es mayor durante el día que en la noche, más alto entre semana que los fines de semana, y tiende a incrementarse en invierno y en verano, especialmente durante los picos de frío y calor.")

        # Gráfico de barras mensual de demanda promedio
        filtered_df_demanda['mes'] = filtered_df_demanda['fecha'].dt.to_period('M').dt.to_timestamp()
        demanda_mensual = filtered_df_demanda.groupby('mes')['valor_demanda_MW'].mean().reset_index()
        fig_demanda_mensual = px.bar(demanda_mensual, x='mes', y='valor_demanda_MW',
                                     title="Demanda Promedio Mensual en MW")
        st.plotly_chart(fig_demanda_mensual)
        st.markdown ("La gráfica muestra la demanda promedio mensual de energía en MW durante un período prolongado, "
                     "cubriendo aproximadamente desde 2011 hasta 2024. A lo largo del tiempo, la demanda promedio "
                     "mensual parece mantenerse relativamente estable, aunque con algunas fluctuaciones. Se observan "
                     "ciertos picos de demanda en distintos años, especialmente alrededor de 2012 y 2017-2018, "
                     "que podrían estar relacionados con factores estacionales, cambios en el consumo, o eventos "
                     "específicos que incrementaron la demanda. Asimismo, hay momentos con disminuciones, que podrían "
                     "deberse a condiciones económicas, climáticas o cambios en la eficiencia energética. Aunque el "
                     "gráfico no especifica los meses exactos, es posible que haya patrones de demanda estacionales, "
                     "como aumentos durante periodos de clima extremo, en los que se usa más energía para calefacción "
                     "o refrigeración. En los últimos años (aproximadamente desde 2023), parece haber una leve disminución "
                     "en la demanda promedio mensual, lo cual podría indicar un cambio en el consumo de energía, "
                     "posiblemente debido a iniciativas de eficiencia energética, cambios en el comportamiento de consumo, "
                     "un aumento de los precios de la energía o una desaceleración económica.")

# Filtros en el Sidebar para la comparación de años de Pablo

        st.sidebar.subheader("Comparación de Años")
        available_years = df_demanda['year'].unique()
        selected_years = st.sidebar.multiselect(
            "Selecciona los años a comparar",
            options=sorted(available_years),
            default=[2022, 2023]
        )

        if selected_years:
            df_demanda_comparador = df_demanda[df_demanda['year'].isin(selected_years)].copy()

            # Ajustar la fecha para que todos los años tengan el mismo año de referencia
            df_demanda_comparador['fecha_ajustada'] = df_demanda_comparador['fecha'].apply(
                lambda x: x.replace(year=2020))

            # Crear la gráfica de comparación con la fecha ajustada
            fig_comparador = px.line(
                df_demanda_comparador, x='fecha_ajustada', y='valor_demanda_MW', color='year',
                title=f"Comparador de Demanda en MW, años {', '.join(map(str, selected_years))}"
            )

            # Calcular métricas para líneas de referencia
            metricas = df_demanda_comparador.groupby('year')['valor_demanda_MW'].agg(['mean', 'median', 'min', 'max'])

            # Añadir líneas de referencia a la gráfica
            for year, row in metricas.iterrows():
                fig_comparador.add_hline(
                    y=row['mean'], line_color='yellow', line_dash="dash",
                    annotation_text=f"Media {year}", annotation_position="top left"
                )
                fig_comparador.add_hline(
                    y=row['median'], line_color='blue', line_dash="dot",
                    annotation_text=f"Mediana {year}", annotation_position="top left"
                )
                fig_comparador.add_hline(
                    y=row['min'], line_color='red', line_dash="dot",
                    annotation_text=f"Mínimo {year}", annotation_position="top left"
                )
                fig_comparador.add_hline(
                    y=row['max'], line_color='green', line_dash="dot",
                    annotation_text=f"Máximo {year}", annotation_position="top left"
                )

            # Mostrar la gráfica comparativa
            st.plotly_chart(fig_comparador)
        st.markdown("Este gráfico dinámico permite comparar la demanda anual de manera visual e intuitiva. A través de "
                    "él, podemos observar las diferencias en la demanda entre los distintos años registrados en nuestra "
                    "base de datos, con indicadores claros del máximo, mediana, media y mínimo de demanda para cada año.")

################ BALANCE

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
        fig2 = px.line(filtered_df_balance[filtered_df_balance['energia']=='Generación renovable'], x='fecha', y='valor_balance_GW', color='energia',
                       title="Balance Generación Energías Renovables en GW")
        st.plotly_chart(fig2)

        st.markdown("La gráfica muestra el balance de generación de energías renovables en GW a lo largo del tiempo, "
                    "desde aproximadamente 2011 hasta 2024. A lo largo del período, se observan fuertes fluctuaciones en "
                    "la generación de energía renovable, lo cual es característico de este tipo de fuentes debido a su "
                    "dependencia de condiciones naturales como el viento, la luz solar y la lluvia para la energía "
                    "hidroeléctrica. La generación no es constante y muestra picos y caídas de forma regular. Aunque "
                    "la variabilidad es alta, se nota una tendencia general al alza en la capacidad de generación "
                    "renovable. Desde 2020 en adelante, parece que los picos máximos son más altos que en años "
                    "anteriores, lo que podría indicar un aumento en la capacidad instalada o una mayor integración "
                    "de energías renovables en el sistema eléctrico. Es probable que existan patrones estacionales en "
                    "la generación, ya que el gráfico muestra ciclos repetitivos. Esto puede deberse a estaciones del "
                    "año donde ciertas fuentes renovables, como la eólica y la hidroeléctrica, tienen una mayor "
                    "o menor disponibilidad. En los últimos años (desde 2022), parece que la generación ha alcanzado "
                    "picos más altos y también presenta una mayor estabilidad en algunos períodos. Esto puede estar "
                    "relacionado con avances tecnológicos o mejoras en la eficiencia de generación renovable, así como "
                    "un mejor manejo de la variabilidad a través de almacenamiento de energía o estrategias de gestión "
                    "de la red. La gráfica muestra una dependencia significativa de factores naturales que influencian "
                    "la generación renovable, pero con una tendencia general positiva en cuanto a la capacidad y "
                    "contribución de las energías renovables en el sistema eléctrico. Esto sugiere que se están "
                    "logrando avances en la integración de estas energías, aunque aún existen desafíos en la gestión de "
                    "su variabilidad.")

        # Gráfico de área apilado para balance energético
        fig_balance_energia = px.area(filtered_df_balance[~(filtered_df_balance['energia']=='Generación renovable')], x='fecha', y='valor_balance_GW', color='energia',
                                      title="Balance Energético por Tipo de Energía en GW")
        st.plotly_chart(fig_balance_energia)

        st.markdown("El gráfico que se presenta muestra la evolución temporal de la generación de energía eléctrica "
                    "a partir de diversas fuentes renovables entre 2011 y 2024. Cada línea representa una fuente "
                    "específica (eólica, hidráulica, solar fotovoltaica, etc.) y su altura en un punto dado indica "
                    "la cantidad de energía generada en ese momento.  Revela una transformación profunda en el sector "
                    "energético, con un claro protagonismo de las energías renovables.  El auge de las energías "
                    "renovables abre nuevas oportunidades en el sector de los servicios energéticos, como la gestión de "
                    "la energía, la eficiencia energética y la comercialización de electricidad. Este hecho ha incentivado"
                    "la construcción de parques eólicos, plantas solares y otras infraestructuras relacionadas con "
                    "las energías renovables, especialmente a partir del año 2020 fruto de una fuerte transición energética"
                    "que cumple con los objetivos de la agenda climática de Horizon 2020 y Horizon 2030")

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

        # Gráfico de evolución de transacciones energéticas general
        fig_evolucion_transacciones=px.histogram(filtered_df_exchanges[~(filtered_df_exchanges['tipo_transaccion']=='saldo')],
                                                 x='fecha', y='valor_GW', color='tipo_transaccion',
                                                 title="Evolución General de Transacciones Energéticas en GW")
        st.plotly_chart(fig_evolucion_transacciones)
        st.markdown("La evolución de las transacciones comerciales entre Redeia S.A. y sus socios internacionales "
                    "muestra una notable reducción en la dependencia de las importaciones hacia el año 2022. "
                    "Este cambio responde, en gran medida, al impulso en la generación de energías renovables, "
                    "especialmente en el sector solar fotovoltaico, que ha permitido a España aumentar gradualmente "
                    "su capacidad de exportación. La transición energética y el crecimiento sostenido del sector "
                    "renovable han favorecido un modelo más autosuficiente, donde las importaciones se utilizan "
                    "de manera estratégica para cubrir picos de demanda, pero ya no constituyen el eje central del "
                    "abastecimiento.Además, una ligera reducción en el consumo energético ha permitido un mayor margen "
                    "para las exportaciones, consolidando a España como un exportador neto en el contexto europeo. "
                    "Así, la combinación de una menor dependencia de combustibles fósiles y el incremento de "
                    "la capacidad renovable posiciona a Redeia S.A. en una posición de liderazgo en el comercio "
                    "energético, apuntalando el camino hacia un sistema más sostenible y eficiente.")

        # Gráfico de evolución de transacciones energéticas por país

        fig_evolucion_transacciones_pais = px.histogram(
            filtered_df_exchanges[~(filtered_df_exchanges['tipo_transaccion'] == 'saldo')],
            x='fecha', y='valor_GW', color='pais',
            title="Evolución por país de Transacciones Energéticas en GW")
        st.plotly_chart(fig_evolucion_transacciones_pais)
        st.markdown("Esta gráfica muestra la evolución histórica de las importaciones y exportaciones de energía "
                    "de España, desglosada por países clave (Francia, Portugal, Marruecos y Andorra). "
                    "Los valores positivos representan exportaciones, mientras que los valores negativos corresponden "
                    "a importaciones.Al interactuar con los filtros, se observa que Francia ha sido tradicionalmente "
                    "el principal proveedor energético de España. Sin embargo, a partir de 2020-2021, se nota una "
                    "tendencia hacia un aumento de las exportaciones, lo que podría estar vinculado al crecimiento en "
                    "la producción de energía renovable en el país. Esta transición resalta el cambio de España de "
                    "importador a exportador energético, reflejando una mayor autosuficiencia y un compromiso con "
                    "fuentes de energía sostenibles.")

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
        fig_generacion_energia = px.area(filtered_df_generation, x='fecha', y='valor_generacion_GW', color='energia',
                                         title="Estructura de generación energética en GW")
        st.plotly_chart(fig_generacion_energia)

        # Visualización de Generación Energética
        fig4 = px.histogram(filtered_df_generation, x='fecha', y='valor_generacion_GW', color='energia',
                            title="Generación en GW")
        st.plotly_chart(fig4)
        st.markdown("Este gráfico ilustra la evolución de la generación de energía en Redeia S.A., mostrando tanto "
                    "fuentes renovables como no renovables entre 2012 y 2024. En tan solo 12 años, se observan dos "
                    "fenómenos clave que reflejan una transición energética en España.En primer lugar, destaca "
                    "la reducción de la dependencia de los combustibles fósiles, especialmente el carbón, que muestra "
                    "una caída drástica en 2019 como fuente principal de energía. Este cambio es un paso importante "
                    "hacia la descarbonización del sector energético.En segundo lugar, se observa un notable crecimiento "
                    "en las energías renovables, con la energía eólica y la solar fotovoltaica liderando este cambio, "
                    "especialmente a partir de 2020. También destacan el incremento de la energía solar térmica y "
                    "la generación hidroeléctrica mediante turbinación de bombeo, cuyo crecimiento ha sido evidente desde 2012."
                    "Respecto a las energías no renovables, la energía nuclear ha mantenido una presencia constante "
                    "como fuente complementaria, necesaria para cubrir la demanda energética actual. Sin embargo, "
                    "se observa una tendencia general a la reducción de otras fuentes no renovables, como los motores "
                    "diésel, turbinas de gas, turbinas de vapor, cogeneración (energía eléctrica y térmica) y residuos "
                    "no renovables. Esta transición hacia fuentes de energía más limpias subraya el compromiso de Redeia "
                    "S.A. con la sostenibilidad y la adaptación al cambio en el panorama energético.")

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
        st.markdown("La estructura de generación energética de esta empresa española se apoya en cinco fuentes "
                    "principales. La energía nuclear constituye el 20.6% del total, subrayando su importancia "
                    "como fuente constante en el mix energético. La energía eólica ocupa el segundo lugar con un 19.9%, "
                    "reflejando el impulso hacia fuentes limpias. La generación mediante ciclo combinado representa "
                    "un 15.1%, seguida de la energía hidráulica con un 10.9%, que continúa siendo una fuente relevante. "
                    "Aunque el carbón, con un 10.5%, aún forma parte de la producción, se encuentra en clara disminución. "
                    "Esta distribución muestra la transición hacia un modelo energético más sostenible, con un incremento "
                    "notable en fuentes renovables y una reducción gradual de los combustibles fósiles.")

    elif choice == "Mapa Coroplético de Intercambio Energético":
        mostrar_mapa_coro()

if __name__ == "__main__":
    main()
