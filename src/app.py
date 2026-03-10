import streamlit as st
import pandas as pd
import plotly.express as px
import time
from database import DataEngine

# Configuracoes da pagina
st.set_page_config(page_title="Squad de IA - Fluxo", layout="wide", initial_sidebar_state="collapsed")
engine = DataEngine()

# Barra lateral de opcoes para desenvolvedores/administradores
with st.sidebar:
    st.header("Opcoes de Sistema")
    
    mostrar_banco = st.toggle("Inspecionar Banco (Raw Data)")
    st.divider()
    
    if st.button("Limpar Banco de Dados (Reset)", type="primary"):
        engine.limpar_historico()
        st.success("Historico apagado com sucesso.")
        time.sleep(1)
        st.rerun()

# Cabecalho principal
st.title("Squad de IA: Prototipo de Fluxo de Dados")
st.markdown("---")

# Divisao em abas para separacao de contexto
tab_cliente, tab_dev, tab_dashboard = st.tabs([
    "Portal de Requisicoes", 
    "Portal do Desenvolvedor", 
    "Dashboard de Performance"
])

# Interface de Entrada de Dados (Quadro Verde)
with tab_cliente:
    st.header("Area do Cliente")
    with st.container(border=True):
        col_form, col_context = st.columns(2)
        
        with col_form:
            cliente = st.text_input("Identificacao do Solicitante")
            df_agentes = engine.obter_agentes()
            agente_id = st.selectbox(
                "Selecionar Agente", 
                options=df_agentes['id'].tolist(),
                format_func=lambda x: df_agentes[df_agentes['id'] == x]['nome'].iloc[0]
            )
            especialidade = df_agentes[df_agentes['id'] == agente_id]['especialidade'].iloc[0]
            st.info(f"Funcao do Agente: {especialidade}")
            
        with col_context:
            desc = st.text_area("Descricao da Tarefa", height=155)
            if st.button("Executar Requisicao", type="primary", use_container_width=True):
                if cliente and desc:
                    engine.registrar_requisicao(cliente, agente_id, desc)
                    st.success("Requisicao registrada e estruturada no banco de dados.")
                else:
                    st.error("Preencha todos os campos obrigatorios.")

# Interface de Gerenciamento de Catalogo (Novo Recurso)
with tab_dev:
    st.header("Cadastro de Novos Agentes")
    with st.container(border=True):
        col_dev1, col_dev2 = st.columns(2)
        
        with col_dev1:
            nome_dev = st.text_input("Nome do Desenvolvedor / Equipe")
            nome_agente = st.text_input("Nome do Agente (Ex: Agente Delta)")
            
        with col_dev2:
            funcao_agente = st.text_input("Funcao ou Especialidade")
            palavras_chave = st.text_area("Palavras-chave (separadas por virgula)", height=68, help="Essas palavras serao usadas pelo motor para calcular a aderencia do prompt.")
            
        if st.button("Registrar Novo Agente", type="primary"):
            if nome_dev and nome_agente and funcao_agente and palavras_chave:
                engine.registrar_agente(nome_dev, nome_agente, funcao_agente, palavras_chave)
                st.success(f"{nome_agente} registrado com sucesso. Atualizando catalogo...")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Preencha todos os dados para registrar o agente.")

# Interface de Saida e Analise
with tab_dashboard:
    st.header("Monitoramento Analitico")
    df = engine.obter_metrics_dash()
    
    if not df.empty:
        # Metricas consolidadas
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Ativacoes", len(df))
        c2.metric("SLA Medio da Squad", f"{df['score_desempenho'].mean():.2f}%")
        status = "Critico" if df['score_desempenho'].mean() < 60 else "Operacional"
        c3.metric("Saude do Sistema", status)

        st.divider()

        # Visualizacao grafica de desempenho
        st.subheader("Eficiencia por Agente e Ativacao")
        fig = px.bar(
            df, 
            x='data_timestamp', 
            y='score_desempenho', 
            color='nome',
            hover_data=['cliente_nome', 'descricao_task'],
            labels={'score_desempenho': 'Eficiencia (%)', 'data_timestamp': 'Horario', 'nome': 'Especialista'},
            template="plotly_dark",
            text='score_desempenho'
        )
        
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="SLA Critico (< 60%)", annotation_position="bottom right")
        fig.update_layout(yaxis_range=[0, 115])
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Tabela formatada de historico
        st.subheader("Rastreamento de Log Tratado")
        st.dataframe(
            df,
            column_config={
                "data_timestamp": "Horario",
                "nome": "Especialista",
                "score_desempenho": st.column_config.ProgressColumn("Eficiencia", min_value=0, max_value=100, format="%.2f%%")
            },
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Aguardando novas requisicoes para processar o dashboard.")

# Inspecao estrutural do banco de dados (Visao Desenvolvedor)
if mostrar_banco:
    st.markdown("---")
    st.header("Inspecao do Banco de Dados (Raw Data)")
    st.caption("Visao das tabelas fisicas armazenadas no SQLite para auditoria.")
    
    st.subheader("Tabela: agentes")
    st.dataframe(engine.obter_agentes(), use_container_width=True)
        
    st.subheader("Tabela: solicitacoes")
    st.dataframe(engine.obter_solicitacoes_raw(), use_container_width=True)

# Polling automatico ativado apenas se a visualizacao de inspecao estiver desativada
if not mostrar_banco:
    time.sleep(5)
    st.rerun()