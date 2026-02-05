import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import ollama
from github import Auth, Github, Repository
from tqdm import tqdm

from functions.commit_utils import process_commit
from functions.data_utils import excel_reader

prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"

# IA Models Used
models_list: ollama.ListResponse = ollama.list()
models = [m.model for m in models_list.models if m is not None and m.model is not None]

df_real = excel_reader("vulnerabilities")
repo_cache: dict[str, Repository.Repository] = {}

token = os.getenv("GITHUB_TOKEN")
if token is None:
    raise RuntimeError("GITHUB_TOKEN environment variable not set.")
auth = Auth.Token(token)
g = Github(auth=auth)

executor_func = partial(process_commit, prompt=prompt, models=models, g=g, repo_cache=repo_cache)

with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(executor_func, df_real.itertuples(index=False)), total=len(df_real), desc="Processing commits", unit=" commits"))