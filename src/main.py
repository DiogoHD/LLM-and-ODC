from pathlib import Path

import ollama
import pandas as pd
from github import Commit, Github

from functions import call_model, create_message, fetch_commit

prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"

# IA Models Used
models_list: ollama.ListResponse = ollama.list()
models = [m.model for m in models_list.models if m is not None and m.model is not None]

df: pd.DataFrame = pd.read_csv("data/input.csv")       # Reads the csv file
output_folder: Path = Path("output")

for row in df.itertuples(index=False):
    
    sha: str = row.P_COMMIT
    sha_folder: Path = output_folder / sha       # Folder's path to save IA's response
    sha_folder.mkdir(parents=True, exist_ok=True)   # Creates the folder if it doesn't exist; parents=True creates every needed parent folder if it doesn't exist; exist_ok=True doesn't give a error if the folder already exists
    
    # Create prompt for the IA
    commit: Commit.Commit = fetch_commit(row.Project, sha)
    content = create_message(commit, prompt)
    
    for message, file_name in content:
        safe_name = file_name.replace("/", "-").replace(".", "_")       # Replaces / and . so it doesn't create multiple directories and a file
        file_folder: Path = sha_folder / safe_name
        file_folder.mkdir(parents=True, exist_ok=True)
        for model in models:  
            call_model(model, message, file_folder)