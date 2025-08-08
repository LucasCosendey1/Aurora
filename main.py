import psycopg2
import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES ---
# As configurações agora são lidas do arquivo .env para maior segurança e flexibilidade.
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "client_encoding": "utf8" # Mantém a configuração de codificação explícita
}

# Lista de regionais válidas para o projeto AURORA
REGIONAIS_VALIDAS = ["ESE", "EMR", "EMS"]

# --- SIMULAÇÃO DA API DO MISTRAL ---
# Esta função foi aprimorada para extrair colaborador, tarefa e regional de um único texto.
def call_mistral_api_simulada(texto_usuario: str) -> dict:
    """
    Simula uma chamada à API do Mistral para extrair dados estruturados de um texto.

    Args:
        texto_usuario: O texto completo informado pelo usuário.

    Returns:
        Um dicionário com 'colaborador', 'tarefa' e 'regional', ou None se falhar.
    """
    print("\n[Mistral SIM] Analisando o texto para extrair informações...")

    # 1. Extrair a Regional
    regional_encontrada = None
    for regional in REGIONAIS_VALIDAS:
        if re.search(r'\b' + regional + r'\b', texto_usuario, flags=re.IGNORECASE):
            regional_encontrada = regional.upper()
            break
    
    if not regional_encontrada:
        print("[Mistral SIM] ERRO: Nenhuma regional válida (ESE, EMR, EMS) foi encontrada.")
        return None

    # 2. Extrair o Colaborador
    colaborador_encontrado = None
    # Procura por padrões como "Meu nome é Carlos", "Eu sou o Carlos", "Aqui é o Carlos"
    padrao_nome = r'(?:meu nome é|eu sou|aqui é)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    match_nome = re.search(padrao_nome, texto_usuario, flags=re.IGNORECASE)
    
    if match_nome:
        colaborador_encontrado = match_nome.group(1).strip()
    else:
        # Se não encontrar um padrão claro, podemos adicionar lógicas mais complexas aqui no futuro.
        # Por enquanto, se não houver um padrão claro, a extração falha.
        print("[Mistral SIM] ERRO: Não foi possível identificar o nome do colaborador. Tente usar 'Meu nome é...' ou 'Eu sou...'.")
        return None

    # 3. Definir a Tarefa
    # A tarefa é o texto original completo. O Mistral real poderia resumi-lo.
    tarefa = texto_usuario

    resultado_json = {
        "colaborador": colaborador_encontrado,
        "tarefa": tarefa,
        "regional": regional_encontrada
    }
    
    print(f"[Mistral SIM] Informações extraídas com sucesso: {resultado_json}")
    return resultado_json

# --- FUNÇÃO DE BANCO DE DADOS (sem alterações) ---
def registrar_atividade_no_banco(colaborador: str, tarefa: str, regional: str):
    """
    Conecta-se ao banco de dados PostgreSQL e insere uma nova atividade.
    """
    conn = None
    try:
        print("\n[DB] Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("[DB] Conexão bem-sucedida!")

        sql_insert = """
            INSERT INTO atividades (colaborador, tarefa, regional, horario)
            VALUES (%s, %s, %s, %s);
        """
        
        horario_atual = datetime.now()
        cur.execute(sql_insert, (colaborador, tarefa, regional, horario_atual))
        conn.commit()
        
        print("\n✅ Sucesso! Atividade registrada no banco de dados AURORA.")
        print(f"   - Colaborador: {colaborador}")
        print(f"   - Tarefa: {tarefa}")
        print(f"   - Regional: {regional}")
        print(f"   - Horário: {horario_atual.strftime('%Y-%m-%d %H:%M:%S')}")

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"\n❌ ERRO: Não foi possível registrar a atividade no banco de dados.")
        print(f"   - Detalhe do erro: {error}")
    finally:
        if conn is not None:
            conn.close()
            print("\n[DB] Conexão com o banco de dados fechada.")

# --- FLUXO PRINCIPAL DO AURORA (atualizado) ---
def iniciar_aurora():
    """
    Função principal que gerencia a interação com o usuário em uma única etapa.
    """
    print("--- Bem-vindo ao AURORA ---")
    print("Sistema de Registro de Atividades da Energisa")
    
    # 1. Obter a descrição completa em uma única entrada
    texto_completo = input("\nPor favor, descreva sua atividade, incluindo seu nome e a regional (ESE, EMR ou EMS):\n> ")

    if not texto_completo:
        print("\n❌ ERRO: A descrição não pode estar vazia.")
        return

    # 2. Chamar o Mistral para processar a informação
    dados_extraidos = call_mistral_api_simulada(texto_completo)

    # 3. Validar e registrar no banco de dados
    if dados_extraidos:
        # Pega todas as informações do dicionário retornado pela simulação
        colaborador_final = dados_extraidos["colaborador"]
        tarefa_final = dados_extraidos["tarefa"]
        regional_final = dados_extraidos["regional"]
        
        registrar_atividade_no_banco(colaborador_final, tarefa_final, regional_final)
    else:
        print("\nOperação cancelada. Não foi possível extrair todas as informações necessárias da sua descrição.")

# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    iniciar_aurora()
