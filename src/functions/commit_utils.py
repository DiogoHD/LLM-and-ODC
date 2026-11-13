import csv
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

import requests
from github import Commit, Github, GithubException, Repository
from gitlab import Gitlab, GitlabError
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project, ProjectCommit

OUTPUT_FOLDER = "trustdev-output"

IGNORED_DIRS: set[str] = {
    # Tests and Examples
    "docs", "doc", "documentation", "examples", "example",
    "test", "tests", "testdata", "fixtures", "mocks", "stubs", "e2e",
    # Dependencies and Virtual Environments (kept venv, removed env for credential leak scanning)
    "vendor", "node_modules", "venv", ".venv",
    # Build, Output and Cache
    "build", "dist", "out", "target", "bin", "obj", "__pycache__", ".cache",
    # Version Control and IDEs
    ".git", ".svn", ".vscode", ".idea", "packages"
}

IGNORED_EXTENSIONS: set[str] = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".svg", ".webp",
    ".psd", ".ai", ".eps", ".indd", ".sketch",

    # Videos and audio
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".wav",

    # Fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",

    # Compressed archives
    ".zip", ".tar", ".gz", ".rar", ".7z",

    # Executables and libraries
    ".exe", ".dll", ".so", ".dylib", ".bin", ".class", ".jar",
    ".pyc", ".pyo", ".o", ".obj", ".lib", ".a", ".pdb", ".elf",

    # Virtual machine and disk images
    ".iso", ".img", ".vhd", ".vhdx", ".vmdk", ".qcow2", ".vdi", ".raw",
    ".sparsebundle", ".sparseimage", ".dmg", ".pkg", ".deb", ".rpm",

    # Documents and presentations
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".txt", ".md", ".rst",

    # Data files and configuration
    ".csv", ".tsv", ".xml", ".toml", ".ini", ".cfg", ".conf",

    # Database files
    ".db", ".sqlite", ".sqlite3", ".db3", ".sqlitedb",

    # Temporary and backup files
    ".log", ".bak", ".tmp", ".swp", ".swo", ".lock", ".map",
}

IGNORED_FILENAMES: set[str] = {
    # Legal and Meta
    "license", "licence", "changelog", "changes", "authors", "readme", 
    "contributing", "code_of_conduct", "security",
    # Dependency Manifests (Ignore if ODC focuses strictly on application logic)
    "go.sum", "package-lock.json", "yarn.lock", "pom.xml", "build.gradle", "requirements.txt",
    # Linters and Git configs
    ".gitignore", ".dockerignore", ".eslintignore", ".prettierrc"
}

# main.py 
def fetch_github_commit(repo_url: str, sha: str, g: Github, repo_cache: dict[str, Repository.Repository]) -> Commit.Commit | None:
    """Fetches a commit given a full GitHub repo path (e.g. 'argoproj/argo-cd') and SHA."""
    try:
        if repo_url not in repo_cache:
            repo_cache[repo_url] = g.get_repo(repo_url)
        return repo_cache[repo_url].get_commit(sha)
    except GithubException as e:
        if e.status == 404:
            print(f"Commit '{sha}' not found in GitHub repository '{repo_url}'")
            return None
        raise


def fetch_gitlab_commit(project: str, sha: str, gl: Gitlab, repo_cache: dict[str, Project]) -> ProjectCommit | None:
    """Given a project and a sha from a commit, fetches the commit from Gitlab """
    
    try:
        repo_name = project

        if repo_name not in repo_cache:
            repo_cache[repo_name] = gl.projects.get(repo_name)

        commit = repo_cache[repo_name].commits.get(sha)
        return commit
    except GitlabGetError as e:
        if e.response_code == 404:
            print(f"Commit '{sha}' not found in Gitlab project '{project}'")
            return None
        raise

@dataclass
class CommitFile:
    filename: str
    changes: int
    patch: str

def create_message(files: list[CommitFile], instruction: str) -> list[tuple[str, str]]:
    """"Given a commit and initial instruction, creates a prompt from the IA
    
    Args:
        commit (CommitFile): A commit from a repository, with its files, changes and patch
        instruction (str): An instruction for the IA that will join with the commit and a intended response format
        
    Returns:
        list[tuple[str, str]]: A list of tuples. Each tuple has a prompt and the name of the file that the prompt was created for
    """
    
    if files is None:
        return []
    
    response_format = "Your response should not provide an explanation and should only contain the following response format for each defect you classify in each file:\nDefect Type: <Defect Type>\nDefect Qualifier: <Defect Qualifier>"  
    # Save prompt for each file from the commit
    prompts = []
    for f in files:
        file_prompt = f"{instruction}\n\nFile name: {f.filename}\nChanges: {f.changes}\nPatch (diff):\n{f.patch}\n\n{response_format}"      # Joins the prompt with the commit and the format intended
        prompts.append((file_prompt, f.filename))
    
    return prompts

