from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}
# Configuración de conexión
engine = create_engine(f'mysql+mysqlconnector://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}')

def insert_data(df_demanda, df_balance, df_exchanges, df_generation):
    with engine.connect() as connection:
        # Insertar dataframes en tablas de la base de datos
        df_demanda.to_sql('demanda_energia', con=connection, if_exists='replace', index=False)
        df_balance.to_sql('balance_energia', con=connection, if_exists='replace', index=False)
        df_exchanges.to_sql('transacciones_energia', con=connection, if_exists='replace', index=False)
        df_generation.to_sql('generacion_energia', con=connection, if_exists='replace', index=False)

def extract_data(query):
    with engine.connect() as connection:
        print("Conexión exitosa a la base de datos")
        return pd.read_sql(query, connection)

def insert_data_batch(df, table_name, batch_size=1000):
    with engine.connect() as connection:
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            batch.to_sql(table_name, con=connection, if_exists='append' if i > 0 else 'replace', index=False)
