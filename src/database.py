import sqlite3
import pandas as pd
import random
from datetime import datetime
from pathlib import Path

class DataEngine:
    # Gerencia a persistencia de dados e regras de negocio
    def __init__(self):
        # Utiliza o diretorio atual (raiz do projeto) como base
        self.root_path = Path.cwd()
        self.data_dir = self.root_path / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "Agentes.db"
        self._bootstrap_database()

    def _get_connection(self):
        # Retorna conexao com o banco SQLite local
        return sqlite3.connect(str(self.db_path))

    def _bootstrap_database(self):
        # Inicializa as tabelas do sistema e o catalogo de agentes se nao existirem
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela atualizada com desenvolvedor e palavras_chave
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    desenvolvedor TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    especialidade TEXT NOT NULL,
                    palavras_chave TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solicitacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agente_id INTEGER,
                    cliente_nome TEXT,
                    descricao_task TEXT,
                    score_desempenho REAL,
                    data_timestamp DATETIME,
                    FOREIGN KEY (agente_id) REFERENCES agentes(id)
                )
            ''')
            
            # Carga inicial dinamica caso o banco esteja vazio
            cursor.execute("SELECT COUNT(*) FROM agentes")
            if cursor.fetchone()[0] == 0:
                agentes_default = [
                    ('Sistema BIRD', 'Agente Alpha', 'Processamento de Linguagem Natural e Traducao', 'texto, linguagem, escrever, traduzir, documento, resumir, redigir, ler'),
                    ('Sistema BIRD', 'Agente Beta', 'Analise Preditiva e Modelagem de Dados', 'dados, prever, analise, modelo, estatistica, tendencia, sql, preditivo, demanda'),
                    ('Sistema BIRD', 'Agente Gamma', 'Auditoria de Seguranca e Conformidade Digital', 'seguranca, lgpd, auditoria, conformidade, acesso, vulnerabilidade, senha, protecao')
                ]
                cursor.executemany("INSERT INTO agentes (desenvolvedor, nome, especialidade, palavras_chave) VALUES (?, ?, ?, ?)", agentes_default)
            conn.commit()

    def registrar_agente(self, desenvolvedor, nome, especialidade, palavras_chave):
        # Insere um novo agente no catalogo dinamico
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agentes (desenvolvedor, nome, especialidade, palavras_chave)
                VALUES (?, ?, ?, ?)
            ''', (desenvolvedor, nome, especialidade, palavras_chave))
            conn.commit()

    def obter_agentes(self):
        # Recupera a lista de agentes cadastrados no catalogo
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM agentes", conn)

    def registrar_requisicao(self, cliente, agente_id, descricao):
        # Busca as palavras-chave do agente especifico direto no banco de dados
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT palavras_chave FROM agentes WHERE id = ?", (agente_id,))
            resultado = cursor.fetchone()
            
        if resultado:
            # Transforma a string do banco (separada por virgula) em uma lista limpa
            palavras_db = [p.strip().lower() for p in resultado[0].split(',')]
        else:
            palavras_db = []
            
        texto_usuario = descricao.lower()
        
        # Cruza as palavras do banco com o texto do usuario
        matches = sum(1 for word in palavras_db if word in texto_usuario)
        
        # Logica de pontuacao baseada na aderencia estrutural do prompt
        if matches == 0:
            final_score = random.uniform(10.0, 35.0)  # Incompativel (Erro critico de roteamento)
        elif matches == 1:
            final_score = random.uniform(75.0, 85.0)  # Compativel parcial (Desempenho aceitavel)
        else:
            final_score = random.uniform(86.0, 100.0) # Alta compatibilidade (Desempenho otimo)
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO solicitacoes (agente_id, cliente_nome, descricao_task, score_desempenho, data_timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (agente_id, cliente, descricao, round(final_score, 2), timestamp))
            conn.commit()

    def obter_metrics_dash(self):
        # Extrai logs formatados unindo as tabelas para visualizacao no dashboard
        query = '''
            SELECT a.nome, a.especialidade, s.cliente_nome, s.descricao_task, s.score_desempenho, s.data_timestamp
            FROM solicitacoes s
            JOIN agentes a ON s.agente_id = a.id
            ORDER BY s.data_timestamp ASC
        '''
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def obter_solicitacoes_raw(self):
        # Retorna a tabela bruta de solicitacoes para auditoria do desenvolvedor
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM solicitacoes", conn)

    def limpar_historico(self):
        # Exclui os dados transacionais mantendo o catalogo de agentes
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM solicitacoes")
            conn.commit()