import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import urllib.request
import urllib.parse
import threading

import banco_dados
import planilha_do
import main

# Garante que o banco existe ao abrir a interface
banco_dados.inicializar_banco()

# ==========================================
# TELA DE LOGIN DO PROXY / PORTAL MILITAR
# ==========================================
def solicitar_credenciais_proxy():
    login_janela = tk.Tk()
    login_janela.title("Autenticação - Rede / Proxy")
    login_janela.geometry("380x250")
    login_janela.grab_set()

    tk.Label(login_janela, text="Acesso Restrito ao Proxy", font=("Arial", 12, "bold")).pack(pady=10)

    # Dica adicionada para caso o proxy exija domínio
    tk.Label(login_janela, text="CPF PORTAL MILITAR:\n(Dica: Se der erro, tente DOMINIO\\CPF)").pack(anchor="w", padx=30)
    entry_cpf = tk.Entry(login_janela, width=35)
    entry_cpf.pack(pady=5, padx=30)

    tk.Label(login_janela, text="SENHA PORTAL MILITAR:").pack(anchor="w", padx=30)
    entry_senha = tk.Entry(login_janela, width=35, show="*")
    entry_senha.pack(pady=5, padx=30)

    credenciais = {}

    def autenticar():
        cpf = entry_cpf.get().strip()
        senha = entry_senha.get().strip()
        if cpf and senha:
            credenciais["cpf"] = cpf
            credenciais["senha"] = senha
            login_janela.destroy()
        else:
            messagebox.showwarning("Aviso", "Preencha o CPF e a Senha para prosseguir.")

    tk.Button(login_janela, text="Entrar no Sistema", command=autenticar, bg="#4CAF50", fg="white", width=20).pack(pady=15)
    
    login_janela.mainloop()
    return credenciais.get("cpf", ""), credenciais.get("senha", "")


def extrair_numero_edital(titulo):
    match = re.search(r'\d+/\d+', titulo)
    if match:
        return match.group(0)
    return titulo

def abrir_janela_contatos():
    janela = tk.Toplevel()
    janela.title("Gerenciar Contatos das Unidades")
    janela.geometry("500x400")
    janela.grab_set() 

    frame_inputs = tk.Frame(janela)
    frame_inputs.pack(pady=10)

    tk.Label(frame_inputs, text="Unidade (Ex: HFAG):").grid(row=0, column=0, padx=5, pady=5)
    entry_unidade = tk.Entry(frame_inputs)
    entry_unidade.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Telefone (com DDD):").grid(row=1, column=0, padx=5, pady=5)
    entry_telefone = tk.Entry(frame_inputs)
    entry_telefone.grid(row=1, column=1, padx=5, pady=5)

    colunas = ("ID", "Unidade", "Telefone")
    tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=10)
    tabela.heading("ID", text="ID")
    tabela.heading("Unidade", text="Unidade")
    tabela.heading("Telefone", text="Telefone")
    tabela.column("ID", width=50)
    tabela.column("Unidade", width=150)
    tabela.column("Telefone", width=200)
    tabela.pack(pady=10)

    def atualizar_tabela():
        for row in tabela.get_children():
            tabela.delete(row)
        for linha in banco_dados.listar_contatos():
            tabela.insert("", tk.END, values=linha)

    def adicionar():
        unidade = entry_unidade.get().strip().upper()
        telefone = entry_telefone.get().strip()
        if unidade and telefone:
            banco_dados.adicionar_contato(unidade, telefone)
            atualizar_tabela()
            entry_unidade.delete(0, tk.END)
            entry_telefone.delete(0, tk.END)
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")

    def excluir():
        selecionado = tabela.selection()
        if selecionado:
            item = tabela.item(selecionado)
            id_contato = item['values'][0]
            banco_dados.excluir_contato(id_contato)
            atualizar_tabela()
        else:
            messagebox.showwarning("Aviso", "Selecione um contato na lista para excluir.")

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack()
    tk.Button(frame_botoes, text="Adicionar / Salvar", command=adicionar, width=15).grid(row=0, column=0, padx=5)
    tk.Button(frame_botoes, text="Excluir Selecionado", command=excluir, width=15).grid(row=0, column=1, padx=5)

    atualizar_tabela()

