import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Simulador Consórcio x Financiamento", layout="wide")

# =========================
# FUNÇÕES AUXILIARES
# =========================
def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_price(valor, juros_anual, meses):
    juros = juros_anual / 100 / 12
    parcela = valor * (juros * (1 + juros) ** meses) / ((1 + juros) ** meses - 1)
    saldo = valor
    dados = []

    for i in range(1, meses + 1):
        juros_mes = saldo * juros
        amort = parcela - juros_mes
        saldo -= amort
        dados.append([i, parcela, amort, juros_mes, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"])

def calcular_sac(valor, juros_anual, meses):
    juros = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    dados = []

    for i in range(1, meses + 1):
        juros_mes = saldo * juros
        parcela = amort + juros_mes
        saldo -= amort
        dados.append([i, parcela, amort, juros_mes, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"])

# =========================
# ABAS
# =========================
aba1, aba2, aba3, aba4 = st.tabs([
    "📦 Consórcio",
    "🏦 Financiamento",
    "🔄 Comparação & Score",
    "📘 Explicação Didática"
])

# =========================
# CONSÓRCIO
# =========================
with aba1:
    st.header("📦 Simulação de Consórcio")

    credito = st.number_input("Crédito (R$)", min_value=10000.0, step=1000.0)
    taxa_adm = st.number_input("Taxa de Administração (%)", min_value=0.0)
    fundo_reserva = st.number_input("Fundo de Reserva (%)", min_value=0.0)
    prazo = st.number_input("Prazo (meses)", min_value=12, step=12)

    parcelas_pagas = st.number_input("Parcelas pagas pré-contemplação", min_value=0, max_value=prazo)
    redutor = st.number_input("Redutor sobre parcela pré (%)", min_value=0.0, max_value=100.0)

    st.subheader("🎯 Lances")
    lance_embutido_pct = st.number_input("Lance Embutido (%)", min_value=0.0, max_value=100.0)
    lance_fixo = st.number_input("Lance Fixo (R$)", min_value=0.0)
    lance_livre = st.number_input("Lance Livre (R$)", min_value=0.0)

    categoria = credito * (1 + (taxa_adm + fundo_reserva) / 100)

    lance_embutido = credito * lance_embutido_pct / 100
    total_lance = lance_embutido + lance_fixo + lance_livre

    credito_liquido = credito - lance_embutido

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor / 100)

    saldo_devedor = categoria - (parcela_pre * parcelas_pagas)

    st.markdown("### 📊 Resultados")
    col1, col2, col3 = st.columns(3)

    col1.metric("Categoria", formatar(categoria))
    col2.metric("Crédito Líquido", formatar(credito_liquido))
    col3.metric("Total de Lance", formatar(total_lance))

    st.metric("Saldo Devedor Atual", formatar(saldo_devedor))

    # Gráfico Consórcio
    meses = list(range(parcelas_pagas, prazo + 1))
    saldos = [max(saldo_devedor - parcela_base * (m - parcelas_pagas), 0) for m in meses]

    df_cons = pd.DataFrame({"Mês": meses, "Saldo Devedor": saldos})
    st.line_chart(df_cons.set_index("Mês"))

# =========================
# FINANCIAMENTO
# =========================
with aba2:
    st.header("🏦 Simulação de Financiamento")

    valor_fin = st.number_input("Valor financiado (R$)", min_value=10000.0)
    juros_anual = st.number_input("Juros Anual (%)", min_value=0.0)
    prazo_fin = st.number_input("Prazo (meses)", min_value=12, step=12)

    df_price = calcular_price(valor_fin, juros_anual, prazo_fin)
    df_sac = calcular_sac(valor_fin, juros_anual, prazo_fin)

    st.subheader("📉 Saldo Devedor")
    st.line_chart(
        pd.DataFrame({
            "PRICE": df_price["Saldo"],
            "SAC": df_sac["Saldo"]
        })
    )

# =========================
# COMPARAÇÃO & SCORE
# =========================
with aba3:
    st.header("🔄 Comparação Inteligente")

    custo_cons = categoria
    custo_fin = df_price["Parcela"].sum()

    score_cons = max(0, 100 - (custo_cons / credito) * 50)
    score_fin = max(0, 100 - (custo_fin / valor_fin) * 50)

    col1, col2 = st.columns(2)
    col1.metric("Score Consórcio", f"{score_cons:.0f}/100")
    col2.metric("Score Financiamento", f"{score_fin:.0f}/100")

    if score_cons > score_fin:
        st.success("🎯 Recomendação: CONSÓRCIO é a melhor estratégia")
    else:
        st.info("🎯 Recomendação: FINANCIAMENTO é a melhor estratégia")

# =========================
# EXPLICAÇÃO DIDÁTICA
# =========================
with aba4:
    st.header("📘 Explicação dos Cálculos")

    st.markdown("""
### 📦 Consórcio
- **Categoria** = Crédito + Taxa de Administração + Fundo de Reserva  
- **Parcela base** = Categoria / Prazo  
- **Parcela pré-contemplação** sofre **redutor (%)**
- **Saldo devedor** considera parcelas já pagas com redutor
- **Lance embutido** reduz o crédito
- **Lance fixo e livre** NÃO reduzem o crédito

---

### 🏦 Financiamento
**PRICE**
- Parcela fixa
- Juros maiores no início

**SAC**
- Amortização fixa
- Parcela decrescente
- Menos juros totais

---

### 🧠 Score
- Avalia custo total vs crédito
- Quanto menor o custo relativo, maior o score
- Recomendação automática baseada no score
""")


