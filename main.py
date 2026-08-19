import requests
import time
re_import = __import__('re')
from datetime import datetime
import urllib.request
import urllib.parse
import urllib3

# Importando os módulos que já construímos
import banco_dados
import planilha_do
import whatsapp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dicionário dinâmico que vai receber os dados digitados na tela inicial
CONFIG_PROXY_AUTON = {"cpf": "", "senha": ""}

def extrair_numero_edital(titulo):
    match = re_import.search(r'\d+/\d+', titulo)
    if match:
        return match.group(0)
    return titulo

def formatar_mensagem_unidade(unidade_destino, titulo_edital, ano, orgao, cnpj, modalidade, situacao, 
                             pub, atualizacao, inicio_vigencia, fim_vigencia, objeto):
    
    def fmt_data(data_str):
        if not data_str:
            return "Não informada"
        try:
            limpa = data_str.split('.')[0]
            return datetime.fromisoformat(limpa).strftime('%d/%m/%Y %H:%M')
        except:
            return data_str

    mensagem = (
        f"🏢 *Unidade do Contrato:* {unidade_destino}\n"
        f"🚨 *{titulo_edital} - PNCP* 🚨\n\n"
        f"📅 *Ano:* {ano}\n"
        f"🏛 *Órgão:* {orgao}\n"
        f"🏢 *CNPJ do Órgão:* {cnpj}\n"
        f"📋 *Modalidade:* {modalidade}\n"
        f"📌 *Situação:* {situacao}\n\n"
        f"🕒 *Data de Publicação PNCP:* {fmt_data(pub)}\n"
        f"🔄 *Data de Atualização PNCP:* {fmt_data(atualizacao)}\n"
        f"🟢 *Início da Vigência/Propostas:* {fmt_data(inicio_vigencia)}\n"
        f"🔴 *Fim da Vigência/Propostas:* {fmt_data(fim_vigencia)}\n\n"
        f"📦 *Objeto:*\n{objeto}\n\n"
        f"_Mensagem automática do sistema de controle do CAE._"
    )
    return mensagem

def formatar_mensagem_comandante(qtd_enviados, lista_unidades):
    hoje = datetime.now().strftime('%d/%m/%Y')
    
    if qtd_enviados == 0:
        return f"Olá essa é uma mensagem automática, hoje ({hoje}) não houve novas atualizações de editais."

    unidades_str = ", ".join(set(lista_unidades)) 
    
    mensagem = (
        f"Olá Comandante, essa é uma mensagem automática!\n hoje ({hoje}) foram enviados:\n "
        f"{qtd_enviados} edital(ais) para a(as) unidade(es): \n({unidades_str}).\n "
        f"Caso tenha alguma duvida consulte a ASSGOV do CAE para mais informações!"
    )
    return mensagem

