import csv
import os
import pandas as pd
from functions import choose_option

# Tuples com os defect types, defect qualifiers
defect_types: dict[str,int] = {"assignment":0, "initialization":0, "checking":0, "timing":0, "algorithm":0, "method":0, "function":0, "interface":0}
defect_qualifiers: dict[str,int]  = {"missing":0, "incorrect":0, "extraneous":0}

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
                text = f.read().lower()
                found = False
                
                pos = text.find("defect type:")
                if pos == -1:
                    for t in defect_types.keys():
                        defect_types[t] = text.count(t)
                else:
                    found = True
                    for t in defect_types.keys():
                        defect_types[t] = text.find(t, pos)
                
                pos = text.find("defect qualifier:")
                if pos == -1:
                    for q in defect_qualifiers.keys():
                        defect_qualifiers[q] = text.count(q)
                else:
                    found = True
                    for q in defect_qualifiers.keys():
                        defect_qualifiers[q] = text.find(q, pos)
            
                csvwriter.writerow([sha, model, choose_option(defect_types, found), choose_option(defect_qualifiers, found)])