# Squad de IA: Protótipo de Fluxo de Dados

Este repositório contém o protótipo (Proof of Concept) do fluxo de dados e orquestração de uma Squad de Agentes de IA. O objetivo é demonstrar a captura de solicitações, o roteamento para especialistas específicos e o monitoramento de eficiência operacional (SLA) em tempo real.

## Objetivo do Projeto
Validar a arquitetura de informação entre a **Camada de Cliente** (entrada de dados) e a **Camada de Execução** (catálogo de agentes de IA), eliminando o efeito "caixa preta" através de logs auditáveis e dashboards de performance. Projeto desenvolvido para o ecossistema de R&D do Brain (BIRD).

## Funcionalidades
* **Portal de Requisições:** Interface para clientes solicitarem tarefas de forma estruturada.
* **Catálogo Dinâmico:** Agentes especialistas (Alpha, Beta e Gamma) com funções isoladas.
* **Motor de Afinidade Textual:** Lógica Python que avalia a aderência do pedido à especialidade do agente, gerando um Score de Eficiência.
* **Dashboard Analítico:** Monitoramento de KPIs (Volume, SLA Médio, Saúde do Sistema) e histórico detalhado em tempo real.

## Arquitetura
A arquitetura foi desenhada com foco em separação de responsabilidades e fácil portabilidade futura para bancos em nuvem:
* **Frontend/Visualização:** Streamlit & Plotly
* **Regras de Negócio:** Python
* **Persistência de Dados:** SQLite (arquivo gerado automaticamente na primeira execução)

## Estrutura do Diretório
```text
SquadIA/
├── data/
│   └── Agentes.db           # Banco de dados (gerado automaticamente)
├── src/
│   ├── app.py               # Interface de usuário (Dashboard e Portal)
│   └── database.py          # Camada de persistência e cálculo de score
├── requirements.txt         # Dependências do projeto
├── .gitignore               # Regras de exclusão para o repositório
└── README.md                # Documentação do projeto
