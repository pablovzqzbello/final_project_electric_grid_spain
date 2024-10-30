from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")

    connection = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

    engine = create_engine(connection)

    return engine