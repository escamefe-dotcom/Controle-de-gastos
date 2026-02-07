import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Minhas Finanças", page_icon="💳", layout="centered")

# CSS Personalizado para melhorar o visual no celular
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] {
        border-radius: 15px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: white;
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
    return pd.DataFrame(columns=['Data', 'Descrição', 'Categoria', 'Valor'])

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

# --- TOPO DO APP ---
st.title("💳 Meu Controle")
st.caption("Organize seus gastos de forma simples")

# --- RESUMO FINANCEIRO (LAYOUT EM COLUNAS) ---
df = st.session_state.transactions
receitas = df[df['Valor'] > 0]['Valor'].sum()
despesas = df[df['Valor'] < 0]['Valor'].sum()
saldo = receitas + despesas

col1, col2 = st.columns(2)
with col1:
    st.metric("Saldo Atual", f"R$ {saldo:.2f}")
with col2:
    cor_saldo = "normal" if saldo >= 0 else "inverse"
    st.metric("Despesas", f"R$ {abs(despesas):.2f}", delta_color=cor_saldo)

st.divider()

# --- ÁREA DE LANÇAMENTO (EXPANDER PARA ECONOMIZAR ESPAÇO) ---
with st.expander("➕ Novo Lançamento", expanded=False):
    desc = st.text_input("O que você comprou?")
    valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0, format="%.2f")
    tipo = st.radio("Tipo:", ["Gasto 🔴", "Ganho 🟢"], horizontal=True)
    cat = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Casa", "Saúde", "Outros"])
    
    if st.button("Salvar Registro", use_container_width=True):
        if desc and valor > 0:
            valor_final = -valor if "Gasto" in tipo else valor
            nova_linha = pd.DataFrame([{
                'Data': datetime.now().date(),
                'Descrição': desc,
                'Categoria': cat,
                'Valor': valor_final
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, nova_linha], ignore_index=True)
            st.session_state.transactions.to_csv(DB_FILE, index=False)
            st.success("Salvo com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha a descrição e o valor.")

# --- VISUALIZAÇÃO ---
tab1, tab2 = st.tabs(["📋 Histórico", "📊 Análise"])

with tab1:
    if df.empty:
        st.info("Nenhuma transação registrada ainda.")
    else:
        # Exibe as transações mais recentes primeiro
        st.dataframe(
            df.sort_values(by='Data', ascending=False), 
            use_container_width=True,
            hide_index=True
        )

with tab2:
    if not df[df['Valor'] < 0].empty:
        st.subheader("Gastos por Categoria")
        gastos_cat = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        st.pie_chart(gastos_cat)
    else:
        st.write("Sem dados para gerar gráficos.")
