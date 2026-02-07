import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Finanças Flávia", page_icon="💰", layout="centered")

# CSS para deixar os cartões bonitos no celular
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
        # Garante que a coluna Data seja tratada corretamente
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=['Data', 'Descrição', 'Categoria', 'Valor'])

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

df = st.session_state.transactions

# --- TOPO: RESUMO POR COLUNAS ---
st.title("📊 Painel Financeiro")

# Cálculos específicos
salario_total = df[df['Categoria'] == 'Salário Flávia']['Valor'].sum()
uber_total = df[df['Categoria'] == 'Uber']['Valor'].sum()
outros_total = df[(df['Categoria'] != 'Salário Flávia') & (df['Categoria'] != 'Uber')]['Valor'].sum()
saldo_geral = df['Valor'].sum()

# Layout de Colunas (Top Cards)
c1, c2 = st.columns(2)
with c1:
    st.metric("Salário Flávia", f"R$ {salario_total:.2f}")
with c2:
    st.metric("Uber (Líquido)", f"R$ {uber_total:.2f}")

st.metric("Saldo Geral em Conta", f"R$ {saldo_geral:.2f}")

st.divider()

# --- LANÇAMENTO ---
with st.expander("➕ Novo Lançamento", expanded=False):
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
    tipo = st.radio("Tipo:", ["Entrada (Ganho)", "Saída (Gasto)"], horizontal=True)
    
    # Categorias atualizadas
    cat = st.selectbox("Categoria", ["Salário Flávia", "Uber", "Alimentação", "Casa", "Lazer", "Outros"])
    
    if st.button("Salvar", use_container_width=True):
        if desc and valor > 0:
            valor_final = valor if "Entrada" in tipo else -valor
            nova_linha = pd.DataFrame([{
                'Data': datetime.now().date(),
                'Descrição': desc,
                'Categoria': cat,
                'Valor': valor_final
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, nova_linha], ignore_index=True)
            st.session_state.transactions.to_csv(DB_FILE, index=False)
            st.success("Registrado!")
            st.rerun()

# --- LISTAGEM ---
st.subheader("📋 Últimas Movimentações")
if not df.empty:
    # Mostra os mais recentes no topo
    st.dataframe(
        df.sort_values(by='Data', ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhum dado registrado.")

