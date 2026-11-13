import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from dotenv import load_dotenv
from github import Auth, Github, Repository
from gitlab import Gitlab
from gitlab.v4.objects import Project
from tqdm import tqdm

from functions.commit_utils import process_commit
from functions.data_utils import csv_reader

prompt = "..."  # (igual ao teu)

# IA Models Used
models = [
    "deepseek-coder-v2:latest",
    "gemma4:31b",
    "qwen3-coder:30b",
    "qwen3.8:27b",
]

NUM_RUNS = 5

df_real = csv_reader("dataset_cve_parsed")
repo_cache: dict[str, Repository.Repository | Project] = {}

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if token is None:
    raise RuntimeError("GITHUB_TOKEN environment variable not set.")
auth = Auth.Token(token)
g = Github(auth=auth)
gl = Gitlab()

times_taken = {}
for model in models:
    print(f"\n=== Model: {model} ===")

    start = time.time()
    for run_idx in range(1, NUM_RUNS + 1):
        run_id = f"run_{run_idx}"
        print(f"\n--- {model} | {run_id} ({run_idx}/{NUM_RUNS}) ---")

        executor_func = partial(
            process_commit,
            prompt=prompt,
            model=model,
            g=g,
            gl=gl,
            repo_cache=repo_cache,
            run_id=run_id,
        )

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(
                tqdm(
                    executor.map(executor_func, df_real.itertuples(index=False)),
                    total=len(df_real),
                    desc=f"{model} ({run_id})",
                    unit=" commits",
                )
            )
    end = time.time()
    times_taken[model] = end - start

with open("times_taken.csv", "w", encoding="utf-8") as f:
    f.write("Model,Time Taken (seconds)\n")
    for model, time_taken in times_taken.items():
        f.write(f"{model},{time_taken}\n")