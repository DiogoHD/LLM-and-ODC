import csv
import os
import re

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
                
                # Uses a raw string (r) so Python can allow escape characters
                # \s* -> Allows spaces
                # (\S+) -> Caputres the first word after the string
                # [:\-–—] -> Allows : (Colon), - (Hyphen), – (En dash) and — (Em dash)
                # re.IGNORECASE makes the search be case-insensitive
                type_match = re.search(r"Defect Type\s*[:\-–—]\s*(\S+)", text, re.IGNORECASE)
                qualifier_match = re.search(r"Defect Qualifier\s*[:\-–—]\s*(\S+)", text, re.IGNORECASE)
                
                # takes the response found
                defect_type = type_match.group(1) if type_match else None
                defect_qualifier = qualifier_match.group(1) if qualifier_match else None
            
                csvwriter.writerow([sha, model, defect_type, defect_qualifier])