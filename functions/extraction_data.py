def extract_ren_noren(start_year=2011, end_year=2025, time_trunc='day'):
    all_gen_df_ren_noren = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/generacion/evolucion-renovable-no-renovable'

        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': time_trunc}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error fetching data for year {year}: {response.status_code}")
            continue

        generation_data_ren_noren = response.json()

        gen_df_ren_noren = []

        for included_data in generation_data_ren_noren.get('included', []):
            values = included_data.get('attributes', {}).get('values', [])

            df_gen = pd.DataFrame(values)

            df_gen['type'] = included_data.get('type')
            df_gen['id'] = included_data.get('id')
            df_gen['groupId'] = included_data.get('groupId')
            df_gen['title'] = included_data.get('attributes', {}).get('title')
            df_gen['description'] = included_data.get('attributes', {}).get('description')
            df_gen['color'] = included_data.get('attributes', {}).get('color')
            df_gen['technology_type'] = included_data.get('attributes', {}).get('type')

            gen_df_ren_noren.append(df_gen)

        all_gen_df_ren_noren.extend(gen_df_ren_noren)

    df_generation_ren_noren = pd.concat(all_gen_df_ren_noren, ignore_index=True)

    #########################################################################

    # Eliminar columnas no deseadas
    df_generation_ren_noren.drop(['id', 'groupId', 'color', 'type'], axis=1, inplace=True)

    # Convertir la columna de fecha al formato estándar
    df_generation_ren_noren['datetime'] = pd.to_datetime(df_generation_ren_noren['datetime'])

    # Reorganizar las columnas restantes
    df_generation_ren_noren = df_generation_ren_noren[
        ['datetime', 'value', 'percentage', 'title', 'description', 'technology_type']]
    return df_generation_ren_noren

###############################

def extract_co2(start_year=2011, end_year=2025, time_trunc='day'):
    all_gen_df_co2 = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/generacion/no-renovables-detalle-emisiones-CO2'

        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': time_trunc}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error fetching data for year {year}: {response.status_code}")
            continue

        generation_data_co2 = response.json()

        gen_df_co2 = []

        for included_data in generation_data_co2.get('included', []):
            values = included_data.get('attributes', {}).get('values', [])

            df_gen = pd.DataFrame(values)

            df_gen['type'] = included_data.get('type')
            df_gen['id'] = included_data.get('id')
            df_gen['groupId'] = included_data.get('groupId')
            df_gen['title'] = included_data.get('attributes', {}).get('title')
            df_gen['description'] = included_data.get('attributes', {}).get('description')
            df_gen['color'] = included_data.get('attributes', {}).get('color')
            df_gen['technology_type'] = included_data.get('attributes', {}).get('type')

            gen_df_co2.append(df_gen)

        all_gen_df_co2.extend(gen_df_co2)

    df_generation_co2 = pd.concat(all_gen_df_co2, ignore_index=True)

    ############################################################################

    # Eliminar columnas no deseadas
    df_generation_co2.drop(['id', 'groupId', 'color', 'type'], axis=1, inplace=True)

    # Convertir la columna de fecha al formato estándar
    df_generation_co2['datetime'] = pd.to_datetime(df_generation_co2['datetime'])

    # Reorganizar las columnas restantes
    df_generation_co2 = df_generation_co2[
        ['datetime', 'value', 'percentage', 'title', 'description', 'technology_type']]

    return df_generation_co2

#########################################################################

def extract_co2(start_year=2011, end_year=2025, time_trunc='day'):
    all_gen_df_co2 = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/generacion/no-renovables-detalle-emisiones-CO2'

        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': time_trunc}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error fetching data for year {year}: {response.status_code}")
            continue

        generation_data_co2 = response.json()

        gen_df_co2 = []

        for included_data in generation_data_co2.get('included', []):
            values = included_data.get('attributes', {}).get('values', [])

            df_gen = pd.DataFrame(values)

            df_gen['type'] = included_data.get('type')
            df_gen['id'] = included_data.get('id')
            df_gen['groupId'] = included_data.get('groupId')
            df_gen['title'] = included_data.get('attributes', {}).get('title')
            df_gen['description'] = included_data.get('attributes', {}).get('description')
            df_gen['color'] = included_data.get('attributes', {}).get('color')
            df_gen['technology_type'] = included_data.get('attributes', {}).get('type')

            gen_df_co2.append(df_gen)

        all_gen_df_co2.extend(gen_df_co2)

    df_generation_co2 = pd.concat(all_gen_df_co2, ignore_index=True)

    ############################################################################

    # Eliminar columnas no deseadas
    df_generation_co2.drop(['id', 'groupId', 'color', 'type'], axis=1, inplace=True)

    # Convertir la columna de fecha al formato estándar
    df_generation_co2['datetime'] = pd.to_datetime(df_generation_co2['datetime'])

    # Reorganizar las columnas restantes
    df_generation_co2 = df_generation_co2[
        ['datetime', 'value', 'percentage', 'title', 'description', 'technology_type']]

    return df_generation_co2

###################################################################

