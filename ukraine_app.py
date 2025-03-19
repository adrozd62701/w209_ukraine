import pandas as pd
import numpy as np
import streamlit as st
from helper_functions import *
st.set_page_config(layout="wide")


st.title("The Conflict in Ukraine")
st.header("Welcome to our app!")
st.write("This app tells the story of the conflict in Ukraine through data visualizations.")
st.write("Please explore the interactive visualizations on our website:")
st.write("**Conflict Map:** <describe conflict map>")
st.write("**Actors Network:** <describe actors network>")
st.write("**Additional Resources:** The final tab on this website has additional resources pertaining to the conflict in Ukraine")


data = load_data()

tab1, tab2, tab3 = st.tabs(["Conflict Map","Actors Network","Additional Resources"])

with st.container():
    with tab1:
        st.dataframe(data.head())
        