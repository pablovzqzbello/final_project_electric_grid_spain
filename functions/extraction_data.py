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