def extract_prueba_demanda(category='demanda', widget='evolucion', start_year=2011, end_year=2025):
    all_data = []

    for year in range(start_year, end_year):
        url = f"https://apidatos.ree.es/es/datos/{category}/{widget}"

        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': 'day'}

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Host': 'apidatos.ree.es'}

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            all_data.append(data)
        else:
            print(f"Error fetching data for year {year}: {response.status_code}")

    demanda = []

    for entry in all_data:
        included = entry.get('included', [])
        for item in included:
            values = item.get('attributes', {}).get('values', [])
            for value in values:
                relevant = {'datetime': value.get('datetime'),
                            'demand_value': value.get('value'),
                            'percentage': value.get('percentage')}
                demanda.append(relevant)

    df_demanda = pd.DataFrame(demanda)

    ##############################################

    # Convertir la columna de fecha al formato de fecha estándar

    df_demanda['datetime'] = pd.to_datetime(df_demanda['datetime'])

    # Eliminar posibles duplicados
    df_demanda.drop_duplicates(inplace=True)

    # (Opcional) Eliminar columna 'percentage' si no es necesaria (En principio LO ES)
    # df_demanda.drop('percentage', axis=1, inplace=True)

    return df_demanda

#########################################################3

# Bloque de Limpieza General

# NO EJECUTAR TODAVÍA, CONSULTAR AL GRUPO

df_ren_noren = extract_ren_noren()
df_co2 = extract_co2()
df_prueba_2 = extract_prueba_2()
df_demanda = extract_prueba_demanda()

# Conversión de fechas al formato estándar
df_ren_noren['datetime'] = pd.to_datetime(df_ren_noren['datetime'])
df_co2['datetime'] = pd.to_datetime(df_co2['datetime'])
df_prueba_2['datetime'] = pd.to_datetime(df_prueba_2['datetime'])
df_demanda['datetime'] = pd.to_datetime(df_demanda['datetime'])

# Eliminar duplicados (aplicado para asegurar que no haya datos redundantes)
df_ren_noren.drop_duplicates(inplace=True)
df_co2.drop_duplicates(inplace=True)
df_prueba_2.drop_duplicates(inplace=True)
df_demanda.drop_duplicates(inplace=True)

# Renombrar columnas para 'consistencia y claridad'
df_ren_noren.rename(columns={'value': 'generation_value', 'percentage': 'generation_percentage'}, inplace=True)
df_co2.rename(columns={'value': 'co2_emission_value'}, inplace=True)
df_demanda.rename(columns={'demand_value': 'energy_demand_value'}, inplace=True)

# Valores numéricos a FLOAT
df_ren_noren['generation_value'] = df_ren_noren['generation_value'].astype(float)
df_co2['co2_emission_value'] = df_co2['co2_emission_value'].astype(float)
df_demanda['energy_demand_value'] = df_demanda['energy_demand_value'].astype(float)

# Reorganizar las columnas para consistencia en la estructura (opcional)
df_ren_noren = df_ren_noren[['datetime', 'generation_value', 'generation_percentage', 'technology_type', 'title', 'description']]
df_co2 = df_co2[['datetime', 'co2_emission_value', 'title', 'description', 'technology_type']]
df_prueba_2 = df_prueba_2[['datetime', 'value', 'percentage', 'technology_type', 'title', 'description']]
df_demanda = df_demanda[['datetime', 'energy_demand_value']]

# Filtrar datos irrelevantes si es necesario (opcional, ejemplo de filtro de fechas)
df_ren_noren = df_ren_noren[df_ren_noren['datetime'] >= '2015-01-01']
df_co2 = df_co2[df_co2['datetime'] >= '2015-01-01']
df_prueba_2 = df_prueba_2[df_prueba_2['datetime'] >= '2015-01-01']
df_demanda = df_demanda[df_demanda['datetime'] >= '2015-01-01']

# Unificar categorías en minúsculas para evitar discrepancias en el uso de texto
df_ren_noren['technology_type'] = df_ren_noren['technology_type'].str.lower()
df_co2['technology_type'] = df_co2['technology_type'].str.lower()
df_prueba_2['technology_type'] = df_prueba_2['technology_type'].str.lower()

# Imprimir un resumen de los DataFrames para verificar antes de la carga a SQL
print("Renovable y No Renovable - Primeras Filas")
print(df_ren_noren.head())
print("Emisiones de CO2 - Primeras Filas")
print(df_co2.head())
print("Estructura de Generación - Primeras Filas")
print(df_prueba_2.head())
print("Demanda de Energía - Primeras Filas")
print(df_demanda.head())

# Si todo es correcto, los DataFrames están listos para ser cargados a la base de datos SQL

# Modelado con Pivot Table

# Modelado con Pivot Table para df_ren_noren
df_ren_noren_pivot = df_ren_noren.pivot_table(
    index=['datetime'], columns='technology_type', values='generation_value', aggfunc='sum'
).reset_index()

# Modelado con Pivot Table para df_co2
df_co2_pivot = df_co2.pivot_table(
    index=['datetime'], columns='technology_type', values='co2_emission_value', aggfunc='sum'
).reset_index()

# Modelado con Pivot Table para df_prueba_2
df_prueba_2_pivot = df_prueba_2.pivot_table(
    index=['datetime'], columns='technology_type', values='value', aggfunc='sum'
).reset_index()

# Resumen de la Demanda Energética Diaria
df_demanda_summary = df_demanda.groupby('datetime').agg({'energy_demand_value': 'sum'}).reset_index()

print("Pivot - Generación Renovable y No Renovable:")
print(df_ren_noren_pivot.head())
print("\nPivot - Emisiones de CO2:")
print(df_co2_pivot.head())
print("\nPivot - Estructura de Generación:")
print(df_prueba_2_pivot.head())
print("\nResumen - Demanda Energética Diaria:")
print(df_demanda_summary.head())

df_ren_noren_pivot.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df_ren_noren_pivot.columns]

df_co2_pivot.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df_co2_pivot.columns]

df_prueba_2_pivot.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df_prueba_2_pivot.columns]

##################################################################