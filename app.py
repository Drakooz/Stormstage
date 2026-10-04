"""Presentation and exploration of StormStage's weather-driven saved replays."""

from html import escape
import base64
import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

from dashboard_data import (
    current_fleet_state, event_label, load_aggregate_results, recorded_events,
)

from replay_data import (
    COMPARISON_POLICIES, POLICIES, STORM_DAYS, get_decision_log,
    get_incidents, get_metrics, get_truck_positions, get_zones,
)

ROOT = Path(__file__).resolve().parent
PRIMARY = "StormStage + on-call"
BASELINE = "Fixed yards (naive)"
DEFAULT_DAY = "2025-02-04"
DEFAULT_HOUR = 1
EXPLORER_POLICIES = (*POLICIES, "fixed_all")
LOAD_ERRORS = (OSError, ValueError, KeyError, TypeError, pd.errors.ParserError)
STATUS_COLORS = {
    "staged": [85, 183, 255], "responding": [255, 71, 94],
    "on_scene": [255, 199, 79], "returning": [30, 224, 190],
    "relocating": [167, 139, 250],
}


def html_text(value) -> str:
    return escape(str(value))


def policy_label(policy: str) -> str:
    return "Fixed, 10 trucks all day" if policy == "fixed_all" else policy


def section(title: str, subtitle: str = "") -> None:
    st.html(f'<div class="ss-section"><h2>{html_text(title)}</h2>'
            f'<p>{html_text(subtitle)}</p></div>')


def icon(kind: str, color: str = "#75caff") -> str:
    paths = {
        "truck": '<path d="M3 5h11v10H3zM14 9h4l3 4v2h-7"/><circle cx="7" cy="17" r="2"/><circle cx="18" cy="17" r="2"/>',
        "weather": '<path d="M5 13a4 4 0 1 1 1-8 6 6 0 0 1 11 2 3 3 0 0 1 1 6zM7 17v4M5 19h4M16 17v4M14 19h4"/>',
        "signal": '<circle cx="12" cy="8" r="2"/><path d="M12 10v11M7 4a6 6 0 0 0 0 9M17 4a6 6 0 0 1 0 9M4 1a10 10 0 0 0 0 15M20 1a10 10 0 0 1 0 15"/>',
        "alert": '<path d="M12 3 2 21h20zM12 9v5M12 17v1"/>',
        "chart": '<path d="M4 20v-7h3v7zM10 20V8h3v12zM16 20V3h3v17z"/>',
        "trophy": '<path d="M7 3h10v5a5 5 0 0 1-10 0zM7 5H3v3a4 4 0 0 0 4 4M17 5h4v3a4 4 0 0 1-4 4M12 13v6M8 21h8"/>',
    }
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="' + color + '" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + paths[kind] + '</svg>')
    # Streamlit sanitizes inline SVG. A self-contained image retains the artwork.
    return '<img class="ss-icon" alt="" src="data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '"/>'


def card(label: str, value: str, detail: str, tone: str = "", symbol: str = "truck") -> str:
    color = "#31dfc9" if tone == "teal" else "#ffca60" if tone == "amber" else "#75caff"
    return (f'<div class="ss-card {tone}">{icon(symbol, color)}<div><div class="ss-label">{html_text(label)}</div>'
            f'<div class="ss-value">{html_text(value)}</div>'
            f'<div class="ss-detail">{html_text(detail)}</div></div></div>')


