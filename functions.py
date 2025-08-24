from github import Github

def create_message(prompt: str, sha: str) -> str:
    "Given a prompt and a sha from a commit, gets the .diff of that commit and creates a message for the IA"
   
    g = Github()
 
    repo = g.get_repo("torvalds/linux")
    commit = repo.get_commit(sha)
    response_format = "Responds only in the format:\nDefect Type: ...\nDefect Qualifier: ..."
    
    with open("prompt.txt", "w") as p:
        for f in commit.files:
            p.write("\nFile name: " + f.filename + "\n")
            p.write("Changes: " + str(f.changes) + "\n")
            p.write("Patch (diff):\n" + f.patch + "\n")

    with open("prompt.txt", "r") as p:
        content = prompt + "\n" + p.read() + "\n" + response_format  # Junta a prompt e o commit
    
    return content

def choose_option(dictionary: dict[str,int], regex: bool) -> str:
    "Returns the response from the model"
    
    # If the response was in the correct format, chooses the option with the lowest position
    if regex:
        output = min(dictionary, key=lambda k: dictionary[k])
    # else, it chooses the option most mentioned by the IA
    else:
        output = max(dictionary, key=lambda k: dictionary[k])
    
    # Resets the values
    for key in dictionary.keys():
        dictionary[key] = 0
        
    return output.capitalize()