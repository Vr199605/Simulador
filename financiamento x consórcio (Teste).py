import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Simulador Consórcio x Financiamento",
    page_icon="💎",
    layout="wide"
)

st.title("💎 Simulador Institucional – Consórcio x Financiamento")

tabs = st.tabs([
    "🏗️ Consórcio",
    "🏦 Financiamento",
    "📊 Comparativo",
    "📘 Explicação Didática",
    "📄 Apresentação ao Cliente"
])

# =========================
# CONSÓRCIO
# =========================
with tabs[0]:
    st.subheader("🏗️ Simulação de Consórcio")

    credito = st.number_input("Crédito desejado (R$)", 10000.0, step=5000.0)
    taxa_adm = st.number_input("Taxa de Administração (%)", 0.0, 30.0, 15.0)
    fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)
    prazo = st.number_input("Prazo (meses)", 12, 240, 180)

    parcelas_pagas = st.number_input("Parcelas pagas pré-contemplação", 0, prazo, 12)
    redutor = st.number_input("Redutor sobre parcela pré-contemplação (%)", 0.0, 50.0, 0.0)

    lance_fixo = st.number_input("Lance Fixo (%)", 0.0, 50.0, 0.0)
    lance_livre = st.number_input("Lance Livre (%)", 0.0, 100.0, 0.0)

    categoria = credito * (1 + (taxa_adm + fundo_reserva) / 100)
    parcela_base = categoria / prazo
    parcela_reduzida = parcela_base * (1 - redutor / 100)

    lance_total = categoria * (lance_fixo + lance_livre) / 100
    saldo_devedor_consorcio = categoria - (parcelas_pagas * parcela_reduzida)

    st.metric("📦 Categoria Total", f"R$ {categoria:,.2f}")
    st.metric("📄 Parcela Base", f"R$ {parcela_base:,.2f}")
    st.metric("🔻 Parcela com Redutor", f"R$ {parcela_reduzida:,.2f}")
    st.metric("🎯 Lance Total", f"R$ {lance_total:,.2f}")
    st.metric("📉 Saldo Devedor Atual", f"R$ {saldo_devedor_consorcio:,.2f}")

    probabilidade = min(100, (lance_fixo + lance_livre) * 1.5)
    st.progress(probabilidade / 100)
    st.caption(f"🎯 Probabilidade estimada de contemplação: **{probabilidade:.1f}%**")

# =========================
# FINANCIAMENTO
# =========================
with tabs[1]:
    st.subheader("🏦 Simulação de Financiamento")

    valor_imovel = st.number_input("Valor do bem (R$)", 50000.0, step=10000.0)
    entrada = st.number_input("Entrada (R$)", 0.0, valor_imovel, 0.0)
    valor_financiado = valor_imovel - entrada

    juros_anual = st.number_input("Juros anual (%)", 0.0, 30.0, 12.0)
    prazo_fin = st.number_input("Prazo (meses)", 12, 420, 240)
    sistema = st.selectbox("Sistema de Amortização", ["PRICE", "SAC"])

    juros_mensal = (1 + juros_anual / 100) ** (1/12) - 1

    parcelas = []

    if sistema == "PRICE":
        parcela = valor_financiado * (juros_mensal * (1 + juros_mensal)**prazo_fin) / ((1 + juros_mensal)**prazo_fin - 1)
        saldo = valor_financiado

        for i in range(1, prazo_fin + 1):
            juros = saldo * juros_mensal
            amort = parcela - juros
            saldo -= amort
            parcelas.append(parcela)

    else:  # SAC
        amort = valor_financiado / prazo_fin
        saldo = valor_financiado

        for i in range(1, prazo_fin + 1):
            juros = saldo * juros_mensal
            parcela = amort + juros
            saldo -= amort
            parcelas.append(parcela)

    total_pago_fin = sum(parcelas)

    st.metric("💰 Valor Financiado", f"R$ {valor_financiado:,.2f}")
    st.metric("📄 Parcela Inicial", f"R$ {parcelas[0]:,.2f}")
    st.metric("💸 Total Pago", f"R$ {total_pago_fin:,.2f}")

# =========================
# COMPARATIVO
# =========================
with tabs[2]:
    st.subheader("📊 Comparativo Automático")

    labels = ["Consórcio", "Financiamento"]
    valores = [categoria, total_pago_fin]

    fig, ax = plt.subplots()
    ax.bar(labels, valores)
    ax.set_ylabel("Valor Total (R$)")
    ax.set_title("Comparativo de Custo Total")

    st.pyplot(fig)

    vantagem = "Consórcio" if categoria < total_pago_fin else "Financiamento"
    st.success(f"🎯 Melhor custo total: **{vantagem}**")

# =========================
# EXPLICAÇÃO DIDÁTICA
# =========================
with tabs[3]:
    st.subheader("📘 Explicação Didática dos Cálculos")

    st.markdown("""
### 🏗️ Consórcio
- **Categoria** = Crédito + Taxa de Administração + Fundo de Reserva  
- **Parcela Base** = Categoria ÷ Prazo  
- **Redutor** atua apenas **antes da contemplação**
- **Lances** são calculados **sobre a categoria**
- **Probabilidade** é uma estimativa proporcional ao lance ofertado

### 🏦 Financiamento
- Juros informados são **anuais**, convertidos para mensal
- **PRICE** → parcelas fixas  
- **SAC** → parcelas decrescentes
- O custo final depende diretamente do prazo e da taxa

### 📊 Comparativo
- Compara o **valor total desembolsado**
- Não considera reinvestimento, inflação ou custo de oportunidade
""")

# =========================
# APRESENTAÇÃO AO CLIENTE
# =========================
with tabs[4]:
    st.subheader("📄 Proposta para o Cliente")

    texto = f"""
========================================
SIMULAÇÃO PERSONALIZADA
========================================

📌 CONSÓRCIO
Crédito: R$ {credito:,.2f}
Categoria Total: R$ {categoria:,.2f}
Parcela Base: R$ {parcela_base:,.2f}
Parcela com Redutor: R$ {parcela_reduzida:,.2f}
Saldo Devedor Atual: R$ {saldo_devedor_consorcio:,.2f}

📌 FINANCIAMENTO
Valor do Bem: R$ {valor_imovel:,.2f}
Entrada: R$ {entrada:,.2f}
Valor Financiado: R$ {valor_financiado:,.2f}
Parcela Inicial: R$ {parcelas[0]:,.2f}
Total Pago: R$ {total_pago_fin:,.2f}

📊 CONCLUSÃO
Melhor custo total estimado: {vantagem}

Simulação institucional – InvestSmartXP
========================================
"""

    st.text_area("Prévia da Proposta", texto, height=400)

    st.download_button(
        label="⬇️ Baixar Proposta (.txt)",
        data=texto,
        file_name="proposta_simulacao.txt",
        mime="text/plain"
    )




















