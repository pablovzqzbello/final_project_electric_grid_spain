import streamlit as st
from auxiliary.db_connection import get_engine
import pandas as pd

def show_home():
    st.title("Exploración de datos de la Red Eléctrica Española")
    st.write("Desde esta página principal podrás acceder a las secciones que más te llamen la atención de nuestra aplicación")
    