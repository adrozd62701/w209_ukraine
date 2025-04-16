import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.colors as pc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def generate_conflict_map(data, selected_date, event_type, civilian_targeting):
    data = data.copy()
    data['event_date'] = pd.to_datetime(data['event_date'], errors="coerce")
    selected_period = pd.to_datetime(selected_date).to_period("M")

    data = data[data['event_date'].dt.to_period("M") == selected_period]

    if event_type != "All":
        data = data[data['event_type'] == event_type]

    if civilian_targeting != "All":
        if civilian_targeting == "Civilian targeting":
            data = data[data['civilian_targeting'] == "Civilian targeting"]
        elif civilian_targeting == "Non-civilian targeting":
            data = data[data['civilian_targeting'].isna()]


    if data.empty:
        return None

    data = data.fillna("")
    data['fatalities'] = data['fatalities'].fillna(0)

    fig = go.Figure()

    # blue density map for general intensity
    fig.add_trace(go.Densitymapbox(
        lat=data['latitude'],
        lon=data['longitude'],
        z=np.ones(len(data)),
        radius=20,
        opacity=0.4,
        colorscale='Blues',
        name="Conflict Intensity"
    ))

    # sub-event type markers (colored and in legend)
    fatal_data = data[data['fatalities'] > 0].copy()
    unique_subtypes = fatal_data['sub_event_type'].unique()

    color_palette = pc.qualitative.Set1 + pc.qualitative.Set2 + pc.qualitative.Set3
    color_map = {subtype: color_palette[i % len(color_palette)] for i, subtype in enumerate(unique_subtypes)}

    for subtype in unique_subtypes:
        sub_data = fatal_data[fatal_data['sub_event_type'] == subtype]
        customdata = np.stack([
            sub_data['event_type'],
            sub_data['sub_event_type'],
            sub_data['actor1'],
            sub_data['actor2'],
            sub_data['location'],
            sub_data['source'],
            sub_data['fatalities']
        ], axis=-1)

        fig.add_trace(go.Scattermapbox(
            lat=sub_data['latitude'],
            lon=sub_data['longitude'],
            mode='markers',
            marker=dict(
                size=np.clip(sub_data['fatalities'] * 3, 5, 50),
                color=color_map[subtype],
                opacity=0.85,
                sizemode='area'
            ),
            name=subtype,
            customdata=customdata,
            hovertemplate="""
                <b>Event Type:</b> %{customdata[0]}<br>
                <b>Sub Event Type:</b> %{customdata[1]}<br>
                <b>Actor 1:</b> %{customdata[2]}<br>
                <b>Actor 2:</b> %{customdata[3]}<br>
                <b>Location:</b> %{customdata[4]}<br>
                <b>Source:</b> %{customdata[5]}<br>
                <b>Fatalities:</b> %{customdata[6]}<br>
                <extra></extra>
            """
        ))

    # final layout
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5,
        mapbox_center={"lat": 48.3794, "lon": 31.1656},
        height=650,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(
            title="Fatality Type",
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.01,
            bgcolor="white",
            borderwidth=1
        )
    )

    return fig


    
def main(data, ukraine_geojson, min_date, max_date):
    # animation
    st.markdown("## Conflict Timeline Overview")
    st.write(
        "This animated map shows the general progression of conflict intensity across Ukraine "
        "from the beginning of the war through today. Each frame represents a monthly snapshot, "
        "with conflict density shown in blue and fatality events marked in dark blue."
    )
    st.image("animations/conflict_overview.gif")

    st.markdown("---")

    # interactive map
    st.markdown("### **Conflict Map**")
    st.write(
        "Explore specific snapshots of the conflict by selecting a key month from the dropdown below. "
        "You can further filter by event type and whether civilians were targeted."
    )

   
    data = data.copy()
    data['event_date'] = pd.to_datetime(data['event_date'], errors="coerce")

    # key event timeline
    month_descriptions = {
        "2022-02": "February 2022 – Initial Invasion & Counteroffensives",
        "2022-04": "April 2022 – Russian Retreat from Northern Ukraine",
        "2022-05": "May 2022 – Mariupol Falls After Prolonged Siege",
        "2022-09": "September 2022 – Kharkiv Counteroffensive",
        "2022-11": "November 2022 – Ukraine Recaptures Kherson",
        "2024-08": "August 2024 – Cross-border Raids into Russia",
        "2025-02": "February 2025 – Missile Strikes & Intelligence Breakdown"
    }

    # dict to lists for dropdown
    month_keys = list(month_descriptions.keys())
    month_labels = list(month_descriptions.values())

    # month dropdown
    selected_label = st.selectbox(
        "Select a key conflict month to explore:",
        options=month_labels
    )
    selected_month_key = month_keys[month_labels.index(selected_label)]
    selected_date = pd.to_datetime(selected_month_key, format="%Y-%m")

    # filter selected month 
    selected_period = selected_date.to_period("M")
    month_data = data[data['event_date'].dt.to_period("M") == selected_period]

    if month_data.empty:
        st.warning("No data available for this selected month.")
        return

    # filter event
    available_event_types = month_data['event_type'].dropna().unique().tolist()
    event_type_options = ["All"] + sorted(available_event_types)
    selected_event_type = st.selectbox("Conflict Type", options=event_type_options)

    # filter civilian 
    if selected_event_type == "All":
        filtered_data_for_targeting = month_data.copy()
    else:
        filtered_data_for_targeting = month_data[month_data['event_type'] == selected_event_type]

    targeting_options = ["All"]
    if "Civilian targeting" in filtered_data_for_targeting['civilian_targeting'].unique():
        targeting_options.append("Civilian targeting")
    if filtered_data_for_targeting['civilian_targeting'].isna().any():
        targeting_options.append("Non-civilian targeting")

    selected_civilian_targeting = st.selectbox("Civilian Targeting", options=targeting_options)

    st.write(" ")
    fig = generate_conflict_map(month_data, selected_date, selected_event_type, selected_civilian_targeting)

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No conflict events match the selected filters for this month.")
