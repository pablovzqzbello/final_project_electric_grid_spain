from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

user= os.getenv('DB_USER'),
password= os.getenv('DB_PASSWORD'),
database= os.getenv('DB_NAME')

# Configuración de conexión
engine = create_engine(f'mysql+pymysql:/{user}/:{password}@localhost/{database}')

def extract_data(query):
    load_dotenv
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    database = os.getenv('DB_NAME')
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@localhost/{database}')
    with engine.connect() as connection:
        print("Conexión exitosa a la base de datos")
        return pd.read_sql(query, connection)


