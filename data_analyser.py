import pandas as pd
from pathlib import Path
from itertools import zip_longest
import matplotlib.pyplot as plt
from functions import extract_defects, create_bar, create_crosstab

folder = Path("responses")
data: list[dict[str, str | None]] = []

for file_path in folder.rglob("*.txt"):     # For every text file in the main folder, including subfolders
    try:
        text = file_path.read_text(encoding="utf-8")    # pathlib method that reads the file and returns a string
    except (OSError, UnicodeDecodeError) as e:      # If there's an error with the path or decoding, it continues
        print(f"Error reading {file_path}: {e}")
        continue
    
    defects = extract_defects(text)

    for defect_type, defect_qualifier in zip_longest(defects["Defect Type"], defects["Defect Qualifier"]):
        data.append({
            "Sha": file_path.parts[1],          # file_path.parts = ('responses', 'sha', 'file_name', 'model.txt')
            "File Name": file_path.parts[2],
            "Model": file_path.stem,            # Returns the stem (file name witouth extension)
            "Defect Type": defect_type, 
            "Defect Qualifier": defect_qualifier
            })
                
# DataFrame
df_output = pd.DataFrame(data)                  # Create DataFrame
df_output.to_csv("output.csv", index=False)     # Export DataFrame to CSV
df_input = pd.read_csv("input.csv")             # Reads CSV with analyzed vulnerabilities

# Creating Bar Graphs
fig, axes = plt.subplots(1, 2, figsize=(16, 8), constrained_layout=True, num="Vulnerabilities", sharey=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
for i, defect in enumerate(["Defect Type", "Defect Qualifier"]):
    crosstab = create_crosstab(df_output, df_input, defect)
    create_bar(crosstab, defect, axes[i])

fig.suptitle("Defect Type and Defect Qualifier Comparison", fontsize=16)         # The Main Title
plt.show()