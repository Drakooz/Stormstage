# StormStage — final design

**PLAN → SCORE → REVISE → RESCORE**

```mermaid
%% Final design: current replay/results use B's stand-in forecast.
%% A's final weather-driven forecast integration and evaluation are pending.
flowchart LR
    subgraph DATA["DATA"]
        I["Open Calgary<br/>Reported traffic incidents"]
        W["ECCC<br/>Hourly weather"]
    end

    subgraph ENGINE["DECISION ENGINE"]
        F["Forecast next 3 hours<br/>Demand by zone"]
        P["PLAN<br/>6 base trucks + up to 4 on-call<br/>Forecast-triggered capacity<br/>Stage near expected demand"]
        V["REVISE<br/>Capacity + re-staging"]
    end

    subgraph EVAL["EVALUATION"]
        B1["Fixed yards (naive)<br/>Primary baseline · 6 trucks"]
        B2["Best fixed plan<br/>Secondary comparator · 6 trucks"]
        R["Replay real incidents<br/>Shared simulation assumptions"]
        S["SCORE / RESCORE<br/>Response performance + truck-hours"]
    end

    subgraph DASH["DASHBOARD"]
        D["Streamlit<br/>Precomputed replay evidence"]
    end

    I --> F
    W --> F
    F ==> P
    P ==> R
    I -->|Same incidents| R
    B1 --> R
    B2 --> R
    R ==> S
    S ==>|Conditions change| V
    V ==>|Refresh hourly| F
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

StormStage's final design uses Open Calgary reported traffic incidents and ECCC hourly weather to forecast demand by zone for the next three hours. It plans with 6 base trucks plus up to 4 forecast-triggered on-call trucks, staging active trucks near expected demand. Fixed yards (naive), the primary baseline, and Best fixed plan, the secondary comparator, each use 6 trucks and share the same incident replay and scoring assumptions. As conditions change, StormStage refreshes demand hourly, revises capacity and staging, and rescores response performance and truck-hours; Streamlit displays precomputed replay evidence.

> **Evidence status:** Current main replays/results use B's stand-in forecast; A's final weather-driven forecast integration and evaluation are pending.

[Standalone Mermaid source](architecture-diagram.mmd)
