from ollama import chat
from colorama import Fore, Style
from requests import get
from functions import create_message

prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With that in mind, what's the defect type of the orthogonal defect classification (ODC) in the following commit?"
url = "https://github.com/torvalds/linux/commit/91b80969ba466ba4b915a4a1d03add8c297add3f"
content = create_message(prompt, url)

# Tuples com os defect types, defect qualifiers e modelos usados
defect_types = ("Assignment", "Initialization", "Checking", "Timing", "Algorithm", "Method", "Function", "Interface")
defect_qualifiers = ("Missing", "Incorrect", "Extraneous")
models = ("gemma3", "llama3.2", "mistral", "phi3")

for model in models:
    stream = chat(
        model = model,  # Este parâmetro define o modelo do ollama a ser usado
        messages = [{'role': 'user', 'content': content}],  # Aqui define-se quem está a usar o modelo e o seu conteúdo
        stream = True,  # Permite ver a resposta enquanto se vai escrevendo
        )
    print("\n----------------------------------------------------")
    print(model)
    print("----------------------------------------------------")
    for chunk in stream:
        text = chunk['message']['content']
        # Algo está mal, porque acho que um chunk pode ter mais do que uma palavra
        if text.capitalize() in defect_types: 
            print(Fore.BLUE + text + Fore.RESET, end='', flush=True)
        elif text.capitalize() in defect_qualifiers:
            print(Fore.RED + text + Fore.RESET, end='', flush=True)
        else:
            print(text, end='', flush=True)