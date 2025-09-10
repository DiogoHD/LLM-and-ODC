from github import Github, GithubException

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
    
    response_format = "Respond only in the format:\nDefect Type: <Defect Type>\nDefect Qualifier: <Defect Qualifier>"
    
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