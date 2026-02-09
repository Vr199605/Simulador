import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Simulador Consórcio x Financiamento",
    layout="wide"
)

# =========================
# FUNÇÕES
# =========================
def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def tabela_price(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        amort = pmt - juros
        saldo -= amort
        dados.append([m, pmt, amort, juros, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"])

def tabela_sac(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        parcela = amort + juros
        saldo -= amort
        dados.append([m, parcela, amort, juros, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Mês", "Parcela", "Amortização", "Juros", "Saldo"])

# =========================
# ABAS
# =========================
aba_cons, aba_fin, aba_comp, aba_info = st.tabs([
    "📦 Consórcio",
    "🏦 Financiamento",
    "🔄 Comparação & Score",
    "📘 Explicação Didática"
])

# =========================
# CONSÓRCIO
# =========================
with aba_cons:
    st.header("📦 Simulação de Consórcio")

    credito = st.number_input("Crédito (R$)", 10000.0, step=1000.0, key="cons_credito")
    taxa_adm = st.number_input("Taxa de Administração (%)", 0.0, key="cons_taxa")
    fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, key="cons_fundo")
    prazo = st.number_input("Prazo (meses)", 12, step=12, key="cons_prazo")

    parcelas_pagas = st.number_input(
        "Parcelas pagas pré-contemplação",
        min_value=0,
        max_value=int(prazo),
        key="cons_parcelas_pagas"
    )

    redutor = st.number_input(
        "Redutor sobre a parcela pré (%)",
        min_value=0.0,
        max_value=100.0,
        key="cons_redutor"
    )

    st.subheader("🎯 Lances")
    lance_emb_pct = st.number_input(
        "Lance embutido (%)",
        min_value=0.0,
        max_value=100.0,
        key="cons_lance_emb"
    )

    lance_fixo = st.number_input(
        "Lance fixo (R$)",
        min_value=0.0,
        key="cons_lance_fixo"
    )

    lance_livre = st.number_input(
        "Lance livre (R$)",
        min_value=0.0,
        key="cons_lance_livre"
    )

    # Cálculos
    categoria = credito * (1 + (taxa_adm + fundo_reserva) / 100)
    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor / 100)

    saldo_devedor = categoria - (parcela_pre * parcelas_pagas)

    lance_embutido = credito * lance_emb_pct / 100
    credito_liquido = credito - lance_embutido

    total_lance = lance_embutido + lance_fixo + lance_livre

    # Resultados
    st.subheader("📊 Resultados")
    c1, c2, c3 = st.columns(3)

    c1.metric("Categoria", brl(categoria))
    c2.metric("Crédito Líquido", brl(credito_liquido))
    c3.metric("Total de Lance", brl(total_lance))

    st.metric("Saldo Devedor Atual", brl(max(saldo_devedor, 0)))

    # Gráfico Consórcio
    meses = list(range(parcelas_pagas, prazo + 1))
    saldos = [max(saldo_devedor - parcela_base * (m - parcelas_pagas), 0) for m in meses]

    df_cons = pd.DataFrame({"Mês": meses, "Saldo": saldos})
    st.line_chart(df_cons.set_index("Mês"))

# =========================
# FINANCIAMENTO
# =========================
with aba_fin:
    st.header("🏦 Simulação de Financiamento")

    valor_fin = st.number_input(
        "Valor financiado (R$)",
        min_value=10000.0,
        step=1000.0,
        key="fin_valor"
    )

    juros_anual = st.number_input(
        "Juros anual (%)",
        min_value=0.0,
        key="fin_juros"
    )

    prazo_fin = st.number_input(
        "Prazo do financiamento (meses)",
        min_value=12,
        step=12,
        key="fin_prazo"
    )

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
# COMPARAÇÃO & SCORE
# =========================
with aba_comp:
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
with aba_info:
    st.header("📘 Explicação Didática dos Cálculos")

    st.markdown("""
### 📦 Consórcio
- **Categoria** = Crédito + Taxa de Administração + Fundo de Reserva  
- **Parcela base** = Categoria ÷ Prazo  
- **Redutor** é aplicado **somente na parcela pré-contemplação**  
- **Saldo devedor** considera parcelas já pagas com redutor  
- **Lance embutido** reduz o crédito  
- **Lance fixo e livre** não reduzem o crédito  

---

### 🏦 Financiamento
**Tabela PRICE**
- Parcela fixa
- Mais juros no início

**Tabela SAC**
- Amortização fixa
- Parcelas decrescentes
- Menor custo total

---

### 🧠 Score
- Compara custo total vs valor financiado
- Quanto menor o custo relativo, maior o score
- Gera recomendação automática
""")




