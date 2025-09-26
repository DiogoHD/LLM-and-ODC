from pathlib import Path

import ollama
from github import Commit, Github, GithubException


# main.py 
def fetch_commit(project: str, sha: str) -> Commit.Commit | None:
    "Given a project and a sha from a commit, fetches the commit"
    
    g = Github()
    
    try:
        # Gets the repository
        match project:
            case "Linux":
                repo = g.get_repo("torvalds/linux")
            case "Mozilla":
                repo = g.get_repo("mozilla/gecko-dev")
            case "Xen":
                repo = g.get_repo("xen-project/xen")
            case _:
                print(f"Unknown Project '{project}' for commit '{sha}'")
                return None
        commit = repo.get_commit(sha)       # Gets the commit
        return commit
        
    except GithubException as e:
        print(f"Error accessing repository '{project}' with commit '{sha}': {e}")       # If it can't access the repo or the commit, ir prints an error
        return None

def create_message(commit: Commit.Commit, prompt: str) -> list[tuple[str, str]]:
    "Given a commit and initial prompt, creates a message from the IA"
    if commit is None:
        return []
    
    response_format = "Your response should not provide an explanation and should only contain the following response format for each defect you classify in each file:\nDefect Type: <Defect Type>\nDefect Qualifier: <Defect Qualifier>"  
    # Save prompt for each file from the commit
    content = []
    for f in commit.files:
        file_prompt = f"{prompt}\n\nFile name: {f.filename}\nChanges: {str(f.changes)}\nPatch (diff):\n{f.patch}\n\n{response_format}"      # Joins the prompt with the commit and the format intended
        content.append((file_prompt, f.filename))
    
    return content



def process_commit(row, prompt: str, models: list[str]) -> None:
    """
    Function used to work with ThreadPoolExecutor() from concurrent.future
    
    Args:
        row (pd.NamedTuple): The return value of itertuples()
        prompt (str): The prompt for the IA
        models (list[str]): A list of the IA models downloaded via ollama
    """
    script_dir = Path(__file__).parent          # Get the folder where this file is located (src/)
    output_dir = script_dir.parent / "output"   # Goes up one level and joins with data directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sha: str = row.P_COMMIT
    sha_dir: Path = output_dir / sha            # Directory's path to save IA's response
    sha_dir.mkdir(parents=True, exist_ok=True)  # Creates the directory if it doesn't exist; parents=True creates every needed parent directory if it doesn't exist; exist_ok=True doesn't give a error if the directory already exists
    
    # Create prompt for the IA
    commit: Commit.Commit = fetch_commit(row.Project, sha)
    content = create_message(commit, prompt)
    
    for message, file_name in content:
        safe_name = file_name.replace("/", "-").replace(".", "_")       # Replaces / and . so it doesn't create multiple directories and a file
        file_dir: Path = sha_dir / safe_name
        file_dir.mkdir(parents=True, exist_ok=True)
        for model in models:  
            call_model(model, message, file_dir)

def call_model(model: str, content: str, folder: Path) -> None:
    "Calls IA model via ollama, runs the specified prompt and stores the response in a text file"
    model_name: str = model.partition(":")[0]    # Take model name before ':' if present
    
    try:
        response: ollama.ChatResponse = ollama.chat(
            model = model,                                      # Defines which ollama's model is going to be used
            messages = [{"role": "user", "content": content}],  # Defines who's using the model and what's going to be its content
            )
        
        # Writes response in a text file
        file_path: Path = folder / f"{model_name}.txt"      # Creates the path to the text folder
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.message.content if response.message and response.message.content else "[No Model Response]")
        except (OSError, PermissionError, UnicodeEncodeError) as e:
            raise RuntimeError(f"Failed to write text file to {file_path}: {e}") from e
        
    except Exception as e:
        print(f"Error calling model {model} for file {folder.name} in commit {folder.parent.name}: {e}")