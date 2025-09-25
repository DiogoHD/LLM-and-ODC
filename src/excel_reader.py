from pathlib import Path

import pandas as pd

excel = pd.read_excel("data/vulnerabilities.xlsx", sheet_name=0, header=1)
excel[["V_ID", "Project"]] = excel[["V_ID", "Project"]].ffill()

desired_cols = ["V_ID", "Project", "CVE", "V_CLASSIFICATION", "P_COMMIT", "Defect Type", "Defect Qualifier", "# Files", "Filenames"]

# Filters the initial excel
df = excel[desired_cols].copy()

# Filters with vulnerabilities only with 1 file
df = df[df["# Files"] == 1]

script_dir = Path(__file__).parent      # Get the folder where this file is located (src/)
data_dir = script_dir.parent / "data"   # Goes up one level and joins with data folder
data_dir.mkdir(parents=True, exist_ok=True)
file_path = data_dir / "input.csv"

try:
    df.to_csv(file_path, index=False, encoding="utf-8")      # Export DataFrame to CSV 
except (OSError, PermissionError, UnicodeEncodeError) as e:
    raise RuntimeError(f"Failed to write CSV to {file_path}: {e}") from e