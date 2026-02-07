import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Finanças Flávia", page_icon="💰")

# --- LÓGICA DE DADOS ---
DB_FILE = "dados.csv"
COLunas = ['Data', 'Descrição', 'Categoria', 'Conta/Cartão', 'Valor']

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Verifica se todas as colunas existem, se não, reconstrói o arquivo
        if not all(c in df.columns for c in COLunas):
            return pd.DataFrame(columns=COLunas)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=COLunas)

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

df = st.session_state.transactions

# --- INTERFACE ---
st.title("📊 Painel Financeiro")

# Cálculo seguro para não dar erro de coluna inexistente
def get_gasto_cartao(nome_cartao):
    if df.empty or 'Conta/Cartão' not in df.columns:
        return 0.0
    return abs(df[(df['Conta/Cartão'] == nome_cartao) & (df['Valor'] < 0)]['Valor'].sum())

# Saldo Geral
saldo_geral = df['Valor'].sum() if not df.empty else 0.0
st.metric("Saldo Geral", f"R$ {saldo_geral:.2f}")

st.subheader("💳 Gastos por Cartão")
c1, c2, c3 = st.columns(3)
c1.metric("Bradesco", f"R$ {get_gasto_cartao('Bradesco'):.2f}")
c2.metric("Inter", f"R$ {get_gasto_cartao('Inter'):.2f}")
c3.metric("C6", f"R$ {get_gasto_cartao('C6'):.2f}")

st.divider()

# --- FORMULÁRIO ---
with st.expander("➕ Novo Lançamento"):
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)
    tipo = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)
    cat = st.selectbox("Categoria", ["Salário Flávia", "Uber", "Alimentação", "Casa", "Lazer", "Outros"])
    origem = st.selectbox("Conta/Cartão", ["Bradesco", "Inter", "C6", "Dinheiro"])
    
    if st.button("Salvar"):
        valor_f = -valor if tipo == "Saída" else valor
        nova_linha = pd.DataFrame([[datetime.now().date(), desc, cat, origem, valor_f]], columns=COLunas)
        st.session_state.transactions = pd.concat([st.session_state.transactions, nova_linha], ignore_index=True)
        st.session_state.transactions.to_csv(DB_FILE, index=False)
        st.success("Salvo!")
        st.rerun()

st.subheader("📋 Histórico")
st.dataframe(df, use_container_width=True, hide_index=True)

