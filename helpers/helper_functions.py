import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import json
import altair as alt
from PIL import Image
import os

@st.cache_data()
def load_timeline():
    timeline_path = 'data/timeline.csv'
    timeline = pd.read_csv(timeline_path)
    timeline = timeline.iloc[:,1:3]

    return timeline

@st.cache_data()
def load_timeline_image():
    timeline_image_path = 'data/timeline_image.png'
    timeline_image = Image.open(timeline_image_path)

    return timeline_image

@st.cache_data()
def load_news():
    news_path = 'data/markers_prototype.csv'
    news = pd.read_csv(news_path)

    return news

@st.cache_data
def load_data():
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # data_path = os.path.join(ROOT_DIR, "data", "Ukraine_Black_Sea_2020_2025_Jan24.csv.gz")
    data_path = 'data/Ukraine_Black_Sea_2020_2025_Jan24.csv.gz'
    data = pd.read_csv(data_path, compression='gzip')
    data = data[data["event_date"] >= "2022-01-01"]
    data = data.iloc[:,2:]

    with open('data/ukraine_border.geojson') as f:
        ukraine_geojson = json.load(f)
    return data, ukraine_geojson

@st.cache_data
def merge_news(data, news):
    news['event_date_news'] = pd.to_datetime(news['event_date'])
    data['event_date'] = pd.to_datetime(data['event_date'])

    news["week"] = news["event_date_news"].dt.to_period("W").apply(lambda r: r.start_time)  
    data['week'] = data["event_date"].dt.to_period("W").apply(lambda r: r.start_time)  

    merged_data = pd.merge(left=data,right=news[['event_date_news','event_type','week','description','url']],how='left',left_on=['week','event_type'], right_on=['week','event_type']).drop(['week','event_date_news'],axis=1)

    return merged_data

def get_tooltip(filtered_data, tooltip_cols):
    filtered_data[tooltip_cols] = filtered_data[tooltip_cols].fillna("")
    
    hover_text = filtered_data[tooltip_cols].values.tolist()

    return filtered_data, hover_text

def generate_conflict_map(df, selected_date, ukraine_geojson):
    df['event_date'] = pd.to_datetime(df['event_date'])


    heatmap_data = df.groupby(['event_date', 'latitude', 'longitude',
                               "event_type",
        "actor1", "actor2", "location", "source"]).agg(
        intensity=('event_id_cnty', 'count'),
        fatalities=('fatalities', 'sum')
    ).reset_index()

    # st.dataframe(heatmap_data)

    # heatmap_data = heatmap_data[heatmap_data['event_type'].isin(selected_event_types)]

    filtered_data = heatmap_data[heatmap_data['event_date'] == selected_date]

    tooltip_cols = [
        "event_type", 
        "actor1", "actor2", "location", "source", "fatalities"
    ]

    filtered_data, hover_text = get_tooltip(filtered_data, tooltip_cols)

    fig = go.Figure()

    # 1. Add Ukraine boundary as a shaded polygon
    fig.add_trace(go.Choroplethmapbox(
        geojson=ukraine_geojson,
        locations=["UKR"],  # must match the feature ID
        z=[1],              # dummy value
        showscale=False,
        marker_opacity=0.04,
        marker_line_width=0,
        colorscale=[[0, 'blue'], [1, 'blue']],  # solid blue
        name="Ukraine Boundary"
    ))


    # 3. Add density layer for conflict intensity
    fig.add_trace(go.Densitymapbox(
        lat=filtered_data['latitude'],
        lon=filtered_data['longitude'],
        z=(filtered_data['intensity']),
        radius=17,
        colorscale='Viridis',
        showscale=True,
        name="Conflict Intensity"
    ))

    # 2. Add fatalities as markers
    fig.add_trace(go.Scattermapbox(
        lat=filtered_data['latitude'],
        lon=filtered_data['longitude'],
        mode='markers',
        marker=dict(
            size=np.clip(filtered_data['fatalities'] * 3, 5, 50),
            color='red',
            opacity=0.8,
            sizemode='area'
        ),
        name="Fatalities",
        customdata=hover_text,
        hovertemplate=
            "<b>Event Type:</b> %{customdata[0]}<br>" +
            "<b>Actor 1:</b> %{customdata[1]}<br>" +
            "<b>Actor 2:</b> %{customdata[2]}<br>" +
            "<b>Location:</b> %{customdata[3]}<br>" +
            "<b>Source:</b> %{customdata[4]}<br>" +
            "<b>Fatalities:</b> %{customdata[5]}<br>" +
            "<extra></extra>"
    ))

    # Map styling
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=4.8,
        mapbox_center={"lat": 48.5, "lon": 34.3615},
        title=f"Conflict Intensity and Fatalities on {selected_date.strftime('%Y-%m-%d')}",
        height=500,
        width=1000,
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    return fig

