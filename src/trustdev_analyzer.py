from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from functions.regex_utils import extract_defects

DEFECT_TYPE_MAP = {
    "assignment": "Assignment/Initialization",
    "initialization": "Assignment/Initialization",
    "assignment/initialization": "Assignment/Initialization",
    "algorithm": "Algorithm/Method",
    "method": "Algorithm/Method",
    "algorithm/method": "Algorithm/Method",
    "checking": "Checking",
    "function": "Function",
    "interface": "Interface",
    "timing": "Timing",
}
DEFECT_QUALIFIER_MAP = {
    "missing": "Missing",
    "incorrect": "Incorrect",
    "extraneous": "Extraneous",
}

ROOT_DIR = Path(__file__).resolve().parents[1]  # Get the root folder
MAIN_FOLDER = ROOT_DIR / "trustdev-output"
RUNS_FOLDER = MAIN_FOLDER / "runs"
OUTPUT_FOLDER = MAIN_FOLDER / "output"

def bar_graph(data: pd.DataFrame, title: str) -> None:
    plt.figure(figsize=(10, 6))
    bars = plt.bar(data.index, data.values)
    plt.bar_label(bars, padding=3, fontsize=8)  # Add labels to the bars
    plt.xlabel("Model")
    plt.ylabel("Count")
    plt.title(title)

rows = []

for run_folder in RUNS_FOLDER.iterdir():
    if not run_folder.is_dir():
        continue

    for project_folder in run_folder.iterdir():    # For every project folder in the main folder
        if not project_folder.is_dir():
            continue

        files = list(project_folder.rglob("*.txt"))

        for file_path in files:     # For every text file in the main folder, including subfolders
            try:
                text = file_path.read_text(encoding="utf-8")    # pathlib method that reads the file and returns a string
            except (OSError, PermissionError, UnicodeDecodeError) as e:      # If there's an error with the path or decoding, it continues
                print(f"Error reading {file_path}: {e}")
                continue
            
            defects = extract_defects(text)
            
            for defect in defects:
                normalized_type = DEFECT_TYPE_MAP.get(
                    defect[0].lower() if defect[0] else "", "Unknown"
                )
                normalized_qualifier = DEFECT_QUALIFIER_MAP.get(
                    defect[1].lower() if defect[1] else "", "Unknown"
                )
                
                if normalized_type == "Unknown" and normalized_qualifier == "Unknown":
                    continue  # Skip if both type and qualifier are unknown

                rows.append({
                    "Run": run_folder.name,
                    "Project": file_path.parts[-4],
                    "Sha": file_path.parts[-3],
                    "File Name": file_path.parts[-2],
                    "Model": file_path.stem,
                    "Defect Type": normalized_type,
                    "Defect Qualifier": normalized_qualifier
                })

data = pd.DataFrame(rows)

if not OUTPUT_FOLDER.exists():
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
with open(f"{OUTPUT_FOLDER}/defects_data.csv", "w", encoding="utf-8", newline="") as f:
    data.to_csv(f, index=False)

# Counts the number of files processed by each model
unique_file_models = data[["File Name", "Model"]].drop_duplicates()
model_counts = unique_file_models["Model"].value_counts()
bar_graph(model_counts, "Number of Files Processed per Model")

# Counts the number of defects identified by each model
model_counts = data["Model"].value_counts()
bar_graph(model_counts, "Number of Defects Identified per Model")

# Creates a crosstab for each model, showing the counts of defect types and defect qualifiers
for model in data["Model"].unique():
    model_data = data[data["Model"] == model]
    
    table = pd.crosstab(index=model_data["Defect Qualifier"], columns=model_data["Defect Type"], margins=True, margins_name="Total")

    if not (OUTPUT_FOLDER / "defect_crosstab").exists():
        (OUTPUT_FOLDER / "defect_crosstab").mkdir(parents=True, exist_ok=True)
    with open(f"{OUTPUT_FOLDER}/defect_crosstab/{model}.csv", "w", encoding="utf-8", newline="") as f:
        table.to_csv(f)

data["Defect"] = data["Defect Type"] + " - " + data["Defect Qualifier"]
group_cols = ["Project", "Sha", "File Name", "Model"]
index_cols = ["Project", "Sha", "File Name"]

# Comparison table with all defects identified by each model for each file
grouped = data.groupby(["Project", "Sha", "File Name", "Model"])["Defect"].agg(lambda x: sorted(x)).reset_index()
comparison_df = grouped.pivot(
    index=["Project", "Sha", "File Name"], 
    columns="Model",
    values="Defect"
).reset_index()

with open(f"{OUTPUT_FOLDER}/total_defects_comparison.csv", "w", encoding="utf-8", newline="") as f:
    comparison_df.to_csv(f, index=False)

# Comparison table with the mode of defects identified by each model for each file
grouped_mode = data.groupby(group_cols)["Defect"].agg(lambda x: x.mode().iloc[0]).reset_index()
mode_df = grouped_mode.pivot(index=index_cols, columns="Model", values="Defect").reset_index()

with open(f"{OUTPUT_FOLDER}/mode_defects_comparison.csv", "w", encoding="utf-8", newline="") as f:
    mode_df.to_csv(f, index=False)