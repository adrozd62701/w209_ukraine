import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

def load_data():
    data_path = 'data/Ukraine_Black_Sea_2020_2025_Jan24.csv.gz'
    data = pd.read_csv(data_path, compression='gzip')
    data = data.iloc[:,2:]
    return data


def generate_conflict_map(df, selected_date):
    df['event_date'] = pd.to_datetime(df['event_date'])

    heatmap_data = df.groupby(['event_date', 'latitude', 'longitude']).agg(
        intensity=('event_type', 'count'),
        fatalities=('fatalities', 'sum')
    ).reset_index()

    filtered_data = heatmap_data[heatmap_data['event_date'] == selected_date]

    fig = go.Figure()

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
        name="Fatalities"
    ))

    fig.add_trace(go.Densitymapbox(
        lat=filtered_data['latitude'],
        lon=filtered_data['longitude'],
        z=filtered_data['intensity'],
        radius=17,
        colorscale='Viridis',
        showscale=True,
        name="Conflict Intensity"
    ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=4.7,
        mapbox_center={"lat": 47.6036, "lon": 34.3615},
        title=f"Conflict Intensity and Fatalities on {selected_date.strftime('%Y-%m-%d')}",
        height=600,
        width=1200,
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    return fig
