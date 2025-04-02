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
    data = data.iloc[:,1:]

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