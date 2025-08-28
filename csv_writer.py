import csv
import os
import regex

def make_pattern(name: str):
    # Uses a raw string so Python can allow escape characters
    pattern = regex.compile(rf"""
    (?:{name})      # Use that word witouth capturing it
    {{e<=1}}        # Fuzzy Matching - Allows at most 1 typo (only possible using the module regex (impossible with re))
    \s*[:\-–—]\s*   # Allows various separators and it can have 0 or multiple spaces before or after the separator
    (?:\d+\)?\s*)?  # If a number appears before the word that we want [2) or 3] it ignores it
    [(<[\{{]*       # Allows the word to be between some kind of brackets
    ([A-Za-z/]+)    # Caputres the first word after the string (that only can contain letters and a /)
    """, regex.IGNORECASE | regex.VERBOSE)
    # regex.IGNORECASE makes the search be case-insensitive
    # regex.VERBOSE makes the search ignore newlines, spaces, tabs and comments
    
    return pattern


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
                
                type_match = regex.search(make_pattern("Defect Type"), text)
                qualifier_match = regex.search(make_pattern("Defect Qualifier"), text)
                
                # Takes the response found
                defect_type = type_match.group(1).strip("'\",*()") if type_match else None
                defect_qualifier = qualifier_match.group(1).strip("'\",*()") if qualifier_match else None
            
                csvwriter.writerow([sha, model, defect_type, defect_qualifier])