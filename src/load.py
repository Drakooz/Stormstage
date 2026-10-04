import pandas as pd

df = pd.read_csv("data/raw/calgary_traffic_incidents_full.csv")

df["START_DT_UTC"] = pd.to_datetime(df["START_DT_UTC"])

df = df[
    (df["START_DT_UTC"] >= "2025-01-01") &
    (df["START_DT_UTC"] < "2026-01-01")
]

df = df[
    [
        "INCIDENT INFO",
        "DESCRIPTION",
        "START_DT_UTC",
        "QUADRANT",
        "Longitude",
        "Latitude",
        "id"
    ]
]

df = df.dropna(subset=["Longitude", "Latitude"])
df = df.sort_values("START_DT_UTC")

print(df.head())
print(df.tail())
print("2025 row count:", len(df))
print("Earliest:", df["START_DT_UTC"].min())
print("Latest:", df["START_DT_UTC"].max())

df.to_csv("data/processed/incidents_clean.csv", index=False)