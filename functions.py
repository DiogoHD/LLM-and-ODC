from github import Github

def create_message(prompt: str, sha: str) -> str:
    "Dado uma prompt e um url de um commit, vai buscar o .diff desse url e junta-o à prompt, de forma a criar a mensagem para a IA"
   
    g = Github()
 
    repo = g.get_repo("torvalds/linux")
    commit = repo.get_commit(sha)
    
    with open("prompt.txt", "w") as p:
        for f in commit.files:
            p.write("\nFile name: " + f.filename + "\n")
            p.write("Changes: " + str(f.changes) + "\n")
            p.write("Patch (diff):\n" + f.patch + "\n")

    with open("prompt.txt", "r") as p:
        content = prompt + "\n" + p.read() # Junta a prompt e o commit
    
    return content

def choose_option(dictionary: dict[str,int]) -> str:
    "Retorna o elemento que apareceu mais vezes"
    # Determina o elemento mais dito pelo modelo com base no dicionario e retorna a chave
    output = max(dictionary, key=lambda k: dictionary[k])
    
    # Reseta os valores do dicionário
    for key in dictionary.keys():
        dictionary[key] = 0
        
    return output.capitalize()