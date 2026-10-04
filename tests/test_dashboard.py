"""Release regressions for time-correct fleet state and preserved explorer access."""

import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from app import EXPLORER_POLICIES

from dashboard_data import PRIMARY, current_fleet_state, load_aggregate_results, recorded_events
from replay_data import STORM_DAYS, get_decision_log, get_truck_positions


@pytest.mark.parametrize("hour,active,decision,transition", [
    (0, 6, "Base fleet", False),
    (1, 10, "+4 on-call activated", True),
    (4, 10, "On-call active", False),
    (22, 6, "4 on-call stood down", True),
    (23, 6, "On-call stood down", False),
])
def test_fleet_state_at_recorded_boundaries(hour, active, decision, transition):
    day = "2025-02-04"
    events = recorded_events(get_decision_log(day, PRIMARY, 23))
    state = current_fleet_state(day, hour, get_truck_positions(day, PRIMARY, hour), events)
    assert state["active"] == active
    assert state["decision"] == decision
    assert ("→" in state["fleet"]) == transition
    if hour == 0:
        assert state["activation"] is None
    else:
        assert state["activation"]["time"] == "01:00"
        assert state["activation"]["signal"] == 2.4
    if hour >= 22:
        assert state["oncall"] == 0
        assert state["latest"]["time"] == "22:00"


def test_aggregate_pairs_and_capacity_comparator():
    evidence = load_aggregate_results()
    assert (evidence["count"], evidence["wins"], evidence["secondary_wins"]) == (12, 10, 8)
    storm = evidence["storm"]
    assert storm.loc[PRIMARY, "truck_hours"] < storm.loc["Fixed, all trucks all day", "truck_hours"]
    assert storm.loc["Fixed, all trucks all day", "avg_min"] < storm.loc[PRIMARY, "avg_min"]


def test_presentation_reruns_and_mode_switch():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=30)
    assert not app.exception
    assert app.radio(key="view_mode").value == "Presentation Mode"
    assert app.selectbox(key="storm_day").value == "2025-02-04"
    assert app.slider(key="replay_hour").value == 1
    for hour in (0, 1, 4, 22, 23):
        app.slider(key="replay_hour").set_value(hour).run(timeout=30)
        assert not app.exception
        assert not app.error
    app.radio(key="view_mode").set_value("Explorer Mode").run(timeout=30)
    assert not app.exception
    for day in STORM_DAYS:
        app.selectbox(key="storm_day").set_value(day).run(timeout=30)
        for policy in EXPLORER_POLICIES:
            app.selectbox(key="explorer_policy").set_value(policy).run(timeout=30)
            assert not app.exception, (day, policy)
            assert not app.error, (day, policy)
    app.radio(key="view_mode").set_value("Presentation Mode").run(timeout=30)
    assert not app.exception
