import pandas as pd

df = pd.read_csv("../data/output/incident.csv")
# df_grp = df.groupby("Issue id").agg(n=("partition_time", "count"))
# print(len(df_grp[df_grp["n"] > 1]))

print(df["Workaround Provided"].unique())
