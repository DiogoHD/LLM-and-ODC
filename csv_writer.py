import csv
import os
from functions import choose_option

folder = "responses"    # Caminho da pasta onde quero guardado as respostas dos modelos de IA
os.makedirs(folder, exist_ok=True)  # Cria a pasta se esta não existir

# Tuples com os defect types, defect qualifiers
defect_types: dict[str,int] = {"assignment":0, "initialization":0, "checking":0, "timing":0, "algorithm":0, "method":0, "function":0, "interface":0}
defect_qualifiers: dict[str,int]  = {"missing":0, "incorrect":0, "extraneous":0}

with open("file.csv", "w", newline='') as csv_file:
    csvwriter = csv.writer(csv_file, dialect="excel")
    csvwriter.writerow(["model", "Defect Type", "Defect Qualifier"])
             
    for file_name in os.listdir(folder):
        f_path = os.path.join(folder, file_name)
        model = file_name[:-4]
        
        with open(f_path, "r") as f:
            text = f.read().lower()
            found = False
            
            for t in defect_types.keys():
                defect_types[t] = text.count(t)
            
            for q in defect_qualifiers.keys():
                defect_qualifiers[q] += text.count(q)
        
            csvwriter.writerow([model, choose_option(defect_types), choose_option(defect_qualifiers)])