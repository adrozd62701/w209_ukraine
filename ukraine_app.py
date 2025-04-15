import pandas as pd
import numpy as np
import streamlit as st
import helpers.conflict_map
import helpers.human_cost
import helpers.actors_network
import helpers.data_loading
import helpers.additional_resources
import os
from datetime import timedelta

data_path = os.path.join(os.path.dirname(__file__),"data","Ukraine_Black_Sea_2020_2025_Mar28.csv.gz")


st.set_page_config(layout="centered")

st.markdown(
    """<style>
div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
    font-size: 20px;
}
    </style>
    """, unsafe_allow_html=True)

st.title("The Conflict in Ukraine")

data, ukraine_geojson = helpers.data_loading.load_data(data_path)
news = helpers.data_loading.load_news()


timeline_image = helpers.data_loading.load_timeline_image()


merged_data = helpers.data_loading.merge_news(data,news)

data['event_date'] = pd.to_datetime(pd.to_datetime(data['event_date'])).apply(lambda x: x.strftime('%Y-%m-%d'))
unique_dates = data['event_date'].sort_values().unique()
min_date = pd.to_datetime(unique_dates[0]).to_pydatetime()
max_date = pd.to_datetime(unique_dates[-1]).to_pydatetime()

st.markdown(
    """
    <style>
        div[data-testid="stTabs"] button {
            font-size: 18px !important;  /* Increase font size */
            padding: 12px 24px !important;  /* Increase padding */
        }
    </style>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Conflict Map","Human Cost","Actors Network","Additional Resources"])

# with st.container():
with tab1:
    st.header("Welcome to our app!")
    st.write("This app tells the story of the conflict in Ukraine through data visualizations.")
    st.write("Our data comes from the [Armed Conflict Location & Event Data (ACLED)](https://acleddata.com). The ACLED is a disaggregated data collection,"
        "analysis, and crisis mapping initiative. ACLED collects information on the dates, actors, locations, fatalities, "
        "and types of all reported political violence and protest events around the world.")
    st.write("Please explore the interactive visualizations on our website:")
    st.write(
        "This animated map shows the general progression of conflict intensity across Ukraine "
        "from the beginning of the war through today. Each frame represents a monthly snapshot, "
        "with conflict density shown in blue and fatality events marked in dark blue."
    )    
    st.write("**Human Cost:** The Human Cost page visualizes the conflict's fatalities. Use this timeline to "
        "better understand when and in what context those deaths occurred. Filter by Event Type in the sidebar, "
        "and hover over marked points to see major news headlines.")
    st.write("**Actors Network:** This shows conflict events between two selected groups by utilizing a bar chart that " \
        "displays each group’s initiated event count and a heatmap to track the conflict events over time.")
    st.write("**Additional Resources:** The final tab on this website has additional resources pertaining to the conflict in Ukraine")

    st.image(timeline_image)


with tab2:
    helpers.conflict_map.main(data, ukraine_geojson, min_date, max_date)
    

with tab3:
    st.markdown("### **Human Cost**")    
    st.write("The Human Cost page visualizes the conflict's fatalities. Use this timeline to "
        "better understand when and in what context those deaths occurred. Filter by Event Type in the sidebar, "
        "and hover over marked points to see major news headlines.")
    
    area_chart = helpers.human_cost.generate_fatalities_by_event_type(merged_data)
    
    # Show charts in Streamlit
    st.altair_chart(area_chart, use_container_width=True)

with tab4:
    st.markdown("### **Actors Network**")
    st.write("This shows conflict events between two selected groups by utilizing a bar chart " \
        "that displays each group’s initiated event count and a heatmap to track the conflict events over time.")
    
    helpers.actors_network.main(data)

with tab5:
    helpers.additional_resources.main()
