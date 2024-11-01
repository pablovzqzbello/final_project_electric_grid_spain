from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def extract_data(query):
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')

    # Crear la cadena de conexión con el formato correcto
    engine = create_engine(f'mysql+pymysql://{user}:{password}@localhost/{database}')

    try:
        with engine.connect() as connection:
            print("Conexión exitosa a la base de datos")
            df=pd.read_sql_query(sql=query, con=connection)
            return df

    except SQLAlchemyError as e:
        print(f"Error de conexión: {e}")


