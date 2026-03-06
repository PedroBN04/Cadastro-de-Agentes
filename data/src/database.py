import sqlite3
import pandas as pd
import random
from datetime import datetime
from pathlib import Path

class DataEngine:
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent
        self.data_dir = self.base_path.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "Agentes.db"
        self._bootstrap_database()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def _bootstrap_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agentes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    especialidade TEXT NOT NULL
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
            
            cursor.execute("SELECT COUNT(*) FROM agentes")
            if cursor.fetchone()[0] == 0:
                agentes = [
                    (101, 'Agente Alpha', 'Processamento de Linguagem Natural e Traducao'),
                    (102, 'Agente Beta', 'Analise Preditiva e Modelagem de Dados'),
                    (103, 'Agente Gamma', 'Auditoria de Seguranca e Conformidade Digital')
                ]
                cursor.executemany("INSERT INTO agentes VALUES (?, ?, ?)", agentes)
            conn.commit()

    def obter_agentes(self):
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM agentes", conn)

    def registrar_requisicao(self, cliente, agente_id, descricao):
        # Vocabulario expandido para garantir acuracia no match
        keywords_map = {
            101: ['texto', 'linguagem', 'escrever', 'traduzir', 'documento', 'resumir', 'redigir', 'ler'],
            102: ['dados', 'prever', 'analise', 'modelo', 'estatistica', 'tendencia', 'sql', 'preditivo', 'demanda'],
            103: ['seguranca', 'lgpd', 'auditoria', 'conformidade', 'acesso', 'vulnerabilidade', 'senha', 'protecao']
        }
        
        texto_usuario = descricao.lower()
        matches = sum(1 for word in keywords_map.get(agente_id, []) if word in texto_usuario)
        
        # Nova logica de pontuacao justa
        if matches == 0:
            final_score = random.uniform(10.0, 35.0)  # Incompativel (Erro critico)
        elif matches == 1:
            final_score = random.uniform(75.0, 85.0)  # Compativel (Bom desempenho)
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
        query = '''
            SELECT a.nome, a.especialidade, s.cliente_nome, s.descricao_task, s.score_desempenho, s.data_timestamp
            FROM solicitacoes s
            JOIN agentes a ON s.agente_id = a.id
            ORDER BY s.data_timestamp ASC
        '''
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def limpar_historico(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM solicitacoes")
            conn.commit()