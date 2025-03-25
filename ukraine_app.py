import pandas as pd
import numpy as np
import streamlit as st
import helpers.helper_functions
import datetime
import os
import altair as alt
from streamlit_timeline import st_timeline
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

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
st.write("Please explore the interactive visualizations on our website:")
st.write("**Conflict Map:** <describe conflict map>")
st.write("**Actors Network:** <describe actors network>")
st.write("**Additional Resources:** The final tab on this website has additional resources pertaining to the conflict in Ukraine")

data, ukraine_geojson = helpers.helper_functions.load_data(data_path)
news = helpers.helper_functions.load_news()

timeline_df = helpers.helper_functions.load_timeline()
timeline_image = helpers.helper_functions.load_timeline_image()

merged_data = helpers.helper_functions.merge_news(data,news)

data['event_date'] = pd.to_datetime(pd.to_datetime(data['event_date'])).apply(lambda x: x.strftime('%Y-%m-%d'))
unique_dates = data['event_date'].sort_values().unique()
min_date = pd.to_datetime(unique_dates[0]).to_pydatetime()
max_date = pd.to_datetime(unique_dates[-1]).to_pydatetime()

# st.image(timeline_image)


tab1, tab2, tab3, tab4 = st.tabs(["Conflict Map","Human Cost","Actors Network","Additional Resources"])

with st.container():
    with tab1:

        if "event_or_date" not in st.session_state:
            st.session_state.event_or_date = "date"

        if "selected_date" not in st.session_state:
            st.session_state.selected_date = min_date  # Default value

        col1, col2, col3 = st.columns([1, 18, 1])  # Layout: Left button, Slider, Right button

        with col1:
            if st.button("⬅️"):
                st.session_state.selected_date -= datetime.timedelta(days=1)

        with col3:
            if st.button("➡️"):
                st.session_state.selected_date += datetime.timedelta(days=1)

        with col2:
            st.session_state.selected_date = st.slider(
                "Select a value",
                min_value=min_date,
                max_value=max_date,
                value=st.session_state.selected_date,
                format='YYYY-MM-DD'
            )
            st.session_state.event_or_date = "date"

        timeline_data = timeline_df.rename(columns={'date':'start','description':'content'})
        timeline_data = timeline_data.to_dict(orient='records')
        

        selected_event = st_timeline(
            timeline_data,
            groups=[],
            options={
                "showCurrentTime":False,
                "selectable":True,
                "zoomable":False,
                "horizontalScroll":False,
                "stack":True,
                "margin": {"item":10},
                # "start":"2022-01-01",
                # "end":"2025-03-01"
            },
            height="500px"
        )  

        if "selected_event" not in st.session_state:
            st.session_state.selected_event = st.session_state.selected_date  # Default value

        if selected_event:
            st.write(pd.to_datetime(selected_event["start"]))
            st.session_state.selected_event = pd.to_datetime(selected_event["start"])
            st.session_state.event_or_date = "event"
        st.write(st.session_state.event_or_date)
        # st.write(st.session_state.selected_date)
        # st.write(st.session_state.selected_event)
        # if selected_event:
            # st.session_state.selected_date = selected_event["start"]

        
        st.write(" ")
        conflict_map_fig = helpers.helper_functions.generate_conflict_map(data, st.session_state.selected_date, ukraine_geojson)
        st.plotly_chart(conflict_map_fig, use_container_width=True)
        notes = helpers.helper_functions.get_notes(st.session_state.selected_date, data)
        st.dataframe(notes.sort_values(by='Fatalities',ascending=False), hide_index=True)

    with tab2:

        area_chart = helpers.helper_functions.generate_fatalities_by_event_type(merged_data)
        
        # Show charts in Streamlit
        st.altair_chart(area_chart, use_container_width=True)

        