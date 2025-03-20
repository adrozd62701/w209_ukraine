import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import json

def load_data():
    data_path = 'data/Ukraine_Black_Sea_2020_2025_Jan24.csv.gz'
    data = pd.read_csv(data_path, compression='gzip')
    data = data.iloc[:,2:]

    with open('data/ukraine_border.geojson') as f:
        ukraine_geojson = json.load(f)
    return data, ukraine_geojson


def get_tooltip(filtered_data, tooltip_cols):
    filtered_data[tooltip_cols] = filtered_data[tooltip_cols].fillna("")
    
    # st.dataframe(filtered_data)
    # st.dataframe(filtered_data[tooltip_cols].values.tolist())
    hover_text = filtered_data[tooltip_cols].values.tolist()

    # st.dataframe(filtered_data)
    # filtered_data["hover_text"] = filtered_data.apply(lambda row: (
    #     f"<b>Disorder Type:</b> {row['disorder_type']}<br>"
    #     f"<b>Event Type:</b> {row['event_type']}<br>"
    #     f"<b>Sub-event Type:</b> {row['sub_event_type']}<br>"
    #     f"<b>Actor 1:</b> {row['actor1']}<br>"
    #     f"<b>Actor 2:</b> {row['actor2']}<br>"
    #     f"<b>Location:</b> {row['location']}<br>"
    #     f"<b>Source:</b> {row['source']}"
    # ), axis=1)

    return filtered_data, hover_text

def generate_conflict_map(df, selected_date, ukraine_geojson):
    df['event_date'] = pd.to_datetime(df['event_date'])

    heatmap_data = df.groupby(['event_date', 'latitude', 'longitude',
                               "disorder_type",
        "actor1", "actor2", "location", "source"]).agg(
        intensity=('event_type', 'count'),
        fatalities=('fatalities', 'sum')
    ).reset_index()

    # st.dataframe(heatmap_data)

    filtered_data = heatmap_data[heatmap_data['event_date'] == selected_date]

    tooltip_cols = [
        "disorder_type", 
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
            "<b>Disorder:</b> %{customdata[0]}<br>" +
            "<b>Actor 1:</b> %{customdata[1]}<br>" +
            "<b>Actor 2:</b> %{customdata[2]}<br>" +
            "<b>Location:</b> %{customdata[3]}<br>" +
            "<b>Source:</b> %{customdata[4]}<br>" +
            "<b>Fatalities:</b> %{customdata[5]}<br>" +
            "<extra></extra>"
    ))

    # 3. Add density layer for conflict intensity
    fig.add_trace(go.Densitymapbox(
        lat=filtered_data['latitude'],
        lon=filtered_data['longitude'],
        z=filtered_data['intensity'],
        radius=17,
        colorscale='Viridis',
        showscale=True,
        name="Conflict Intensity"
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

