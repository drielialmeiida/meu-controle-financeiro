import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Controle Financeiro Pessoal", layout="wide")

st.title("📊 Controle Financeiro Pessoal")

# Inicialização do estado da sessão (banco de dados temporário na memória)
if "saldo_conta" not in st.session_state:
    st.session_state.saldo_conta = 0.0
if "transacoes" not in st.session_state:
    st.session_state.transacoes = []

# Menu na barra lateral
opcao = st.sidebar.selectbox(
    "Navegação",
    ["Resumo do Mês", "Adicionar Receita", "Lançar Despesa", "Ver Histórico"]
)

# 1. RESUMO
if opcao == "Resumo do Mês":
    st.header("Painel Principal")
    st.metric(label="Saldo Atual em Conta", value=f"R$ {st.session_state.saldo_conta:.2f}")
    
    if st.session_state.transacoes:
        st.subheader("Últimas Movimentações")
        df = pd.DataFrame(st.session_state.transacoes)
        st.dataframe(df, use_container_width=True)

# 2. RECEITA
elif opcao == "Adicionar Receita":
    st.header("Adicionar Receita")
    with st.form("form_receita"):
        descricao = st.text_input("Descrição (ex: Salário)")
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        categoria = st.text_input("Categoria", value="Salário")
        submetido = st.form_submit_button("Salvar Receita")
        
        if submetido:
            st.session_state.saldo_conta += valor
            st.session_state.transacoes.append({
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Tipo": "Receita",
                "Descrição": descricao,
                "Valor (R$)": valor,
                "Categoria": categoria
            })
            st.success(f"Receita de R$ {valor:.2f} adicionada com sucesso!")

# 3. DESPESA
elif opcao == "Lançar Despesa":
    st.header("Lançar Despesa")
    with st.form("form_despesa"):
        descricao = st.text_input("Descrição (ex: Mercado)")
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        categoria = st.text_input("Categoria", value="Alimentação")
        submetido = st.form_submit_button("Salvar Despesa")
        
        if submetido:
            st.session_state.saldo_conta -= valor
            st.session_state.transacoes.append({
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Tipo": "Despesa",
                "Descrição": descricao,
                "Valor (R$)": valor,
                "Categoria": categoria
            })
            st.success(f"Despesa de R$ {valor:.2f} lançada com sucesso!")

# 4. HISTÓRICO
elif opcao == "Ver Histórico":
    st.header("Histórico Completo")
    if st.session_state.transacoes:
        df = pd.DataFrame(st.session_state.transacoes)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhuma transação registada ainda.")
