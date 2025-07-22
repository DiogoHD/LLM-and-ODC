from requests import get

def create_message(prompt: str, url: str) -> str:
    "Dado uma prompt e um url de um commit, vai buscar o .diff desse url e junta-o à prompt, de forma a criar a mensagem para a IA"
    
    # Adiciona a extensão ao url se este ainda não a tiver
    if not url.endswith(".diff"):
        url += ".diff"

    response = get(url)               # Envia um pedido HTTP do tipo GET para o url e retorna um objeto Response com várias informações sobre a reposta do servidor
    response.raise_for_status()       # Dá erro se não conseguir aceder
    commit = response.text            # Devolve apenas o conteúdo da resposta HTTP como string
    content = prompt + "\n" + commit  # Junta a prompt e o commit
    return content