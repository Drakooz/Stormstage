"""StormStage dashboard for weather-driven precomputed replays."""

import pandas as pd
import pydeck as pdk
import streamlit as st

from replay_data import (
    COMPARISON_POLICIES,
    POLICIES,
    STORM_DAYS,
    get_decision_log,
    get_incidents,
    get_metrics,
    get_truck_positions,
    get_zones,
)


DEFAULT_HOUR = 15
STATUS_COLORS = {
    "staged": [2, 132, 199],
    "responding": [220, 38, 38],
    "on_scene": [245, 158, 11],
    "returning": [22, 163, 74],
    "relocating": [147, 51, 234],
}


def load_zones() -> pd.DataFrame:
    """Validate the replay grid provided by B's interface."""
    zones = get_zones()
    required_columns = {"zone_id", "lat", "lon"}
    if not required_columns.issubset(zones.columns):
        raise ValueError("Replay zones must contain zone_id, lat, and lon columns.")
    zones = zones[["zone_id", "lat", "lon"]].copy()
    if zones.empty or zones.isna().any().any() or zones["zone_id"].duplicated().any():
        raise ValueError("Replay zones must contain unique zone IDs and complete coordinates.")
    zones["lat"] = pd.to_numeric(zones["lat"], errors="raise")
    zones["lon"] = pd.to_numeric(zones["lon"], errors="raise")
    if not zones["lat"].between(-90, 90).all() or not zones["lon"].between(-180, 180).all():
        raise ValueError("Replay zones contain coordinates outside valid latitude/longitude ranges.")
    return zones


def show_truck_map(zones: pd.DataFrame, trucks: pd.DataFrame, shared_view: dict[str, float]) -> None:
    """Fix both comparison cameras to the shared zone-centered viewport."""
    map_trucks = trucks.copy()
    map_trucks["color"] = [STATUS_COLORS.get(status, [100, 116, 139]) for status in trucks["status"]]
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(**shared_view),
        # A view-level state overrides each chart's retained interactive camera.
        views=[pdk.View("MapView", controller=False, view_state=shared_view)],
        layers=[
            pdk.Layer(
                "ScatterplotLayer", data=zones[["lat", "lon"]],
                get_position="[lon, lat]", get_fill_color=[148, 163, 184],
                get_radius=40, radius_min_pixels=3,
            ),
            pdk.Layer(
                "ScatterplotLayer", data=map_trucks,
                get_position="[lon, lat]", get_fill_color="color",
                get_radius=140, radius_min_pixels=3,
            ),
        ],
    ))
    st.caption("Gray: replay zones · Blue: staged · Red: responding · Amber: on scene · "
               "Green: returning · Purple: relocating. Overlapping trucks may share a marker.")
    st.dataframe(trucks[["unit_id", "zone_id", "status", "lat", "lon"]], hide_index=True, width="stretch")


def show_metrics(day: str, policy: str) -> None:
    values = get_metrics(day, policy)
    st.subheader(policy)
    st.caption(f"WEATHER-DRIVEN PRECOMPUTED REPLAY · {day} · Full-day simulated replay metrics.")
    st.metric("Average response time", f"{values['avg_response_min']:.1f} min")
    st.metric("90th percentile response time", f"{values['p90_response_min']:.1f} min")
    st.metric("Percent reached within 15 minutes", f"{values['pct_within_15']:.1f}%")
    st.metric("Truck relocations", str(values["relocation_count"]))
    if "activations" in values:
        st.metric("On-call activations", str(values["activations"]))
    if "truck_hours" in values:
        st.metric("Truck-hours", f"{values['truck_hours']:.1f}")


def main() -> None:
    st.set_page_config(page_title="StormStage", page_icon="❄️", layout="wide")
    st.title("StormStage")
    st.markdown("Adaptive tow-truck staging for Calgary winter incidents.")
    st.info("WEATHER-DRIVEN PRECOMPUTED REPLAY: these exports were generated with A's integrated "
            "weather-driven forecast. Metrics are simulated replay outcomes, not field-deployment results.")

    if not STORM_DAYS:
        st.error("No precomputed replay days are available.")
        st.stop()

    with st.sidebar:
        st.header("Replay controls")
        day = st.selectbox("Storm day", STORM_DAYS)
        hour = st.slider("Current hour", min_value=0, max_value=23, value=DEFAULT_HOUR, format="%02d:00")
        policy = st.selectbox("Policy", POLICIES, index=POLICIES.index("StormStage + on-call"))
        st.radio("Play / Pause (placeholder)", ("Pause", "Play"), horizontal=True)
        st.caption("Precomputed replay in Calgary local time (America/Edmonton). "
                   "Play/Pause does not advance time yet; use the hour slider.")

    try:
        zones = load_zones()
        selected_trucks = get_truck_positions(day, policy, hour)
        comparison_trucks = {
            name: get_truck_positions(day, name, hour)
            for name in COMPARISON_POLICIES
        }
        decision_log = get_decision_log(day, policy, hour)
        incidents = get_incidents(day, policy, hour)
    except (OSError, ValueError, KeyError, pd.errors.ParserError) as error:
        st.error(f"Unable to load the precomputed replay: {error}")
        st.stop()

    st.caption(f"WEATHER-DRIVEN PRECOMPUTED REPLAY · {day} · {hour:02d}:00 Calgary local time · Selected policy: {policy}")
    st.subheader("Calgary zones")
    st.map(zones[["lat", "lon"]])
    st.caption(f"{len(zones)} citywide grid zones used by the precomputed replay.")
    shared_view = {
        "latitude": float((zones["lat"].min() + zones["lat"].max()) / 2),
        "longitude": float((zones["lon"].min() + zones["lon"].max()) / 2),
        "zoom": 10,
        "pitch": 0,
        "bearing": 0,
    }
    with st.expander(f"Selected policy — replay truck positions and metrics: {policy}"):
        st.caption(f"On-duty truck positions at {hour:02d}:00.")
        show_truck_map(zones, selected_trucks, shared_view)
        show_metrics(day, policy)

    st.subheader("Staging comparison — precomputed truck positions")
    st.caption(f"Both panels show on-duty trucks at {hour:02d}:00. Main comparison: "
               + " vs. ".join(COMPARISON_POLICIES) + ".")
    for column, name in zip(st.columns(2), COMPARISON_POLICIES):
        with column:
            st.subheader(name)
            show_truck_map(zones, comparison_trucks[name], shared_view)

    st.divider()
    st.subheader("Results — weather-driven precomputed replay")
    st.warning("Full-day metrics for the selected storm day, independent of the hour slider. "
               "Metrics are simulated replay outcomes, not field-deployment results.")
    for column, name in zip(st.columns(2), COMPARISON_POLICIES):
        with column:
            show_metrics(day, name)

    st.divider()
    st.subheader("Decision log — precomputed replay")
    st.caption(f"Recorded decisions for {policy} through {hour:02d}:59 on {day}, Calgary local time.")
    for message in decision_log:
        st.write(message)

    st.divider()
    st.subheader("Incidents — precomputed replay")
    st.caption(f"{len(incidents)} incidents started through {hour:02d}:59 on {day} for {policy}. "
               "Response times are completed replay outcomes, including responses after the selected hour.")
    st.dataframe(incidents[["time", "lat", "lon", "unit_id", "response_min"]],
                 hide_index=True, width="stretch")


if __name__ == "__main__":
    main()
