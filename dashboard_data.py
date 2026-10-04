"""Read-only presentation calculations over the validated replay and result files."""

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from replay_data import get_truck_positions

ROOT = Path(__file__).resolve().parent
PRIMARY = "StormStage + on-call"
BASELINE = "Fixed yards (naive)"


def recorded_events(messages: list[str]) -> list[dict]:
    """Group actual logged unit actions at the same time and recorded signal."""
    events = {}
    for message in messages:
        match = re.match(r"^(\d{2}):(\d{2})\s+—\s+(.+)$", message)
        if not match:
            continue
        hour, minute, reason = match.groups()
        kind = ("activate" if "called in:" in reason else
                "stand down" if "stood down:" in reason else
                "move" if " -> zone " in reason else
                "staged" if "units staged" in reason else "other")
        signal_match = re.search(r"\bx(\d+(?:\.\d+)?) normal", reason)
        signal = float(signal_match.group(1)) if signal_match else None
        event = events.setdefault((hour, minute, kind, signal), {
            "time": f"{hour}:{minute}", "minute": int(hour) * 60 + int(minute),
            "kind": kind, "signal": signal, "units": set(), "reasons": [],
        })
        unit = re.search(r"\bUnit (\d+)\b", reason)
        if unit:
            event["units"].add(int(unit.group(1)))
        event["reasons"].append(reason)
    return sorted(events.values(), key=lambda event: event["minute"])


def event_label(event: dict) -> str:
    count = len(event["units"])
    if event["kind"] == "activate":
        return f"+{count} on-call activated"
    if event["kind"] == "stand down":
        return f"{count} on-call stood down"
    if event["kind"] == "move":
        return f"{count} truck{'s' if count != 1 else ''} relocated"
    if event["kind"] == "staged":
        match = re.search(r"(\d+) units staged", event["reasons"][0])
        return f"{match[1]} base trucks" if match else "Initial staging"
    return event["reasons"][0].split(" (", 1)[0].rstrip(".")


def event_fleet(day: str, policy: str, event: dict) -> tuple[int, int]:
    previous = max(0, event["minute"] - 1)
    before = get_truck_positions(day, policy, previous // 60, previous % 60)
    after = get_truck_positions(day, policy, event["minute"] // 60, event["minute"] % 60)
    return before["unit_id"].nunique(), after["unit_id"].nunique()


def current_fleet_state(day: str, hour: int, trucks: pd.DataFrame, events: list[dict]) -> dict:
    """Separate the current snapshot, exact-hour change, and historical signal.

    Base-unit identity comes from the initial replay snapshot, not an assumed ID
    range. Later stand-downs or moves never erase an earlier activation's reason.
    """
    initial = get_truck_positions(day, PRIMARY, 0)
    base_ids = set(initial["unit_id"])
    active_ids = set(trucks["unit_id"])
    visible = [event for event in events if event["minute"] <= hour * 60]
    changes = [event for event in visible if event["kind"] != "staged"]
    latest = changes[-1] if changes else None
    activations = [event for event in visible if event["kind"] == "activate"]
    activation = activations[-1] if activations else None
    exact = latest if latest and latest["minute"] == hour * 60 else None
    base = len(active_ids & base_ids)
    oncall = len(active_ids - base_ids)
    fleet = f"{len(active_ids)} active trucks"
    if exact and exact["kind"] in ("activate", "stand down"):
        before, after = event_fleet(day, PRIMARY, exact)
        fleet = f"{before} → {after} active trucks"
    decision = (event_label(exact) if exact else "On-call active" if oncall
                else "On-call stood down" if latest and latest["kind"] == "stand down"
                else "Base fleet")
    decision_detail = (f"Recorded at {latest['time']}" if exact else
                       f"Last change at {latest['time']}" if latest else "No on-call activation yet")
    signal = activation["signal"] if activation else None
    trigger = f"{signal:g}× normal" if signal is not None else "No activation yet"
    trigger_detail = (f"Recorded at {activation['time']}" if exact and exact["kind"] == "activate"
                      else f"Activated at {activation['time']} · historical signal" if activation
                      else "No activation signal recorded yet")
    return dict(active=len(active_ids), base=base, oncall=oncall, fleet=fleet,
                fleet_detail=f"{base} base + {oncall} on-call" if oncall else f"{base} base trucks",
                decision=decision, decision_detail=decision_detail, trigger=trigger,
                trigger_detail=trigger_detail, activation=activation, latest=latest, exact=exact)


@lru_cache(maxsize=1)
def load_aggregate_results() -> dict:
    """Cache immutable release evidence; restart the app after replacing result files."""
    summary = pd.read_csv(ROOT / "results" / "test_summary.csv")
    storm = summary[summary["day_type"] == "storm"].set_index("policy")
    by_day = pd.read_csv(ROOT / "results" / "test_by_day.csv")
    daily = by_day[by_day["day_type"] == "storm"].pivot(index="day", columns="policy", values="avg_min")
    paired = daily[[BASELINE, PRIMARY, "Best fixed plan"]].dropna()
    if paired.empty or not storm.index.is_unique:
        raise ValueError("Storm evaluation rows must be nonempty and unique.")
    return dict(storm=storm, count=len(paired),
                wins=int((paired[PRIMARY] < paired[BASELINE]).sum()),
                secondary_wins=int((paired[PRIMARY] < paired["Best fixed plan"]).sum()))
