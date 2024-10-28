from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, engine
from sqlalchemy.exc import SQLAlchemyError
import mysql.connector
import mysql
from functions.extraction_data import *

df_demanda=extract_demand()
df_balance=extract_balance()
df_exchanges=extract_exchange()
df_generation=extract_generation()
df_generation_co2=extract_co2()

def insert_data(df_demanda, df_balance, df_exchanges, df_generation, df_generation_co2):
    load_dotenv()
    config = {
        'host': os.getenv('HOST'),
        'user': os.getenv('USER'),
        'password': os.getenv('PASSWORD'),
        'database': os.getenv('DATABASE')
    }

    try:
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            print("Conexión exitosa a la base de datos MySQL")
            db_info = connection.get_server_info()
            print("Versión del servidor MySQL:", db_info)

            # Aquí puedes realizar las inserciones a la base de datos
            try:
                df_demanda.to_sql('demanda_energia', con=engine, if_exists='append', index=False)
                print("Datos de demanda insertados correctamente.")

                df_balance.to_sql('balance_energia', con=engine, if_exists='append', index=False)
                print("Datos de balance insertados correctamente.")

                df_exchanges.to_sql('transacciones_energia', con=engine, if_exists='append', index=False)
                print("Datos de intercambios insertados correctamente.")

                df_generation.to_sql('generacion_energia', con=engine, if_exists='append', index=False)
                print("Datos de generación insertados correctamente.")

                df_generation_co2.to_sql('generacion_co2', con=engine, if_exists='append', index=False)
                print("Datos de generación_co2 insertados correctamente.")

            except SQLAlchemyError as e:
                print("Ocurrió un error durante la inserción de datos:", str(e))

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión cerrada.")
