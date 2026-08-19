import pandas as pd

# Link modificado para exportar a aba "IMPORTRANGE - DO" direto como CSV
URL_PLANILHA = "Coloque o link da planilha do google sheets" #essa parte é completamente facultativa, eu usei essa planilha_do.py, como um identificador de unidade a partir de uma planilha interna, a planilha que eu usei era um import range da outra planilha kkk

# Nomes exatos baseados no seu print
NOME_COLUNA_EDITAL = "Nº DA CONTRATAÇÃO"
NOME_COLUNA_UNIDADE = "UApd"

def buscar_unidade_apoiada(numero_sequencial, ano):
    """
    Lê a aba específica da planilha da DO no Google Sheets e cruza o número 
    do edital para retornar a sigla da unidade apoiada (ex: DIRSA, HFAG).
    """
    # Formata o dado recebido da API para ficar igual ao do Sheets (ex: "90077/2025")
    edital_formatado = f"{numero_sequencial}/{ano}" 

    try:
        # Lê a planilha direto da web. 
        # (Nota: A planilha precisa estar com acesso "Qualquer pessoa com o link" para isso funcionar direto)
        df = pd.read_csv(URL_PLANILHA)
        
        # Limpa possíveis espaços invisíveis nos cabeçalhos que sempre quebram os scripts
        df.columns = df.columns.str.strip()
        
        # Converte a coluna inteira para texto para garantir que o "==" vai funcionar
        df[NOME_COLUNA_EDITAL] = df[NOME_COLUNA_EDITAL].astype(str).str.strip()
        
        # Faz a busca
        filtro = df[df[NOME_COLUNA_EDITAL] == edital_formatado]
        
        if not filtro.empty:
            unidade = filtro.iloc[0][NOME_COLUNA_UNIDADE]
            return str(unidade).strip()
        else:
            return "UNIDADE NÃO LOCALIZADA"
            
    except Exception as e:
        print(f"Erro ao acessar ou ler a planilha do Google Sheets: {e}")
        print("DICA: Verifique se a planilha está aberta para leitura ou se a internet caiu.")
        return "ERRO DE LEITURA"

# Teste rápido
if __name__ == "__main__":
    # Testando com um dado real do seu print (linha 9)
    numero_teste = "90077"
    ano_teste = "2025"
    
    unidade_encontrada = buscar_unidade_apoiada(numero_teste, ano_teste)
    print(f"Pesquisando {numero_teste}/{ano_teste}...")
    print(f"Resultado: {unidade_encontrada} (Esperado: HFAG)")