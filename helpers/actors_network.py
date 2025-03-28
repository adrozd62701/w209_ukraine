import streamlit as st
import pandas as pd
import altair as alt
import re
import calendar

def main(df):
    
    # st.set_page_config(layout="wide")  

    # st.title("Conflict Events (Battles) Between Actors")
    
    # df = pd.read_csv("Jan24_ACLED.gz", compression="gzip")
    
    # --------------------------------------------------------------------------------
    # 1. Filter Data for Battles and Prepare Columns
    # --------------------------------------------------------------------------------
    df = df[df["event_type"] == "Battles"].copy()
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["year"] = df["event_date"].dt.year
    df["month"] = df["event_date"].dt.month
    
    def simplify_actor_name(name):
        name = re.sub(r"\(\d{4}-?\d{0,4}\)", "", name).strip()
        name = re.sub(r"\b(International Legion|Main Directorate of Intelligence|Navy|1st Donetsk Army Corps|Territorial Defense Forces|Air Force|National Guard|Marines|State Border Guard Service|Special Forces|Chechen Battalion of Ramzan Kadyrov|2nd Luhansk Army Corps|Federal Security Service|Security Service of Ukraine|Kastus Kalinouski Regiment|Municipal Guard|Aidar Battallion|State Emergency Service of Ukraine)\b", "", name, flags=re.IGNORECASE).strip()
        return name

    df["actor1"] = df["actor1"].apply(simplify_actor_name)
    df["actor2"] = df["actor2"].apply(simplify_actor_name)

    # --------------------------------------------------------------------------------
    # 2. Actor Selection
    # --------------------------------------------------------------------------------
    all_actors = pd.unique(df[["actor1", "actor2"]].values.ravel("K"))
    actor_options = [a for a in all_actors if pd.notnull(a)]
    
    actor_options = ["(None)"] + sorted(actor_options)
    
    st.sidebar.markdown("### **Select Two Actors**")
    selected_actor1 = st.sidebar.selectbox("Actor 1", actor_options, index=0)
    selected_actor2 = st.sidebar.selectbox("Actor 2", actor_options, index=0)

    if selected_actor1 == "(None)" or selected_actor2 == "(None)":
        st.warning("Please pick two actors to begin")
        # st.stop()
    
    if (selected_actor1 == selected_actor2) & ((selected_actor1 != "(None)")|(selected_actor2 != "(None)")):
        st.warning("The two actors must be different")
        # st.stop()
    if (selected_actor1 != "(None)")&(selected_actor2 != "(None)")&(selected_actor1!=selected_actor2):
        # --------------------------------------------------------------------------------
        # 3. Filter Rows Where both Selected Actors Are Present
        # --------------------------------------------------------------------------------
        mask_actors = (
            ((df["actor1"] == selected_actor1) | (df["actor2"] == selected_actor1)) &
            ((df["actor1"] == selected_actor2) | (df["actor2"] == selected_actor2))
        )
        df_actors = df[mask_actors].copy()

        # --------------------------------------------------------------------------------
        # 4. If No Events, Display a Message and Stop
        # --------------------------------------------------------------------------------
        if df_actors.empty:
            st.warning("No events detected between groups")
            st.stop()

        # --------------------------------------------------------------------------------
        # 5. Display Total Events Between Actors
        # --------------------------------------------------------------------------------
        total_events = len(df_actors)
        st.markdown(f"**Total conflict events between {selected_actor1} and {selected_actor2}: {total_events}**")

        # --------------------------------------------------------------------------------
        # 6. Bar Chart: Count Events Where the Actor Appears as Actor1
        #    (Always show both actors, even if one has zero events)
        # --------------------------------------------------------------------------------
        df_bar = df_actors[df_actors["actor1"].isin([selected_actor1, selected_actor2])]
        counts_series = df_bar["actor1"].value_counts()

        actor_counts = counts_series.reindex([selected_actor1, selected_actor2], fill_value=0).reset_index()
        actor_counts.columns = ["actor", "count"]

        st.subheader("**Conflict Events Instigated by each Actor**")
        

        sorted_actors = actor_counts.sort_values("count", ascending=False)["actor"].tolist()

        bar_chart = (
        alt.Chart(actor_counts)
        .mark_bar()
        .encode(
            x=alt.X(
                "actor:O",
                sort=sorted_actors,  
                title="Actor",
                axis=alt.Axis(labelAngle=0, labelLimit=500, labelOverlap="greedy")
            ),
            y=alt.Y("count:Q", title="Number of Events"),
            tooltip=["actor", "count"],
            color=alt.Color(
                "actor:N",
                scale=alt.Scale(domain=sorted_actors, range=["#1f77b4", "#aec7e8"]),
                legend=alt.Legend(labelLimit=1000, labelOverlap="greedy", orient="top")
            )
        )
        .properties(width=800, height=400)
        )


        st.altair_chart(bar_chart, use_container_width=False)
        
        # --------------------------------------------------------------------------------
        # 7. Heatmap: Events by Month and Year (Only Years with Events)
        # --------------------------------------------------------------------------------
        st.subheader("**Heatmap: Conflict Events by Month and Year between the Actors**")
        
        years_with_events = sorted(df_actors["year"].unique())
        months = list(range(1, 13))
        
        grid = pd.DataFrame([(y, m) for y in years_with_events for m in months], columns=["year", "month"])
        
        counts = df_actors.groupby(["year", "month"]).size().reset_index(name="count")
        heatmap_data = pd.merge(grid, counts, on=["year", "month"], how="left").fillna(0)
        
        heatmap_data["month_name"] = heatmap_data["month"].apply(lambda x: calendar.month_abbr[x])  # Short names: "Jan", "Feb", etc.

        heatmap_chart = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X("month_name:O", title="Month", axis=alt.Axis(labelAngle=0, labelLimit=60)),
            y=alt.Y("year:O", title="Year"),
            color=alt.Color(
                "count:Q", 
                scale=alt.Scale(scheme="blues"), 
                title="Event Count",
                legend=alt.Legend(labelLimit=1000, labelOverlap="greedy")
            ),
            tooltip=["year", "month_name", "count"]
        ).properties(width=600, height=400)
        
        st.altair_chart(heatmap_chart, use_container_width=True)
        
        # --------------------------------------------------------------------------------
        # 8. Filter Events by Selected Year, Month, and Keyword
        # --------------------------------------------------------------------------------
        st.subheader("**Filter Conflict Events by Year, Month, and Keyword**")
        
        month_names = {m: calendar.month_name[m] for m in months}

        selected_heatmap_year = st.selectbox("Select Year", years_with_events)
        selected_heatmap_month = st.selectbox("Select Month", options=months, format_func=lambda m: month_names[m])
        keyword = st.text_input("Enter a keyword to filter conflict events")
        
        df_filtered = df_actors[
            (df_actors["year"] == selected_heatmap_year) &
            (df_actors["month"] == selected_heatmap_month)
        ].copy()

        if keyword:
            df_filtered = df_filtered[df_filtered["notes"].str.contains(keyword, case=False, na=False)]

        st.markdown("### **Conflict Event Details**")
        df_filtered['event_date'] = df_filtered['event_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        df_filtered.rename(columns={'event_date':'Event Date','notes':'Event Description'},inplace=True)
        df_filtered = df_filtered.sort_values(by='Event Date')

        column_config = {
            "Event Date": st.column_config.DateColumn("Event Date", width="small"),
            "Event Description": st.column_config.TextColumn("Event Description", width="medium")
        }

        st.dataframe(df_filtered[["Event Date", "Event Description"]].reset_index(drop=True), hide_index=True, column_config=column_config)