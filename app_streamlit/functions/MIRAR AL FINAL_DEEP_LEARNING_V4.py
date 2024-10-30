#!/usr/bin/env python
# coding: utf-8

# # FUNCIONES DE EXTRACCIÓN DE LOS DATOS CON LIMPIEZA

# En esta parte se ha explorado las funcionalidades del API de Red Eléctrica de España. Como se puede apreciar, se han obtenido los resultados concerientes a la demanda, balance, generación e intercambio de energía. 
# 
# Varios problemas que se pueden observar a nivel código:
#     El api solo permite la extracción de información anual, no nos permite realizar un histórico anual, sí mensual, diario y por hora.
#     cada endpoint es un enlace diferente, obliga a realizar bucles para poder extraer más información
#     
# Ventajas.
#     El API no es complicada, no necesita API KEY, no necesita tokens o eso parece, solo conocer bien como se contruiye el endpoint o la url base con la que trabajar. 
#     EL API en cada categoría permite obtener todo tipo de información acerca de la huella del CO2 y del precio de la energía por lo que se podría extraer.
#     
# Encotnré una posible solución a la extracción para obtener más años de los que indica el api y así mismo obtener todos los meses al mismo tiempo. 

# In[2]:


import requests
import pandas as pd
import numpy as np


# In[3]:


######################################################################################################################################################


# In[4]:


# FUNCIONES PARA LA APLICACIÓN 

def extract_demand(category='demanda', widget='evolucion', start_year=2011, end_year=2025):
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
    df_demanda['fecha_extraccion'] = pd.Timestamp.now()
    df_demanda["fecha_extraccion"]= df_demanda["fecha_extraccion"].dt.floor("s")
    df_demanda.rename(columns={'datetime':'fecha', 'demand_value':'valor_demanda_MW', 'percentage':'porcentaje'},inplace=True)
    df_demanda.drop(['porcentaje'], axis=1, inplace=True)
    df_demanda['fecha']=df_demanda['fecha'].str.split('T').str[0]
    df_demanda['fecha']=pd.to_datetime(df_demanda['fecha'])
    return df_demanda


# In[5]:


#FUNCIÓN DOS

def extract_balance(start_year=2011, end_year=2025, time_trunc='day'):
    all_data = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/balance/balance-electrico'
        
        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': time_trunc}

        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data for year {year}: {response.status_code}")
            continue
        
        balance_data = response.json()
        content_data = balance_data.get('included', [])[0].get('attributes', {}).get('content', [])

        data_list = []

        for item in content_data:
            type_name = item['type'] 
            values = item.get('attributes', {}).get('values', [])
            
            for value in values:
                value['type'] = type_name
                data_list.append(value)

        all_data.extend(data_list)  

    df_balance = pd.DataFrame(all_data) 
    df_balance['fecha_extraccion'] = pd.Timestamp.now()
    df_balance["fecha_extraccion"]= df_balance["fecha_extraccion"].dt.floor("s")
    df_balance.rename(columns={'datetime':'fecha', 'value':'valor_balance_GW', 'percentage':'porcentaje','type':'energia'},inplace=True)
    df_balance.drop(['porcentaje'], axis=1, inplace=True)
    df_balance['fecha']=df_balance['fecha'].str.split('T').str[0]
    df_balance['fecha']=pd.to_datetime(df_balance['fecha'])
    return df_balance


# In[6]:


#FUNCIÓN TRES

def extract_exchange(start_year=2011, end_year=2025, time_trunc='day', widget='todas-fronteras-fisicos'):
    all_lines = []

    for year in range(start_year, end_year):
        url = f'https://apidatos.ree.es/es/datos/intercambios/{widget}'
        
        params = {'start_date': f'{year}-01-01T00:00',
                  'end_date': f'{year}-12-31T23:59',
                  'time_trunc': time_trunc}

        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data for year {year}: {response.status_code}")
            continue  
        exchange_data = response.json()
        
        lines = []
        
        for country in exchange_data.get('included', []):
            country_name = country.get('id')
            
            if 'content' in country.get('attributes', {}): 
                for content in country['attributes']['content']:
                    trade_type = content.get('attributes', {}).get('title')
                    values = content.get('attributes', {}).get('values', [])
                    
                    for item in values:
                        line = {'country': country_name,
                                'type': trade_type,
                                'value': item.get('value'),
                                'percentage': item.get('percentage'),
                                'datetime': item.get('datetime')}
                        lines.append(line)
        
        all_lines.extend(lines)  

    df_exchanges = pd.DataFrame(all_lines) 
    df_exchanges['fecha_extraccion'] = pd.Timestamp.now()
    df_exchanges["fecha_extraccion"]= df_exchanges["fecha_extraccion"].dt.floor("s")
    df_exchanges.rename(columns={'datetime':'fecha', 'value':'valor_GW', 'percentage':'porcentaje','type':'tipo_transaccion','country':'pais'},inplace=True)
    df_exchanges.drop(['porcentaje'], axis=1, inplace=True)
    df_exchanges['fecha']=df_exchanges['fecha'].str.split('T').str[0]
    df_exchanges['fecha']=pd.to_datetime(df_exchanges['fecha'])
    return df_exchanges


