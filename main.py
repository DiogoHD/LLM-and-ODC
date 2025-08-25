import ollama
import os
from github import Github
import pandas as pd
from functions import create_message


prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"

# IA Models Used
models_list: ollama.ListResponse = ollama.list()
models = [m.model for m in models_list.models]

df = pd.read_csv("input.csv")       # Reads the csv file

for index, row in df.iterrows():
    
    sha = row["P_COMMIT"]
    folder = os.path.join("responses", sha)     # Folder's path to save IA's response
    os.makedirs(folder, exist_ok=True)          # Creates the folder if it doens't exist
    content = create_message(row["Project"], prompt, sha)
    
    for model in models:
        
        if ":" in model:
            pos = model.find(":")
            model_name = model[:pos]
        elif model is None:
            continue
        else:
            model_name = model
        
        response: ollama.ChatResponse = ollama.chat(
            model = model,  # Este parâmetro define o modelo do ollama a ser usado
            messages = [{'role': 'user', 'content': content}],  # Aqui define-se quem está a usar o modelo e o seu conteúdo
            )
        
        path = os.path.join(folder, model_name + ".txt")  # Cria o caminho para o ficheiro no formato correto
        
        with open(path, "w", encoding="utf-8") as f:
            if response.message and response.message.content:
                f.write(response.message.content)
            else:
                f.write("[Sem Resposta do Modelo]")