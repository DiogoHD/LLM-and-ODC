from github import Github

def create_message(project: str, prompt: str, sha: str) -> str:
    "Given a prompt and a sha from a commit, gets the .diff of that commit and creates a message for the IA"
   
    g = Github()
    
    if project == "Linux":
        repo = g.get_repo("torvalds/linux")
    elif project == "Mozilla":
        repo = g.get_repo("mozilla/gecko-dev")
    elif project == "Xen":
        repo = g.get_repo("xen-project/xen")
    commit = repo.get_commit(sha)
    response_format = "Respond only in the format:\nDefect Type: ...\nDefect Qualifier: ..."
    
    with open("prompt.txt", "w") as p:
        for f in commit.files:
            p.write("\nFile name: " + f.filename + "\n")
            p.write("Changes: " + str(f.changes) + "\n")
            p.write("Patch (diff):\n" + f.patch + "\n")

    with open("prompt.txt", "r") as p:
        content = prompt + "\n" + p.read() + "\n" + response_format  # Junta a prompt e o commit
    
    return content