import ollama
from pathlib import Path
from github import Github
import pandas as pd
from functions import create_message


prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"

# IA Models Used
models_list: ollama.ListResponse = ollama.list()
models = [m.model for m in models_list.models]

df: pd.DataFrame = pd.read_csv("input.csv")       # Reads the csv file
responses_fodler: Path = Path("responses")

for index, row in df.iterrows():
    
    sha: str = row["P_COMMIT"]
    sha_folder: Path = responses_fodler / sha       # Folder's path to save IA's response
    sha_folder.mkdir(parents=True, exist_ok=True)   # Creates the folder if it doens't exist; parents=True creates every needed parent folder if it doesn't exist; exist_ok=True doesn't give a error if the folder already exists
    
    # Create prompt for the IA
    content = create_message(row["Project"], prompt, sha)
    if content is None:     # If there's some error in the function, goes to the next commit
        continue
        
    for model in models:
        if model is None:
            continue
        
        model_name: str = model.split(":", 1)[0]    # Splits : first ocurrence  and takes the first word before that ocurrence       
        
        try:
            response: ollama.ChatResponse = ollama.chat(
                model = model,                                      # Defines which ollama's model is going to be used
                messages = [{"role": "user", "content": content}],  # Defines who's using the model and what's going to be its content
                )
        except Exception as e:
            print(f"Error calling model {model} for commit {sha}: {e}")
            continue
        
        file_path: Path = sha_folder / f"{model_name}.txt"      # Creates the path to the text folder
        
        # Writes response in a text file
        with open(file_path, "w", encoding="utf-8") as f:
            if response.message and response.message.content:
                f.write(response.message.content)
            else:
                f.write("[No Model Response]")