def table_html(headers: list[str], rows: list[list], highlight: int | None = None) -> str:
    head = "".join(f"<th>{html_text(h)}</th>" for h in headers)
    body = "".join(
        f'<tr class="{"ss-highlight" if i == highlight else ""}">'
        + "".join(f"<td>{html_text(c)}</td>" for c in row) + "</tr>"
        for i, row in enumerate(rows)
    )
    return (f'<div class="ss-table-wrap"><table class="ss-table">'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def html_table(headers: list[str], rows: list[list], highlight: int | None = None) -> None:
    st.html(table_html(headers, rows, highlight))


@st.cache_data(show_spinner=False)
def load_zones() -> pd.DataFrame:
    """Keep the existing replay-grid validation."""
    zones = get_zones()
    if not {"zone_id", "lat", "lon"}.issubset(zones.columns):
        raise ValueError("Replay zones must contain zone_id, lat, and lon columns.")
    zones = zones[["zone_id", "lat", "lon"]].copy()
    if zones.empty or zones.isna().any().any() or zones["zone_id"].duplicated().any():
        raise ValueError("Replay zones must contain unique zone IDs and complete coordinates.")
    zones["lat"] = pd.to_numeric(zones["lat"], errors="raise")
    zones["lon"] = pd.to_numeric(zones["lon"], errors="raise")
    if not zones["lat"].between(-90, 90).all() or not zones["lon"].between(-180, 180).all():
        raise ValueError("Replay zones contain coordinates outside valid latitude/longitude ranges.")
    return zones


def replay_metadata(day: str) -> dict:
    return json.loads((ROOT / "data" / "processed" / "replay" / day / "metrics.json").read_text())


def show_status(day: str, hour: int, trucks: pd.DataFrame, events: list[dict]) -> None:
    state = current_fleet_state(day, hour, trucks, events)
    date_label = pd.Timestamp(day).strftime("%b %d, %Y").replace(" 0", " ")
    st.html('<div class="ss-grid">'
            + card("Storm replay", date_label, f"{hour:02d}:00 · Calgary time", "ice", "weather")
            + card("Fleet", state["fleet"], state["fleet_detail"], "teal")
            + card("Decision", state["decision"], state["decision_detail"], "teal", "signal")
            + card("Trigger event", state["trigger"], state["trigger_detail"], "amber", "alert")
            + '</div>')


def show_timeline(events: list[dict], policy: str) -> int:
    title_column, slider_column = st.columns([1, 5])
    with title_column:
        section("Storm timeline", "Calgary time · Recorded events")
    with slider_column:
        hour = st.slider("Replay hour", 0, 23, DEFAULT_HOUR, format="%02d:00", key="replay_hour", label_visibility="collapsed")
    event_html = []
    for event in events:
        tone = "current" if event["minute"] == hour * 60 else "past" if event["minute"] < hour * 60 else ""
        event_html.append(f'<span class="ss-event {tone}"><b>{html_text(event["time"])}</b>'
                          f'{html_text(event_label(event))}</span>')
    st.html('<div class="ss-events">' + "".join(event_html) + '</div>')
    return hour


def map_view(zones: pd.DataFrame) -> dict:
    return {"latitude": float((zones["lat"].min() + zones["lat"].max()) / 2),
            "longitude": float((zones["lon"].min() + zones["lon"].max()) / 2),
            "zoom": 8.6, "pitch": 0, "bearing": 0}


def show_map(zones: pd.DataFrame, trucks: pd.DataFrame, incidents: pd.DataFrame,
             view: dict, key: str, height: int = 420, fixed_camera: bool = False) -> None:
    points = []
    for (lat, lon), group in trucks.groupby(["lat", "lon"], sort=False):
        ids = " / ".join(f"T{int(unit):02d}" for unit in group["unit_id"])
        details = "; ".join(f"Unit {int(row.unit_id)}: {row.status}" for row in group.itertuples())
        points.append({"lat": lat, "lon": lon, "label": ids,
                       "tooltip_title": f"Truck units {ids}", "tooltip_detail": html_text(details),
                       "icon": {"url": truck_marker(group.iloc[0]["status"] if group["status"].nunique() == 1 else "mixed"),
                                "width": 64, "height": 48, "anchorY": 24}})
    incident_points = incidents[["lat", "lon", "time"]].copy()
    incident_points["tooltip_title"] = "Reported incident"
    incident_points["tooltip_detail"] = pd.to_datetime(incident_points["time"]).dt.strftime("%H:%M · Calgary local time")
    layers = [
        pdk.Layer("ScatterplotLayer", data=zones, get_position="[lon, lat]",
                  get_fill_color=[100, 116, 139, 65], get_radius=30, radius_min_pixels=2),
        pdk.Layer("ScatterplotLayer", data=incident_points, get_position="[lon, lat]",
                  get_fill_color=[248, 113, 113, 180], get_radius=80, radius_min_pixels=4, pickable=True),
        pdk.Layer("IconLayer", data=points, get_position="[lon, lat]", get_icon="icon",
                  get_size=38, pickable=True),
        pdk.Layer("TextLayer", data=points, get_position="[lon, lat]", get_text="label",
                  get_color=[239, 246, 255], get_size=14, get_pixel_offset=[0, -26],
                  get_background_color=[3, 18, 32, 235], background=True,
                  get_border_color=[89, 165, 206], get_border_width=1, background_padding=[5, 3]),
    ]
    deck = pdk.Deck(map_provider="carto", map_style=pdk.map_styles.DARK,
                    initial_view_state=pdk.ViewState(**view), layers=layers,
                    tooltip={"html": "<b>{tooltip_title}</b><br/>{tooltip_detail}",
                             "style": {"backgroundColor": "#101e31", "color": "#e7eef8"}})
    if fixed_camera:
        deck.views = [pdk.View("MapView", controller=False, view_state=view)]
    st.pydeck_chart(deck, height=height, key=key)


def truck_marker(status: str) -> str:
    color = "#" + "".join(f"{c:02x}" for c in STATUS_COLORS.get(status, [148, 163, 184]))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" viewBox="0 0 64 48">'
           '<path d="M6 9h33v26H6zM39 18h10l9 11v6H39z" '
           f'fill="{color}" stroke="#d9f1ff" stroke-width="2"/>'
           '<path d="M43 21h5l6 8H43z" fill="#082139"/>'
           '<circle cx="17" cy="36" r="6" fill="#082139" stroke="#d9f1ff" stroke-width="2"/>'
           '<circle cx="48" cy="36" r="6" fill="#082139" stroke="#d9f1ff" stroke-width="2"/></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def show_legend(trucks: pd.DataFrame) -> None:
    labels = {"staged": "Available", "responding": "Responding", "on_scene": "On scene",
              "returning": "Returning", "relocating": "Relocating"}
    legend = []
    for status, label in labels.items():
        if status == "relocating" and status not in trucks["status"].values:
            continue
        color = "#" + "".join(f"{c:02x}" for c in STATUS_COLORS[status])
        legend.append(f'<span style="color:{color}">{icon("truck", color)}{label}</span>')
    if (trucks.groupby(["lat", "lon"])["status"].nunique() > 1).any():
        legend.append(f'<span>{icon("truck", "#94a3b8")}Shared position · mixed status</span>')
    st.html('<div class="ss-legend">' + "".join(legend)
            + '<span><i class="ss-dot"></i>Reported incident</span></div>')


def show_explanation(day: str, hour: int, trucks: pd.DataFrame,
                     events: list[dict], meta: dict, values: dict) -> None:
    state = current_fleet_state(day, hour, trucks, events)
    activation = state["activation"]
    signal = activation["signal"] if activation else None
    threshold = meta.get("surge_at")
    signal_html = (f'<div class="ss-signal">{signal:g}× normal</div>' if signal is not None
                   else '<div class="ss-signal">Base plan</div>')
    paragraphs = [f"On-call activation threshold: {threshold:.1f}×" if threshold is not None else "Threshold unavailable",
                  "Trigger combines weather lift and recent incident activity."]
    if activation:
        paragraphs.append(f"Activated at {activation['time']}" +
                          (" · historical signal" if not state["exact"] or state["exact"]["kind"] != "activate" else ""))
    else:
        paragraphs.append("No on-call activation recorded by this snapshot.")
    if state["latest"] and state["latest"]["kind"] == "stand down":
        paragraphs.append(f"{event_label(state['latest'])} at {state['latest']['time']}.")
    relocations = values["relocation_count"]
    paragraphs.append("This replay records no relocations." if relocations == 0
                      else f"This day's completed replay records {relocations} truck relocations.")
    body = "".join(f'<p>{html_text(text)}</p>' for text in paragraphs)
    st.html('<div class="ss-explanation"><h3>Why StormStage changed the plan</h3>' + signal_html
            + f'<div class="ss-fleet">{html_text(state["fleet"])}</div>'
            + f'<div class="ss-decision">{html_text(state["decision"])}</div>' + body + '</div>')


def day_comparison(day: str, baseline: dict, stormstage: dict) -> None:
    avg = baseline["avg_response_min"]
    outcome = ""
    if avg > 0:
        reduction = (avg - stormstage["avg_response_min"]) / avg * 100
        label = "lower" if reduction >= 0 else "higher"
        outcome = f'<div class="ss-outcome"><strong>{abs(reduction):.1f}% {label}</strong> simulated average response</div>'
    response = f"{avg:.1f} → {stormstage['avg_response_min']:.1f} min"
    capacity = f"{baseline['truck_hours']:g} → {stormstage['truck_hours']:g} truck-hours"
    policies = ""
    for name, values, tone in [("Fixed yards · 6 trucks", baseline, ""), (PRIMARY, stormstage, "teal")]:
        rows = [["Average response", f"{values['avg_response_min']:.1f} min"],
                ["P90", f"{values['p90_response_min']:.1f} min"],
                ["Within 15 min", f"{values['pct_within_15']:.1f}%"],
                ["Truck-hours", f"{values['truck_hours']:g}"]]
        policies += (f'<div class="ss-policy {tone}"><div class="ss-policy-title">{html_text(name)}</div>'
                     + table_html([], rows) + '</div>')
    trade = ("Faster simulated response required additional on-call capacity."
             if stormstage["truck_hours"] > baseline["truck_hours"] and stormstage["avg_response_min"] < avg
             else "Compare simulated response alongside the capacity used.")
    st.html('<div class="ss-band ss-day"><div class="ss-headline"><h2>Did the decision help?</h2>'
            + f'<div class="ss-note">{html_text(pd.Timestamp(day).strftime("%b %d, %Y"))} only · Full-day outcomes</div>'
            + f'<div class="ss-value">{html_text(response)}</div>' + outcome + '</div>' + policies
            + f'<div><div class="ss-mini"><div class="ss-label">Response</div><div class="ss-value">{html_text(response)}</div></div>'
            + f'<div class="ss-mini"><div class="ss-label">Capacity</div><div class="ss-value">{html_text(capacity)}</div></div></div>'
            + f'<div class="ss-trade">{trade}</div></div>')
    st.caption("Full-day simulated outcomes, independent of the slider. Truck-hours measure capacity use, not monetary cost.")


def aggregate_evidence() -> None:
    try:
        evidence = load_aggregate_results()
        storm, count = evidence["storm"], evidence["count"]
        policies = [BASELINE, PRIMARY, "Fixed, all trucks all day"]
        rows = [[name.replace("Fixed, all trucks all day", "Fixed 10 trucks all day"),
                 f"{storm.loc[name, 'avg_min']:.1f} min", f"{storm.loc[name, 'p90_min']:.1f} min",
                 f"{storm.loc[name, 'pct_within_15']:.1f}%", f"{storm.loc[name, 'truck_hours']:g}"]
                for name in policies]
        same = storm.loc["StormStage (same 6 trucks)", "avg_min"]
        adaptive = storm.loc[PRIMARY, "avg_min"]
        baseline, oncall, allday = (storm.loc[name] for name in policies)
    except LOAD_ERRORS as error:
        st.warning(f"Aggregate evidence is unavailable: {error}")
        return
    kpis = [("Average response", f"{baseline['avg_min']:.1f} → {oncall['avg_min']:.1f} min", "Fixed yards → on-call"),
            ("Reached within 15 minutes", f"{baseline['pct_within_15']:.1f}% → {oncall['pct_within_15']:.1f}%", "Mean daily share"),
            ("Capacity", f"{oncall['truck_hours']:g} truck-hours/day", f"vs {allday['truck_hours']:g} with all 10 active all day")]
    kpi_html = ''.join(f'<div class="ss-mini"><div class="ss-label">{html_text(label)}</div>'
                       f'<div class="ss-value">{html_text(value)}</div><div class="ss-note">{html_text(detail)}</div></div>'
                       for label, value, detail in kpis)
    st.html('<div class="ss-band ss-aggregate"><div>'
            + f'<h2>Across {count} storm test days</h2><div class="ss-note">{count} designated storm test days using a causal forecast · Separate from the selected replay day</div>'
            + '<div class="ss-kpis">' + kpi_html + '</div></div>'
            + table_html(["Policy", "Avg response", "Mean daily p90", "Within 15 min", "Truck-hours/day"], rows, highlight=1)
            + f'<div class="ss-win">{icon("trophy", "#ffcc63")}<span>StormStage beat Fixed yards on <strong>{evidence["wins"]} of {count}</strong> storm days.</span></div></div>')
    st.caption(f"{count} designated storm test days using a causal forecast · Means of daily metrics, not pooled statistics. "
               f"On-call beat Best fixed plan on {evidence['secondary_wins']} of {count}. All ten active all day was faster, with higher capacity use.")
    score_detail = ("No aggregate improvement" if same >= baseline['avg_min'] and same >= storm.loc['Best fixed plan', 'avg_min']
                    else "Compare against fixed baselines")
    story = [("PLAN", "Re-stage the same 6 trucks", "Original hypothesis"), ("SCORE", f"{same:.1f} min", score_detail),
             ("REVISE", "Forecast-triggered on-call", "Capacity timing"), ("RESCORE", f"{adaptive:.1f} min", "Simulated average response")]
    steps = '<span class="ss-arrow">→</span>'.join(
        f'<div class="ss-step"><b>{title}</b><span>{html_text(value)}</span><small>{html_text(detail)}</small></div>'
        for title, value, detail in story)
    st.html('<div class="ss-band ss-strategy"><h2>The evidence changed our strategy</h2>'
            + '<div class="ss-story">' + steps + '</div></div>')


def technical_details(day: str, policy: str, hour: int, trucks: pd.DataFrame,
                      incidents: pd.DataFrame, messages: list[str], meta: dict) -> None:
    with st.expander("Decision log"):
        st.caption(f"Recorded decisions for {policy} through {hour:02d}:59, Calgary local time.")
        for message in messages:
            st.write(message)
    with st.expander("Truck table"):
        st.caption(f"On-duty positions at {hour:02d}:00. Units can share a map marker.")
        st.dataframe(trucks, hide_index=True, width="stretch")
    with st.expander("Incident table"):
        st.caption("Completed response outcomes include arrivals after the selected hour.")
        st.dataframe(incidents[["time", "lat", "lon", "unit_id", "response_min"]], hide_index=True, width="stretch")
    with st.expander("Assumptions & limitations"):
        st.write("Weather-driven precomputed simulation, not live optimization. Metrics are simulated replay outcomes, not field-deployment results.")
        st.write("Reported traffic incidents are not all collisions or all tow calls. The selected replay day is separate from the aggregate evaluation.")
        st.write("Shared assumptions: nearest-arrival dispatch; straight-line distance × 1.3 at 40 km/h; 30 minutes on scene. Truck-hours measure capacity use, not monetary savings.")
        st.write("The surge signal uses the larger of weather lift and recent-incident nowcast. Current weather is persisted over the three-hour forecast horizon.")
        st.write("A's causal forecast trains before the requested UTC decision date. It explicitly reserves Feb 4, Feb 14, and Nov 24, plus following UTC dates. The broader exclusion wording in RESULTS.md is not established by that implementation; no complete exclusion of all evaluation days is claimed here.")
        st.write("No customer, partner, field deployment, pricing, or monetary savings validation exists. Replay scores inform the tested policy revision; they are not an online optimizer feedback signal.")
        st.caption(f"Replay forecast source: {meta.get('forecast', 'unknown')} · All replay hours: Calgary local time (America/Edmonton).")
    with st.expander("Additional policies"):
        try:
            evidence = load_aggregate_results()
            st.caption("All aggregate policies, including same-six and all-ten capacity comparators.")
            st.dataframe(evidence["storm"].reset_index(), hide_index=True, width="stretch")
        except LOAD_ERRORS as error:
            st.warning(f"Aggregate evidence is unavailable: {error}")
        other = st.selectbox("Inspect another policy", EXPLORER_POLICIES,
                             index=EXPLORER_POLICIES.index("Best fixed plan"),
                             format_func=policy_label, key="additional_policy")
        try:
            values = get_metrics(day, other)
            st.dataframe(pd.DataFrame([values]), hide_index=True, width="stretch")
        except LOAD_ERRORS as error:
            st.error(f"Unable to load this policy: {error}")
        st.caption("Use Explorer Mode for this policy's map, positions, incidents, and decisions.")


def presentation(day: str, hour: int, zones: pd.DataFrame, meta: dict, events: list[dict]) -> None:
    try:
        trucks = get_truck_positions(day, PRIMARY, hour)
        incidents = get_incidents(day, PRIMARY, hour)
        values = get_metrics(day, PRIMARY)
        baseline = get_metrics(day, BASELINE)
        messages = get_decision_log(day, PRIMARY, hour)
        map_column, decision_column = st.columns([1.55, 1], gap="medium")
        with map_column:
            with st.container(key="operations"):
                section("Calgary operations map", f"Trucks at {hour:02d}:00 · Reported incidents through {hour:02d}:59")
                show_map(zones, trucks, incidents, map_view(zones), "presentation_map", height=320)
                show_legend(trucks)
        with decision_column:
            show_explanation(day, hour, trucks, events, meta, values)
        day_comparison(day, baseline, values)
        aggregate_evidence()
        section("Technical details & evidence", "Saved replay data, additional policies, and model limitations")
        technical_details(day, PRIMARY, hour, trucks, incidents, messages, meta)
    except LOAD_ERRORS as error:
        st.error(f"Unable to load the precomputed replay: {error}")
        st.stop()


def explorer(day: str, policy: str, hour: int, zones: pd.DataFrame, meta: dict) -> None:
    try:
        trucks = get_truck_positions(day, policy, hour)
        incidents = get_incidents(day, policy, hour)
        messages = get_decision_log(day, policy, hour)
        values = get_metrics(day, policy)
        section(policy_label(policy), f"{day} · {hour:02d}:00 Calgary local time · Saved replay positions")
        show_map(zones, trucks, incidents, map_view(zones), "explorer_map")
        show_legend(trucks)
        st.caption("Trucks at the hour's start; reported incidents through the hour's end. Tooltips show statuses; colors distinguish truck activity.")
        html_table(["Full-day metric", "Value"], [[name, values[name]] for name in values])
        technical_details(day, policy, hour, trucks, incidents, messages, meta)
        with st.expander("Compare primary policies side by side"):
            view = map_view(zones)
            for column, name in zip(st.columns(2), COMPARISON_POLICIES):
                with column:
                    st.subheader(name)
                    comparison = get_truck_positions(day, name, hour)
                    show_map(zones, comparison, get_incidents(day, name, hour), view,
                             f"comparison_{name}", height=350, fixed_camera=True)
                    st.dataframe(comparison, hide_index=True, width="stretch")
                    st.dataframe(pd.DataFrame([get_metrics(day, name)]), hide_index=True, width="stretch")
        with st.expander("Calgary zone grid"):
            st.map(zones[["lat", "lon"]])
            st.dataframe(zones, hide_index=True, width="stretch")
        aggregate_evidence()
    except LOAD_ERRORS as error:
        st.error(f"Unable to load the precomputed replay: {error}")
        st.stop()


def main() -> None:
    st.set_page_config(page_title="StormStage", page_icon="❄️", layout="wide")
    st.html("<style>" + (ROOT / "dashboard.css").read_text(encoding="utf-8") + "</style>")
    hero, controls = st.columns([3, 2], gap="large")
    with hero:
        st.html('<div class="ss-hero"><h1>StormStage</h1><p>Weather-aware fleet staging for Calgary winters</p>'
                '<span class="ss-evidence">Weather-driven precomputed simulation</span></div>')
    with controls:
        mode_column, day_column = st.columns([1.5, 1])
        with mode_column:
            mode = st.radio("View", ("Presentation Mode", "Explorer Mode"), horizontal=True, key="view_mode", label_visibility="collapsed")
        if not STORM_DAYS:
            st.error("No precomputed replay days are available.")
            st.stop()
        default_index = STORM_DAYS.index(DEFAULT_DAY) if DEFAULT_DAY in STORM_DAYS else 0
        with day_column:
            day = st.selectbox("Storm replay day", STORM_DAYS, index=default_index, key="storm_day",
                               format_func=lambda day: pd.Timestamp(day).strftime("%b %d, %Y"), label_visibility="collapsed")
    st.caption("Simulated replay outcomes, not field-deployment results. Details below.")
    try:
        zones = load_zones()
        meta = replay_metadata(day)
        events = recorded_events(get_decision_log(day, PRIMARY, 23))
    except LOAD_ERRORS as error:
        st.error(f"Unable to load the precomputed replay: {error}")
        st.stop()
    # Status is rendered above the timeline while the slider controls this rerun's snapshot.
    if mode == "Presentation Mode":
        status_container = st.container()
        with st.container(key="timeline"):
            hour = show_timeline(events, PRIMARY)
        with status_container:
            try:
                show_status(day, hour, get_truck_positions(day, PRIMARY, hour), events)
            except LOAD_ERRORS as error:
                st.error(f"Unable to load the precomputed replay: {error}")
                st.stop()
        presentation(day, hour, zones, meta, events)
    else:
        policy = st.selectbox("Policy", EXPLORER_POLICIES, index=EXPLORER_POLICIES.index(PRIMARY),
                              format_func=policy_label, key="explorer_policy")
        try:
            policy_events = recorded_events(get_decision_log(day, policy, 23))
        except LOAD_ERRORS as error:
            st.error(f"Unable to load the precomputed replay: {error}")
            st.stop()
        hour = show_timeline(policy_events, policy)
        explorer(day, policy, hour, zones, meta)


if __name__ == "__main__":
    main()
