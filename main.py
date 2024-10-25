import streamlit as st
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from functions.extraction_data import *

def main ():

    st.title("Red Eléctrica de España. Investigación de mercado, sostenibilidad y rendimiento")

    st.text("Este proyecto tiene como objetivo al consolidación de una aplicación innovadora en el mercado que nos"
            "permita obtener datos a tiempo real del mercado eléctrico español. En primer lugar, de la demanda energética." 
            "En segundo lugar, la generación de energía dispuesta entre energías renovables y no renovables. En tercer lugar,"
            "un balance de producción general, en el que podamos ver la evolución del consumo energético español."
            "En cuarto lugar, un estudio sobre la importación y exportación de energía entre España y sus partners."
            "Agradecemos a Redeia Corporación S.A. la disposición de un API accesible para la consulta de su base de datos")





if __name__ == "__main__":
    main()