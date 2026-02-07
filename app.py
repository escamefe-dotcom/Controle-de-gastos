import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Finanças Flávia", page_icon="💰", layout="wide")

# --- CONFIGURAÇÃO DE ARQUIVO ---
DB_FILE = "dados.csv"
COLUNAS = ['Data', 'Descrição', 'Categoria', 'Conta/Cartão', 'Valor']

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not all(c in df.columns for c in COLUNAS):
            return pd.DataFrame(columns=COLUNAS)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=COLUNAS)

# Inicialização
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

# --- INTERFACE ---
st.title("📊 Gestão Financeira")

# Resumo no Topo
df = st.session_state.transactions
saldo_total = df['Valor'].sum() if not df.empty else 0.0
st.metric("Saldo Geral", f"R$ {saldo_total:.2f}")

st.divider()

# --- ABAS: LANÇAR / GERENCIAR / ANALISAR ---
tab_novo, tab_gerenciar, tab_analise = st.tabs(["➕ Novo", "⚙️ Editar/Excluir", "📈 Gráficos"])

with tab_novo:
    with st.form("form_novo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            desc = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.0, step=0.01)
        with col2:
            tipo = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)
            cat = st.selectbox("Categoria", ["Salário Flávia", "Uber", "Alimentação", "Casa", "Lazer", "Outros"])
            origem = st.selectbox("Conta/Cartão", ["Bradesco", "Inter", "C6", "Dinheiro"])
        
        if st.form_submit_button("Salvar Registro", use_container_width=True):
            if desc and valor > 0:
                valor_f = -valor if tipo == "Saída" else valor
                nova_linha = pd.DataFrame([[datetime.now().date(), desc, cat, origem, valor_f]], columns=COLUNAS)
                st.session_state.transactions = pd.concat([st.session_state.transactions, nova_linha], ignore_index=True)
                st.session_state.transactions.to_csv(DB_FILE, index=False)
                st.success("Salvo!")
                st.rerun()

with tab_gerenciar:
    if df.empty:
        st.info("Nenhum lançamento para gerenciar.")
    else:
        st.write("Selecione uma linha para editar ou excluir:")
        
        # Adiciona um seletor para escolher qual linha manipular
        linha_index = st.selectbox("Escolha o registro (pelo ID)", df.index, format_func=lambda x: f"ID {x}: {df.loc[x, 'Descrição']} (R$ {df.loc[x, 'Valor']})")
        
        col_ed, col_ex = st.columns(2)
        
        with col_ex:
            if st.button("🗑️ EXCLUIR REGISTRO", use_container_width=True, type="primary"):
                st.session_state.transactions = df.drop(linha_index)
                st.session_state.transactions.to_csv(DB_FILE, index=False)
                st.success("Excluído com sucesso!")
                st.rerun()

        with col_ed:
            st.write("---")
            st.caption("Editar Campos:")
            nova_desc = st.text_input("Nova Descrição", value=df.loc[linha_index, 'Descrição'])
            novo_valor = st.number_input("Novo Valor", value=float(abs(df.loc[linha_index, 'Valor'])))
            
            if st.button("💾 SALVAR ALTERAÇÃO", use_container_width=True):
                # Mantém o sinal (positivo/negativo) original
                sinal = -1 if df.loc[linha_index, 'Valor'] < 0 else 1
                st.session_state.transactions.at[linha_index, 'Descrição'] = nova_desc
                st.session_state.transactions.at[linha_index, 'Valor'] = novo_valor * sinal
                st.session_state.transactions.to_csv(DB_FILE, index=False)
                st.success("Alterado!")
                st.rerun()

        st.divider()
        st.dataframe(df, use_container_width=True)

with tab_analise:
    if not df.empty:
        st.subheader("Gastos por Categoria")
        gastos = df[df['Valor'] < 0]
        if not gastos.empty:
            st.bar_chart(gastos.groupby('Categoria')['Valor'].sum().abs())
        else:
            st.write("Sem gastos para exibir gráficos.")
