import sqlite3
import pandas as pd
import random
import difflib
from datetime import datetime
from pathlib import Path

class DataEngine:
    # Gerencia a persistencia de dados, regras de negocio e simulacao de roteamento cognitivo
    def __init__(self):
        # Utiliza o diretorio raiz do projeto como base absoluta para evitar subpastas
        self.root_path = Path.cwd()
        self.data_dir = self.root_path / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "Agentes.db"
        self._bootstrap_database()

    def _get_connection(self):
        # Retorna a conexao com o banco de dados relacional (SQLite local)
        return sqlite3.connect(str(self.db_path))

    def _bootstrap_database(self):
        # Inicializa a modelagem de tabelas e aplica a carga de dados default se necessario
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de dimensionamento (Catalogo de Especialistas)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    desenvolvedor TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    especialidade TEXT NOT NULL,
                    palavras_chave TEXT NOT NULL
                )
            ''')
            
            # Tabela de fatos (Transacoes e Logs de Roteamento)
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
            
            # Populacao inicial dinamica do ambiente
            cursor.execute("SELECT COUNT(*) FROM agentes")
            if cursor.fetchone()[0] == 0:
                agentes_default = [
                    ('Sistema Base', 'Agente Alpha', 'Processamento de Linguagem Natural', 'texto, linguagem, escrever, traduzir, documento, resumir, redigir, ler'),
                    ('Sistema Base', 'Agente Beta', 'Analise Preditiva e Modelagem de Dados', 'dados, prever, analise, modelo, estatistica, tendencia, sql, preditivo, demanda'),
                    ('Sistema Base', 'Agente Gamma', 'Auditoria de Seguranca Digital', 'seguranca, lgpd, auditoria, conformidade, acesso, vulnerabilidade, senha, protecao')
                ]
                cursor.executemany("INSERT INTO agentes (desenvolvedor, nome, especialidade, palavras_chave) VALUES (?, ?, ?, ?)", agentes_default)
            conn.commit()

    def registrar_agente(self, desenvolvedor, nome, especialidade, palavras_chave):
        # Persiste um novo perfil de especialista integrado pelo Portal do Desenvolvedor
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agentes (desenvolvedor, nome, especialidade, palavras_chave)
                VALUES (?, ?, ?, ?)
            ''', (desenvolvedor, nome, especialidade, palavras_chave))
            conn.commit()

    def obter_agentes(self):
        # Retorna o dataframe do catalogo ativo para popular as interfaces (Frontend)
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM agentes", conn)

    def registrar_requisicao(self, cliente, agente_id, descricao):
        # Extrai as regras de roteamento diretamente da base de dados
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT palavras_chave FROM agentes WHERE id = ?", (agente_id,))
            resultado = cursor.fetchone()
            
        if resultado:
            # Tratamento de string: divide por virgula e remove espacos/maiusculas
            palavras_db = [p.strip().lower() for p in resultado[0].split(',')]
        else:
            palavras_db = []
            
        # Normaliza o input do usuario para a validacao semantica
        texto_usuario = descricao.lower().split()
        forca_conexao = 0.0
        
        # Algoritmo de Similaridade Cognitiva (NLP Leve)
        for palavra_chave in palavras_db:
            
            # 1. Busca de Radical (Stemming): valida substrings comuns ("analisar" vs "analise")
            if any(palavra_chave in word or word in palavra_chave for word in texto_usuario):
                forca_conexao += 1.0
                continue
                
            # 2. Busca Fuzzy (Distancia de Levenshtein): tolerancia a erros de digitacao tipograficos
            similares = difflib.get_close_matches(palavra_chave, texto_usuario, n=1, cutoff=0.75)
            if similares:
                forca_conexao += 0.8  # Peso reduzido por ser uma inferencia probabilistica
        
        # Atribuicao do nivel de servico (SLA) via forca conectiva
        if forca_conexao == 0:
            final_score = random.uniform(10.0, 39.0)  # Roteamento incorreto (Falha Critica)
        elif forca_conexao < 1.5:
            final_score = random.uniform(60.0, 84.0)  # Roteamento aceitavel (Aderencia Parcial)
        else:
            final_score = random.uniform(85.0, 100.0) # Roteamento ideal (Alta Aderencia)
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Persistencia do log transacional da avaliacao
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO solicitacoes (agente_id, cliente_nome, descricao_task, score_desempenho, data_timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (agente_id, cliente, descricao, round(final_score, 2), timestamp))
            conn.commit()

    def obter_metrics_dash(self):
        # View analitica: JOIN entre transacoes e catalogo para injecao no Dashboard
        query = '''
            SELECT a.nome, a.especialidade, s.cliente_nome, s.descricao_task, s.score_desempenho, s.data_timestamp
            FROM solicitacoes s
            JOIN agentes a ON s.agente_id = a.id
            ORDER BY s.data_timestamp ASC
        '''
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def obter_solicitacoes_raw(self):
        # Extrai os dados brutos da tabela de fatos para auditoria no Modo Desenvolvedor
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM solicitacoes", conn)

    def limpar_historico(self):
        # Trunca a tabela de transacoes sem afetar a integridade do catalogo de agentes
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM solicitacoes")
            conn.commit()