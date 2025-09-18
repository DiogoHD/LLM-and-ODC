import pandas as pd

excel = pd.read_excel("vulnerabilities.xlsx", sheet_name=0, header=1)
excel[["V_ID", "Project"]] = excel[["V_ID", "Project"]].ffill()

desired_cols = ["V_ID", "Project", "CVE", "V_CLASSIFICATION", "P_COMMIT", "Defect Type", "Defect Qualifier", "# Files", "Filenames"]

# Filters the initial excel
df = excel[desired_cols].copy()

# Filters with vulnerabilites only with 1 file
df = df[df["# Files"] == 1]

df.to_csv("input.csv", index=False)