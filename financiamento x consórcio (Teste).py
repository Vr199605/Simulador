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
    if juros_anual == 0:
        parcela = valor / meses
        saldo = valor
        dados = []
        for i in range(1, meses + 1):
            saldo -= parcela
            dados.append([i, parcela, 0, parcela, max(saldo, 0)])
        return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])

    i = juros_anual / 100 / 12
    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)

    saldo = valor
    dados = []
    for n in range(1, meses + 1):
        juros = saldo * i
        amort = pmt - juros
        saldo -= amort
        dados.append([n, pmt, juros, amort, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])


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

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor_pct / 100)
    parcela_pos = parcela_base

    saldo_atual = categoria - (parcelas_pagas * parcela_pre)
    saldo_atual = max(saldo_atual, 0)

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_livre = categoria * (lance_livre_pct / 100)
    lance_fixo = categoria * (lance_fixo_pct / 100)
    lance_total = lance_embutido + lance_livre + lance_fixo

    credito_liquido = credito - lance_embutido

    # Probabilidade simplificada de contemplação
    probabilidade = min(90, 10 + lance_total / categoria * 100)

    saldos = []
    saldo_tmp = categoria
    for i in range(prazo):
        if i < parcelas_pagas:
            saldo_tmp -= parcela_pre
        else:
            saldo_tmp -= parcela_pos
        saldos.append(max(saldo_tmp, 0))

    df_saldo = pd.DataFrame({
        "Parcela": range(1, prazo + 1),
        "Saldo Devedor": saldos
    })

    return {
        "Categoria": categoria,
        "Parcela Pré": parcela_pre,
        "Parcela Pós": parcela_pos,
        "Saldo Atual": saldo_atual,
        "Lance Total": lance_total,
        "Crédito Líquido": credito_liquido,
        "Probabilidade": probabilidade,
        "DataFrame": df_saldo
    }

# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_did = st.tabs([
    "🤝 Consórcio",
    "🏦 Financiamento",
    "📘 Aba Didática"
])

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    st.header("Simulação de Consórcio")

    c1, c2 = st.columns([1, 2])

    with c1:
        credito = st.number_input("Crédito contratado (R$)", 50000.0, 3000000.0, 300000.0)
        prazo = st.number_input("Prazo (meses)", 60, 240, 180)

        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        parcelas_pagas = st.number_input("Parcelas pagas pré-contemplação", 0, prazo, 0)

        st.subheader("🎯 Lances")
        lance_embutido_pct = st.number_input("Lance Embutido (%)", 0.0, 100.0, 20.0)
        lance_livre_pct = st.number_input("Lance Livre (% categoria)", 0.0, 100.0, 5.0)
        lance_fixo_pct = st.number_input("Lance Fixo (% categoria)", 0.0, 100.0, 0.0)

        st.subheader("🔻 Redutor")
        redutor_pct = st.number_input("Redutor na parcela pré (%)", 0.0, 50.0, 0.0)

    res = calcular_consorcio(
        credito, prazo, taxa_adm, fundo_reserva,
        parcelas_pagas, lance_embutido_pct,
        lance_livre_pct, lance_fixo_pct, redutor_pct
    )

    with c2:
        st.markdown(f"""
        ### 📊 Resumo

        • **Categoria:** R$ {res['Categoria']:,.2f}  
        • **Parcela pré:** R$ {res['Parcela Pré']:,.2f}  
        • **Parcela pós:** R$ {res['Parcela Pós']:,.2f}  
        • **Saldo atual:** R$ {res['Saldo Atual']:,.2f}  
        • **Lance total:** R$ {res['Lance Total']:,.2f}  
        • **Crédito líquido:** R$ {res['Crédito Líquido']:,.2f}  
        • **Probabilidade estimada:** {res['Probabilidade']:.1f}%
        """)

        st.line_chart(res["DataFrame"].set_index("Parcela"))

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    st.header("Simulação de Financiamento (Tabela Price)")

    c1, c2 = st.columns([1, 2])

    with c1:
        valor_fin = st.number_input("Valor financiado (R$)", 50000.0, 3000000.0, 300000.0)
        juros_anual = st.number_input("Juros anual (%)", 0.0, 30.0, 12.0)
        prazo_fin = st.number_input("Prazo (meses)", 12, 420, 240)

    df_price = tabela_price(valor_fin, juros_anual, prazo_fin)

    with c2:
        st.metric("Parcela", f"R$ {df_price.iloc[0]['Prestação']:,.2f}")
        st.metric("Total pago", f"R$ {df_price['Prestação'].sum():,.2f}")
        st.line_chart(df_price.set_index("Parcela")[["Saldo"]])

# =========================
# ABA DIDÁTICA
# =========================
with tab_did:
    st.header("📘 Entenda os Cálculos")

    st.markdown("""
### 🤝 Consórcio
- **Categoria:** crédito + taxa de administração + fundo de reserva  
- **Parcela pré:** parcela reduzida antes da contemplação  
- **Parcela pós:** parcela cheia após contemplação  
- **Lance embutido:** abatido do crédito  
- **Probabilidade:** estimativa baseada no percentual de lance  

### 🏦 Financiamento
- **Sistema Price:** parcelas fixas  
- **Juros compostos mensais**  
- **Amortização cresce ao longo do tempo**  
- **Total pago sempre > valor financiado**
    """)

# =========================
# RODAPÉ
# =========================
st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking 2026</center>",
    unsafe_allow_html=True
)










