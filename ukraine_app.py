import pandas as pd
import numpy as np
import streamlit as st
from helper_functions import *

st.title("My Streamlit Web App")
st.write("Welcome to my Streamlit site!")

data = load_data()
st.dataframe(data.head())

name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}!")