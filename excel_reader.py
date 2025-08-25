import pandas as pd

excel = pd.read_excel("vulnerabilities.xlsx", sheet_name=0, header=1)
excel[["V_ID", "Project"]] = excel[["V_ID", "Project"]].ffill()

desired_cols = ["V_ID", "Project", "CVE", "V_CLASSIFICATION", "P_COMMIT", "Defect Type", "Defect Qualifier", "# Files"]

# Filters the initial excel
df = excel[desired_cols].copy()

# Deletes this line
df = df[df["Project"] != "CVE-2007-6151+C7+E7"]

# Counts how many lines each vulnerability ocuppies
df["lines"] = df.groupby("V_ID")["V_ID"].transform("count")

# Filters with vulnerabilites only with 1 line
df = df[df["lines"] == 1]
df.drop(columns=["lines"], inplace=True)

# Filters with vulnerabilites only with 1 file
df = df[df["# Files"] == 1]


df.to_csv("input.csv", index=False)