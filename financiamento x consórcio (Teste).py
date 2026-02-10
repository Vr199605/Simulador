import streamlit as st
import numpy as np

st.set_page_config(page_title="Consórcio x Financiamento", layout="wide")

# ======================
# FUNÇÕES
# ======================

def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def taxa_efetiva_consorcio(taxa_adm, fundo_reserva, prazo):
    if prazo <= 0:
        return 0
    return ((taxa_adm + fundo_reserva) / prazo) * 12

def score_taxas(t_cons, t_fin):
    if t_cons == 0 or t_fin == 0:
        return "⚠️ Preencha todos os dados"
    if t_cons < t_fin * 0.8:
        return "🟢 Consórcio muito vantajoso"
    elif t_cons < t_fin:
        return "🟡 Consórcio levemente melhor"
    else:
        return "🔴 Financiamento mais vantajoso"

# ======================
# ABAS
# ======================

tabs = st.tabs([
    "🏦 Consórcio",
    "💰 Financiamento",
    "📊 Comparativo",
    "📘 Didática",
    "📄 Proposta Cliente"
])

# ======================
# CONSÓRCIO
# ======================
with tabs[0]:
    st.header("🏦 Consórcio")

    administradora = st.selectbox(
        "Administradora",
        ["CNP", "Itaú", "Porto"],
        key="adm_cons"
    )

    grupo = None
    if administradora == "CNP":
        grupo = st.selectbox(
            "Grupo",
            ["1021", "1053", "Demais Grupos"],
            key="grupo_cnp"
        )

    credito = st.number_input(
        "Crédito desejado",
        min_value=0.0,
        step=1000.0,
        key="credito_cons"
    )

    prazo = st.number_input(
        "Prazo (meses)",
        min_value=1,
        key="prazo_cons"
    )

    meses_contemplacao = st.number_input(
        "Meses para contemplação",
        min_value=0,
        key="meses_cont"
    )

    taxa_adm = st.number_input(
        "Taxa de administração (%)",
        min_value=0.0,
        key="taxa_adm"
    )

    fundo_reserva = st.number_input(
        "Fundo reserva (%)",
        min_value=0.0,
        key="fundo_res"
    )

    redutor = st.number_input(
        "Redutor pré-contemplação (%)",
        min_value=0.0,
        key="redutor"
    )

    categoria = credito * (1 + (taxa_adm + fundo_reserva) / 100)

    # regras de lance
    base_lance = "crédito"
    if administradora == "CNP" and grupo in ["1021", "1053"]:
        base_lance = "categoria"
    elif administradora == "Porto":
        base_lance = "categoria"

    base_valor = categoria if base_lance == "categoria" else credito

    lance_fixo = base_valor * 0.3
    lance_livre = base_valor * 0.2

    parcela_base = categoria / prazo if prazo > 0 else 0
    parcela_pre = parcela_base * (1 - redutor / 100)
    parcela_pos = parcela_base

    if base_valor > 0:
        prob = min(90, 20 + (lance_fixo / base_valor) * 100)
    else:
        prob = 0

    taxa_cons = taxa_efetiva_consorcio(taxa_adm, fundo_reserva, prazo)

    st.subheader("📌 Resultado")
    st.write("Crédito:", formatar(credito))
    st.write("Crédito líquido:", formatar(credito))
    st.write("Parcela pré:", formatar(parcela_pre))
    st.write("Parcela pós:", formatar(parcela_pos))
    st.write("Lance fixo:", formatar(lance_fixo))
    st.write("Lance livre:", formatar(lance_livre))
    st.write(f"🎯 Probabilidade estimada: **{prob:.0f}%**")

# ======================
# FINANCIAMENTO
# ======================
with tabs[1]:
    st.header("💰 Financiamento")

    valor_bem = st.number_input(
        "Valor do bem",
        min_value=0.0,
        key="valor_bem"
    )

    entrada = st.number_input(
        "Entrada",
        min_value=0.0,
        key="entrada"
    )

    prazo_fin = st.number_input(
        "Prazo (meses)",
        min_value=1,
        key="prazo_fin"
    )

    juros_anual = st.number_input(
        "Juros anual (%)",
        min_value=0.0,
        key="juros_anual"
    )

    sistema = st.selectbox(
        "Sistema",
        ["PRICE", "SAC"],
        key="sistema"
    )

    saldo = valor_bem - entrada
    juros_mensal = (juros_anual / 100) / 12 if juros_anual > 0 else 0

    if saldo > 0 and prazo_fin > 0:
        if sistema == "PRICE" and juros_mensal > 0:
            parcela = saldo * (juros_mensal * (1 + juros_mensal) ** prazo_fin) / ((1 + juros_mensal) ** prazo_fin - 1)
        else:
            parcela = (saldo / prazo_fin) + saldo * juros_mensal
    else:
        parcela = 0

    taxa_fin = juros_anual

    st.subheader("📌 Resultado")
    st.write("Saldo financiado:", formatar(saldo))
    st.write("Parcela inicial:", formatar(parcela))

# ======================
# COMPARATIVO
# ======================
with tabs[2]:
    st.header("📊 Comparativo por Taxas")

    st.write("Taxa efetiva Consórcio:", f"{taxa_cons:.2f}% a.a")
    st.write("Taxa efetiva Financiamento:", f"{taxa_fin:.2f}% a.a")

    resultado = score_taxas(taxa_cons, taxa_fin)
    st.success(resultado)

# ======================
# DIDÁTICA
# ======================
with tabs[3]:
    st.header("📘 Didática")

    st.markdown("""
**Consórcio**
- Não possui juros
- Custo vem das taxas
- Redutor só afeta parcela pré

**Financiamento**
- Juros compostos
- PRICE = fixa
- SAC = decrescente

**Comparativo**
- Avalia custo do dinheiro no tempo
""")

# ======================
# PROPOSTA
# ======================
with tabs[4]:
    st.header("📄 Proposta Cliente")

    texto = f"""
PROPOSTA PERSONALIZADA

CONSÓRCIO
Crédito: {formatar(credito)}
Parcela pré: {formatar(parcela_pre)}
Parcela pós: {formatar(parcela_pos)}

FINANCIAMENTO
Parcela inicial: {formatar(parcela)}

CONCLUSÃO
{resultado}
"""

    st.text_area("Proposta", texto, height=300)
    st.download_button("⬇️ Baixar TXT", texto, "proposta_cliente.txt")













