# In[7]:


def extract_generation(start_year=2011, end_year=2025, time_trunc='day'):
    all_gen_df = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/generacion/estructura-generacion'
        
        params = {
            'start_date': f'{year}-01-01T00:00',
            'end_date': f'{year}-12-31T23:59',
            'time_trunc': time_trunc 
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data for year {year}: {response.status_code}")
            continue  
        
        generation_data = response.json()
        
        gen_df = []

        for included_data in generation_data.get('included', []):
            values = included_data.get('attributes', {}).get('values', [])
            
            df_gen = pd.DataFrame(values)
            
            df_gen['type'] = included_data.get('type')
            df_gen['id'] = included_data.get('id')
            df_gen['groupId'] = included_data.get('groupId')
            df_gen['title'] = included_data.get('attributes', {}).get('title')
            df_gen['description'] = included_data.get('attributes', {}).get('description')
            df_gen['color'] = included_data.get('attributes', {}).get('color')
            df_gen['technology_type'] = included_data.get('attributes', {}).get('type')
            
            gen_df.append(df_gen)

        all_gen_df.extend(gen_df)  

    df_generation = pd.concat(all_gen_df, ignore_index=True)  

    df_generation = df_generation[['datetime', 'value', 'percentage', 'type', 'id', 'groupId', 'title', 'description', 'color', 'technology_type']]
    df_generation['fecha_extraccion'] = pd.Timestamp.now()
    df_generation["fecha_extraccion"]= df_generation["fecha_extraccion"].dt.floor("s")
    df_generation.rename(columns={'datetime':'fecha', 'value':'valor_generacion_GW', 'percentage':'porcentaje','type':'energia', 'technology_type':'tipo_tecnología'},inplace=True)
    df_generation.drop(['porcentaje', 'title', 'groupId','id', 'description', 'color'], axis=1, inplace=True)
    df_generation['fecha']=df_generation['fecha'].str.split('T').str[0]
    df_generation['fecha']=pd.to_datetime(df_generation['fecha'])
    return df_generation


# In[8]:


#########################EXTRAS######################################EXTRAS################################################EXTRAS####################


# In[9]:


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

    df_generation_ren_noren = df_generation_ren_noren[['datetime', 'value', 'percentage', 'type', 'id', 'groupId', 'title', 'description', 'color', 'technology_type']]
    
    return df_generation_ren_noren


# In[10]:


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

    df_generation_co2 = df_generation_co2[['datetime', 'value', 'percentage', 'type', 'id', 'groupId', 'title', 'description', 'color', 'technology_type']]
    df_generation_co2.drop(['id', 'groupId', 'title','description', 'percentage', 'color', 'technology_type'],axis=1, inplace=True)
    df_generation_co2['fecha_extraccion'] = pd.Timestamp.now()
    df_generation_co2["fecha_extraccion"]= df_generation_co2["fecha_extraccion"].dt.floor("s")
    df_generation_co2.rename(columns={'datetime':'fecha', 'value':'valor', 'percentage':'porcentaje', 'type':'energia'},inplace=True)
    df_generation_co2['fecha']=df_generation_co2['fecha'].str.split('T').str[0]
    df_generation_co2['fecha']=pd.to_datetime(df_generation_co2['fecha'])
    return df_generation_co2


# In[11]:


def extract_prueba(start_year=2011, end_year=2025, time_trunc='day'):
    all_gen_df_co2 = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/generacion/potencia-instalada'
        
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

    df_generation_co2 = df_generation_co2[['datetime', 'value', 'percentage', 'type', 'id', 'groupId', 'title', 'description', 'color', 'technology_type']]
    
    return df_generation_co2


# In[12]:


def extract_prueba_2(start_year=2011, end_year=2025, time_trunc='day'):
    all_gen_df_co2 = []

    for year in range(start_year, end_year):
        url = 'https://apidatos.ree.es/es/datos/generacion/estructura-generacion'
        
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

    df_generation_co2 = df_generation_co2[['datetime', 'value', 'percentage', 'type', 'id', 'groupId', 'title', 'description', 'color', 'technology_type']]
    
    return df_generation_co2


# In[13]:


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
    return df_demanda


# In[14]:


################################################################################################################################################


# # EDA PARA COMPROBAR LA RELACIÓN DE LOS DATOS

# In[15]:


import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# In[16]:


df_demanda=extract_demand()
df_balance=extract_balance()
df_exchanges=extract_exchange()
df_generation=extract_generation()
df_generation_co2=extract_co2()


# In[17]:


df_demanda


# In[18]:


df_balance


# In[19]:


df_exchanges


# In[20]:


df_generation


# In[21]:


df_generation_co2


# In[22]:


df_demanda.to_csv('demanda')
df_balance.to_csv('balance')
df_exchanges.to_csv('exchanges')
df_generation.to_csv('generacion')
df_generation_co2.to_csv('generacion_co2')


# In[23]:


px.histogram(df_exchanges[~(df_exchanges['tipo_transaccion']=='saldo')], x='fecha', y='valor_GW', color='pais')


# In[24]:


df_exchanges_fil = df_exchanges[df_exchanges['tipo_transaccion'].isin(['Importación', 'Exportación'])]
df_exchanges_fil = df_exchanges_fil.sort_values(by=['pais', 'tipo_transaccion', 'fecha'])
df_exchanges_fil['suma_acumulada'] = df_exchanges_fil.groupby(['pais', 'tipo_transaccion'])['valor_GW'].cumsum()
df_exchanges_fil


# In[25]:


px.histogram(df_exchanges_fil, x='fecha', y='suma_acumulada', color='pais')


# In[26]:


px.histogram(df_exchanges[~(df_exchanges['tipo_transaccion']=='saldo')], x='fecha', y='valor_GW', color='tipo_transaccion')


# In[27]:


px.violin(df_exchanges[~(df_exchanges['tipo_transaccion']=='saldo')], x='valor_GW')


# In[28]:


px.box(df_exchanges[~(df_exchanges['tipo_transaccion']=='saldo')], x='valor_GW')


# In[29]:


px.box(df_generation[~(df_generation['energia']=='Generacion total')], x='valor_generacion_GW')


# In[30]:


df_generation['energia'].value_counts()


# In[31]:


df_generation.describe()


# In[32]:


px.box(df_balance[~(df_balance['energia']=='Generación renovable')], x='valor_balance_GW')


# In[33]:


px.box(df_demanda, x='valor_demanda_MW')


# In[34]:


px.histogram(df_generation[~(df_generation['energia']=='Generación total')], x='fecha', y='valor_generacion_GW', color='energia')


# In[35]:


px.pie(df_generation[~(df_generation['energia']=='Generación total')], values='valor_generacion_GW', names='energia')


# In[36]:


px.line(df_demanda, x='fecha', y='valor_demanda_MW')


# In[37]:


df_generation


# In[38]:


df_demanda


# In[39]:


df_generation_grouped=df_generation.groupby('fecha', as_index=False).agg({'valor_generacion_GW':'sum'})


# In[40]:


df_generation_grouped['crecimiento_generacion']=df_generation_grouped['valor_generacion_GW'].cumsum()


# In[41]:


df_generation_grouped


# In[42]:


df_relations=pd.concat([df_demanda, df_generation_grouped], axis=1)


# In[43]:


df_relations


# In[44]:


df_relations.drop('fecha', axis=1, inplace=True)


# In[45]:


df_relations


# In[46]:


px.scatter(df_relations, x='valor_demanda_MW', y='valor_generacion_GW')


# In[47]:


df_generation_co2


# In[48]:


df_generation_co2=df_generation_co2[~(df_generation_co2['energia'].isin(['tCO2 eq./MWh', 'Total tCO2 eq.']))]


# In[49]:


df_generation_co2


# In[50]:


px.histogram(df_generation_co2, x='fecha', y='valor', color='energia')


# In[51]:


df_generation_co2_grouped=df_generation_co2.groupby('fecha', as_index=False)['valor'].sum()


# In[52]:


df_generation_co2_grouped


# In[53]:


px.line(df_generation_co2_grouped, x='fecha', y='valor')


# In[54]:


df_relations_2=pd.concat([df_relations, df_generation_co2_grouped], axis=1)


# In[55]:


df_relations_2


# In[56]:


px.scatter(df_relations_2, x='valor_generacion_GW', y='valor')


# In[57]:


px.scatter(df_relations_2, x='valor_demanda_MW', y='valor')


# In[58]:


sns.heatmap(df_relations_2[['valor_demanda_MW', 'valor_generacion_GW', 'valor']].corr(), annot=True)
plt.show()


# In[59]:


df_generation_fil=df_generation[~(df_generation['energia']=='Generación total')]


# In[60]:


df_generation_fil


# In[61]:


df_generation_fil = pd.concat(objs = [df_generation_fil, pd.get_dummies(data = df_generation_fil['energia'], prefix = 'energia', dtype = int)],
                                  axis = 1).drop('energia', axis = 1)


# In[62]:


df_generation_fil


# In[63]:


df_generation_fil = pd.concat(objs = [df_generation_fil, pd.get_dummies(data = df_generation_fil['tipo_tecnología'], prefix = 'tipo_tecnología', dtype = int)],
                                  axis = 1).drop('tipo_tecnología', axis = 1)


# In[64]:


df_generation_fil.drop('fecha_extraccion', axis=1, inplace=True)


# In[65]:


plt.figure(figsize=(20,12))
sns.heatmap(df_generation_fil.corr(), annot=True)
plt.show()


# In[66]:


df_balance


# In[67]:


df_balance_heat = pd.concat(objs = [df_balance, pd.get_dummies(data = df_balance['energia'], prefix = 'energia', dtype = int)],
                                  axis = 1).drop('energia', axis = 1)


# In[68]:


plt.figure(figsize=(16,8))
sns.heatmap(df_balance_heat.corr(), annot=True)
plt.show()


# In[69]:


df_exchanges_fil


# In[70]:


df_exchanges_heat=pd.concat(objs = [df_exchanges_fil, pd.get_dummies(data = df_exchanges_fil['tipo_transaccion'], prefix = 'tipo_transaccion', dtype = int)],
                                  axis = 1).drop('tipo_transaccion', axis = 1)


# In[71]:


df_exchanges_heat=pd.concat(objs = [df_exchanges_heat, pd.get_dummies(data = df_exchanges_heat['pais'], prefix = 'pais', dtype = int)],
                                  axis = 1).drop('pais', axis = 1)


# In[72]:


df_exchanges_heat


# In[73]:


plt.figure(figsize=(16,8))
sns.heatmap(df_exchanges_heat.corr(), annot=True)
plt.show()


# In[74]:


df_demanda


# In[75]:


import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import LSTM, Dense, Dropout, Input
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go
from datetime import timedelta

def predecir_y_graficar_demanda(df, sequence_length=30, n_future_days=30, epochs=50, batch_size=32):
    # Escalar los datos
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df[['valor_demanda_MW']])

    # Preparar los datos en secuencias
    X, y = [], []
    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i, 0])
        y.append(data_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Construir y entrenar el modelo LSTM según la nueva estructura
    model = Sequential()
    model.add(Input(shape=(X.shape[1], 1)))
    model.add(LSTM(units=64, activation='tanh', return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(units=32, activation='tanh'))
    model.add(Dropout(0.3))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

    # Realizar predicciones para los próximos 30 días utilizando una ventana deslizante
    test_input = data_scaled[-sequence_length:]
    predicciones = []
    for _ in range(n_future_days):
        pred = model.predict(test_input.reshape(1, sequence_length, 1))
        predicciones.append(pred[0, 0])
        test_input = np.append(test_input[1:], pred)  # Desplazar la ventana hacia adelante

    predicciones = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))

    # Crear fechas para las predicciones
    fecha_inicio = df['fecha'].iloc[-1] + timedelta(days=1)
    fechas_prediccion = [fecha_inicio + timedelta(days=i) for i in range(n_future_days)]

    # Graficar con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['valor_demanda_MW'], mode='lines', name='Demanda Histórica'))
    fig.add_trace(go.Scatter(x=fechas_prediccion, y=predicciones.flatten(), mode='lines', name='Predicción de Demanda'))
    fig.update_layout(title="Predicción de Demanda para los Próximos 30 Días", xaxis_title="Fecha", yaxis_title="Demanda (MW)", template="plotly_white")
    fig.show()

