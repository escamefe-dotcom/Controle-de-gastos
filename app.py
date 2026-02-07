import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Finanças Flávia", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DADOS ---
DB_FILE = "dados.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=['Data', 'Descrição', 'Categoria', 'Conta/Cartão', 'Valor'])

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

df = st.session_state.transactions

# --- TOPO: RESUMO GERAL ---
st.title("📊 Painel Financeiro")

# Cálculos de Saldo
saldo_geral = df['Valor'].sum()
st.metric("Saldo Geral em Conta", f"R$ {saldo_geral:.2f}")

# Resumo por Cartão (apenas gastos/saídas)
st.write("---")
st.subheader("💳 Gastos por Cartão")
c1, c2, c3 = st.columns(3)

def get_gasto_cartao(nome_cartao):
    return abs(df[(df['Conta/Cartão'] == nome_cartao) & (df['Valor'] < 0)]['Valor'].sum())

c1.metric("Bradesco", f"R$ {get_gasto_cartao('Bradesco'):.2f}")
c2.metric("Inter", f"R$ {get_gasto_cartao('Inter'):.2f}")
c3.metric("C6 Bank", f"R$ {get_gasto_cartao('C6'):.2f}")

st.divider()

# --- NOVO LANÇAMENTO ---
with st.expander("➕ Novo Lançamento", expanded=False):
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
    tipo = st.radio("Tipo:", ["Saída (Gasto) 🔴", "Entrada (Ganho) 🟢"], horizontal=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        cat = st.selectbox("Categoria", ["Uber", "Salário Flávia", "Alimentação", "Casa", "Lazer", "Outros"])
    with col_b:
        # AQUÍ ESTÃO OS TEUS CARTÕES
        origem = st.selectbox("Conta/Cartão", ["Bradesco", "Inter", "C6", "Dinheiro/Outro"])
    
    if st.button("Salvar Registro", use_container_width=True):
        if desc and valor > 0:
            valor_final = -valor if "Saída" in tipo else valor
            nova_linha = pd.DataFrame([{
                'Data': datetime.now().date(),
                'Descrição': desc,
                'Categoria': cat,
                'Conta/Cartão': origem,
                'Valor': valor_final
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, nova_linha], ignore_index=True)
            st.session_state.transactions.to_csv(DB_FILE, index=False)
            st.success("Registado com sucesso!")
            st.rerun()

# --- LISTAGEM ---
st.subheader("📋 Histórico Recente")
if not df.empty:
    st.dataframe(
        df.sort_values(by='Data', ascending=False),
        use_container_width=True,
        hide_index=True
    )