def executar_fluxo_completo():
    print("\n" + "="*50)
    print("INICIANDO VARREDURA DE EDITAIS...")
    print("="*50)

    historico = banco_dados.listar_historico()
    editais_ja_enviados = [linha[1] for linha in historico]
    
    contatos_cadastrados = {linha[1]: linha[2] for linha in banco_dados.listar_contatos()}
    telefone_comandante = banco_dados.buscar_numero_comandante()

    url_busca = "https://pncp.gov.br/api/search/"
    params_busca = {
        "tipos_documento": "edital",
        "ordenacao": "-data",
        "pagina": 1,
        "tam_pagina": 10,
        "status": "recebendo_proposta",
        "unidades": 419
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    proxies_config = None
    if CONFIG_PROXY_AUTON["cpf"] and CONFIG_PROXY_AUTON["senha"]:
        cpf_codificado = urllib.parse.quote(CONFIG_PROXY_AUTON["cpf"])
        senha_codificada = urllib.parse.quote(CONFIG_PROXY_AUTON["senha"])
        
        proxies_sistema = urllib.request.getproxies()
        if proxies_sistema:
            proxies_config = {}
            for proto, url_proxy in proxies_sistema.items():
                if "://" in url_proxy:
                    base, rest = url_proxy.split("://", 1)
                    proxies_config[proto] = f"{base}://{cpf_codificado}:{senha_codificada}@{rest}"

    editais = []
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            # verify=False ADICIONADO AQUI
            resposta = requests.get(url_busca, params=params_busca, headers=headers, proxies=proxies_config, verify=False, timeout=30)
            resposta.raise_for_status()
            editais = resposta.json().get("items", [])
            break 
        except Exception as e:
            print(f"⚠️ Tentativa {tentativa + 1} falhou devido a instabilidade na API: {e}")
            if tentativa < tentativas - 1:
                print("Aguardando 3 segundos para tentar novamente...")
                time.sleep(3)
            else:
                print("❌ Erro crítico: O servidor do PNCP fechou a conexão repetidas vezes. Verifique a rede/proxy.")
                return

    editais_para_processar = []
    for edital in editais:
        titulo_bruto = edital.get("title", "")
        id_edital = extrair_numero_edital(titulo_bruto)
        if id_edital not in editais_ja_enviados:
            editais_para_processar.append(edital)

    if not editais_para_processar:
        print("Nenhum edital novo para enviar. Sistema atualizado!")
        return

    driver = whatsapp.iniciar_driver()
    if not driver:
        print("Falha ao iniciar o WhatsApp. Abortando operação.")
        return

    qtd_sucesso = 0
    unidades_notificadas = []
    hoje_str = datetime.now().strftime('%d/%m/%Y %H:%M')

    for edital in editais_para_processar:
        titulo_bruto = edital.get("title", "")
        id_edital = extrair_numero_edital(titulo_bruto)
        
        cnpj = edital.get("orgao_cnpj")
        ano = edital.get("ano")
        numero_seq = edital.get("numero_sequencial")
        orgao_nome = edital.get("orgao_nome")

        print(f"\nProcessando Edital: {id_edital}...")

        partes = id_edital.split('/')
        if len(partes) == 2:
            num_pesquisa, ano_pesquisa = partes[0], partes[1]
        else:
            num_pesquisa, ano_pesquisa = numero_seq, ano

        unidade_destino = planilha_do.buscar_unidade_apoiada(num_pesquisa, ano_pesquisa)
        
        # O PULO DO GATO: Pega a descrição da busca geral caso a específica falhe
        objeto_resumo_busca = edital.get("description") or ""
        
        url_especifica = f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano_pesquisa}/{numero_seq}"
        try:
            # CORREÇÃO CRÍTICA: verify=False ADICIONADO AQUI TAMBÉM!
            resp_esp = requests.get(url_especifica, headers=headers, proxies=proxies_config, verify=False, timeout=30)
            dados_completos = resp_esp.json()
        except:
            dados_completos = {}

        modalidade = dados_completos.get("modalidadeLicitacaoNome") or edital.get("modalidade_licitacao_nome", "Não informada")
        situacao = dados_completos.get("situacaoCompraNome") or edital.get("situacao_nome", "Não informada")
        pub = edital.get("data_publicacao_pncp", "")
        atualizacao = edital.get("data_atualizacao_pncp", "")
        inicio_vigencia = dados_completos.get("dataInicioVigencia") or edital.get("data_inicio_vigencia", "")
        fim_vigencia = dados_completos.get("dataFimVigencia") or edital.get("data_fim_vigencia", "")
        
        # AQUI A REDE DE SEGURANÇA: Se dados_completos falhar, ele usa o objeto_resumo_busca
        objeto_texto = dados_completos.get("objetoCompra") or dados_completos.get("objeto") or objeto_resumo_busca or "Sem descrição detalhada."

        telefone_destino = contatos_cadastrados.get(unidade_destino)

        if telefone_destino:
            mensagem = formatar_mensagem_unidade(
                unidade_destino=unidade_destino,
                titulo_edital=id_edital, 
                ano=ano_pesquisa, 
                orgao=orgao_nome, 
                cnpj=cnpj, 
                modalidade=modalidade, 
                situacao=situacao, 
                pub=pub, 
                atualizacao=atualizacao, 
                inicio_vigencia=inicio_vigencia, 
                fim_vigencia=fim_vigencia, 
                objeto=objeto_texto
            )
            
            sucesso = whatsapp.enviar_mensagem(driver, telefone_destino, mensagem)
            
            if sucesso:
                banco_dados.registrar_envio(id_edital, unidade_destino, hoje_str, "✅ Enviado")
                qtd_sucesso += 1
                unidades_notificadas.append(unidade_destino)
            else:
                banco_dados.registrar_envio(id_edital, unidade_destino, hoje_str, "❌ Falha no Envio")
        else:
            print(f"⚠️ Unidade {unidade_destino} não encontrada nos contatos do sistema.")
            banco_dados.registrar_envio(id_edital, unidade_destino, hoje_str, "❌ Sem Telefone")

    if telefone_comandante and qtd_sucesso > 0:
        print("\nEnviando relatório para o Comandante...")
        msg_comandante = formatar_mensagem_comandante(qtd_sucesso, unidades_notificadas)
        whatsapp.enviar_mensagem(driver, telefone_comandante, msg_comandante)
    
    time.sleep(3)
    whatsapp.fechar_driver(driver)
    print("\n✅ CICLO FINALIZADO COM SUCESSO!")

if __name__ == "__main__":
    executar_fluxo_completo()