# Llamada a la función con tu DataFrame `df_demanda`
predecir_y_graficar_demanda(df_demanda)


# In[76]:


import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import LSTM, Dense, Dropout, Input
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go
from datetime import timedelta

def predecir_y_graficar_demanda(df, sequence_length=30, n_future_days=30, epochs=50, batch_size=32):
    # Escalar los datos de manera correcta
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df[['valor_demanda_MW']])

    # Preparar los datos en secuencias
    X, y = [], []
    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i, 0])
        y.append(data_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Construir y entrenar el modelo LSTM según la nueva estructura
    model = Sequential([
        Input(shape=(X.shape[1], 1)),
        LSTM(units=64, activation='tanh', return_sequences=True),
        Dropout(0.3),
        LSTM(units=32, activation='tanh'),
        Dropout(0.3),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

    # Realizar predicciones para los próximos 30 días utilizando una ventana deslizante
    test_input = data_scaled[-sequence_length:]
    predicciones = []
    for _ in range(n_future_days):
        pred = model.predict(test_input.reshape(1, sequence_length, 1))
        predicciones.append(pred[0, 0])
        test_input = np.append(test_input[1:], pred)  # Desplazar la ventana hacia adelante

    # Invertir la escala de las predicciones
    predicciones = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))

    # Crear fechas para las predicciones
    fecha_inicio = df['fecha'].iloc[-1] + timedelta(days=1)
    fechas_prediccion = [fecha_inicio + timedelta(days=i) for i in range(n_future_days)]

    # Graficar con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['valor_demanda_MW'], mode='lines', name='Demanda Histórica'))
    fig.add_trace(go.Scatter(x=fechas_prediccion, y=predicciones.flatten(), mode='lines', name='Predicción de Demanda'))
    fig.update_layout(title="Predicción de Demanda para los Próximos 30 Días", xaxis_title="Fecha", yaxis_title="Demanda (MW)", template="plotly_white")
    fig.show()

# Llamada a la función con tu DataFrame `df_demanda`
predecir_y_graficar_demanda(df_demanda)


# In[81]:


df_balance


# In[82]:


def predecir_y_graficar_balance(df, sequence_length=30, n_future_days=30, epochs=50, batch_size=32):
    # Escalar los datos de manera correcta
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df[['valor_balance_GW']])

    # Preparar los datos en secuencias
    X, y = [], []
    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i, 0])
        y.append(data_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Construir y entrenar el modelo LSTM según la nueva estructura
    model = Sequential([
        Input(shape=(X.shape[1], 1)),
        LSTM(units=64, activation='tanh', return_sequences=True),
        Dropout(0.3),
        LSTM(units=32, activation='tanh'),
        Dropout(0.3),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

    # Realizar predicciones para los próximos 30 días utilizando una ventana deslizante
    test_input = data_scaled[-sequence_length:]
    predicciones = []
    for _ in range(n_future_days):
        pred = model.predict(test_input.reshape(1, sequence_length, 1))
        predicciones.append(pred[0, 0])
        test_input = np.append(test_input[1:], pred)  # Desplazar la ventana hacia adelante

    # Invertir la escala de las predicciones
    predicciones = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))

    # Crear fechas para las predicciones
    fecha_inicio = df.index[-1] + timedelta(days=1)
    fechas_prediccion = [fecha_inicio + timedelta(days=i) for i in range(n_future_days)]

    # Graficar con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['valor_balance_GW'], mode='lines', name='Balance Histórico'))
    fig.add_trace(go.Scatter(x=fechas_prediccion, y=predicciones.flatten(), mode='lines', name='Predicción de Balance'))
    fig.update_layout(title="Predicción de Balance para los Próximos 30 Días", xaxis_title="Fecha", yaxis_title="Balance (GW)", template="plotly_white")
    fig.show()

# Preprocesamiento del DataFrame `df_balance`
df_balance_filtrado = (df_balance[~(df_balance['energia'] == 'Generación Renovable')].groupby('fecha').agg({'valor_balance_GW': 'sum'}))

# Llamada a la función con el DataFrame procesado
predecir_y_graficar_balance(df_balance_filtrado)


# In[83]:


df_exchanges


# In[87]:


def predecir_y_graficar_exchanges(df, sequence_length=30, n_future_days=30, epochs=50, batch_size=32):
    # Escalar los datos de manera correcta
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df[['valor_GW']])

    # Preparar los datos en secuencias
    X, y = [], []
    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i, 0])
        y.append(data_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Construir y entrenar el modelo LSTM según la nueva estructura
    model = Sequential([
        Input(shape=(X.shape[1], 1)),
        LSTM(units=64, activation='tanh', return_sequences=True),
        Dropout(0.3),
        LSTM(units=32, activation='tanh'),
        Dropout(0.3),
        Dense(units=1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

    # Realizar predicciones para los próximos 30 días utilizando una ventana deslizante
    test_input = data_scaled[-sequence_length:]
    predicciones = []
    for _ in range(n_future_days):
        pred = model.predict(test_input.reshape(1, sequence_length, 1))
        predicciones.append(pred[0, 0])
        test_input = np.append(test_input[1:], pred)  # Desplazar la ventana hacia adelante

    # Invertir la escala de las predicciones
    predicciones = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))

    # Crear fechas para las predicciones
    fecha_inicio = df.index[-1] + timedelta(days=1)
    fechas_prediccion = [fecha_inicio + timedelta(days=i) for i in range(n_future_days)]

    # Graficar con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['valor_GW'], mode='lines', name='Saldo Histórico'))
    fig.add_trace(go.Scatter(x=fechas_prediccion, y=predicciones.flatten(), mode='lines', name='Predicción de Saldo'))
    fig.update_layout(title="Predicción de Saldo para los Próximos 30 Días", xaxis_title="Fecha", yaxis_title="Saldo (GW)", template="plotly_white")
    fig.show()

# Preprocesamiento del DataFrame `df_balance`
df_exchanges_filtrado = (df_exchanges[df_exchanges['tipo_transaccion'] == 'saldo'].groupby('fecha').agg({'valor_GW': 'mean'}))

# Llamada a la función con el DataFrame procesado
predecir_y_graficar_exchanges(df_exchanges_filtrado)


# In[ ]:


def predecir_y_graficar_exchanges(df, sequence_length=30, n_future_days=30, epochs=50, batch_size=32):
    # Escalar los datos de manera correcta
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df[['valor_GW']])

    # Preparar los datos en secuencias
    X, y = [], []
    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i, 0])
        y.append(data_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Construir y entrenar el modelo LSTM según la nueva estructura
    model = Sequential([
        Input(shape=(X.shape[1], 1)),
        LSTM(units=64, activation='tanh', return_sequences=True),
        Dropout(0.3),
        LSTM(units=32, activation='tanh'),
        Dropout(0.3),
        Dense(units=1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

    # Realizar predicciones para los próximos 30 días utilizando una ventana deslizante
    test_input = data_scaled[-sequence_length:]
    predicciones = []
    for _ in range(n_future_days):
        pred = model.predict(test_input.reshape(1, sequence_length, 1))
        predicciones.append(pred[0, 0])
        test_input = np.append(test_input[1:], pred)  # Desplazar la ventana hacia adelante

    # Invertir la escala de las predicciones
    predicciones = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))

    # Crear fechas para las predicciones
    fecha_inicio = df.index[-1] + timedelta(days=1)
    fechas_prediccion = [fecha_inicio + timedelta(days=i) for i in range(n_future_days)]

    # Graficar con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['valor_GW'], mode='lines', name='Saldo Histórico'))
    fig.add_trace(go.Scatter(x=fechas_prediccion, y=predicciones.flatten(), mode='lines', name='Predicción de Saldo'))
    fig.update_layout(title="Predicción de Saldo para los Próximos 30 Días", xaxis_title="Fecha", yaxis_title="Saldo (GW)", template="plotly_white")
    fig.show()

# Preprocesamiento del DataFrame `df_balance`
df_exchanges_filtrado = (df_exchanges[df_exchanges['tipo_transaccion'] == 'saldo'].groupby('fecha').agg({'valor_GW': 'mean'}))

# Llamada a la función con el DataFrame procesado
predecir_y_graficar_exchanges(df_exchanges_filtrado)

