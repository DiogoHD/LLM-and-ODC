from github import Github

def create_message(project: str, prompt: str, sha: str) -> str:
    "Given a prompt and a sha from a commit, gets the commit and creates a message for the IA"
   
    g = Github()
    
    # Gets the repository 
    if project == "Linux":
        repo = g.get_repo("torvalds/linux")
    elif project == "Mozilla":
        repo = g.get_repo("mozilla/gecko-dev")
    elif project == "Xen":
        repo = g.get_repo("xen-project/xen")
    commit = repo.get_commit(sha)
    response_format = "Respond only in the format:\nDefect Type: <Defect Type>\nDefect Qualifier: <Defect Qualifier>"
    
    # Write commit in txt file
    with open("prompt.txt", "w") as p:
        for f in commit.files:
            p.write("\nFile name: " + f.filename + "\n")
            p.write("Changes: " + str(f.changes) + "\n")
            p.write("Patch (diff):\n" + f.patch + "\n")

    # Joins the prompt with the commit and the format intended
    with open("prompt.txt", "r") as p:
        content = prompt + "\n" + p.read() + "\n" + response_format  
    
    return content