def abrir_janela_comandante():
    janela = tk.Toplevel()
    janela.title("Número do Comandante")
    janela.geometry("300x150")
    janela.grab_set()

    tk.Label(janela, text="Telefone do Comandante (com DDD):").pack(pady=10)
    entry_telefone = tk.Entry(janela, width=25)
    entry_telefone.pack(pady=5)

    numero_atual = banco_dados.buscar_numero_comandante()
    if numero_atual:
        entry_telefone.insert(0, numero_atual)

    def salvar():
        telefone = entry_telefone.get().strip()
        if telefone:
            banco_dados.salvar_numero_comandante(telefone)
            messagebox.showinfo("Sucesso", "Número do Comandante salvo com sucesso!")
            janela.destroy()
        else:
            messagebox.showwarning("Aviso", "O campo não pode ficar vazio.")

    tk.Button(janela, text="Salvar Número", command=salvar).pack(pady=10)

def abrir_janela_historico():
    janela = tk.Toplevel()
    janela.title("Painel de Controle de Envios")
    janela.geometry("650x450")
    janela.grab_set()

    colunas = ("ID", "Edital", "Unidade", "Data", "Status")
    tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=12)
    for col in colunas:
        tabela.heading(col, text=col)
    
    tabela.column("ID", width=40)
    tabela.column("Edital", width=100)
    tabela.column("Unidade", width=100)
    tabela.column("Data", width=150)
    tabela.column("Status", width=200) # Aumentei pra caber o emoji bonitinho
    tabela.pack(pady=15, padx=10, fill="x")

    def atualizar_tabela():
        for row in tabela.get_children():
            tabela.delete(row)
        for linha in banco_dados.listar_historico():
            tabela.insert("", tk.END, values=linha)

    def excluir_selecionado():
        selecionado = tabela.selection()
        if selecionado:
            item = tabela.item(selecionado[0])
            id_registro = item['values'][0]
            banco_dados.excluir_registro_historico(id_registro)
            atualizar_tabela()
        else:
            messagebox.showwarning("Aviso", "Selecione um edital no histórico para excluir.")

    def limpar():
        resposta = messagebox.askyesno("Atenção", "Tem certeza que deseja excluir TODO o histórico?")
        if resposta:
            banco_dados.limpar_historico()
            atualizar_tabela()

    frame_botoes_hist = tk.Frame(janela)
    frame_botoes_hist.pack(pady=5)
    
    tk.Button(frame_botoes_hist, text="🗑️ Excluir Selecionado", command=excluir_selecionado, width=20).grid(row=0, column=0, padx=10)
    tk.Button(frame_botoes_hist, text="⚠️ Limpar TUDO", command=limpar, bg="#ffcccc", width=20).grid(row=0, column=1, padx=10)
    
    atualizar_tabela()

