import csv
import os
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
    "Extracts Defect Type and Defect Qualifier form a given text"
    result = {}
    for defect in ["Defect Type", "Defect Qualifier"]:
        match = regex.search(make_pattern(defect), text)                      # Finds the defect in the given text, using a especific pattern
        result[defect] = match.group(1).strip("'\",*()") if match else None  # If found, it strips the defect from unwanted characters, otherwise returns None
    return result

folder = "responses"

with open("file.csv", "w", newline='') as csv_file:
    csvwriter = csv.writer(csv_file, dialect="excel")
    csvwriter.writerow(["Sha", "Model", "Defect Type", "Defect Qualifier"])
           
    for sha in os.listdir(folder):
        sha_path = os.path.join(folder, sha)
        
        for file_name in os.listdir(sha_path):
            f_path = os.path.join(sha_path, file_name)
            model = file_name[:-4]
            
            with open(f_path, "r") as f:
                text = f.read()
                defects = extract_defects(text)
         
                csvwriter.writerow([sha, model, defects["Defect Type"], defects["Defect Qualifier"]])