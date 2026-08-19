import requests

def buscar_editais_cae():
    url = "https://pncp.gov.br/api/search/"

    # Estes parâmetros foram extraídos exatamente da Request URL do seu F12
    params = {
        "tipos_documento": "edital",
        "ordenacao": "-data",
        "pagina": 1,
        "tam_pagina": 100,
        "status": "recebendo_proposta",
        "unidades": 120195  
    }

    # Mantendo o cabeçalho similar ao do seu amigo para evitar bloqueios
    headers = {
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=60)
        
        # Levanta um erro se o status não for 200 OK (como o bolinha verde do seu print)
        resposta.raise_for_status() 
        
        data = resposta.json()
        
        # Retorna apenas a lista de editais que o projeto precisa
        return data.get("items", [])

    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão com a API do PNCP: {e}")
        return []

# Testando a função de forma isolada
if __name__ == "__main__":
    editais = buscar_editais_cae()
    for edital in editais:
        print(f"Edital encontrado: {edital.get('numero_sequencial')} / {edital.get('ano')}")