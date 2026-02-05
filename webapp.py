import streamlit as st
import pandas as pd
import sqlite3
import os

# Configuração da página
st.set_page_config(page_title="Meu Gerenciador Financeiro", layout="wide")

st.title("💰 Meu Gerenciador Financeiro Visual")

# Verificação se o arquivo do banco existe na pasta
if not os.path.exists("receitas_despesas.db"):
    st.error("❌ O arquivo 'receitas_despesas.db' não foi encontrado nesta pasta!")
else:
    # Conectamos ao banco
    conn = sqlite3.connect("receitas_despesas.db")

    # --- BARRA LATERAL ---
    st.sidebar.header("Menu de Navegação")
    aba = st.sidebar.radio("Escolha uma tela:", ["Resumo", "Transações", "Contas"])

    if aba == "Resumo":
        st.subheader("📊 Visão Geral")

        # Tenta carregar os dados
        try:
            query = """
                SELECT c.nome_categoria as Categoria, SUM(t.valor) as Total 
                FROM transacao t 
                JOIN categoria c ON t.id_categoria = c.id 
                GROUP BY c.nome_categoria
            """
            df_gastos = pd.read_sql(query, conn)

            if df_gastos.empty:
                st.warning("Ainda não existem transações para mostrar no gráfico.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### Gastos por Categoria")
                    st.bar_chart(df_gastos.set_index("Categoria"))
                with col2:
                    st.write("### Tabela de Valores")
                    st.dataframe(df_gastos)
        except Exception as e:
            st.error(f"Erro ao carregar resumo: {e}")

    elif aba == "Transações":
        st.subheader("📝 Histórico de Gastos")
        try:
            query_t = """
                SELECT t.id, t.data, t.descricao, t.valor, c.nome_categoria, co.nome_instituicao
                FROM transacao t
                JOIN categoria c ON t.id_categoria = c.id
                JOIN conta co ON t.id_conta = co.id
                ORDER BY t.data DESC
            """
            df_t = pd.read_sql(query_t, conn)
            st.dataframe(df_t, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar transações: {e}")

    conn.close()
