import streamlit as st
import pandas as pd
import plotly.express as px
import time
from database import DataEngine

st.set_page_config(page_title="Squad de IA - Fluxo", layout="wide", initial_sidebar_state="collapsed")
engine = DataEngine()

with st.sidebar:
    st.header("Opcoes de Desenvolvedor")
    if st.button("Limpar Banco de Dados (Reset)", type="primary"):
        engine.limpar_historico()
        st.success("Historico apagado com sucesso!")
        time.sleep(1)
        st.rerun()

st.title("Squad de IA: Prototipo de Fluxo de Dados")
st.markdown("---")

tab_cliente, tab_dashboard = st.tabs(["Portal de Requisicoes", "Dashboard de Performance"])

with tab_cliente:
    st.header("Area do Cliente")
    with st.container(border=True):
        col_f, col_i = st.columns(2)
        with col_f:
            cliente = st.text_input("Identificacao do Solicitante")
            df_agentes = engine.obter_agentes()
            agente_id = st.selectbox(
                "Selecionar Agente", 
                options=df_agentes['id'].tolist(),
                format_func=lambda x: df_agentes[df_agentes['id'] == x]['nome'].iloc[0]
            )
            esp = df_agentes[df_agentes['id'] == agente_id]['especialidade'].iloc[0]
            st.info(f"Funcao: {esp}")
        with col_i:
            desc = st.text_area("Descricao da Tarefa", height=155)
            if st.button("Executar Requisicao", type="primary", use_container_width=True):
                if cliente and desc:
                    engine.registrar_requisicao(cliente, agente_id, desc)
                    st.success("Requisicao registrada no Agentes.db")
                else:
                    st.error("Preencha todos os campos.")

with tab_dashboard:
    st.header("Monitoramento Analitico")
    df = engine.obter_metrics_dash()
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Ativacoes", len(df))
        c2.metric("SLA Medio da Squad", f"{df['score_desempenho'].mean():.2f}%")
        status = "Critico" if df['score_desempenho'].mean() < 60 else "Operacional"
        c3.metric("Saude do Sistema", status)

        st.divider()

        st.subheader("Eficiencia por Agente e Ativacao")
        
        # Grafico atualizado: Legenda por agente e exibicao de valores
        fig = px.bar(
            df, 
            x='data_timestamp', 
            y='score_desempenho', 
            color='nome', # Define as cores por especialista (Gera a legenda clara)
            hover_data=['cliente_nome', 'descricao_task'],
            labels={'score_desempenho': 'Eficiencia (%)', 'data_timestamp': 'Horario da Requisicao', 'nome': 'Especialista'},
            template="plotly_dark",
            text='score_desempenho' # Imprime a nota na propria barra
        )
        
        # Formata o numero impresso na barra e cria a linha de SLA
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="SLA Critico (< 60%)", annotation_position="bottom right")
        fig.update_layout(yaxis_range=[0, 115]) # Garante espaco para o texto fora da barra
        
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("Rastreamento de Log")
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
        st.info("O banco de dados esta limpo. Faca uma nova requisicao para gerar os graficos.")

time.sleep(5)
st.rerun()