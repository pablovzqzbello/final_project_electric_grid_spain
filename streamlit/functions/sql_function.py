from dotenv import load_dotenv
import os
from sqlalchemy import *
from sqlalchemy.exc import SQLAlchemyError
from streamlit.functions.extraction_data import *

#INVOCAMOS LAS FUNCIONES DE EXTRACCIÓN PARA LA OBTENCIÓN DE DATOS

df_demanda=extract_demand()
df_balance=extract_balance()
df_exchanges=extract_exchange()
df_generation=extract_generation()
df_generation_co2=extract_co2()

#CARGAMOS NUESTRO.ENV PARA CONFIGURAR LA CONEXIÓN A LA BDD

load_dotenv()

config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }

#CONEXIÓN Y CREACIÓN DE BASE DE DATOS SI NO EXISTE, SELECCIONAMOS LA BDD PARA CREAR LUEGO TABLAS
#CREAMOS UN ENGINE DENTRO DE LA FUNCIÓN SIN ESPECIFICAR BDD PORQUE AÚN NO EXISTE

def create_db():
    engine_no_db = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}/')
    try:
        with engine_no_db.connect() as connection: 
            print("Conexión establecida.")
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database']}"))
            connection.execute(text(f"USE {config['database']}"))
            print("Base de datos creada y en uso")
    except SQLAlchemyError as e:
        print(f"Error: {e}")

#FUNCIÓN PARA CREACIÓN DE TABLAS

def create_tables():
    engine = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}')
    try:
        with engine.connect() as connection:
            print("Conexión establecida.")
            query = """
                CREATE TABLE IF NOT EXISTS demanda_energia (
                    fecha DATE PRIMARY KEY,
                    valor_demanda_MW FLOAT,
                    fecha_extraccion DATETIME);
                    
                CREATE TABLE balance_energia (
                    fecha DATE,
                    valor_balance_GW FLOAT,
                    energia VARCHAR(50),
                    fecha_extraccion DATETIME,
                    PRIMARY KEY (fecha, energia),
                    FOREIGN KEY (fecha) REFERENCES demanda_energia(fecha)); 

                CREATE TABLE transacciones_energia (
                    pais VARCHAR(50),
                    tipo_transaccion VARCHAR(20),
                    valor_GW FLOAT,
                    fecha DATE,
                    fecha_extraccion DATETIME,
                    PRIMARY KEY (pais, tipo_transaccion, fecha),
                    FOREIGN KEY (fecha) REFERENCES demanda_energia(fecha));

                CREATE TABLE generacion_energia (
                    fecha DATE,
                    valor_generacion_GW FLOAT,
                    energia VARCHAR(50),
                    tipo_tecnología VARCHAR(50),
                    fecha_extraccion DATETIME,
                    PRIMARY KEY (fecha, energia, tipo_tecnología),
                    FOREIGN KEY (fecha) REFERENCES demanda_energia(fecha));

                """
            connection.execute(text(query))
            print("Se han creado las tablas demanda_energia, balance_energia, transacciones_energia y generacion_energia")
    except SQLAlchemyError as e:
        print(f"Error: {e}")

#FUNCIÓN PARA INSERTAR LOS DATOS EN LA BASE DE DATOS

def insert_data(df_demanda, df_balance, df_exchanges, df_generation):
    
    engine = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}')
    
    try:
        
        with engine.connect() as connection:
            
            print("Conexión exitosa a la base de datos")
    
            df_demanda.to_sql('demanda_energia', con=engine, if_exists='replace', index=False)
            print("Datos de demanda insertados correctamente.")
                
            df_balance.to_sql('balance_energia', con=engine, if_exists='replace', index=False)
            print("Datos de balance insertados correctamente.")
    
            df_exchanges.to_sql('transacciones_energia', con=engine, if_exists='replace', index=False)
            print("Datos de intercambios insertados correctamente.")
    
            df_generation.to_sql('generacion_energia', con=engine, if_exists='replace', index=False)
            print("Datos de generación insertados correctamente.")

    except SQLAlchemyError as e:
        print(f"Error al insertar datos: {e}")

def extract_data(query):
    engine = create_engine(f'mysql+mysqlconnector://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}')
    try:
        with engine.connect() as connection:
            
            print("Conexión exitosa a la base de datos")

            df = pd.read_sql(query, connection)
            
    except SQLAlchemyError as e:
        print(f"Error: {e}")
    return df