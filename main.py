from ollama import chat
import csv
import os
from github import Github
from functions import create_message, choose_option



prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"
sha = "b363b3304bcf68c4541683b2eff70b29f0446a5b"
content = create_message(prompt, sha)

# Tuples com os defect types, defect qualifiers e modelos usados
defect_types: dict[str,int] = {"assignment":0, "initialization":0, "checking":0, "timing":0, "algorithm":0, "method":0, "function":0, "interface":0}
defect_qualifiers: dict[str,int]  = {"missing":0, "incorrect":0, "extraneous":0}
models = ("gemma3", "llama3.2", "mistral", "phi3")

with open("file.csv", "w", newline='') as f:
    csvwriter = csv.writer(f, dialect="excel")
    csvwriter.writerow(["model", "Defect Type", "Defect Qualifier"])

for model in models:
    stream = chat(
        model = model,  # Este parâmetro define o modelo do ollama a ser usado
        messages = [{'role': 'user', 'content': content}],  # Aqui define-se quem está a usar o modelo e o seu conteúdo
        stream = True,  # Permite ver a resposta enquanto se vai escrevendo
        )
    
    folder = "responses"    # Caminho da pasta onde quero guardado as respostas dos modelos de IA
    os.makedirs(folder, exist_ok=True)  # Cria a pasta se esta não existir
    file_name = model + ".txt"
    path = os.path.join(folder, file_name)
    
    with open(path, "w") as f:
        for chunk in stream:        
            found = False
            text = chunk['message']['content']
            
            # Encontra os defect types e qualifiers no texto
            # Neste momento mete de outra cor para melhor identificação manual mas, no futuro, servirá para automatizar
            for t in defect_types.keys():
                if t in text.lower():
                    defect_types[t] += 1
                    found = True
                    break
            
            for q in defect_qualifiers.keys():
                if q in text.lower():
                    defect_qualifiers[q] += 1
                    found = True
                    break
            
            f.write(text)
            
    with open("file.csv", "a", newline='') as f:
        csvwriter = csv.writer(f, dialect="excel")
        csvwriter.writerow([model, choose_option(defect_types), choose_option(defect_qualifiers)])