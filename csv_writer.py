import pandas as pd
from pathlib import Path
from itertools import zip_longest
from functions import extract_defects

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
df = pd.DataFrame(data)                 # Create DataFrame
df.to_csv("output.csv", index=False)    # Export DataFrame to CSV