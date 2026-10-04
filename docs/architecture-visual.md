# StormStage — final design

**PLAN → SCORE → REVISE → RESCORE**

```mermaid
%% Integrated source a: causal weather-driven forecast and saved replay evidence.
flowchart LR
    subgraph DATA["DATA"]
        I["Open Calgary<br/>Reported traffic incidents"]
        W["ECCC<br/>Hourly weather"]
    end

    subgraph ENGINE["DECISION ENGINE"]
        F["Causal weather-driven forecast<br/>Next 3 hours by zone"]
        P["PLAN<br/>6 base trucks + up to 4 on-call<br/>Forecast-triggered capacity<br/>Stage near expected demand"]
        V["REVISE<br/>Capacity policy / hourly staging"]
    end

    subgraph EVAL["EVALUATION"]
        B1["Fixed yards (naive)<br/>Primary baseline · 6 trucks"]
        B2["Best fixed plan<br/>Secondary comparator · 6 trucks"]
        R["Replay real incidents<br/>Shared simulation assumptions"]
        S["SCORE / RESCORE<br/>Response performance + truck-hours"]
    end

    subgraph DASH["DASHBOARD"]
        D["Streamlit<br/>Weather-driven precomputed replay"]
    end

    I --> F
    W --> F
    F ==> P
    P ==> R
    I -->|Same incidents| R
    B1 --> R
    B2 --> R
    R ==> S
    S -.->|Offline policy experiment| E["Team revises same-six policy to on-call / rescores"]
    F -->|Refresh hourly| V
    V ==> P
    S --> D

    classDef data fill:#eff6ff,stroke:#2563eb,color:#172554
    classDef loop fill:#ecfdf5,stroke:#047857,color:#064e3b,stroke-width:2px
    classDef baseline fill:#f8fafc,stroke:#64748b,color:#1e293b
    classDef dashboard fill:#faf5ff,stroke:#7e22ce,color:#3b0764
    class I,W data
    class F,P,V,R,S loop
    class B1,B2 baseline
    class D dashboard
    style DATA fill:#f8fbff,stroke:#93c5fd,color:#172554
    style ENGINE fill:#f5fffa,stroke:#6ee7b7,color:#064e3b
    style EVAL fill:#fffbeb,stroke:#fbbf24,color:#78350f
    style DASH fill:#fcfaff,stroke:#c4b5fd,color:#3b0764
```

StormStage uses Open Calgary reported traffic incidents and ECCC hourly weather to forecast demand by zone for the next three hours. It plans with 6 base trucks plus up to 4 forecast-triggered on-call trucks. Fixed yards (naive), the primary baseline, and Best fixed plan, the secondary comparator, each use 6 trucks under shared replay assumptions. The backend refreshes demand and revises capacity/staging hourly; completed replay outcomes supply scores. Streamlit displays saved positions, reasons, and full-day metrics in Calgary local time, rather than executing the loop when the slider moves.

**Measured revision:** same-six-truck staging averaged 14.2 minutes and did not improve the fixed baselines. With on-call capacity, average storm-day response was 10.6 minutes versus 14.1 for Fixed yards, using 176.5 truck-hours/day versus 240 for keeping ten trucks active all day. The all-ten-truck policy was faster at 7.5 minutes. These are aggregates across 12 designated storm test days ([summary](../results/test_summary.csv)), not the Feb 4 demo-day result of 20.1 versus 9.8 minutes ([per-day results](../results/test_by_day.csv)). This is the **PLAN → SCORE → REVISE → RESCORE** policy story; response scores do not directly trigger hourly replanning.

> **Evidence boundary:** source `a` is integrated and causal: fitting stops before the requested UTC decision date. A explicitly reserves Feb 4, Feb 14, and Nov 24, plus following UTC dates. The broader all-evaluation-days exclusion claim in `results/RESULTS.md` is not established by `forecast.py`; do not repeat it. Metrics are simulated replay outcomes, not field-deployment results. Reported incidents are not all collisions or all tow calls.

The inline diagram above is the current judge-facing visual; see [architecture specification](architecture-spec.md) for interfaces and limitations.
