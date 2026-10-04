import pandas as pd

df = pd.read_csv("data/raw/calgary_traffic_incidents_full.csv")

print(df.head())
print(df.columns)
print(len(df))
