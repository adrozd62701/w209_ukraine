import pandas as pd
import numpy as np
import streamlit as st
from helper_functions import *
import datetime
st.set_page_config(layout="wide")


st.title("The Conflict in Ukraine")
st.header("Welcome to our app!")
st.write("This app tells the story of the conflict in Ukraine through data visualizations.")
st.write("Please explore the interactive visualizations on our website:")
st.write("**Conflict Map:** <describe conflict map>")
st.write("**Actors Network:** <describe actors network>")
st.write("**Additional Resources:** The final tab on this website has additional resources pertaining to the conflict in Ukraine")


data, ukraine_geojson = load_data()
data['event_date'] = pd.to_datetime(pd.to_datetime(data['event_date'])).apply(lambda x: x.strftime('%Y-%m-%d'))
unique_dates = data['event_date'].sort_values().unique()
min_date = pd.to_datetime(unique_dates[0]).to_pydatetime()
max_date = pd.to_datetime(unique_dates[-1]).to_pydatetime()

tab1, tab2, tab3, tab4 = st.tabs(["Conflict Map","Actors Network","Additional Resources","dataset"])
# min_date = datetime.date(2011,1,1)
# max_date = datetime.date(2012,1,1)

# st.slider("select date test",
#           min_value=min_date,
#           max_value=max_date,
#           value=min_date)

with st.container():
    with tab1:

        selected_date = st.slider(
            "Select a date:",
            min_value=min_date,
            max_value=max_date,
            value=min_date
            # format="YYYY-MM-DD"
        )

        fig = generate_conflict_map(data, selected_date, ukraine_geojson)
        st.plotly_chart(fig, use_container_width=True)
    with tab4:
        st.dataframe(data)
        