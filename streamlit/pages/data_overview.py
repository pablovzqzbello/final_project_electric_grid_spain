import streamlit as st
import pandas as pd
from auxiliary.db_connection import get_engine

def show_data_overview():
    st.title("Presentación de datos")
    engine = get_engine()
    query = "SELECT * FROM balance_energia"
    df = pd.read_sql(query, engine)

    st.write("Datos en sucio")
    st.dataframe(df)