def call_model(model: str, prompt: str, folder: Path) -> None:
    """Calls IA model via ollama, runs the specified prompt and stores the response in a text file
    
    Args:
        model (str): The name of the IA model that will be run
        prompt (str): The message that will be given to the IA
        folder (Path): The folder where the text file will be stored in
    """
    
    model_name: str = model.partition(":")[0]       # Take model name before ':' if present
    file_path: Path = folder / f"{model_name}.txt"  # Creates the path to the text folder
    metrics_path: Path = folder / "metrics.csv"  # Creates the path to the metrics text folder
    
    if file_path.exists():
        return
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 4096,
            }
    }
    
    try:
        # Calls the model and measures the time taken for the response
        start = time.perf_counter()
        response = requests.post(
            os.getenv("CHAT_ENDPOINT"), 
            json=payload,
            auth=requests.auth.HTTPBasicAuth(os.getenv("CHAT_API_NAME"), os.getenv("CHAT_API_PASSWORD")),
        )
        response.raise_for_status()  # Raises an HTTPError if the response was an error
        elapsed = time.perf_counter() - start
        
        data = response.json()
        content = data["message"]["content"]
        prompt_eval_count = data.get("prompt_eval_count", 0)
        response_eval_count = data.get("eval_count", 0)
        
        file_path.write_text(content, encoding="utf-8")
        
        write_header = not metrics_path.exists()
        with open(metrics_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["Model", "Elapsed Time (seconds)", "Prompt Tokens", "Response Tokens", "Total Tokens"])
            
            writer.writerow([
                model, 
                round(elapsed, 3),
                prompt_eval_count, 
                response_eval_count, 
                prompt_eval_count + response_eval_count
            ])
            
    except (requests.RequestException, KeyError, TypeError, OSError) as e:
        print(f"Error calling model {model} or writing file {file_path}: {e}")

def normalize_github_files(commit: Commit.Commit) -> list[CommitFile]:
    if commit is None:
        return []
    
    return [
        CommitFile(
            filename=f.filename,
            changes=f.changes,
            patch=f.patch or ""
        )
        for f in commit.files
    ]

def normalize_gitlab_files(commit: ProjectCommit) -> list[CommitFile]:
    if commit is None:
        return []
    
    return [
        CommitFile(
            filename=f["new_path"],
            changes=f["diff"].count("\n"),  # aproximação, gitlab não dá changes direto
            patch=f["diff"] or ""
        )
        for f in commit.diff()
    ]

CACHE_DIR = Path(__file__).resolve().parents[2] / OUTPUT_FOLDER / ".commit_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_commit_files(row, g: Github, gl: Gitlab, repo_cache) -> list[CommitFile] | None:
    """Devolve os ficheiros do commit (None se não existe). Só vai à API na 1ª vez."""
    sha: str = row.P_COMMIT
    path = CACHE_DIR / f"{row.PLATFORM}__{row.REPO_PATH.replace('/', '-')}__{sha}.json"

    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return None if data is None else [CommitFile(**d) for d in data]

    if row.PLATFORM == "github":
        commit = fetch_github_commit(row.REPO_PATH, sha, g, repo_cache)
        files = normalize_github_files(commit) if commit is not None else None
    elif row.PLATFORM == "gitlab":
        commit = fetch_gitlab_commit(row.REPO_PATH, sha, gl, repo_cache)
        files = normalize_gitlab_files(commit) if commit is not None else None
    else:
        raise ValueError("Unsupported URL format")

    # Save the files to a temporary file first, then rename to avoid partial writes
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(None if files is None else [asdict(f) for f in files]),
        encoding="utf-8",
    )
    tmp.replace(path)
    return files

def should_ignore_file(filename: str) -> bool:
    """Returns True if the file is not source code worth classifying (docs, assets, lockfiles...)."""
    path = PurePosixPath(filename.lower())

    if any(part in IGNORED_DIRS for part in path.parts[:-1]):
        return True

    test_suffixes = ("_test.go", "_spec.rb", "test.ts", "test.js", "spec.js", "spec.ts", "test.py")
    if filename.lower().endswith(test_suffixes):
        return True

    if path.name in IGNORED_FILENAMES:
        return True
    if path.suffix in {"", ".md", ".rst", ".txt"} and path.stem in IGNORED_FILENAMES:
        return True

    return any(path.name.endswith(ext) for ext in IGNORED_EXTENSIONS)

def process_commit(
    row,
    prompt: str,
    model: str,
    g: Github,
    gl: Gitlab,
    repo_cache: dict[str, Repository.Repository | Project],
    run_id: str,
) -> None:
    sha: str = row.P_COMMIT
    
    try:
        files = get_commit_files(row, g, gl, repo_cache)
    except (GithubException, GitlabError, requests.RequestException) as e:
        print(f"Error fetching commit files for '{sha}' in repository '{row.REPO_PATH}': {e}")
        return
    
    if files is None:
        return

    files = [f for f in files if not should_ignore_file(f.filename)]
    if not files:
        print(f"No relevant files found in commit '{sha}' of repository '{row.REPO_PATH}'")
        return

    root_dir = Path(__file__).resolve().parents[2]
    sha_dir = root_dir / OUTPUT_FOLDER / "runs" / run_id / row.REPO_PATH.replace("/", "-") / sha

    for message, file_name in create_message(files, prompt):
        safe_name = file_name.replace("/", "-").replace(".", "_")
        file_dir = sha_dir / safe_name
        file_dir.mkdir(parents=True, exist_ok=True)
        call_model(model, message, file_dir)