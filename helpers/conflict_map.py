import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
        radius=20,
        opacity=0.8,
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
