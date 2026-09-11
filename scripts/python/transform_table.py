import os
import pandas as pd
import configparser

conf = configparser.ConfigParser()
conf.read("./config.conf")
input_filepath = conf["datasource"]["input_filepath"]
output_filepath = conf["datasource"]["output_filepath"]

tiers = ["(Tier 0)", "(Tier 1-2)", "(Tier 1-2).1", "(Tier 1-2).2", "(Tier 3)", "(Tier 3).1"]
cols_tier = ["Custom field " + c for c in tiers]
tier_label = dict(zip(cols_tier, ["0", "1-2", "1-2", "1-2", "3", "3"]))

cols_incident_all = [
    "Issue Type", "Issue key", "Issue id", "Summary", "Priority", "Status", "PIC", "Workaround Provided", "Resolution", "Project Name",
    "Reporter", "Reporter Id", "Created", "Updated", "Time to resolution", "Time to first response", "Assignee", "Assignee Id", "Version",
    "Closure Provided", "partition_time"
]

cols_incident_solver_all = ["Issue id", "Updated", "Solver", "Tier", "partition_time"]

def extract_duration(time):
    if time is None or pd.isnull(time):
        return None
    else:
        time = str(time)
        day = 0
        neg = time[0] == "-"
        time = time[1:] if neg else time
        if ", " in time:
            day = int(time.split(", ")[0].split(" ")[0]) * 86400
            time = time.split(", ")[1]
        # print(time)

        time_split = [int(float(u)) for u in time.split(":")]
        if len(time_split) < 3:
            time_split.reverse()
            time_split += [0] * (3 - len(time_split))
            time_split.reverse()
        time_dict = dict(zip(["h", "m", "s"], time_split))

        time_sec = day + time_dict["h"] * 3600 + time_dict["m"] * 60 + time_dict["s"]
        return time_sec if not neg else -time_sec

list_incident_all = []
list_incident_solver = []

for f in os.listdir(input_filepath):
    filepath_f = os.path.join(input_filepath, f)
    if os.path.isfile(filepath_f):
        pdate_fname = f.split("_")[1]
        ptime_fname = f.split("_")[2].split(".")[0]
        partition_time = "20" + pdate_fname[4:] + pdate_fname[2:4] + pdate_fname[:2] + ptime_fname

        df = pd.read_excel(filepath_f)
        cols_tier_existing = list(set(df.columns).intersection(set(cols_tier)))

        cols_rename = [
            "PIC", "Workaround Provided", "Project Name", "Time to resolution",
            "Time to first response", "Version", "Closure Provided"
        ]

        df_incident = df.drop(columns=cols_tier_existing) \
            .rename({f"Custom field ({col})": col for col in cols_rename}, axis=1) \

        df_incident["Created"] = pd.to_datetime(df_incident["Created"], format="%d/%m/%Y %H:%M")
        df_incident["Updated"] = pd.to_datetime(df_incident["Updated"], format="%d/%m/%Y %H:%M")
        df_incident["Time to resolution"] = df_incident["Time to resolution"].apply(extract_duration)
        df_incident["Time to first response"] = df_incident["Time to first response"].apply(extract_duration)

        df_incident_w_dt = df_incident[cols_incident_all[:-1]].copy()
        df_incident_w_dt["partition_time"] = partition_time
        list_incident_all.append(df_incident_w_dt)

        for col in cols_tier_existing:
            df_incident_solver_t = df[["Issue id", "Updated", col]].rename({col: "Solver"}, axis=1)
            df_incident_solver_t = df_incident_solver_t[df_incident_solver_t["Solver"].notnull()]
            df_incident_solver_t["Updated"] = pd.to_datetime(df_incident_solver_t["Updated"], format="%d/%m/%Y %H:%M")
            df_incident_solver_t["Tier"] = tier_label[col]
            df_incident_solver_t["partition_time"] = partition_time
            list_incident_solver.append(df_incident_solver_t)

if list_incident_all:
    df_incident_all = pd.concat(list_incident_all, ignore_index=True)
    df_incident_solver_all = pd.concat(list_incident_solver, ignore_index=True)
else:
    df_incident_all = pd.DataFrame(columns=cols_incident_all)
    df_incident_solver_all = pd.DataFrame(columns=cols_incident_solver_all)

df_incident_update = df_incident_all.sort_values(
        by=["Issue id", "Updated", "partition_time"],
        ascending=[True, False, False]
    ) \
    .drop_duplicates(subset=["Issue id"], keep="first")

df_incident_solver_update = df_incident_solver_all.sort_values(
        by=["Issue id", "Solver", "Tier", "Updated", "partition_time"],
        ascending=[True, True, True, False, False]
    ) \
    .drop_duplicates(subset=["Issue id", "Solver", "Tier"], keep="first")

df_incident_out = df_incident_update
df_incident_out["Created Week"] = df_incident_out["Created"].dt.to_period("W").dt.to_timestamp()
df_incident_out["Created Month"] = df_incident_out["Created"].dt.to_period("M").dt.to_timestamp()
df_incident_out["SLA Achievement"] = df_incident_out["Time to resolution"].apply(lambda x: "Within SLA" if x > 0 else "Over SLA")
df_incident_out["Status Group"] = df_incident_out["Status"] \
    .apply(lambda x: None if pd.isnull(x) else ("DONE" if x in ["Closed", "Resolved", "Canceled"] else "OPEN"))

df_incident_solver_out = df_incident_solver_update

df_incident_out.to_csv(os.path.join(output_filepath, "incident.csv"), index=False)
df_incident_solver_out.to_csv(os.path.join(output_filepath, "solver.csv"), index=False)
