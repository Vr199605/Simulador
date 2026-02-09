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

st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    color: gray;
    padding: 8px;
}
h1, h2, h3 { color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================

def score_estrategia(custo_total, prazo, parcela):
    score = 100
    score -= custo_total / 100000
    score -= parcela / 2000
    score -= prazo / 10
    return max(0, round(score, 1))


def calcular_consorcio(valor_credito, prazo, taxa_adm, fundo_reserva,
                       lance_embutido_pct, lance_livre, lance_fixo):

    taxa_total = (taxa_adm + fundo_reserva) / 100
    valor_plano = valor_credito * (1 + taxa_total)
    parcela = valor_plano / prazo

    lance_embutido = valor_credito * (lance_embutido_pct / 100)
    lance_total = lance_embutido + lance_livre + lance_fixo
    credito_liquido = valor_credito - lance_embutido

    return {
        "Parcela": parcela,
        "Valor Plano": valor_plano,
        "Lance Total": lance_total,
        "Lance Embutido": lance_embutido,
        "Crédito Líquido": credito_liquido
    }


def calcular_financiamento(valor, taxa_mensal, prazo, modelo):
    saldo = valor
    parcelas = []

    if modelo == "SAC":
        amortizacao = valor / prazo
        for _ in range(prazo):
            juros = saldo * taxa_mensal
            parcela = amortizacao + juros
            parcelas.append(parcela)
            saldo -= amortizacao
    else:
        parcela_fixa = valor * (taxa_mensal * (1 + taxa_mensal) ** prazo) / ((1 + taxa_mensal) ** prazo - 1)
        for _ in range(prazo):
            juros = saldo * taxa_mensal
            amortizacao = parcela_fixa - juros
            parcelas.append(parcela_fixa)
            saldo -= amortizacao

    total_pago = sum(parcelas)
    juros_totais = total_pago - valor

    return parcelas[0], parcelas[-1], total_pago, juros_totais

# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_comp, tab_txt, tab_did = st.tabs(
    ["🤝 Consórcio", "🏦 Financiamento", "🔄 Comparação", "📄 Proposta (.txt)", "📘 Explicação Didática"]
)

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    st.header("Simulador de Consórcio")

    c1, c2 = st.columns([1, 2])

    with c1:
        valor_credito = st.number_input("Valor do Crédito (R$)", 50000.0, 3000000.0, 300000.0)
        prazo_c = st.number_input("Prazo (meses)", 60, 240, 180)
        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        st.subheader("💰 Lances")
        lance_embutido_pct = st.number_input("Lance Embutido (%)", 0.0, 100.0, 20.0, step=0.1)
        lance_livre = st.number_input("Lance Livre (R$)", 0.0, 5000000.0, 0.0)
        lance_fixo = st.number_input("Lance Fixo (R$)", 0.0, 5000000.0, 0.0)

    res_c = calcular_consorcio(
        valor_credito, prazo_c, taxa_adm, fundo_reserva,
        lance_embutido_pct, lance_livre, lance_fixo
    )

    with c2:
        st.markdown(f"""
        <div class="card">
        • Parcela mensal: <b>R$ {res_c['Parcela']:,.2f}</b><br>
        • Lance total: <b>R$ {res_c['Lance Total']:,.2f}</b><br>
        • Crédito líquido: <b>R$ {res_c['Crédito Líquido']:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    st.header("Simulador de Financiamento")

    f1, f2 = st.columns([1, 2])

    with f1:
        valor_bem = st.number_input("Valor do Bem (R$)", 100000.0, 5000000.0, 500000.0)
        entrada = st.number_input("Entrada (R$)", 0.0, valor_bem * 0.9, valor_bem * 0.2)
        prazo_f = st.number_input("Prazo (meses)", 12, 420, 240)

        juros_anual = st.number_input("Taxa de Juros Anual (%)", 1.0, 30.0, 12.0) / 100
        modelo = st.selectbox("Sistema de Amortização", ["Price", "SAC"])

    taxa_mensal = (1 + juros_anual) ** (1 / 12) - 1
    valor_financiado = valor_bem - entrada

    p_ini, p_fim, total_pago, juros = calcular_financiamento(
        valor_financiado, taxa_mensal, prazo_f, modelo
    )

    with f2:
        st.markdown(f"""
        <div class="card">
        • Valor financiado: <b>R$ {valor_financiado:,.2f}</b><br>
        • Parcela inicial: <b>R$ {p_ini:,.2f}</b><br>
        • Parcela final: <b>R$ {p_fim:,.2f}</b><br>
        • Total pago: <b>R$ {total_pago:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

# =========================
# COMPARAÇÃO
# =========================
with tab_comp:
    st.header("🔄 Comparação Inteligente")

    score_cons = score_estrategia(res_c["Valor Plano"], prazo_c, res_c["Parcela"])
    score_fin = score_estrategia(total_pago, prazo_f, p_ini)

    st.metric("Score Consórcio", score_cons)
    st.metric("Score Financiamento", score_fin)

    if score_cons > score_fin:
        st.success("🎯 Estratégia recomendada: CONSÓRCIO")
    else:
        st.success("🎯 Estratégia recomendada: FINANCIAMENTO")

# =========================
# PROPOSTA TXT
# =========================
with tab_txt:
    st.header("📄 Gerar Proposta (.txt)")

    proposta = f"""
PROPOSTA FINANCEIRA – INTELLIGENCE BANKING

CONSÓRCIO
Crédito: R$ {valor_credito:,.2f}
Parcela: R$ {res_c['Parcela']:,.2f}
Lance total: R$ {res_c['Lance Total']:,.2f}
Crédito líquido: R$ {res_c['Crédito Líquido']:,.2f}

FINANCIAMENTO
Valor financiado: R$ {valor_financiado:,.2f}
Sistema: {modelo}
Parcela inicial: R$ {p_ini:,.2f}
Parcela final: R$ {p_fim:,.2f}
Total pago: R$ {total_pago:,.2f}

RECOMENDAÇÃO
{"CONSÓRCIO" if score_cons > score_fin else "FINANCIAMENTO"}
"""

    st.download_button("⬇️ Baixar Proposta", proposta, "proposta_intelligence.txt")

# =========================
# EXPLICAÇÃO DIDÁTICA
# =========================
with tab_did:
    st.header("📘 Explicação Didática dos Cálculos")

    st.subheader("🤝 Consórcio")
    st.markdown("""
- **Parcela** = (Crédito + taxas) ÷ prazo  
- **Taxa total** = taxa de administração + fundo de reserva  
- **Lance embutido** reduz o crédito recebido  
- **Lance livre e fixo** não reduzem o crédito, apenas aumentam competitividade  
- **Crédito líquido** = crédito contratado − lance embutido
""")

    st.subheader("🏦 Financiamento")
    st.markdown("""
**PRICE**
- Parcelas fixas
- Juros maiores no início
- Amortização cresce ao longo do tempo

**SAC**
- Parcelas decrescentes
- Amortização fixa
- Menor custo total de juros
""")

    st.subheader("🧠 Score de Estratégia")
    st.markdown("""
O score começa em **100 pontos** e sofre penalizações por:
- Custo total elevado
- Parcela mensal alta
- Prazo longo

Quanto **maior o score**, melhor a estratégia financeira.
""")

# =========================
# RODAPÉ
# =========================
st.markdown(
    '<div class="footer">Desenvolvido por Victor • Intelligence Banking 2026</div>',
    unsafe_allow_html=True
)
