from github import Github, GithubException
import ollama
from pathlib import Path

def create_message(project: str, prompt: str, sha: str) -> str | None:
    "Given a prompt and a sha from a commit, gets the commit and creates a message for the IA"
   
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
        
    except GithubException as e:
        print(f"Error accessing repository '{project}' with commit '{sha}': {e}")       # If it can't access the repo or the commit, ir prints an error
        return None
    
    response_format = "Your response should not provide an explanation and should only contain the following response format for each defect you classify:\nDefect Type: <Defect Type>\nDefect Qualifier: <Defect Qualifier>"
    
    # Write commit in txt file
    with open("prompt.txt", "w", encoding="utf-8") as p:
        for f in commit.files:
            p.write(f"\nFile name: {f.filename}\n")
            p.write(f"Changes: {str(f.changes)}\n")
            p.write(f"Patch (diff):\n{f.patch}\n")

    # Joins the prompt with the commit and the format intended
    with open("prompt.txt", "r", encoding="utf-8") as p:
        content = prompt + "\n" + p.read() + "\n" + response_format  
    
    return content

def call_model(model: str, content: str, sha_folder: Path) -> None:
    model_name: str = model.partition(":")[0]    # Take model name before ':' if present
    try:
        response: ollama.ChatResponse = ollama.chat(
            model = model,                                      # Defines which ollama's model is going to be used
            messages = [{"role": "user", "content": content}],  # Defines who's using the model and what's going to be its content
            )
        
        # Writes response in a text file
        file_path: Path = sha_folder / f"{model_name}.txt"      # Creates the path to the text folder
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.message.content if response.message and response.message.content else "[No Model Response]")
        
    except Exception as e:
        print(f"Error calling model {model} for commit {sha_folder.name}: {e}")