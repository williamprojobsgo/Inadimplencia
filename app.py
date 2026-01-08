import pandas as pd
import streamlit as st
import plotly.express as px
import math

# ===========================
# CONFIGURAÇÃO
# ===========================
st.set_page_config(
    page_title="Inadimplência",
    page_icon="📊",
    layout="wide"
)

# ===========================
# CARREGAR DADOS
# ===========================
@st.cache_data
def carregar_dados():
    df = pd.read_excel("geral_com_vendedor_numero.xlsx")

    df["Venc."] = pd.to_datetime(df["Venc."], dayfirst=True, errors="coerce")

    df["Saldo(R$)"] = (
        df["Saldo(R$)"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df["Vendedor"] = df["Vendedor"].astype(str)
    return df

df = carregar_dados()

# ===========================
# SIDEBAR (FILTROS)
# ===========================
st.sidebar.title("🎯 Filtros")

vendedor = st.sidebar.selectbox(
    "Vendedor",
    options=["Todos"] + sorted(df["Vendedor"].dropna().unique().tolist())
)

periodo = st.sidebar.date_input(
    "Período de vencimento",
    []
)

# ===========================
# FILTRAR DADOS
# ===========================
dados = df.copy()

if vendedor != "Todos":
    dados = dados[dados["Vendedor"] == vendedor]

if len(periodo) == 2:
    dados = dados[
        (dados["Venc."] >= pd.to_datetime(periodo[0])) &
        (dados["Venc."] <= pd.to_datetime(periodo[1]))
    ]

# ===========================
# TÍTULO
# ===========================
st.title("📊 Dashboard de Inadimplência")

# ===========================
# KPIs
# ===========================
col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Total em Aberto",
    f"R$ {dados['Saldo(R$)'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

col2.metric(
    "📄 Títulos em Aberto",
    len(dados)
)

col3.metric(
    "👥 Clientes Inadimplentes",
    dados["Cliente"].nunique()
)

st.divider()

# ===========================
# ABAS
# ===========================
aba1, aba2, aba3 = st.tabs(["📈 Visão Geral", "🕒 Clientes", "🏆 Vendedores"])

# ===========================
# VISÃO GERAL
# ===========================
with aba1:
    graf_df = (
        dados
        .dropna(subset=["Venc."])
        .groupby(dados["Venc."].dt.to_period("M"))["Saldo(R$)"]
        .sum()
        .reset_index()
    )

    graf_df["Venc."] = graf_df["Venc."].astype(str)

    fig = px.line(
        graf_df,
        x="Venc.",
        y="Saldo(R$)",
        markers=True,
        title="Evolução da Inadimplência"
    )

    st.plotly_chart(fig, use_container_width=True)

# ===========================
# CLIENTES
# ===========================
with aba2:
    st.subheader("Clientes Mais Recentes")

    dados_recentes = dados.sort_values("Venc.", ascending=False)

    por_pagina = 10
    total_paginas = math.ceil(len(dados_recentes) / por_pagina)

    pagina = st.number_input(
        "Página",
        min_value=1,
        max_value=max(1, total_paginas),
        step=1
    )

    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina

    st.dataframe(
        dados_recentes.iloc[inicio:fim][["Cliente", "Saldo(R$)", "Venc."]],
        use_container_width=True
    )

    st.divider()

    # ===========================
    # TOP CLIENTES INADIMPLENTES
    # ===========================
    st.subheader("🚨 Clientes com Maior Inadimplência")

    top_clientes = (
        dados
        .groupby("Cliente", as_index=False)["Saldo(R$)"]
        .sum()
        .sort_values("Saldo(R$)", ascending=False)
        .head(10)
    )

    col1, col2 = st.columns([2, 3])

    with col1:
        st.dataframe(top_clientes, use_container_width=True)

    with col2:
        fig_clientes = px.bar(
            top_clientes,
            x="Saldo(R$)",
            y="Cliente",
            orientation="h",
            title="Top 10 Clientes Inadimplentes",
            text_auto=True
        )
        st.plotly_chart(fig_clientes, use_container_width=True)
# ===========================
# VENDEDORES
# ===========================
with aba3:
    ranking = (
        dados
        .groupby("Vendedor", as_index=False)["Saldo(R$)"]
        .sum()
        .sort_values("Saldo(R$)", ascending=False)
    )

    fig_bar = px.bar(
        ranking,
        x="Vendedor",
        y="Saldo(R$)",
        title="Ranking de Inadimplência por Vendedor",
        text_auto=True
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.dataframe(ranking, use_container_width=True)

# ===========================
# RODAPÉ
# ===========================
st.caption("📌 Dashboard desenvolvido por William")

