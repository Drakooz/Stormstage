"""Demo fixtures only: these are not forecasts or measured replay results."""

import pandas as pd


MOCK_STORM_DAYS = ("2025-02-04", "2025-01-10", "2025-03-08")
DEFAULT_HOUR = 15
POLICIES = ("Fixed staging", "Historical hotspots", "StormStage")
COMPARISON_POLICIES = ("Fixed staging", "StormStage")

# Each entry gives the zone for Units 1 through 6. Coordinates always come
# from the repository's zones.csv, never from invented geographic fixtures.
MOCK_TRUCK_ZONES = {
    "Fixed staging": ("Z01", "Z05", "Z11", "Z16", "Z20", "Z08"),
    "Historical hotspots": ("Z06", "Z09", "Z13", "Z17", "Z19", "Z04"),
    "StormStage": ("Z06", "Z10", "Z13", "Z17", "Z19", "Z05"),
}
MOCK_RELOCATION_HOUR = 15
MOCK_STORMSTAGE_AFTER_SNOW = ("Z06", "Z10", "Z14", "Z17", "Z19", "Z05")

# Static illustrative values for the entire demo, not computed from incidents.
MOCK_METRICS = {
    "Fixed staging": {
        "avg_response_min": 19.2,
        "p90_response_min": 31.0,
        "pct_within_15": 42.0,
        "relocation_count": 0,
    },
    "StormStage": {
        "avg_response_min": 12.4,
        "p90_response_min": 21.5,
        "pct_within_15": 71.0,
        "relocation_count": 4,
    },
}

# Hour, policy (None means all policies), and human-readable demo message.
MOCK_DECISION_LOG = (
    (0, None, "00:00: Mock replay ready. Six demo units staged."),
    (15, "StormStage", "15:00: Snow detected. Reforecasting next 3 hours."),
    (
        15,
        "StormStage",
        "15:00: Unit 3 moved to Z14. Reason: forecast demand increased "
        "in southeast Calgary.",
    ),
    (15, "Fixed staging", "15:00: Snow detected. Demo units remain at fixed staging zones."),
    (15, "Historical hotspots", "15:00: Snow detected. Demo units remain at historical hotspot zones."),
)


def get_mock_truck_positions(zones: pd.DataFrame, policy: str, hour: int) -> pd.DataFrame:
    """Join mock assignments to real zone coordinates for the selected hour."""
    zone_ids = MOCK_TRUCK_ZONES[policy]
    if policy == "StormStage" and hour >= MOCK_RELOCATION_HOUR:
        zone_ids = MOCK_STORMSTAGE_AFTER_SNOW
    missing_zones = set(zone_ids) - set(zones["zone_id"])
    if missing_zones:
        raise ValueError(f"Mock truck assignments reference missing zones: {sorted(missing_zones)}")
    assignments = pd.DataFrame({"unit_id": range(1, len(zone_ids) + 1), "zone_id": zone_ids})
    return assignments.merge(zones[["zone_id", "lat", "lon"]], on="zone_id", validate="many_to_one")


def get_mock_decision_log(policy: str, hour: int) -> list[str]:
    """Return fixture messages up to the selected hour; no backend is invoked."""
    return [
        message
        for event_hour, event_policy, message in MOCK_DECISION_LOG
        if event_hour <= hour and event_policy in (None, policy)
    ]
