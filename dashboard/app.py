from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

WAREHOUSE = Path("warehouse/nyc_taxi.duckdb")
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="NYC Taxi Analytics", page_icon="🚕", layout="wide")

st.title("🚕 NYC Taxi Analytics Engineering Dashboard")
st.caption("Powered by Python → DuckDB → dbt → SQL → Streamlit")

if not WAREHOUSE.exists():
    st.error("Warehouse not found. Run `make download`, `make load`, and `make dbt-build` first.")
    st.stop()


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(WAREHOUSE), read_only=True)


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    return get_connection().execute(sql).df()


bounds = query(
    """
    select min(pickup_date) as min_date, max(pickup_date) as max_date
    from marts.fct_trips
    """
).iloc[0]

boroughs = query(
    """
    select distinct pickup_borough as borough
    from marts.fct_trips
    where pickup_borough is not null
    order by 1
    """
)["borough"].tolist()

with st.sidebar:
    st.header("Filters")
    selected_dates = st.date_input(
        "Pickup date range",
        value=(bounds["min_date"], bounds["max_date"]),
        min_value=bounds["min_date"],
        max_value=bounds["max_date"],
    )
    selected_borough = st.selectbox("Pickup borough", ["All"] + boroughs)
    st.markdown("---")
    st.markdown("**Model layer:** `marts.fct_trips`")
    st.markdown("**Warehouse:** DuckDB")

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates if isinstance(selected_dates, date) else bounds["min_date"]

borough_filter = ""
if selected_borough != "All":
    safe_borough = selected_borough.replace("'", "''")
    borough_filter = f" and pickup_borough = '{safe_borough}'"

base_filter = f"""
    pickup_date between date '{start_date}' and date '{end_date}'
    and trip_quality_flag = 'standard'
    {borough_filter}
"""

kpis = query(
    f"""
    select
        count(*) as trips,
        sum(total_amount) as revenue,
        avg(total_amount) as avg_trip_value,
        avg(tip_rate) as avg_tip_rate,
        avg(trip_distance_miles) as avg_distance
    from marts.fct_trips
    where {base_filter}
    """
).iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Trips", f"{int(kpis['trips']):,}")
c2.metric("Revenue", f"${float(kpis['revenue'] or 0):,.0f}")
c3.metric("Avg trip value", f"${float(kpis['avg_trip_value'] or 0):,.2f}")
c4.metric("Avg tip rate", f"{float(kpis['avg_tip_rate'] or 0):.1%}")
c5.metric("Avg distance", f"{float(kpis['avg_distance'] or 0):.2f} mi")

st.markdown("---")

trend = query(
    f"""
    select
        pickup_date,
        count(*) as trips,
        sum(total_amount) as revenue
    from marts.fct_trips
    where {base_filter}
    group by 1
    order by 1
    """
)

left, right = st.columns(2)
with left:
    st.subheader("Daily revenue")
    st.plotly_chart(
        px.line(trend, x="pickup_date", y="revenue", markers=True, labels={"revenue": "Revenue ($)"}),
        use_container_width=True,
    )
with right:
    st.subheader("Daily trip demand")
    st.plotly_chart(
        px.line(trend, x="pickup_date", y="trips", markers=True),
        use_container_width=True,
    )

zones = query(
    f"""
    select
        pickup_zone as zone,
        pickup_borough as borough,
        count(*) as trips,
        sum(total_amount) as revenue,
        avg(total_amount) as avg_trip_value,
        avg(revenue_per_mile) as revenue_per_mile,
        avg(tip_rate) as tip_rate
    from marts.fct_trips
    where {base_filter}
      and pickup_zone is not null
    group by 1, 2
    order by revenue desc
    limit 15
    """
)

left, right = st.columns([1.1, 0.9])
with left:
    st.subheader("Top pickup zones by revenue")
    st.plotly_chart(
        px.bar(
            zones.sort_values("revenue"),
            x="revenue",
            y="zone",
            orientation="h",
            hover_data=["borough", "trips", "avg_trip_value"],
            labels={"revenue": "Revenue ($)", "zone": "Pickup zone"},
        ),
        use_container_width=True,
    )

with right:
    st.subheader("Airport vs regular trips")
    airport = query(
        f"""
        select
            case when is_airport_trip then 'Airport' else 'Non-airport' end as trip_type,
            count(*) as trips,
            avg(total_amount) as avg_trip_value,
            avg(trip_distance_miles) as avg_distance,
            avg(tip_rate) as avg_tip_rate
        from marts.fct_trips
        where {base_filter}
        group by 1
        """
    )
    st.plotly_chart(
        px.bar(airport, x="trip_type", y="avg_trip_value", text_auto=".2f", labels={"avg_trip_value": "Avg trip value ($)"}),
        use_container_width=True,
    )

st.subheader("Demand heatmap: weekday × pickup hour")
heat = query(
    f"""
    select pickup_weekday, pickup_hour, count(*) as trips
    from marts.fct_trips
    where {base_filter}
    group by 1, 2
    """
)
heat["pickup_weekday"] = pd.Categorical(heat["pickup_weekday"], categories=WEEKDAY_ORDER, ordered=True)
pivot = heat.pivot(index="pickup_weekday", columns="pickup_hour", values="trips").fillna(0)
st.plotly_chart(
    px.imshow(
        pivot,
        aspect="auto",
        labels={"x": "Pickup hour", "y": "Weekday", "color": "Trips"},
    ),
    use_container_width=True,
)

st.subheader("Zone efficiency table")
display = zones.copy()
display["revenue"] = display["revenue"].round(2)
display["avg_trip_value"] = display["avg_trip_value"].round(2)
display["revenue_per_mile"] = display["revenue_per_mile"].round(2)
display["tip_rate"] = (display["tip_rate"] * 100).round(1)
display = display.rename(columns={"tip_rate": "tip_rate_%"})
st.dataframe(display, use_container_width=True, hide_index=True)

with st.expander("How this dashboard is built"):
    st.markdown(
        """
        The UI reads only from **dbt-modeled marts**, not raw files. Python handles ingestion, DuckDB stores the warehouse,
        dbt owns transformation/testing/lineage, and Streamlit presents decision-ready metrics. This separation keeps
        ingestion, transformation, and presentation independently maintainable.
        """
    )