def iniciar_interface():
    # 1. Abre a tela de login ANTES do painel principal
    cpf_usuario, senha_usuario = solicitar_credenciais_proxy()
    
    if not cpf_usuario or not senha_usuario:
        messagebox.showwarning("Aviso", "Iniciando sem credenciais. A rede pode bloquear a busca dos editais.")
    
    # 2. Salva as credenciais na memória do main para a API usar
    main.CONFIG_PROXY_AUTON = {
        "cpf": cpf_usuario,
        "senha": senha_usuario
    }

    # 3. Abre o painel principal
    root = tk.Tk()
    root.title("Controle Automático - Editais PNCP (CAE)")
    root.geometry("750x650") 
    
    tk.Label(root, text="Painel de Controle - Editais PNCP", font=("Arial", 14, "bold")).pack(pady=10)

    # --- FRAME DE PRÉ-VISUALIZAÇÃO ---
    frame_preview = tk.LabelFrame(root, text=" Pré-visualização de Editais Recentes (API & Planilha DO) ", font=("Arial", 10, "bold"))
    frame_preview.pack(fill="both", expand=True, padx=15, pady=5)

    # Estrutura da Tabela
    colunas_prev = ("Edital", "Órgão", "Unidade Destino", "Objeto_Oculto")
    tabela_prev = ttk.Treeview(frame_preview, columns=colunas_prev, show="headings", height=6, displaycolumns=("Edital", "Órgão", "Unidade Destino"))
    
    tabela_prev.heading("Edital", text="Nº Edital")
    tabela_prev.heading("Órgão", text="Órgão")
    tabela_prev.heading("Unidade Destino", text="Unidade")
    
    tabela_prev.column("Edital", width=100)
    tabela_prev.column("Órgão", width=300)
    tabela_prev.column("Unidade Destino", width=150)
    tabela_prev.pack(side="top", fill="both", expand=True, padx=5, pady=5)
    
    # --- CAIXINHA DE TEXTO PARA LER O OBJETO ---
    frame_detalhes = tk.Frame(frame_preview)
    frame_detalhes.pack(fill="both", expand=False, padx=5, pady=5)
    
    tk.Label(frame_detalhes, text="📦 Objeto do Edital Selecionado:", font=("Arial", 9, "bold")).pack(anchor="w")
    
    texto_objeto = tk.Text(frame_detalhes, height=4, wrap="word", bg="#f9f9f9", font=("Arial", 9))
    texto_objeto.pack(fill="both", expand=True)

    def ao_selecionar_edital(event):
        """Atualiza a caixinha de texto com o objeto do edital selecionado na tabela"""
        selecionado = tabela_prev.selection()
        if selecionado:
            item = tabela_prev.item(selecionado[0])
            objeto_completo = item['values'][3]
            texto_objeto.delete("1.0", tk.END)
            texto_objeto.insert(tk.END, objeto_completo)

    tabela_prev.bind("<<TreeviewSelect>>", ao_selecionar_edital)

    def carregar_preview():
        """Busca os dados na API passando as credenciais no formato do Proxy."""
        for row in tabela_prev.get_children():
            tabela_prev.delete(row)
        texto_objeto.delete("1.0", tk.END) 
        
        try:
            url_busca = "https://pncp.gov.br/api/search/"
            params_busca = {
                "tipos_documento": "edital",
                "ordenacao": "-data",
                "pagina": 1,
                "tam_pagina": 10,
                "status": "recebendo_proposta",
                "unidades": 419
            }
            headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
            
            proxies_config = None
            if main.CONFIG_PROXY_AUTON["cpf"] and main.CONFIG_PROXY_AUTON["senha"]:
                cpf_codificado = urllib.parse.quote(main.CONFIG_PROXY_AUTON["cpf"])
                senha_codificada = urllib.parse.quote(main.CONFIG_PROXY_AUTON["senha"])
                
                proxies_sistema = urllib.request.getproxies()
                if proxies_sistema:
                    proxies_config = {}
                    for proto, url_proxy in proxies_sistema.items():
                        if "://" in url_proxy:
                            base, rest = url_proxy.split("://", 1)
                            proxies_config[proto] = f"{base}://{cpf_codificado}:{senha_codificada}@{rest}"

            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            resposta = requests.get(url_busca, params=params_busca, headers=headers, proxies=proxies_config, verify=False, timeout=15)
            resposta.raise_for_status()
            editais = resposta.json().get("items", [])

            for edital in editais:
                titulo_bruto = edital.get("title", "")
                id_edital = extrair_numero_edital(titulo_bruto)
                
                orgao = edital.get("orgao_nome", "Órgão não informado")
                
                objeto_resumo = edital.get("description") or "Sem descrição disponível."
                objeto_resumo = objeto_resumo.replace('\n', ' ') 
                
                partes = id_edital.split('/')
                if len(partes) == 2:
                    num_pesquisa, ano_pesquisa = partes[0], partes[1]
                else:
                    num_pesquisa, ano_pesquisa = edital.get("numero_sequencial"), edital.get("ano")

                unidade_encontrada = planilha_do.buscar_unidade_apoiada(num_pesquisa, ano_pesquisa)
                
                tabela_prev.insert("", tk.END, values=(id_edital, orgao, unidade_encontrada, objeto_resumo))
            
            messagebox.showinfo("Sucesso", "Pré-visualização atualizada! Clique em um edital para ler o Objeto.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os dados da API:\n{e}")

    tk.Button(frame_preview, text="🔄 Atualizar Pré-visualização", command=carregar_preview, bg="#e6f2ff").pack(pady=5)

    # --- BOTÕES DE AÇÃO DO SISTEMA ---
    frame_botoes = tk.Frame(root)
    frame_botoes.pack(pady=10)

    def disparar_envios():
        resposta = messagebox.askokcancel("Confirmar Execução", "Deseja iniciar o envio automático dos editais via WhatsApp?")
        if resposta:
            thread = threading.Thread(target=main.executar_fluxo_completo)
            thread.start()
            messagebox.showinfo("Iniciado", "O robô foi acionado em segundo plano! Acompanhe o progresso pelo terminal.")

    tk.Button(frame_botoes, text="▶ INICIAR ENVIO DE EDITAIS", command=disparar_envios, width=30, height=2, bg="#d9f2d9", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)

    # Menu secundário
    frame_menu = tk.Frame(root)
    frame_menu.pack(pady=5)

    tk.Button(frame_menu, text="1. Gerenciar Contatos", command=abrir_janela_contatos, width=22).grid(row=0, column=0, padx=5)
    tk.Button(frame_menu, text="2. Nº do Comandante", command=abrir_janela_comandante, width=22).grid(row=0, column=1, padx=5)
    tk.Button(frame_menu, text="3. Histórico de Envios", command=abrir_janela_historico, width=22).grid(row=0, column=2, padx=5)

    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()