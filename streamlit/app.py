import streamlit as st
from config import configure_page
from pages.home import show_home
from dotenv import load_dotenv
from pages.data_overview import show_data_overview
import os

configure_page()

def main():
    st.sidebar.title("Navegación")
    page = st.sidebar.selectbox("Selecciona la vista", ["Inicio", "Presentación de Datos"])

    # Llama a la función correspondiente según la página seleccionada
    if page == "Inicio":
        show_home()
    elif page == "Presentación de Datos":
        show_data_overview()

if __name__ == "__main__":
    main()
