import pandas as pd
from pathlib import Path
from itertools import zip_longest
import matplotlib.pyplot as plt
from functions import extract_defects, create_bar

folder = Path("responses")
data: list[dict[str, str | None]] = []

for sha_dir in folder.iterdir():    # For every folder and file in the main folder 
    if sha_dir.is_dir():            # Only runs the code if it's a folder
        for file_path in sha_dir.rglob("*.txt"):
            
            try:
                text = file_path.read_text(encoding="utf-8")    # pathlib method that reads the file and returns a string
            except (OSError, UnicodeDecodeError) as e:      # If there's an error with the path or decoding, it continues
                print(f"Error reading {file_path}: {e}")
                continue
            
            defects = extract_defects(text)
        
            for defect_type, defect_qualifier in zip_longest(defects["Defect Type"], defects["Defect Qualifier"]):
                data.append({
                    "Sha": sha_dir.name,        # sha_dir is a path, so sha_dir.name only returns the name of the folder and not the entire path
                    "Model": file_path.stem,    # Returns the stem (file name witouth extension)
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
    create_bar(df_output, df_input, defect, axes[i])

fig.suptitle("Defect Type and Defect Qualifier Comparison", fontsize=16)         # The Main Title
plt.show()