import pandas as pd
import numpy as np
import streamlit as st

st.title("My Streamlit Web App")
st.write("Welcome to my Streamlit site!")

name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}!")