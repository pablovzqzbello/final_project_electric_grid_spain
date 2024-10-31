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

def create_tables():
    engine = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}')
    try:
        with engine.connect() as connection:
            print("Conexión establecida.")
            query = """
                CREATE TABLE IF NOT EXISTS demanda_energia (
                    fecha DATE PRIMARY KEY,
                    valor_demanda_MW FLOAT,
                    fecha_extraccion DATETIME
                );

                CREATE TABLE IF NOT EXISTS balance_energia (
                    fecha DATE,
                    valor_balance_GW FLOAT,
                    energia VARCHAR(50),
                    fecha_extraccion DATETIME,
                    PRIMARY KEY (fecha, energia)
                );

                CREATE TABLE IF NOT EXISTS transacciones_energia (
                    pais VARCHAR(50),
                    tipo_transaccion VARCHAR(20),
                    valor_GW FLOAT,
                    fecha DATE,
                    fecha_extraccion DATETIME,
                    PRIMARY KEY (pais, tipo_transaccion, fecha)
                );

                CREATE TABLE IF NOT EXISTS generacion_energia (
                    fecha DATE,
                    valor_generacion_GW FLOAT,
                    energia VARCHAR(50),
                    tipo_tecnología VARCHAR(50),
                    fecha_extraccion DATETIME,
                    PRIMARY KEY (fecha, energia, tipo_tecnología)
                );
            """
            connection.execute(text(query))
            print("Tablas creadas exitosamente.")
    except SQLAlchemyError as e:
        print(f"Error al crear las tablas: {e}")

def insert_data(df_demanda, df_balance, df_exchanges, df_generation):
    engine = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}')
    try:
        with engine.connect() as connection:
            print("Conexión exitosa a la base de datos")
            df_demanda.to_sql('demanda_energia', con=connection, if_exists='replace', index=False)
            print("Datos de demanda insertados correctamente.")
            df_balance.to_sql('balance_energia', con=connection, if_exists='replace', index=False)
            print("Datos de balance insertados correctamente.")
            df_exchanges.to_sql('transacciones_energia', con=connection, if_exists='replace', index=False)
            print("Datos de intercambios insertados correctamente.")
            df_generation.to_sql('generacion_energia', con=connection, if_exists='replace', index=False)
            print("Datos de generación insertados correctamente.")
    except SQLAlchemyError as e:
        print(f"Error al insertar datos: {e}")

def extract_data(query):
    engine = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}')
    try:
        with engine.connect() as connection:
            print("Conexión exitosa a la base de datos")
            df = pd.read_sql(query, connection)
            return df
    except SQLAlchemyError as e:
        print(f"Error al extraer datos: {e}")
        return None

