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
# FUNÇÕES AUXILIARES
# =========================

def probabilidade_contemplacao(lance_total, credito):
    if credito <= 0:
        return 0
    pct = (lance_total / credito) * 100
    if pct < 10:
        return 15
    elif pct < 20:
        return 30
    elif pct < 30:
        return 55
    elif pct < 40:
        return 75
    else:
        return 90


def score_estrategia(custo_total, prazo, parcela):
    score = 100
    score -= custo_total / 150000
    score -= parcela / 3000
    score -= prazo / 15
    return max(0, round(score, 1))


# =========================
# CONSÓRCIO
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

    # Regras por administradora
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

    prob = probabilidade_contemplacao(lance_total, credito)

    return {
        "Categoria": categoria,
        "Parcela Pré": parcela_pre,
        "Parcela Pós": parcela_pos,
        "Saldo Atual": saldo_atual,
        "Lance Total": lance_total,
        "Crédito Líquido": credito_liquido,
        "Probabilidade": prob,
        "Custo Total": categoria
    }


# =========================
# FINANCIAMENTO
# =========================
def tabela_price(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    if i == 0:
        prest = valor / meses
        return prest, prest, valor, 0

    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    total = pmt * meses
    juros = total - valor
    return pmt, pmt, total, juros


def tabela_sac(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    parcelas = []

    for _ in range(meses):
        juros = saldo * i
        parcelas.append(amort + juros)
        saldo -= amort

    total = sum(parcelas)
    juros_total = total - valor
    return parcelas[0], parcelas[-1], total, juros_total


# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_comp, tab_did, tab_apres = st.tabs(
    ["🤝 Consórcio", "🏦 Financiamento", "📊 Comparativo", "📘 Didática", "🧾 Apresentação"]
)

# =========================
# ABA CONSÓRCIO
# =========================
with tab_cons:
    c1, c2 = st.columns(2)

    with c1:
        credito = st.number_input("Crédito (R$)", value=300000.0, step=5000.0)
        prazo = st.number_input("Prazo (meses)", min_value=1, value=180)

        taxa_adm = st.number_input("Taxa de Administração (%)", value=15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", value=2.0)

        meses_contemplacao = st.number_input("Meses até a contemplação", min_value=0, value=12)
        redutor_pct = st.number_input("Redutor sobre parcela pré (%)", value=0.0)

        administradora = st.selectbox("Administradora", ["CNP", "Itaú", "Porto"])

        grupo = "Demais Grupos"
        if administradora == "CNP":
            grupo = st.selectbox("Grupo", ["1021", "1053", "Demais Grupos"])

        lance_embutido_pct = st.number_input("Lance embutido (%)", value=20.0)
        lance_fixo_pct = st.number_input("Lance fixo (%)", value=0.0)
        lance_livre_pct = st.number_input("Lance livre (%)", value=5.0)

    res_c = calcular_consorcio(
        credito, prazo, taxa_adm, fundo_reserva, meses_contemplacao,
        lance_embutido_pct, lance_livre_pct, lance_fixo_pct,
        redutor_pct, administradora, grupo
    )

    with c2:
        st.metric("Categoria", f"R$ {res_c['Categoria']:,.2f}")
        st.metric("Parcela Pré", f"R$ {res_c['Parcela Pré']:,.2f}")
        st.metric("Parcela Pós", f"R$ {res_c['Parcela Pós']:,.2f}")
        st.metric("Saldo Atual", f"R$ {res_c['Saldo Atual']:,.2f}")
        st.metric("Lance Total", f"R$ {res_c['Lance Total']:,.2f}")
        st.metric("Probabilidade de Contemplação", f"{res_c['Probabilidade']}%")


# =========================
# ABA FINANCIAMENTO
# =========================
with tab_fin:
    f1, f2 = st.columns(2)

    with f1:
        valor_bem = st.number_input("Valor do bem (R$)", value=500000.0)
        entrada = st.number_input("Entrada (R$)", value=100000.0)
        prazo_f = st.number_input("Prazo (meses)", min_value=1, value=240)
        juros_anual = st.number_input("Juros anual (%)", value=12.0)
        sistema = st.selectbox("Sistema", ["Price", "SAC"])

    valor_fin = max(valor_bem - entrada, 0)

    if sistema == "Price":
        p_ini, p_fim, total_fin, juros_fin = tabela_price(valor_fin, juros_anual, prazo_f)
    else:
        p_ini, p_fim, total_fin, juros_fin = tabela_sac(valor_fin, juros_anual, prazo_f)

    with f2:
        st.metric("Valor financiado", f"R$ {valor_fin:,.2f}")
        st.metric("Parcela inicial", f"R$ {p_ini:,.2f}")
        st.metric("Parcela final", f"R$ {p_fim:,.2f}")
        st.metric("Total pago", f"R$ {total_fin:,.2f}")
        st.metric("Juros totais", f"R$ {juros_fin:,.2f}")


# =========================
# COMPARATIVO
# =========================
with tab_comp:
    score_cons = score_estrategia(res_c["Custo Total"], prazo, res_c["Parcela Pré"])
    score_fin = score_estrategia(total_fin, prazo_f, p_ini)

    st.metric("Score Consórcio", score_cons)
    st.metric("Score Financiamento", score_fin)

    df_comp = pd.DataFrame({
        "Estratégia": ["Consórcio", "Financiamento"],
        "Custo Total (R$)": [res_c["Custo Total"], total_fin]
    })

    st.bar_chart(df_comp.set_index("Estratégia"))

    st.success(
        "🎯 Estratégia recomendada: " +
        ("CONSÓRCIO" if score_cons > score_fin else "FINANCIAMENTO")
    )


# =========================
# DIDÁTICA
# =========================
with tab_did:
    st.markdown("""
### 📘 Explicação Didática

**Consórcio**
- Categoria = Crédito + Taxas
- Parcela pré = parcela base − redutor
- Parcela pós = parcela integral
- Lance embutido reduz o crédito
- Lance fixo e livre variam conforme administradora
- Probabilidade baseada no % do lance

**Financiamento**
- PRICE: parcela fixa
- SAC: parcela decrescente
- Juros convertidos de anual para mensal

**Score**
- Considera custo total, prazo e impacto da parcela
""")


# =========================
# APRESENTAÇÃO / TXT
# =========================
with tab_apres:
    proposta = f"""
PROPOSTA FINANCEIRA – INTELLIGENCE BANKING
----------------------------------------

CONSÓRCIO
Crédito: R$ {credito:,.2f}
Categoria: R$ {res_c['Categoria']:,.2f}
Parcela pré: R$ {res_c['Parcela Pré']:,.2f}
Parcela pós: R$ {res_c['Parcela Pós']:,.2f}
Lance total: R$ {res_c['Lance Total']:,.2f}
Probabilidade: {res_c['Probabilidade']}%

FINANCIAMENTO
Valor financiado: R$ {valor_fin:,.2f}
Sistema: {sistema}
Parcela inicial: R$ {p_ini:,.2f}
Parcela final: R$ {p_fim:,.2f}
Total pago: R$ {total_fin:,.2f}

RECOMENDAÇÃO
{"CONSÓRCIO" if score_cons > score_fin else "FINANCIAMENTO"}
"""

    st.download_button(
        "⬇️ Baixar proposta (.txt)",
        proposta,
        file_name="proposta_intelligence_banking.txt"
    )

st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking 2026</center>",
    unsafe_allow_html=True
)





































