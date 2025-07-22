from ollama import chat
from colorama import Fore
from functions import create_message, choose_option

prompt = "A defect type can be one of the following categories: 1) Assignment/Initialization: a problem related to an assignment of a variable or no assignment at all; 2) Checking: a problem with conditional logic (e.g., condition in a if-clause or in a loop); 3) Timing: a problem with serialization of shared resources; 4) Algorithm/Method: a problem with implementation that does not require a design change to be fixed; 5) Function: a problem that needs a reasonable amount of code to be fixed due to incorrect implementation or no implementation at all; 6) Interface: a problem in the interaction between components (e.g., parameter list). With this in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? On the other hand, a defect qualifier can be one of the following categories: 1) Missing: new code needs to be added to fix the defect; 2) Incorrect: the code is incorrectly implemented and needs adjustment to fix the defect; 3) Extraneous: unnecessary. With that in mind, what’s the defect type of the orthogonal defect classification (ODC) in the following commit? With this in mind, what’s the defect type and defect qualifier of the orthogonal defect classification (ODC) in the following commit?"
url = "https://github.com/torvalds/linux/commit/91b80969ba466ba4b915a4a1d03add8c297add3f"
content = create_message(prompt, url)

# Tuples com os defect types, defect qualifiers e modelos usados
defect_types: dict[str,int] = {"assignment":0, "initialization":0, "checking":0, "timing":0, "algorithm":0, "method":0, "function":0, "interface":0}
defect_qualifiers: dict[str,int]  = {"missing":0, "incorrect":0, "extraneous":0}
models = ("gemma3", "llama3.2", "mistral", "phi3")

for model in models:
    stream = chat(
        model = model,  # Este parâmetro define o modelo do ollama a ser usado
        messages = [{'role': 'user', 'content': content}],  # Aqui define-se quem está a usar o modelo e o seu conteúdo
        stream = True,  # Permite ver a resposta enquanto se vai escrevendo
        )
    
    for chunk in stream:        
        found = False
        text = chunk['message']['content']
        
        # Encontra os defect types e qualifiers no texto
        # Neste momento mete de outra cor para melhor identificação manual mas, no futuro, servirá para automatizar
        for t in defect_types.keys():
            if t in text.lower():
                defect_types[t] += 1
                found = True
                print(Fore.BLUE + text + Fore.RESET, end='', flush=True)
                break
        
        for q in defect_qualifiers.keys():
            if q in text.lower():
                defect_qualifiers[q] += 1
                found = True
                print(Fore.RED + text + Fore.RESET, end='', flush=True)
        
        if not found:
            print(text, end='', flush=True)
            
    print("\n----------------------------------------------------")
    print(model)
    print(choose_option(defect_types))
    print(choose_option(defect_qualifiers))
    print("----------------------------------------------------")