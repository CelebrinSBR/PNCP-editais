import sqlite3
import os

DB_NAME = "controle_editais.db"

def conectar():
    """Cria a conexão com o banco de dados."""
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria as tabelas estruturadas caso não existam."""
    conexao = conectar()
    cursor = conexao.cursor()

    # Tabela de Contatos das Unidades (ex: HFAG, SDAP)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unidade TEXT UNIQUE NOT NULL,
            telefone TEXT NOT NULL
        )
    """)

    # Tabela para armazenar o número do Comandante (terá apenas 1 registro)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    """)

    # Tabela de Histórico de Envios para controle visual e relatório
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_envios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_edital TEXT NOT NULL,
            unidade_destino TEXT NOT NULL,
            data_envio TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()
    print("Banco de dados inicializado com sucesso.")

# ==========================================
# FUNÇÕES PARA CONTATOS DAS UNIDADES
# ==========================================
def adicionar_contato(unidade, telefone):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("INSERT INTO contatos (unidade, telefone) VALUES (?, ?)", (unidade, telefone))
        conexao.commit()
    except sqlite3.IntegrityError:
        print(f"Erro: A unidade {unidade} já está cadastrada.")
    finally:
        conexao.close()

def listar_contatos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, unidade, telefone FROM contatos")
    resultado = cursor.fetchall()
    conexao.close()
    return resultado

def excluir_contato(id_contato):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM contatos WHERE id = ?", (id_contato,))
    conexao.commit()
    conexao.close()

# ==========================================
# FUNÇÕES PARA O COMANDANTE
# ==========================================
def salvar_numero_comandante(telefone):
    """Usa a instrução REPLACE para inserir ou atualizar o número."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("REPLACE INTO configuracoes (chave, valor) VALUES ('telefone_comandante', ?)", (telefone,))
    conexao.commit()
    conexao.close()

def buscar_numero_comandante():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'telefone_comandante'")
    resultado = cursor.fetchone()
    conexao.close()
    return resultado[0] if resultado else None

# ==========================================
# FUNÇÕES PARA O HISTÓRICO DE ENVIOS
# ==========================================
def registrar_envio(numero_edital, unidade_destino, data_envio, status="Enviado"):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO historico_envios (numero_edital, unidade_destino, data_envio, status)
        VALUES (?, ?, ?, ?)
    """, (numero_edital, unidade_destino, data_envio, status))
    conexao.commit()
    conexao.close()

def listar_historico():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, numero_edital, unidade_destino, data_envio, status FROM historico_envios ORDER BY id DESC")
    resultado = cursor.fetchall()
    conexao.close()
    return resultado

def limpar_historico():
    """Função para o botão de excluir histórico (para testes)."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM historico_envios")
    conexao.commit()
    conexao.close()

# Inicializa o banco ao rodar o script
if __name__ == "__main__":
    inicializar_banco()
    
def excluir_registro_historico(id_registro):
    """Exclui um envio específico do histórico usando o ID do banco."""
    conexao = conectar() 
    cursor = conexao.cursor()
    # Tem que estar historico_envios aqui embaixo!
    cursor.execute("DELETE FROM historico_envios WHERE id = ?", (id_registro,))
    conexao.commit()
    conexao.close()