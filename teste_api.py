import requests
import json

def inspecionar_todos_os_campos():
    url = "https://pncp.gov.br/api/search/"

    params = {
        "tipos_documento": "edital",
        "ordenacao": "-data",
        "pagina": 1,
        "tam_pagina": 1, # Pegamos apenas 1 para detalhar todos os campos
        "status": "recebendo_proposta",
        "unidades": 419
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print("Consultando a API do PNCP para mapear todos os campos disponíveis...\n")

    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=30)
        resposta.raise_for_status() 
        data = resposta.json()
        
        editais = data.get("items", [])
        
        if not editais:
            print("Nenhum edital encontrado com esses filtros.")
            return

        # Pega o primeiro edital retornado pela API
        primeiro_edital = editais[0]

        print("="*60)
        print("ESTRUTURA COMPLETA DE DADOS RETORNADA PELA API (SEARCH):")
        print("="*60)
        
        # Imprime o dicionário inteiro formatado em JSON legível
        print(json.dumps(primeiro_edital, ensure_ascii=False, indent=4))
        
        print("="*60)
        print("Dica: Procure nas chaves acima qual delas representa o número do edital (ex: sequencial, numero, etc.)")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar: {e}")

if __name__ == "__main__":
    inspecionar_todos_os_campos()