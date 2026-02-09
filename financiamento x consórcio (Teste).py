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
    i = (1 + juros_anual / 100) ** (1/12) - 1
    if i == 0:
        parcela = valor / meses
        saldo = valor
        dados = []
        for m in range(1, meses + 1):
            saldo -= parcela
            dados.append([m, parcela, parcela, 0, max(saldo, 0)])
        return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Amortização", "Juros", "Saldo"])

    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        amort = pmt - juros
        saldo -= amort
        dados.append([m, pmt, amort, juros, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Amortização", "Juros", "Saldo"])


def tabela_sac(valor, juros_anual, meses):
    i = (1 + juros_anual / 100) ** (1/12) - 1
    amort = valor / meses
    saldo = valor
    dados = []

    for m in range(1, meses + 1):
        juros = saldo * i
        prest = amort + juros
        saldo -= amort
        dados.append([m, prest, amort, juros, max(saldo, 0)])

    return pd.DataFrame(dados, columns=["Parcela", "Prestação", "Amortização", "Juros", "Saldo"])


def calcular_consorcio(
    credito, prazo, taxa_adm, fundo_reserva,
    parcelas_pagas, lance_emb_pct,
    lance_livre_pct, lance_fixo_pct,
    redutor_pct
):
    taxa_total = taxa_adm + fundo_reserva
    categoria = credito * (1 + taxa_total / 100)

    parcela_cheia = categoria / prazo
    parcela_pre = parcela_cheia * (1 - redutor_pct / 100)
    parcela_pos = parcela_cheia

    saldo_atual = max(categoria - parcelas_pagas * parcela_pre, 0)

    lance_emb = credito * (lance_emb_pct / 100)
    lance_livre = categoria * (lance_livre_pct / 100)
    lance_fixo = categoria * (lance_fixo_pct / 100)

    lance_total = lance_emb + lance_livre + lance_fixo

    credito_liquido = credito - lance_emb

    return {
        "Categoria": categoria,
        "ParcelaPre": parcela_pre,
        "ParcelaPos": parcela_pos,
        "Saldo": saldo_atual,
        "Lance": lance_total,
        "CreditoLiquido": credito_liquido
    }


def score_contemplacao(lance_pct, parcelas_pagas, prazo):
    score = (lance_pct * 0.7) + ((parcelas_pagas / prazo) * 100 * 0.3)
    return min(score, 100)


# =========================
# TÍTULO
# =========================
st.title("💎 Intelligence Banking Pro — Simulador Profissional")

tabs = st.tabs([
    "🤝 Consórcio",
    "🏦 Financiamento",
    "📊 Comparativo",
    "📘 Didática",
    "📄 Apresentação"
])

# =========================
# CONSÓRCIO
# =========================
with tabs[0]:
    st.header("Simulação de Consórcio")

    c1, c2 = st.columns(2)

    with c1:
        credito = st.number_input("Crédito contratado (R$)", 50000.0, 3000000.0, 300000.0)
        prazo = st.number_input("Prazo (meses)", 60, 240, 180)

        taxa_adm = st.number_input("Taxa de Administração (%)", 0.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        parcelas_pagas = st.number_input("Parcelas pagas pré-contemplação", 0, prazo, 0)

        st.subheader("🎯 Lances")
        lance_emb = st.number_input("Lance Embutido (%)", 0.0, 100.0, 20.0)
        lance_livre = st.number_input("Lance Livre (% da categoria)", 0.0, 100.0, 5.0)
        lance_fixo = st.number_input("Lance Fixo (% da categoria)", 0.0, 100.0, 0.0)

        redutor = st.number_input("Redutor sobre parcela pré (%)", 0.0, 50.0, 0.0)

    cons = calcular_consorcio(
        credito, prazo, taxa_adm, fundo_reserva,
        parcelas_pagas, lance_emb,
        lance_livre, lance_fixo, redutor
    )

    score = score_contemplacao(lance_emb + lance_livre + lance_fixo, parcelas_pagas, prazo)

    with c2:
        st.metric("Categoria", f"R$ {cons['Categoria']:,.2f}")
        st.metric("Parcela pré-contemplação", f"R$ {cons['ParcelaPre']:,.2f}")
        st.metric("Parcela pós-contemplação", f"R$ {cons['ParcelaPos']:,.2f}")
        st.metric("Crédito Líquido", f"R$ {cons['CreditoLiquido']:,.2f}")
        st.metric("Lance Total", f"R$ {cons['Lance']:,.2f}")
        st.progress(score / 100)
        st.caption(f"🎯 Probabilidade estimada de contemplação: **{score:.1f}%**")

# =========================
# FINANCIAMENTO
# =========================
with tabs[1]:
    st.header("Simulação de Financiamento")

    f1, f2 = st.columns(2)

    with f1:
        valor_bem = st.number_input("Valor do bem (R$)", 50000.0, 5000000.0, 500000.0)
        entrada = st.number_input("Entrada (R$)", 0.0, valor_bem, 100000.0)
        valor_fin = valor_bem - entrada

        juros_anual = st.number_input("Juros anual (%)", 0.0, 20.0, 10.0)
        prazo_fin = st.number_input("Prazo (meses)", 60, 420, 360)
        sistema = st.selectbox("Sistema", ["PRICE", "SAC"])

    df_fin = tabela_price(valor_fin, juros_anual, prazo_fin) if sistema == "PRICE" else tabela_sac(valor_fin, juros_anual, prazo_fin)

    with f2:
        st.metric("Valor financiado", f"R$ {valor_fin:,.2f}")
        st.metric("Parcela inicial", f"R$ {df_fin.iloc[0]['Prestação']:,.2f}")
        st.metric("Total de juros", f"R$ {df_fin['Juros'].sum():,.2f}")

# =========================
# COMPARATIVO
# =========================
with tabs[2]:
    st.header("📊 Comparativo Consórcio x Financiamento")

    comp = pd.DataFrame({
        "Modalidade": ["Consórcio", "Financiamento"],
        "Custo Total": [
            cons["Categoria"],
            df_fin["Prestação"].sum()
        ]
    }).set_index("Modalidade")

    st.bar_chart(comp)

# =========================
# DIDÁTICA
# =========================
with tabs[3]:
    st.header("📘 Explicação dos Cálculos")

    st.markdown("""
### 🔹 Consórcio
- **Categoria** = Crédito + taxas  
- **Parcela pré** = parcela cheia − redutor  
- **Parcela pós** = parcela cheia  
- **Crédito líquido** = crédito − lance embutido  

### 🔹 Financiamento
- **PRICE**: parcela fixa  
- **SAC**: parcela decrescente  
- Juros anual convertido para mensal  

### 🔹 Score
- Lance (70%)
- Tempo no grupo (30%)
""")

# =========================
# APRESENTAÇÃO
# =========================
with tabs[4]:
    st.header("📄 Proposta para o Cliente")

    proposta = f"""
PROPOSTA FINANCEIRA — INTELLIGENCE BANKING

CONSÓRCIO
Crédito contratado: R$ {credito:,.2f}
Categoria: R$ {cons['Categoria']:,.2f}
Parcela pré: R$ {cons['ParcelaPre']:,.2f}
Parcela pós: R$ {cons['ParcelaPos']:,.2f}
Crédito líquido: R$ {cons['CreditoLiquido']:,.2f}
Probabilidade de contemplação: {score:.1f}%

FINANCIAMENTO
Valor do bem: R$ {valor_bem:,.2f}
Entrada: R$ {entrada:,.2f}
Valor financiado: R$ {valor_fin:,.2f}
Sistema: {sistema}
Parcela inicial: R$ {df_fin.iloc[0]['Prestação']:,.2f}
Total de juros: R$ {df_fin['Juros'].sum():,.2f}
"""

    st.text_area("Prévia da proposta", proposta, height=300)

    st.download_button(
        "📥 Baixar proposta TXT",
        proposta,
        file_name="proposta_intelligence_banking.txt"
    )

# =========================
# RODAPÉ
# =========================
st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking Pro</center>",
    unsafe_allow_html=True
)
























