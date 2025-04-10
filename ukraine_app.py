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
# st.dataframe(data.sort_values(by='event_date',ascending=False))
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
    st.write("**Authors:** Akanksha Chattopadhyay, Alice Drozd, Sooyeon Kim, Rina Palta")
    st.write("This app tells the story of the conflict in Ukraine through data visualizations. " \
        "Our data comes from the [Armed Conflict Location & Event Data (ACLED)](https://acleddata.com). The ACLED is a disaggregated data collection, "
        "analysis, and crisis mapping initiative. ACLED collects information on the dates, actors, locations, fatalities, "
        "and types of all reported political violence and protest events around the world.")
    
    st.image(timeline_image)
    st.divider()
    st.write("Please explore the interactive visualizations on our website:")
    st.write("**Conflict Map:** This page features an interactive map that highlights the intensity "
        "and distribution of conflict events across Ukraine. By utilizing a heatmap overlay, users can visualize "
        "concentrations of conflict-related incidents, providing a clear picture of the most affected areas. The timeline slider allows navigation through the conflict chronologically, month by month. Users can also apply filters to differentiate between various event types and subtypes, and distinguish civilian versus non-civilian targeting. Hover over specific points to get detailed information about each incident, including fatalities and involved actors, offering a deeper insight into the human cost and strategic movements within the region.")
    st.write("**Human Cost:** The Human Cost page visualizes the conflict's fatalities. Use this timeline to "
        "better understand when and in what context those deaths occurred. Filter by Event Type in the sidebar, "
        "and hover over marked points to see major news headlines.")
    st.write("**Actors Network:** This page shows conflict events between two selected actors by utilizing a bar "
        "chart that displays each actor’s event count and a heatmap to track trends over time. There is also a "
        "capability to filter the data by year, month, and keyword to easily drill down into specific details of the conflict events.")
    st.write("**Additional Resources:** The final tab on this website has additional resources pertaining to the conflict in Ukraine")



with tab2:
    # st.sidebar.markdown("### **Conflict Map**")
    # disorder_type = st.sidebar.selectbox('Disorder Type:', ['All'] + sorted(data['disorder_type'].unique().tolist()))
    # event_type = st.sidebar.selectbox('Event Type:', ['All'] + sorted(data['event_type'].unique().tolist()))
    # sub_event_type = st.sidebar.selectbox('Sub Event Type:', ['All'] + sorted(data['sub_event_type'].unique().tolist()))
    # civilian_targeting = st.sidebar.selectbox('Civilian Targeting:', ['All', 'Civilian targeting', 'Non-civilian targeting'])


    st.markdown("### **Conflict Map**")
    st.write("This page features an interactive map that highlights the intensity "
        "and distribution of conflict events across Ukraine. By utilizing a heatmap overlay, users can visualize "
        "concentrations of conflict-related incidents, providing a clear picture of the most affected areas. The timeline slider allows navigation through the conflict chronologically, month by month. Users can also apply filters to differentiate between various event types and subtypes, and distinguish civilian versus non-civilian targeting. Hover over specific points to get detailed information about each incident, including fatalities and involved actors, offering a deeper insight into the human cost and strategic movements within the region.")
    
    disorder_type = st.selectbox('Disorder Type:', ['All'] + sorted(data['disorder_type'].unique().tolist()))
    event_type = st.selectbox('Event Type:', ['All'] + sorted(data['event_type'].unique().tolist()))
    sub_event_type = st.selectbox('Sub Event Type:', ['All'] + sorted(data['sub_event_type'].unique().tolist()))
    civilian_targeting = st.selectbox('Civilian Targeting:', ['All', 'Civilian targeting', 'Non-civilian targeting'])
    
    selected_date = st.slider(
        "Select a date:",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        format="MM/DD/YYYY",
        step=timedelta(days=30)  # Approximation for one month
    )
    # st.sidebar.divider()
    st.write(" ")
    conflict_map_fig = helpers.conflict_map.generate_conflict_map(data, selected_date, ukraine_geojson, disorder_type, event_type, sub_event_type, civilian_targeting)
    st.plotly_chart(conflict_map_fig, use_container_width=True)

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
    st.write("This page shows conflict events between two selected actors by utilizing a bar "
        "chart that displays each actor’s event count and a heatmap to track trends over time. There is also a "
        "capability to filter the data by year, month, and keyword to easily drill down into specific details of the conflict events.")
    
    helpers.actors_network.main(data)

with tab5:
    helpers.additional_resources.main()
