from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import ollama
import pandas as pd

from functions import process_commit

prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"

# IA Models Used
models_list: ollama.ListResponse = ollama.list()
models = [m.model for m in models_list.models if m is not None and m.model is not None]

script_dir = Path(__file__).parent      # Get the folder where this file is located (src/)
data_dir = script_dir.parent / "data"   # Goes up one level and joins with data folder
data_dir.mkdir(parents=True, exist_ok=True)
input_path = data_dir / "input.csv"
try:
    df: pd.DataFrame = pd.read_csv(input_path, encoding="utf-8")  # Reads the csv file
except (OSError, PermissionError, UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
    raise RuntimeError(f"Cannot read the required CSV from {input_path}: {e}") from e

executor_func = partial(process_commit, prompt=prompt, models=models)

with ThreadPoolExecutor() as executor:
    executor.map(executor_func, df.itertuples(index=False))