import pandas as pd
import numpy as np
import streamlit as st
from helpers.helper_functions import *
import datetime
import os

data_path = os.path.join(os.path.dirname(__file__),"data","Ukraine_Black_Sea_2020_2025_Jan24.csv.gz")


st.set_page_config(layout="wide")

st.markdown(
    """<style>
div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
    font-size: 20px;
}
    </style>
    """, unsafe_allow_html=True)

st.title("The Conflict in Ukraine")
st.header("Welcome to our app!")
st.write("This app tells the story of the conflict in Ukraine through data visualizations.")
st.write("Please explore the interactive visualizåations on our website:")
st.write("**Conflict Map:** <describe conflict map>")
st.write("**Actors Network:** <describe actors network>")
st.write("**Additional Resources:** The final tab on this website has additional resources pertaining to the conflict in Ukraine")

data, ukraine_geojson = load_data(data_path)
news = load_news()


timeline_image = load_timeline_image()

st.image(timeline_image)


merged_data = merge_news(data,news)

data['event_date'] = pd.to_datetime(pd.to_datetime(data['event_date'])).apply(lambda x: x.strftime('%Y-%m-%d'))
unique_dates = data['event_date'].sort_values().unique()
min_date = pd.to_datetime(unique_dates[0]).to_pydatetime()
max_date = pd.to_datetime(unique_dates[-1]).to_pydatetime()


tab1, tab2, tab3, tab4 = st.tabs(["Conflict Map","Human Cost","Actors Network","Additional Resources"])

with st.container():
    with tab1:
        
        selected_date = st.slider(
            "**Select a date:**",
            min_value=min_date,
            max_value=max_date,
            value=min_date
        )

        st.write(" ")
        conflict_map_fig = generate_conflict_map(data, selected_date, ukraine_geojson)
        st.plotly_chart(conflict_map_fig, use_container_width=True)

    with tab2:

        area_chart = generate_fatalities_by_event_type(merged_data)
        
        # Show charts in Streamlit
        st.altair_chart(area_chart, use_container_width=True)

        