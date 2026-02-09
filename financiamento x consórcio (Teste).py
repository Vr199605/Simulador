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

def tabela_price(valor, juros_anual, meses):
    if meses <= 0:
        return pd.DataFrame()

    i = juros_anual / 100 / 12

    # CASO JUROS ZERO (correção do erro)
    if i == 0:
        parcela = valor / meses
        saldo = valor
        dados = []
        for m in range(1, meses + 1):
            saldo -= parcela
            dados.append([m, parcela, parcela, 0.0, max(saldo, 0)])
        return pd.DataFrame(
            dados,
            columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"]
        )

    parcela = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        amort = parcela - juros
        saldo -= amort
        dados.append([m, parcela, amort, juros, max(saldo, 0)])

    return pd.DataFrame(
        dados,
        columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"]
    )


def tabela_sac(valor, juros_anual, meses):
    if meses <= 0:
        return pd.DataFrame()

    i = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        parcela = amort + juros
        saldo -= amort
        dados.append([m, parcela, amort, juros, max(saldo, 0)])

    return pd.DataFrame(
        dados,
        columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"]
    )


def calcular_consorcio(
    credito,
    prazo,
    taxa_adm,
    fundo_reserva,
    parcelas_pagas,
    lance_embutido_pct,
    lance_livre_pct,
    lance_fixo_pct,
    redutor_pct
):
    taxa_total_pct = taxa_adm + fundo_reserva
    categoria = credito * (1 + taxa_total_pct / 100)

    parcela = categoria / prazo

    # Redutor aplicado SOMENTE na fase pré
    parcela_pre = parcela * (1 - redutor_pct / 100)

    saldo = categoria - (parcelas_pagas * parcela_pre)
    saldo = max(saldo, 0)

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_livre = categoria * (lance_livre_pct / 100)
    lance_fixo = categoria * (lance_fixo_pct / 100)

    lance_total = lance_embutido + lance_livre + lance_fixo

    credito_liquido = credito - lance_embutido

    # gráfico saldo devedor
    saldos = []
    saldo_tmp = categoria
    for i in range(prazo):
        saldo_tmp -= parcela
        saldos.append(max(saldo_tmp, 0))

    df_saldo = pd.DataFrame({
        "Parcela": range(1, prazo + 1),
        "Saldo Devedor": saldos
    })

    return {
        "Categoria": categoria,
        "Parcela": parcela,
        "Parcela Pré": parcela_pre,
        "Saldo Atual": saldo,
        "Lance Total": lance_total,
        "Crédito Líquido": credito_liquido,
        "DataFrame": df_saldo
    }

# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin = st.tabs(["🤝 Consórcio", "🏦 Financiamento"])

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    st.header("Simulação de Consórcio – Modelo Avançado")

    c1, c2 = st.columns([1, 2])

    with c1:
        credito = st.number_input("Crédito contratado (R$)", 50000.0, 3000000.0, 300000.0)
        prazo = st.number_input("Prazo total (meses)", 60, 240, 180)

        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        parcelas_pagas = st.number_input(
            "Parcelas pagas pré-contemplação",
            0, prazo, 0
        )

        st.subheader("🎯 Lances")
        lance_embutido_pct = st.number_input("Lance Embutido (%)", 0.0, 100.0, 20.0)
        lance_livre_pct = st.number_input("Lance Livre (% da categoria)", 0.0, 100.0, 5.0)
        lance_fixo_pct = st.number_input("Lance Fixo (% da categoria)", 0.0, 100.0, 0.0)

        st.subheader("🔻 Redutor")
        redutor_pct = st.number_input(
            "Redutor sobre a parcela pré (%)",
            0.0, 50.0, 0.0
        )

    res = calcular_consorcio(
        credito,
        prazo,
        taxa_adm,
        fundo_reserva,
        parcelas_pagas,
        lance_embutido_pct,
        lance_livre_pct,
        lance_fixo_pct,
        redutor_pct
    )

    with c2:
        st.markdown(f"""
        ### 📊 Resumo Financeiro

        • **Categoria:** R$ {res['Categoria']:,.2f}  
        • **Parcela padrão:** R$ {res['Parcela']:,.2f}  
        • **Parcela pré (com redutor):** R$ {res['Parcela Pré']:,.2f}  
        • **Saldo atual:** R$ {res['Saldo Atual']:,.2f}  
        • **Lance total:** R$ {res['Lance Total']:,.2f}  
        • **Crédito líquido:** R$ {res['Crédito Líquido']:,.2f}
        """)

        st.subheader("📉 Gráfico de Saldo Devedor")
        st.line_chart(
            res["DataFrame"].set_index("Parcela")
        )

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    st.header("Simulação de Financiamento")

    valor_fin = st.number_input("Valor financiado (R$)", 10000.0, step=1000.0)
    juros_anual = st.number_input("Juros anual (%)", 0.0, 30.0, 12.0)
    prazo_fin = st.number_input("Prazo (meses)", 12, 420, 240)

    df_price = tabela_price(valor_fin, juros_anual, prazo_fin)
    df_sac = tabela_sac(valor_fin, juros_anual, prazo_fin)

    st.subheader("📉 Saldo Devedor")
    st.line_chart(
        pd.DataFrame({
            "PRICE": df_price["Saldo"].values,
            "SAC": df_sac["Saldo"].values
        })
    )

# =========================
# RODAPÉ
# =========================
st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking 2026</center>",
    unsafe_allow_html=True
)






