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
# FUNÇÕES FINANCIAMENTO
# =========================

def tabela_price(valor, juros_anual, meses):
    if valor <= 0 or meses <= 0:
        return pd.DataFrame()

    i = juros_anual / 100 / 12

    if i == 0:
        parcela = valor / meses
        saldo = valor
        dados = []
        for n in range(1, meses + 1):
            saldo -= parcela
            dados.append([n, parcela, 0, parcela, max(saldo, 0)])
        return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])

    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    saldo = valor
    dados = []

    for n in range(1, meses + 1):
        juros = saldo * i
        amort = pmt - juros
        saldo -= amort
        dados.append([n, pmt, juros, amort, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])


def tabela_sac(valor, juros_anual, meses):
    if valor <= 0 or meses <= 0:
        return pd.DataFrame()

    i = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    dados = []

    for n in range(1, meses + 1):
        juros = saldo * i
        prest = amort + juros
        saldo -= amort
        dados.append([n, prest, juros, amort, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Juros", "Amortização", "Saldo"])


# =========================
# FUNÇÃO CONSÓRCIO
# =========================

def calcular_consorcio(
    credito, prazo, taxa_adm, fundo_reserva,
    parcelas_pagas, lance_embutido_pct,
    lance_livre_pct, lance_fixo_pct, redutor_pct
):
    categoria = credito * (1 + (taxa_adm + fundo_reserva) / 100)

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor_pct / 100)

    saldo_atual = categoria - parcelas_pagas * parcela_pre
    saldo_atual = max(saldo_atual, 0)

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_livre = categoria * (lance_livre_pct / 100)
    lance_fixo = categoria * (lance_fixo_pct / 100)
    lance_total = lance_embutido + lance_livre + lance_fixo

    credito_liquido = credito - lance_embutido
    probabilidade = min(90, 10 + (lance_total / categoria) * 100)

    saldos = []
    saldo_tmp = categoria
    for i in range(prazo):
        saldo_tmp -= parcela_pre if i < parcelas_pagas else parcela_base
        saldos.append(max(saldo_tmp, 0))

    df = pd.DataFrame({
        "Parcela": range(1, prazo + 1),
        "Saldo Devedor": saldos
    })

    return {
        "Categoria": categoria,
        "Parcela Pré": parcela_pre,
        "Parcela Pós": parcela_base,
        "Saldo Atual": saldo_atual,
        "Lance Total": lance_total,
        "Crédito Líquido": credito_liquido,
        "Probabilidade": probabilidade,
        "DataFrame": df
    }


# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_comp, tab_did = st.tabs([
    "🤝 Consórcio",
    "🏦 Financiamento",
    "📊 Comparativo",
    "📘 Aba Didática"
])

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    c1, c2 = st.columns([1, 2])

    with c1:
        credito = st.number_input("Crédito (R$)", 50000.0, 3000000.0, 300000.0)
        prazo = st.number_input("Prazo (meses)", 60, 240, 180)
        taxa_adm = st.number_input("Taxa Adm (%)", 5.0, 30.0, 15.0)
        fundo = st.number_input("Fundo Reserva (%)", 0.0, 5.0, 2.0)
        parcelas_pagas = st.number_input("Parcelas pré pagas", 0, prazo, 0)

        st.subheader("🎯 Lances")
        emb = st.number_input("Lance embutido (%)", 0.0, 100.0, 20.0)
        livre = st.number_input("Lance livre (% categoria)", 0.0, 100.0, 5.0)
        fixo = st.number_input("Lance fixo (% categoria)", 0.0, 100.0, 0.0)

        red = st.number_input("Redutor pré (%)", 0.0, 50.0, 0.0)

    res = calcular_consorcio(
        credito, prazo, taxa_adm, fundo,
        parcelas_pagas, emb, livre, fixo, red
    )

    with c2:
        st.markdown(f"""
        • **Categoria:** R$ {res['Categoria']:,.2f}  
        • **Parcela pré:** R$ {res['Parcela Pré']:,.2f}  
        • **Parcela pós:** R$ {res['Parcela Pós']:,.2f}  
        • **Crédito líquido:** R$ {res['Crédito Líquido']:,.2f}  
        • **Probabilidade:** {res['Probabilidade']:.1f}%
        """)
        st.line_chart(res["DataFrame"].set_index("Parcela"))

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    c1, c2 = st.columns([1, 2])

    with c1:
        valor_bem = st.number_input("Valor do bem (R$)", 50000.0, 3000000.0, 300000.0)
        entrada = st.number_input("Entrada (R$)", 0.0, valor_bem, 60000.0)
        juros = st.number_input("Juros anual (%)", 0.0, 30.0, 12.0)
        prazo_fin = st.number_input("Prazo (meses)", 12, 420, 240)
        sistema = st.selectbox("Sistema", ["PRICE", "SAC"])

    valor_fin = max(valor_bem - entrada, 0)

    df = tabela_price(valor_fin, juros, prazo_fin) if sistema == "PRICE" else tabela_sac(valor_fin, juros, prazo_fin)

    with c2:
        st.metric("Valor financiado", f"R$ {valor_fin:,.2f}")
        if not df.empty:
            st.metric("Primeira parcela", f"R$ {df.iloc[0]['Prestação']:,.2f}")
            st.metric("Total pago", f"R$ {df['Prestação'].sum():,.2f}")
            st.line_chart(df.set_index("Parcela")[["Saldo"]])

# =========================
# COMPARATIVO
# =========================
with tab_comp:
    st.header("📊 Consórcio × Financiamento")

    total_fin = df['Prestação'].sum() if not df.empty else 0

    st.markdown(f"""
    ### Comparativo financeiro

    **Consórcio**
    - Crédito líquido: R$ {res['Crédito Líquido']:,.2f}
    - Parcela média: R$ {res['Parcela Pós']:,.2f}

    **Financiamento**
    - Total pago: R$ {total_fin:,.2f}
    - Parcela inicial: R$ {df.iloc[0]['Prestação']:,.2f if not df.empty else 0}

    👉 **Regra prática**:  
    Consórcio favorece planejamento e custo total menor.  
    Financiamento favorece urgência.
    """)

# =========================
# DIDÁTICA
# =========================
with tab_did:
    st.markdown("""
### 🤝 Consórcio
- Categoria = crédito + taxas  
- Lance embutido reduz o crédito  
- Redutor atua apenas antes da contemplação  

### 🏦 Financiamento
- PRICE: parcela fixa  
- SAC: parcela decrescente  
- Entrada reduz juros totais  

### 📊 Comparativo
- Custo total  
- Fluxo de caixa  
- Estratégia ideal depende do perfil
""")

# =========================
# RODAPÉ
# =========================
st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking 2026</center>",
    unsafe_allow_html=True
)














