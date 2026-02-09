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
    credito, prazo, taxa_adm, fundo_reserva, parcelas_pagas,
    lance_embutido_pct, lance_livre_pct, lance_fixo_pct,
    redutor_pct, administradora, grupo
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    categoria = credito * (1 + taxa_total)

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor_pct / 100)
    parcela_pos = parcela_base

    saldo_atual = max(categoria - parcelas_pagas * parcela_pre, 0)

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

    elif administradora == "Itaú":
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
        prazo = st.number_input("Prazo (meses)", 60, 240, 180)

        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        parcelas_pagas = st.number_input("Parcelas pagas pré-contemplação", 0, prazo, 0)
        redutor_pct = st.number_input("Redutor (%)", 0.0, 50.0, 0.0)

        administradora = st.selectbox(
            "Administradora",
            ["CNP", "Itaú", "Porto"]
        )

        grupo = "Demais Grupos"
        if administradora == "CNP":
            grupo = st.selectbox(
                "Grupo",
                ["1021", "1053", "Demais Grupos"]
            )

        lance_embutido_pct = st.number_input("Lance embutido (%)", 0.0, 100.0, 20.0)
        lance_fixo_pct = st.number_input("Lance fixo (%)", 0.0, 100.0, 0.0)
        lance_livre_pct = st.number_input("Lance livre (%)", 0.0, 100.0, 5.0)

    res_cons = calcular_consorcio(
        credito, prazo, taxa_adm, fundo_reserva, parcelas_pagas,
        lance_embutido_pct, lance_livre_pct, lance_fixo_pct,
        redutor_pct, administradora, grupo
    )

    with c2:
        st.metric("Categoria", f"R$ {res_cons['Categoria']:,.2f}")
        st.metric("Parcela Pré", f"R$ {res_cons['Parcela Pré']:,.2f}")
        st.metric("Parcela Pós", f"R$ {res_cons['Parcela Pós']:,.2f}")
        st.metric("Lance Total", f"R$ {res_cons['Lance Total']:,.2f}")
        st.metric("Crédito Líquido", f"R$ {res_cons['Crédito Líquido']:,.2f}")
        st.metric("Probabilidade de Contemplação", f"{res_cons['Probabilidade']:.1f}%")


# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    c1, c2 = st.columns(2)

    with c1:
        valor_imovel = st.number_input("Valor do bem (R$)", 50000.0, 3000000.0, 300000.0)
        entrada = st.number_input("Entrada (R$)", 0.0, valor_imovel, 60000.0)
        prazo_fin = st.number_input("Prazo (meses)", 60, 420, 360)
        juros_anual = st.number_input("Juros anual (%)", 0.0, 20.0, 10.5)
        sistema = st.selectbox("Sistema de Amortização", ["PRICE", "SAC"])

    valor_fin = valor_imovel - entrada

    df_fin = tabela_price(valor_fin, juros_anual, prazo_fin) if sistema == "PRICE" else tabela_sac(valor_fin, juros_anual, prazo_fin)

    parcela_ini = df_fin.iloc[0]["Prestação"] if not df_fin.empty else 0.0
    total_pago = df_fin["Prestação"].sum() if not df_fin.empty else 0.0

    with c2:
        st.metric("Valor financiado", f"R$ {valor_fin:,.2f}")
        st.metric("Parcela inicial", f"R$ {parcela_ini:,.2f}")
        st.metric("Total pago", f"R$ {total_pago:,.2f}")


# =========================
# COMPARATIVO
# =========================
with tab_comp:
    df_comp = pd.DataFrame({
        "Modalidade": ["Consórcio", "Financiamento"],
        "Parcela Inicial": [res_cons["Parcela Pré"], parcela_ini],
        "Custo Total": [res_cons["Categoria"], total_pago]
    }).set_index("Modalidade")

    st.bar_chart(df_comp)


# =========================
# DIDÁTICA
# =========================
with tab_did:
    st.markdown("""
### 📘 Explicação dos Cálculos

**Consórcio**
- Categoria = Crédito + Taxas
- Parcela Pré = Parcela Base – Redutor
- Parcela Pós = Parcela Base
- Lances variam conforme administradora e grupo
- Probabilidade = Lance Total ÷ Crédito

**Financiamento**
- PRICE → parcelas fixas
- SAC → parcelas decrescentes
- Entrada reduz juros totais
""")


# =========================
# APRESENTAÇÃO
# =========================
with tab_apres:
    texto = f"""
SIMULAÇÃO – INTELLIGENCE BANKING

CONSÓRCIO
Crédito: R$ {credito:,.2f}
Parcela Pré: R$ {res_cons['Parcela Pré']:,.2f}
Parcela Pós: R$ {res_cons['Parcela Pós']:,.2f}
Lance Total: R$ {res_cons['Lance Total']:,.2f}
Probabilidade de Contemplação: {res_cons['Probabilidade']:.1f}%

FINANCIAMENTO
Valor do bem: R$ {valor_imovel:,.2f}
Entrada: R$ {entrada:,.2f}
Parcela Inicial: R$ {parcela_ini:,.2f}
Total Pago: R$ {total_pago:,.2f}
"""

    st.download_button(
        "📥 Baixar proposta (.txt)",
        texto,
        file_name="proposta_intelligence_banking.txt"
    )

st.markdown("<center>Desenvolvido por Victor • Intelligence Banking 2026</center>", unsafe_allow_html=True)

































