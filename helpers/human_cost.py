import pandas as pd
import streamlit as st
import altair as alt

def generate_fatalities_by_event_type(df):
    data = df.copy()
    data = data[data['event_type']!='Riots']
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
        # "Riots": "#d62728",
        "Strategic developments": "#9467bd",
        "Violence against civilians": "#d62728"
    }

    # Create Streamlit dropdown
    st.markdown("### **Human Cost**")
    # selected_event_type = st.sidebar.radio("Select Event Type:", event_types, index=0, horizontal=False)
    selected_event_type = st.radio("Select Event Type:", event_types, index=0, horizontal=False)
    # st.sidebar.divider()

    # Apply filtering logic
    if selected_event_type != "All Event Types":
        weekly_data = weekly_data[weekly_data["event_type"] == selected_event_type]
        # detail_data = detail_data[detail_data["event_type"] == selected_event_type]

    color_scale = alt.Scale(domain=list(color_mapping.keys()), range=list(color_mapping.values()))

    
    # Area Chart
    area_chart = alt.Chart(weekly_data).mark_area(opacity=0.7).encode(
        x=alt.X("week:T", 
                title="Week of", 
                axis=alt.Axis(format="%m/%d/%Y", ticks=True, tickCount="month"),
               ),
        y=alt.Y("fatalities:Q", title="Total Fatalities"),
        color=alt.Color("event_type:N", title="Event Type", scale=color_scale,
                        legend=alt.Legend(
                            orient="bottom",  # Move legend to bottom
                            # direction="horizontal",  # Arrange legend items horizontally
                            titleAnchor="middle"  # Center the legend title
                        )),
        tooltip=[
            alt.Tooltip("week:T", title="Week of"),
            alt.Tooltip("event_type:N", title="Event Type"),
            alt.Tooltip("fatalities:Q", title="Fatalities"),
            alt.Tooltip("description:N", title="Major News"),            
            # alt.Tooltip("url:N", title="URL"),
            ],
        # href='url'
    ).properties(
        title="Fatalities by Event Type",
        width=700,
        height=500
    )



    news_points = weekly_data[weekly_data["description"] != ""]

    # Circular markers for news articles
    news_markers = alt.Chart(news_points).mark_circle(size=100, color="black", opacity=0.8).encode(
        x="week:T",
        y="fatalities:Q",
        tooltip=[
            alt.Tooltip("week:T", title="Week of"),
            alt.Tooltip("event_type:N", title="Event Type"),
            alt.Tooltip("fatalities:Q", title="Fatalities"),
            alt.Tooltip("description:N", title="Major News"),
            # alt.Tooltip("url:N", title="URL")

        ]
    )

    url_selection = alt.selection_point(fields=['url'],nearest=False, on='click')

    # Larger invisible hit area for better interaction
    news_hit_area = alt.Chart(news_points).mark_point(size=1000, opacity=0).encode(
        x="week:T",
        y="fatalities:Q",
        tooltip=[
            alt.Tooltip("week:T", title="Week of"),
            alt.Tooltip("event_type:N", title="Event Type"),
            alt.Tooltip("fatalities:Q", title="Fatalities"),
            alt.Tooltip("description:N", title="Major News"),
            # alt.Tooltip("url:N", title="URL")

        ],
        href='url'
    ).add_params(url_selection)

    return area_chart + news_markers + news_hit_area


