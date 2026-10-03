"""First StormStage dashboard shell, using explicitly labeled demo fixtures."""

from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

from mock_data import (
    COMPARISON_POLICIES,
    DEFAULT_HOUR,
    MOCK_METRICS,
    MOCK_STORM_DAYS,
    POLICIES,
    get_mock_decision_log,
    get_mock_truck_positions,
)


ZONES_PATH = Path(__file__).resolve().parent / "zones.csv"


def load_zones() -> pd.DataFrame:
    """Read the current repository zone schema without caching teammate data."""
    zones = pd.read_csv(ZONES_PATH, dtype={"zone_id": str})
    required_columns = {"zone_id", "lat", "lon"}
    if not required_columns.issubset(zones.columns):
        raise ValueError("zones.csv must contain zone_id, lat, and lon columns.")
    zones = zones[["zone_id", "lat", "lon"]].copy()
    if zones.empty or zones.isna().any().any() or zones["zone_id"].duplicated().any():
        raise ValueError("zones.csv must contain unique zone IDs and complete coordinates.")
    zones["lat"] = pd.to_numeric(zones["lat"], errors="raise")
    zones["lon"] = pd.to_numeric(zones["lon"], errors="raise")
    if not zones["lat"].between(-90, 90).all() or not zones["lon"].between(-180, 180).all():
        raise ValueError("zones.csv contains coordinates outside valid latitude/longitude ranges.")
    return zones


def show_truck_map(zones: pd.DataFrame, trucks: pd.DataFrame, shared_view: dict[str, float]) -> None:
    """Fix both comparison cameras to the shared zone-centered viewport."""
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
                "ScatterplotLayer", data=trucks[["lat", "lon"]],
                get_position="[lon, lat]", get_fill_color=[2, 132, 199],
                get_radius=140, radius_min_pixels=3,
            ),
        ],
    ))
    st.caption("Gray: real zone locations · Blue: mock truck positions (overlaps may share a marker).")
    st.dataframe(trucks[["unit_id", "zone_id"]], hide_index=True, width="stretch")


def show_metrics(policy: str) -> None:
    values = MOCK_METRICS[policy]
    st.subheader(policy)
    st.caption("MOCK / DEMO — static placeholders, not measured results.")
    st.metric("Average response time", f"{values['avg_response_min']:.1f} min")
    st.metric("90th percentile response time", f"{values['p90_response_min']:.1f} min")
    st.metric("Percent reached within 15 minutes", f"{values['pct_within_15']:.0f}%")
    st.metric("Truck relocations", str(values["relocation_count"]))


def main() -> None:
    st.set_page_config(page_title="StormStage", page_icon="❄️", layout="wide")
    st.title("StormStage")
    st.markdown("Adaptive tow-truck staging for Calgary winter incidents.")
    st.info("MOCK / DEMO: truck positions, storm days, metrics, and decision messages are illustrative. "
            "Zone coordinates come from zones.csv. No forecast or simulator is connected.")

    with st.sidebar:
        st.header("Replay controls")
        day = st.selectbox("Storm day (mock)", MOCK_STORM_DAYS)
        hour = st.slider("Current hour", min_value=0, max_value=23, value=DEFAULT_HOUR, format="%02d:00")
        policy = st.selectbox("Policy", POLICIES, index=POLICIES.index("StormStage"))
        st.radio("Play / Pause (placeholder)", ("Pause", "Play"), horizontal=True)
        st.caption("Mock replay controls. Play/Pause does not advance time yet; use the hour slider. "
                   "Storm days share the same demo fixtures.")

    try:
        zones = load_zones()
        # TODO A: Consume teammate forecast DataFrame[zone_id, expected_incidents]
        # here for a future demand view. Do not import or call the forecast stub.

        # TODO B: Consume simulator per-incident response log and per-hour truck
        # positions here; replace these mock positions with the selected replay hour.
        selected_trucks = get_mock_truck_positions(zones, policy, hour)
        comparison_trucks = {
            name: get_mock_truck_positions(zones, name, hour)
            for name in COMPARISON_POLICIES
        }
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Unable to load the zone map: {error}")
        st.stop()

    st.caption(f"Mock replay · {day} · {hour:02d}:00 · Selected policy: {policy}")
    st.subheader("Calgary zones")
    st.map(zones[["lat", "lon"]])
    st.caption(f"{len(zones)} real zone locations from the repository's zones.csv.")
    with st.expander(f"Selected policy — mock truck assignments: {policy}"):
        st.dataframe(selected_trucks, hide_index=True, width="stretch")

    st.subheader("Staging comparison — mock truck positions")
    st.caption("Both panels use the selected hour. The comparison always shows Fixed staging and StormStage.")
    shared_view = {
        "latitude": float((zones["lat"].min() + zones["lat"].max()) / 2),
        "longitude": float((zones["lon"].min() + zones["lon"].max()) / 2),
        "zoom": 11,
        "pitch": 0,
        "bearing": 0,
    }
    for column, name in zip(st.columns(2), COMPARISON_POLICIES):
        with column:
            st.subheader(name)
            show_truck_map(zones, comparison_trucks[name], shared_view)

    st.divider()
    st.subheader("Results — mock / demo data")
    st.warning("Illustrative placeholders only. These values do not change with the replay controls "
               "and do not establish a measured benefit for either policy.")
    # TODO C: Replace MOCK_METRICS with teammate metrics output:
    # avg_response_min, p90_response_min, pct_within_15, relocation_count.
    for column, name in zip(st.columns(2), COMPARISON_POLICIES):
        with column:
            show_metrics(name)

    st.divider()
    st.subheader("Decision log — mock / demo")
    st.caption(f"Illustrative messages for {policy} through {hour:02d}:00; no reforecast or relocation is executed.")
    for message in get_mock_decision_log(policy, hour):
        st.write(message)


if __name__ == "__main__":
    main()
