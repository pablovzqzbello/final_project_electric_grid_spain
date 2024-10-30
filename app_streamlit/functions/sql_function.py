from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

#FUNCIÓN PARA INSERTAR LOS DATOS EN LA BASE DE DATOS

load_dotenv()
host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

def insert_data(df_demanda, df_balance, df_exchanges, df_generation):
    load_dotenv()

    with engine.connect() as connection:
        df_demanda.to_sql('demanda', con=connection, if_exists='replace', index=False)
        df_balance.to_sql('balance', con=connection, if_exists='replace', index=False)
        df_exchanges.to_sql('intercambios', con=connection, if_exists='replace', index=False)
        df_generation.to_sql('generacion_energia', con=connection, if_exists='replace', index=False)

    connection.close()

def extract_data(query):
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, con=connection)
        return df
    except SQLAlchemyError as e:
        st.error(f"Error al extraer datos: {e}")
    return df