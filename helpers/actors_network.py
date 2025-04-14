import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import re
import calendar
from datetime import datetime

def main(df):
    # st.set_page_config(layout="wide")
    st.title("Conflict Events (Battles) Between Groups")

    # df = pd.read_csv("Jan24_ACLED.gz", compression="gzip")

    # Filter and prep
    df = df[df["event_type"] == "Battles"].copy()
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["year"] = df["event_date"].dt.year
    df["month"] = df["event_date"].dt.month

    def simplify_group(name):
        if pd.isnull(name):
            return ""
        name = re.sub(r"\(\d{4}-?\d{0,4}\)", "", name).strip()
        name = re.sub(r"\b(International Legion|Main Directorate of Intelligence|Navy|1st Donetsk Army Corps|Territorial Defense Forces|Air Force|National Guard|Marines|State Border Guard Service|Special Forces|Chechen Battalion of Ramzan Kadyrov|2nd Luhansk Army Corps|Federal Security Service|Security Service of Ukraine|Kastus Kalinouski Regiment|Municipal Guard|Aidar Battallion|State Emergency Service of Ukraine)\b", "", name, flags=re.IGNORECASE).strip()
        name = re.sub(r"\s{2,}", " ", name).strip()
        return name if name else "Unknown"

    df["actor1"] = df["actor1"].apply(simplify_group)
    df["actor2"] = df["actor2"].apply(simplify_group)

    # Valid groups
    group_counts = pd.concat([df["actor1"], df["actor2"]]).value_counts()
    valid_groups = sorted([g for g in group_counts.index if g and group_counts[g] > 0])

    st.markdown("### **Select Two Groups**")
    st.info("Groups represent organized forces involved in battles, such as military units, paramilitaries, and other organizations")

    selected_group1 = st.selectbox("Select Primary Group", ["None"] + valid_groups, index=0)

    if selected_group1 != "None":
        compatible_df = df[(df["actor1"] == selected_group1) | (df["actor2"] == selected_group1)]
        compatible_list = pd.unique(compatible_df[["actor1", "actor2"]].values.ravel("K"))
        compatible_list = sorted([g for g in compatible_list if g and g != selected_group1])
    else:
        compatible_list = valid_groups

    selected_group2 = st.selectbox("Select Opposing Group", ["None"] + compatible_list, index=0)

    if selected_group1 == "None" or selected_group2 == "None":
        st.warning("Please select both groups to proceed.")
        # return
    else:
        # Filter events between selected groups
        mask_groups = (
            ((df["actor1"] == selected_group1) | (df["actor2"] == selected_group1)) &
            ((df["actor1"] == selected_group2) | (df["actor2"] == selected_group2))
        )
        df_groups = df[mask_groups].copy()

        if df_groups.empty:
            st.warning("No events detected between the selected groups.")
            # return
        else:
            total_events = len(df_groups)
            #st.markdown(f"**Total conflict events between `{selected_group1}` and `{selected_group2}`: {total_events}**")

            # Bar Chart: Conflict Initiation by Group
            st.subheader(f"**Conflict Initiation Comparison between Groups**")
            st.markdown("""
            This bar graph shows the number of conflict events each group **initiated**.  
            """)

            initiations = df_groups.groupby("actor1").size().reset_index(name="count")
            initiations = initiations[initiations["actor1"].isin([selected_group1, selected_group2])]

            group_event_counts = {
                selected_group1: initiations[initiations["actor1"] == selected_group1]["count"].sum(),
                selected_group2: initiations[initiations["actor1"] == selected_group2]["count"].sum(),
            }

            sorted_groups = sorted(group_event_counts.items(), key=lambda x: -x[1])
            bar_data = pd.DataFrame({
                "Group": [g[0] for g in sorted_groups],
                "Initiated Events": [g[1] for g in sorted_groups],
                "Color": ["indianred", "steelblue"]
            })

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=bar_data["Group"],
                y=bar_data["Initiated Events"],
                marker_color=bar_data["Color"],
                text=bar_data["Initiated Events"],
                textposition="auto",
                name="Events Initiated"
            ))

            for i, row in bar_data.iterrows():
                if row["Initiated Events"] == 0:
                    fig.add_annotation(
                        x=row["Group"],
                        y=0,
                        text="No initiated events",
                        showarrow=False,
                        font=dict(color="gray", size=12),
                        yshift=20
                    )

            fig.update_layout(
                yaxis_title="Number of Events Initiated",
                xaxis_title="Group",
                margin=dict(l=10, r=10, t=30, b=10),
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Heatmap of Monthly Activity
            st.subheader("**Heatmap: Conflict Events by Month and Year**")
            st.markdown("""
            This heatmap shows the **number of conflict events per month and year** between the selected groups.  
            It helps highlight **seasonal or yearly conflict trends**.
            """)

            years = sorted(df_groups["year"].dropna().unique())
            months = list(range(1, 13))
            grid = pd.DataFrame([(y, m) for y in years for m in months], columns=["year", "month"])

            monthly_counts = (
            df_groups.groupby(["year", "month"], as_index=False)
            .agg(count=("event_type", "count")))
            heatmap_data = pd.merge(grid, monthly_counts, on=["year", "month"], how="left").fillna(0)
            heatmap_data = heatmap_data.drop_duplicates(subset=["year", "month"])


            heatmap_data["date"] = pd.to_datetime(dict(year=heatmap_data.year, month=heatmap_data.month, day=1))
            cutoff_date = datetime(2025, 3, 31)
            heatmap_data["data_status"] = heatmap_data["date"].apply(
                lambda x: "Data Pending" if x > cutoff_date else "Data Available"
            )

            heatmap_data["display_count"] = heatmap_data.apply(
                lambda row: None if row["data_status"] == "Data Pending" else row["count"], axis=1
            )

            heatmap_data["month_name"] = heatmap_data["month"].apply(lambda x: calendar.month_abbr[x])
            month_order = list(calendar.month_abbr[1:])  

            heatmap = alt.Chart(heatmap_data).mark_rect(
            stroke='white',  
            strokeWidth=0.5  
            ).encode(
            x=alt.X(
                "month_name:O",
                sort=month_order,
                title="Month",
                axis=alt.Axis(labelAngle=0),
                scale=alt.Scale(paddingInner=0, paddingOuter=0)
            ),
            y=alt.Y("year:O", title="Year"),
            color=alt.condition(
                alt.datum.data_status == "Data Pending",
                alt.value("#eeeeee"),  
                alt.Color("display_count:Q", scale=alt.Scale(scheme="cividis"), title="Event Count")
            ),
            tooltip=[
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip("month_name:O", title="Month"),
                alt.Tooltip("count:Q", title="Event Count")    ]
            ).properties(width=700, height=400)



            st.altair_chart(heatmap, use_container_width=True)

if __name__ == "__main__":
    main()
