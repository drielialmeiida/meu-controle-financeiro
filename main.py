import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Controle Financeiro Pessoal", layout="wide", page_icon="💰")

st.title("📊 Controle Financeiro Pessoal")

# Inicialização das variáveis de sessão
if "saldo_conta" not in st.session_state:
    st.session_state.saldo_conta = 0.0
if "transacoes" not in st.session_state:
    # Criamos um DataFrame pandas vazio para guardar e editar as transações
    st.session_state.transacoes = pd.DataFrame(columns=["ID", "Data", "Tipo", "Descrição", "Valor (R$)", "Categoria"])

# Recalcular saldo total com base na tabela
def recalcular_saldo():
    if not st.session_state.transacoes.empty:
        receitas = st.session_state.transacoes[st.session_state.transacoes["Tipo"] == "Receita"]["Valor (R$)"].sum()
        despesas = st.session_state.transacoes[st.session_state.transacoes["Tipo"] == "Despesa"]["Valor (R$)"].sum()
        st.session_state.saldo_conta = receitas - despesas
    else:
        st.session_state.saldo_conta = 0.0

recalcular_saldo()

# Cartões de Resumo no Topo
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Saldo em Conta", value=f"R$ {st.session_state.saldo_conta:.2f}")
with col2:
    tot_rec = st.session_state.transacoes[st.session_state.transacoes["Tipo"] == "Receita"]["Valor (R$)"].sum() if not st.session_state.transacoes.empty else 0.0
    st.metric(label="Total Receitas", value=f"R$ {tot_rec:.2f}")
with col3:
    tot_desp = st.session_state.transacoes[st.session_state.transacoes["Tipo"] == "Despesa"]["Valor (R$)"].sum() if not st.session_state.transacoes.empty else 0.0
    st.metric(label="Total Despesas", value=f"R$ {tot_desp:.2f}")

st.markdown("---")

# Criando abas para organização
aba_resumo, aba_novo, aba_editar = st.tabs(["📈 Painel / Editar Tabela", "➕ Lançar Receita/Despesa", "⚙️ Opções Avançadas"])

with aba_resumo:
    st.subheader("📋 Transações Registadas (Clique em qualquer célula para Editar)")
    
    if not st.session_state.transacoes.empty:
        # st.data_editor permite editar os valores diretamente na tabela!
        tabela_editada = st.data_editor(
            st.session_state.transacoes,
            num_rows="dynamic", # Permite eliminar ou adicionar linhas facilmente
            use_container_width=True,
            column_config={
                "Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Tipo": st.column_config.SelectboxColumn(options=["Receita", "Despesa"])
            },
            key="editor_transacoes"
        )
        
        # Atualiza os dados gravados se houver alterações na tabela
        if not tabela_editada.equals(st.session_state.transacoes):
            st.session_state.transacoes = tabela_editada
            recalcular_saldo()
            st.success("Alterações guardadas e saldo recalculado!")
            st.rerun()
    else:
        st.info("Nenhuma transação registada ainda.")

with aba_novo:
    st.subheader("Novo Lançamento")
    with st.form("form_transacao", clear_on_submit=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tipo = st.selectbox("Tipo de Lançamento", ["Receita", "Despesa"])
            descricao = st.text_input("Descrição (ex: Salário, Supermercado)")
        with col_t2:
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
            categoria = st.text_input("Categoria", value="Geral")
            
        submetido = st.form_submit_button("Guardar Lançamento")
        
        if submetido:
            novo_id = len(st.session_state.transacoes) + 1
            nova_linha = pd.DataFrame([{
                "ID": novo_id,
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Tipo": tipo,
                "Descrição": descricao,
                "Valor (R$)": valor,
                "Categoria": categoria
            }])
            
            st.session_state.transacoes = pd.concat([st.session_state.transacoes, nova_linha], ignore_index=True)
            recalcular_saldo()
            st.success(f"{tipo} de R$ {valor:.2f} adicionada com sucesso!")
            st.rerun()

with aba_editar:
    st.subheader("Gestão de Dados")
    if st.button("🔴 Apagar Todas as Transações"):
        st.session_state.transacoes = pd.DataFrame(columns=["ID", "Data", "Tipo", "Descrição", "Valor (R$)", "Categoria"])
        st.session_state.saldo_conta = 0.0
        st.success("Todos os dados foram eliminados.")
        st.rerun()
