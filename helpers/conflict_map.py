import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import json
import altair as alt
from PIL import Image

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
def load_data(data_path):
    # ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # data_path = os.path.join(ROOT_DIR, "data", "Ukraine_Black_Sea_2020_2025_Jan24.csv.gz")
    # data_path = 'data/Ukraine_Black_Sea_2020_2025_Jan24.csv.gz'
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

def generate_conflict_map(df, selected_date, ukraine_geojson, disorder_type, event_type, sub_event_type, civilian_targeting):
    df['event_date'] = pd.to_datetime(df['event_date'])
    df['month_year'] = df['event_date'].dt.to_period('M')

    # Filter data based on the month and year of the selected date
    selected_period = pd.to_datetime(selected_date).to_period('M')
    df = df[df['month_year'] == selected_period]
    
    # Apply filters based on the widgets' current settings
    if disorder_type != 'All':
        df = df[df['disorder_type'] == disorder_type]
    if event_type != 'All':
        df = df[df['event_type'] == event_type]
    if sub_event_type != 'All':
        df = df[df['sub_event_type'] == sub_event_type]
    if civilian_targeting == 'Civilian targeting':
        df = df[df['civilian_targeting'] == 'Yes']
    elif civilian_targeting == 'Non-civilian targeting':
        df = df[df['civilian_targeting'] == 'No']

     # Aggregate data
    heatmap_data = df.groupby(['month_year', 'latitude', 'longitude', "event_type", "actor1", "actor2", "location", "source"]).agg(
        intensity=('event_id_cnty', 'count'),
        fatalities=('fatalities', 'sum')
    ).reset_index()

    tooltip_cols = [
        "event_type", 
        "actor1", "actor2", "location", "source", "fatalities"
    ]

    # filtered_data, hover_text = get_tooltip(filtered_data, tooltip_cols)
    filtered_data, hover_text = get_tooltip(heatmap_data, tooltip_cols)

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
