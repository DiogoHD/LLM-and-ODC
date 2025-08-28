import csv
import os
import regex

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
                
                # We now use regex so we can allow errors
                # (?:   ) -> To use that word witouth capturing it
                # {e<=1} -> Allows 1 typo
                # Uses a raw string (r) so Python can allow escape characters
                # \s* -> Allows spaces
                # (\S+) -> Caputres the first word after the string
                # [:\-–—] -> Allows : (Colon), - (Hyphen), – (En dash) and — (Em dash)
                # regex.IGNORECASE makes the search be case-insensitive
                type_match = regex.search(r"(?:Defect Type){e<=1}\s*[:\-–—]\s*(\S+)", text, regex.IGNORECASE)
                qualifier_match = regex.search(r"(?:Defect Qualifier){e<=1}\s*[:\-–—]\s*(\S+)", text, regex.IGNORECASE)
                
                # Takes the response found
                defect_type = type_match.group(1).strip("'\",*()") if type_match else None
                defect_qualifier = qualifier_match.group(1).strip("'\",*()") if qualifier_match else None
            
                csvwriter.writerow([sha, model, defect_type, defect_qualifier])