def generate_fatalities_by_event_type(df):
    data = df.copy()
    data["event_date"] = pd.to_datetime(data["event_date"])
    data = data[data["event_date"] >= "2022-01-01"]
    data["week"] = data["event_date"].dt.to_period("W").apply(lambda r: r.start_time)

    weekly_data = data.groupby(["week", "event_type"], as_index=False).agg({'fatalities':'sum','url':lambda x:x.value_counts(dropna=False).index[0],'description':lambda x:x.value_counts(dropna=False).index[0]})
    # detail_data = data.groupby(["event_type", "admin1"], as_index=False).agg({'fatalities':'sum','url':'mode','description':'mode'})
    weekly_data['url'] = weekly_data['url'].fillna("")
    weekly_data['description'] = weekly_data['description'].fillna("")

    # Define unique event types + "All of the above"
    event_types = sorted(data["event_type"].unique())
    event_types.insert(0, "All Event Types")  # Default option

    
    # Fixed color mapping for each event type
    color_mapping = {
        "Battles": "#1f77b4",
        "Explosions/Remote violence": "#ff7f0e",
        "Protests": "#2ca02c",
        "Riots": "#d62728",
        "Strategic developments": "#9467bd",
        "Violence against civilians": "#8c564b"
    }

    # Create Streamlit dropdown
    selected_event_type = st.radio("Select Event Type:", event_types, index=0, horizontal=True)

    # Apply filtering logic
    if selected_event_type != "All Event Types":
        weekly_data = weekly_data[weekly_data["event_type"] == selected_event_type]
        # detail_data = detail_data[detail_data["event_type"] == selected_event_type]

    color_scale = alt.Scale(domain=list(color_mapping.keys()), range=list(color_mapping.values()))

    # Area Chart
    area_chart = alt.Chart(weekly_data).mark_area(opacity=0.7).encode(
        x=alt.X("week:T", title="Week"),
        y=alt.Y("fatalities:Q", title="Total Fatalities"),
        color=alt.Color("event_type:N", title="Event Type", scale=color_scale),
        tooltip=[
            alt.Tooltip("week:T", title="Week"),
            alt.Tooltip("event_type:N", title="Event Type"),
            alt.Tooltip("fatalities:Q", title="Fatalities"),
            alt.Tooltip("description:N", title="Major News"),            
            alt.Tooltip("url:N", title="URL")

        ]
    ).properties(
        title="Fatalities by Event Type (Weekly)",
        width=700,
        height=300
    )

    news_points = weekly_data[weekly_data["description"] != ""]

    # Circular markers for news articles
    news_markers = alt.Chart(news_points).mark_circle(size=100, color="black", opacity=0.8).encode(
        x="week:T",
        y="fatalities:Q",
        tooltip=[
            alt.Tooltip("week:T", title="Week"),
            alt.Tooltip("event_type:N", title="Event Type"),
            alt.Tooltip("fatalities:Q", title="Fatalities"),
            alt.Tooltip("description:N", title="Major News"),
            alt.Tooltip("url:N", title="URL")

        ]
    )

    # Larger invisible hit area for better interaction
    news_hit_area = alt.Chart(news_points).mark_point(size=1000, opacity=0).encode(
        x="week:T",
        y="fatalities:Q",
        tooltip=[
            alt.Tooltip("week:T", title="Week"),
            alt.Tooltip("event_type:N", title="Event Type"),
            alt.Tooltip("fatalities:Q", title="Fatalities"),
            alt.Tooltip("description:N", title="Major News"),
            alt.Tooltip("url:N", title="URL")

        ]
    )

    return area_chart + news_markers + news_hit_area


