import os
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
    "deepseek-coder-v2:16b",
    "gemma4:31b",
    "gpt-oss:120b_custom",
    "qwen3-coder:30b",
    "qwen3.8:27b",
]

NUM_RUNS = 5

df_real = csv_reader("cves_merged")
repo_cache: dict[str, Repository.Repository | Project] = {}

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if token is None:
    raise RuntimeError("GITHUB_TOKEN environment variable not set.")
auth = Auth.Token(token)
g = Github(auth=auth)
gl = Gitlab()

for model in models:
    print(f"\n=== Model: {model} ===")

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

        with ThreadPoolExecutor(max_workers=1) as executor:
            list(
                tqdm(
                    executor.map(executor_func, df_real.itertuples(index=False)),
                    total=len(df_real),
                    desc=f"{model} ({run_id})",
                    unit=" commits",
                )
            )