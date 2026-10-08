import streamlit as st
import pandas as pd
import database
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Controle Financeiro VIP", layout="wide", page_icon="💰")

# Inicializa as tabelas do banco de dados SQLite
database.criar_tabelas()

# Garantir que a tabela de transações existe na base de dados
def criar_tabela_transacoes():
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

criar_tabela_transacoes()

# Função para carregar transações do SQLite
def carregar_transacoes():
    conn = database.conectar()
    df = pd.read_sql_query("SELECT id AS ID, data AS Data, tipo AS Tipo, descricao AS Descrição, valor AS 'Valor (R$)', categoria AS Categoria FROM transacoes ORDER BY id DESC", conn)
    conn.close()
    return df

st.title("📊 Controle Financeiro Pessoal (Com SQLite)")

# Carrega os dados atuais do banco
df_transacoes = carregar_transacoes()

# Cálculos para os Cartões no Topo
if not df_transacoes.empty:
    receitas = df_transacoes[df_transacoes["Tipo"] == "Receita"]["Valor (R$)"].sum()
    despesas = df_transacoes[df_transacoes["Tipo"] == "Despesa"]["Valor (R$)"].sum()
    saldo_atual = receitas - despesas
else:
    receitas = 0.0
    despesas = 0.0
    saldo_atual = 0.0

# Cartões de Resumo no Topo
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Saldo em Conta", value=f"R$ {saldo_atual:.2f}")
with col2:
    st.metric(label="Total Receitas", value=f"R$ {receitas:.2f}")
with col3:
    st.metric(label="Total Despesas", value=f"R$ {despesas:.2f}")

st.markdown("---")

# Abas de Navegação
aba_resumo, aba_novo, aba_categorias, aba_config = st.tabs([
    "📈 Painel / Editar Tabela", 
    "➕ Lançar Receita/Despesa", 
    "🏷️ Categorias", 
    "⚙️ Opções Avançadas"
])

# 1. ABA PAINEL / EDITAR TABELA
with aba_resumo:
    st.subheader("📋 Transações Gravadas na Base de Dados")
    
    if not df_transacoes.empty:
        # Tabela interativa para editar dados direto na tela
        tabela_editada = st.data_editor(
            df_transacoes,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Tipo": st.column_config.SelectboxColumn(options=["Receita", "Despesa"])
            },
            key="editor_transacoes"
        )
        
        # Se alterares algo na tabela, atualiza a base de dados
        if not tabela_editada.equals(df_transacoes):
            conn = database.conectar()
            cursor = conn.cursor()
            # Limpa e regrava atualizado para manter sincronizado com o SQLite
            cursor.execute("DELETE FROM transacoes;")
            for _, row in tabela_editada.iterrows():
                if pd.notna(row["Descrição"]) and row["Descrição"] != "":
                    cursor.execute("""
                        INSERT INTO transacoes (data, tipo, descricao, valor, categoria)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(row["Data"]), str(row["Tipo"]), str(row["Descrição"]), float(row["Valor (R$)"]), str(row["Categoria"])))
            conn.commit()
            conn.close()
            st.success("Base de dados atualizada com sucesso!")
            st.rerun()
    else:
        st.info("Nenhuma transação registada na base de dados ainda.")

# 2. ABA NOVO LANÇAMENTO
with aba_novo:
    st.subheader("Novo Lançamento")
    
    # Busca categorias do SQLite para o menu de opções
    conn = database.conectar()
    categorias_db = pd.read_sql_query("SELECT nome FROM categorias ORDER BY nome", conn)["nome"].tolist()
    conn.close()
    
    if not categorias_db:
        categorias_db = ["Geral", "Salário", "Alimentação", "Mercado"]

    with st.form("form_transacao", clear_on_submit=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tipo = st.selectbox("Tipo de Lançamento", ["Receita", "Despesa"])
            descricao = st.text_input("Descrição (ex: Salário, Supermercado)")
        with col_t2:
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
            categoria = st.selectbox("Categoria", categorias_db)
            
        submetido = st.form_submit_button("Guardar no Banco de Dados")
        
        if submetido:
            if descricao.strip() != "":
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                conn = database.conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO transacoes (data, tipo, descricao, valor, categoria)
                    VALUES (?, ?, ?, ?, ?)
                """, (data_hoje, tipo, descricao.strip(), valor, categoria))
                conn.commit()
                conn.close()
                st.success(f"{tipo} de R$ {valor:.2f} gravada com sucesso no SQLite!")
                st.rerun()
            else:
                st.warning("Preencha a descrição do lançamento.")

# 3. ABA CATEGORIAS
with aba_categorias:
    st.subheader("⚙️ Gerenciar Categorias")
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        with st.form("form_nova_cat", clear_on_submit=True):
            nome_cat = st.text_input("Nome da Nova Categoria")
            tipo_cat = st.selectbox("Tipo", ["Receita", "Despesa"])
            btn_cat = st.form_submit_button("Criar Categoria")
            
            if btn_cat and nome_cat.strip() != "":
                try:
                    conn = database.conectar()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", (nome_cat.strip(), tipo_cat))
                    conn.commit()
                    conn.close()
                    st.success(f"Categoria '{nome_cat}' criada!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Esta categoria já existe.")

    with col_c2:
        conn = database.conectar()
        df_cat = pd.read_sql_query("SELECT id AS ID, nome AS Categoria, tipo AS Tipo FROM categorias ORDER BY tipo, nome", conn)
        conn.close()
        st.dataframe(df_cat, use_container_width=True)

# 4. ABA OPÇÕES AVANÇADAS
with aba_config:
    st.subheader("Gestão de Dados")
    if st.button("🔴 Apagar Todas as Transações do Banco de Dados"):
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes;")
        conn.commit()
        conn.close()
        st.success("Todas as transações foram apagadas do SQLite.")
        st.rerun()
