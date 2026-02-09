import streamlit as st
import pandas as pd
import numpy as np

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Intelligence Banking Pro",
    page_icon="💎",
    layout="wide"
)

# =========================
# FUNÇÕES
# =========================

def calcular_consorcio(
    credito, prazo, taxa_adm, fundo_reserva, meses_contemplacao,
    lance_embutido_pct, lance_livre_pct, lance_fixo_pct,
    redutor_pct, administradora, grupo
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    categoria = credito * (1 + taxa_total)

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor_pct / 100)
    parcela_pos = parcela_base

    saldo_atual = max(categoria - meses_contemplacao * parcela_pre, 0)

    # 🎯 BASE DE CÁLCULO DOS LANCES
    if administradora == "CNP":
        if grupo in ["1021", "1053"]:
            base_fixo = categoria
            base_livre = credito
        else:
            base_fixo = credito
            base_livre = credito
    elif administradora == "Porto":
        base_fixo = categoria
        base_livre = categoria
    else:  # Itaú
        base_fixo = credito
        base_livre = credito

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_fixo = base_fixo * (lance_fixo_pct / 100)
    lance_livre = base_livre * (lance_livre_pct / 100)

    lance_total = lance_embutido + lance_fixo + lance_livre
    credito_liquido = credito - lance_embutido

    prob_cont = min((lance_total / credito) * 100, 100)

    return {
        "Categoria": categoria,
        "Parcela Pré": parcela_pre,
        "Parcela Pós": parcela_pos,
        "Saldo Atual": saldo_atual,
        "Lance Total": lance_total,
        "Crédito Líquido": credito_liquido,
        "Probabilidade": prob_cont
    }


def tabela_price(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    if i == 0:
        prest = valor / meses
        saldo = valor
        dados = []
        for m in range(1, meses + 1):
            saldo -= prest
            dados.append([m, prest, 0, prest, max(saldo, 0)])
        return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])

    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        amort = pmt - juros
        saldo -= amort
        dados.append([m, pmt, juros, amort, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])


def tabela_sac(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        prest = amort + juros
        saldo -= amort
        dados.append([m, prest, juros, amort, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])


# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_comp, tab_did, tab_apres = st.tabs(
    ["🤝 Consórcio", "🏦 Financiamento", "📊 Comparativo", "📘 Didática", "🧾 Apresentação"]
)

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    c1, c2 = st.columns(2)

    with c1:
        credito = st.number_input("Crédito (R$)", 50000.0, 3000000.0, 300000.0)

        prazo = st.number_input(
            "Prazo (meses)",
            min_value=1,
            step=1,
            value=180
        )

        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        meses_contemplacao = st.number_input(
            "Meses até a contemplação",
            min_value=0,
            max_value=prazo,
            step=1,
            value=0
        )

        redutor_pct = st.number_input("Redutor (%)", 0.0, 50.0, 0.0)

        administradora = st.selectbox("Administradora", ["CNP", "Itaú", "Porto"])

        grupo = "Demais Grupos"
        if administradora == "CNP":
            grupo = st.selectbox("Grupo", ["1021", "1053", "Demais Grupos"])

        lance_embutido_pct = st.number_input("Lance embutido (%)", 0.0, 100.0, 20.0)
        lance_fixo_pct = st.number_input("Lance fixo (%)", 0.0, 100.0, 0.0)
        lance_livre_pct = st.number_input("Lance livre (%)", 0.0, 100.0, 5.0)

    res_cons = calcular_consorcio(
        credito, prazo, taxa_adm, fundo_reserva, meses_contemplacao,
        lance_embutido_pct, lance_livre_pct, lance_fixo_pct,
        redutor_pct, administradora, grupo
    )

    with c2:
        st.metric("Categoria", f"R$ {res_cons['Categoria']:,.2f}")
        st.metric("Parcela Pré", f"R$ {res_cons['Parcela Pré']:,.2f}")
        st.metric("Parcela Pós", f"R$ {res_cons['Parcela Pós']:,.2f}")
        st.metric("Saldo Atual", f"R$ {res_cons['Saldo Atual']:,.2f}")
        st.metric("Lance Total", f"R$ {res_cons['Lance Total']:,.2f}")
        st.metric("Probabilidade de Contemplação", f"{res_cons['Probabilidade']:.1f}%")


# =========================
# RODAPÉ
# =========================
st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking 2026</center>",
    unsafe_allow_html=True
)



































