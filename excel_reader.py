import pandas as pd

excel = pd.read_excel("vulnerabilities.xlsx", sheet_name=0, header=1)
excel[["V_ID", "Project"]] = excel[["V_ID", "Project"]].ffill()

desired_cols = ["V_ID", "Project", "CVE", "V_CLASSIFICATION", "P_COMMIT", "Defect Type", "Defect Qualifier", "# Files"]

# Filters the initial excel
df = excel[desired_cols].copy()

# Deletes this line
df = df[df["Project"] != "CVE-2007-6151+C7+E7"]

# Filters with vulnerabilites only with 1 file
df = df[df["# Files"] == 1]

df.to_csv("input.csv", index=False)