from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import requests

load_dotenv()

def last_update():
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')

    engine = create_engine(f'mysql+pymysql://{user}:{password}@localhost/{database}')
    query = "SELECT MAX(fecha_extraccion) AS fecha_mas_reciente FROM balance_energia"
    try:
        with engine.connect() as connection:
            print("Conexión exitosa a la base de datos")
            last_update_date = pd.read_sql_query(sql = query, con=connection)
            last_update_date["fecha_mas_reciente"] = last_update_date["fecha_mas_reciente"].dt.date
            return last_update_date
    except SQLAlchemyError as e:
        print(f"Error de conexión: {e}")

start_day = last_update()
start_day


end_day = datetime.today().strftime('%Y-%m-%d')
end_day

def extract_balance(start_day, end_day, time_trunc='day'):
    all_data = []
    url = 'https://apidatos.ree.es/es/datos/balance/balance-electrico'
    
    # Definir la fecha de inicio y fin en el mismo día
    params = {
        'start_date': f'{start_day}', 
        'end_date': f'{end_day}', 
        'time_trunc': time_trunc
    }

    response = requests.get(url, params=params, timeout=60)
    if response.status_code == 200:
        balance_data = response.json()
        content_data = balance_data.get('included', [])[0].get('attributes', {}).get('content', [])
        for item in content_data:
            type_name = item['type']
            values = item.get('attributes', {}).get('values', [])
            for value in values:
                all_data.append({
                    'fecha': value.get('datetime', '').split('T')[0],
                    'valor_balance_GW': value.get('value'),
                    'energia': type_name
                })
    else:
        print(f"Error fetching data for date {start_day}: {response.status_code}")

    df_balance = pd.DataFrame(all_data)
    df_balance['fecha_extraccion'] = pd.Timestamp.now().floor("min")
    df_balance['fecha'] = pd.to_datetime(df_balance['fecha'], errors='coerce')
    
    return df_balance

extract_balance(start_day, end_day, time_trunc='day')