import pandas as pd
from pathlib import Path
import regex

def make_pattern(name: str) -> regex.Pattern:
    "Creates a regex pattern to extract values associated with the especified field"
    # Uses a raw string so Python can allow escape characters
    pattern = regex.compile(rf"""
    (?:{name})      # Use that word witouth capturing it
    {{e<=1}}        # Fuzzy Matching - Allows at most 1 typo (only possible using the module regex (impossible with re))
    \s*[:\-–—]\s*   # Allows various separators and it can have 0 or multiple spaces before or after the separator
    (?:\d+\)?\s*)?  # If a number appears before the word that we want [2) or 3] it ignores it
    [(<[\{{]*       # Allows the word to be between some kind of brackets
    ([A-Za-z/]+)    # Captures the first word after the string (that only can contain letters and a /)
    """, regex.IGNORECASE | regex.VERBOSE)
    # regex.IGNORECASE makes the search be case-insensitive
    # regex.VERBOSE makes the search ignore newlines, spaces, tabs and comments
    
    return pattern

def extract_defects(text: str) -> dict[str, str | None]:
    "Extracts 'Defect Type' and 'Defect Qualifier' from a given text into a dictionary"
    result = {}
    for defect in ["Defect Type", "Defect Qualifier"]:
        match = regex.search(make_pattern(defect), text)                        # Finds the defect in the given text, using a especific pattern
        result[defect] = match.group(1).strip("'\",*()") if match else None     # If found, it strips the defect from unwanted characters, otherwise returns None
    return result

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
        
            data.append({
                "Sha": sha_dir.name,        # sha_dir is a path, so sha_dir.name only returns the name of the folder and not the entire path
                "Model": file_path.stem,    # Returns the stem (file name witouth extension)
                "Defect Type": defects["Defect Type"], 
                "Defect Qualifier": defects["Defect Qualifier"]
                })
                
# DataFrame
df = pd.DataFrame(data)                 # Create DataFrame
df.to_csv("output.csv", index=False)    # Export DataFrame to CSV