import streamlit as st
import numpy as np

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="Intelligence Banking Pro",
    page_icon="💎",
    layout="wide"
)

# =========================
# FUNÇÕES AUXILIARES
# =========================

def score_taxa(taxa_cons, taxa_fin):
    if taxa_cons < taxa_fin:
        return "CONSÓRCIO"
    elif taxa_fin < taxa_cons:
        return "FINANCIAMENTO"
    else:
        return "EMPATE"


# =========================
# CONSÓRCIO
# =========================
def calcular_consorcio(
    credito, prazo, taxa_adm, fundo_reserva, meses_contemplacao,
    lance_embutido_pct, lance_livre_pct, lance_fixo_pct,
    redutor_pct, administradora, grupo, recurso_proprio
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    categoria = credito * (1 + taxa_total)

    parcela_base = categoria / prazo if prazo > 0 else 0
    parcela_pre = parcela_base * (1 - redutor_pct / 100)
    parcela_pos = parcela_base

    saldo_atual = max(categoria - meses_contemplacao * parcela_pre, 0)

    if administradora == "CNP":
        if grupo in ["1021", "1053"]:
            base_fixo, base_livre = categoria, credito
        else:
            base_fixo = base_livre = credito
    elif administradora == "Porto":
        base_fixo = base_livre = categoria
    else:
        base_fixo = base_livre = credito

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_fixo = base_fixo * (lance_fixo_pct / 100)
    lance_livre = base_livre * (lance_livre_pct / 100)

    lance_total = lance_embutido + lance_fixo + lance_livre + recurso_proprio
    credito_liquido = credito - lance_embutido

    return {
        "Crédito": credito,
        "Crédito Líquido": credito_liquido,
        "Categoria": categoria,
        "Parcela Pré": parcela_pre,
        "Parcela Pós": parcela_pos,
        "Saldo": saldo_atual,
        "Lance Total": lance_total,
        "Taxa Efetiva": taxa_total,
        "Custo Total": categoria
    }


# =========================
# FINANCIAMENTO
# =========================
def tabela_price(valor, juros_anual, meses):
    if valor <= 0 or meses <= 0 or juros_anual <= 0:
        return 0, 0, 0
    i = juros_anual / 100 / 12
    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    total = pmt * meses
    return pmt, pmt, total


def tabela_sac(valor, juros_anual, meses):
    if valor <= 0 or meses <= 0 or juros_anual <= 0:
        return 0, 0, 0
    i = juros_anual / 100 / 12
    amort = valor / meses
    saldo = valor
    parcelas = []
    for _ in range(meses):
        parcelas.append(amort + saldo * i)
        saldo -= amort
    return parcelas[0], parcelas[-1], sum(parcelas)


# =========================
# INTERFACE
# =========================
st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_comp, tab_did = st.tabs(
    ["🤝 Consórcio", "🏦 Financiamento", "📊 Comparativo", "📘 Didática"]
)

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    c1, c2 = st.columns(2)

    with c1:
        credito = st.number_input("Crédito (R$)", value=300000.0, key="cred")
        prazo = st.number_input("Prazo (meses)", min_value=1, value=180, key="prazo_c")
        taxa_adm = st.number_input("Taxa Administração (%)", value=15.0, key="taxa")
        fundo = st.number_input("Fundo Reserva (%)", value=2.0, key="fundo")
        meses = st.number_input("Meses até contemplação", min_value=0, value=12, key="meses")
        redutor = st.number_input("Redutor pré (%)", value=0.0, key="red")
        recurso_proprio = st.number_input("Recurso próprio (R$)", value=0.0, key="rp")

        adm = st.selectbox("Administradora", ["CNP", "Itaú", "Porto"], key="adm")
        grupo = st.selectbox("Grupo", ["1021", "1053", "Demais Grupos"], key="grupo") if adm == "CNP" else "Demais Grupos"

        le = st.number_input("Lance embutido (%)", value=20.0, key="le")
        lf = st.number_input("Lance fixo (%)", value=0.0, key="lf")
        ll = st.number_input("Lance livre (%)", value=5.0, key="ll")

    res_c = calcular_consorcio(
        credito, prazo, taxa_adm, fundo, meses,
        le, ll, lf, redutor, adm, grupo, recurso_proprio
    )

    with c2:
        for k, v in res_c.items():
            if "Taxa" in k:
                st.metric(k, f"{v*100:.2f}%")
            else:
                st.metric(k, f"R$ {v:,.2f}")

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    f1, f2 = st.columns(2)

    with f1:
        valor = st.number_input("Valor do bem", value=500000.0, key="valor")
        entrada = st.number_input("Entrada", value=100000.0, key="entrada")
        prazo_f = st.number_input("Prazo (meses)", min_value=1, value=240, key="prazo_f")
        juros = st.number_input("Juros anual (%)", value=12.0, key="juros")
        sistema = st.selectbox("Sistema", ["Price", "SAC"], key="sist")

    financiado = max(valor - entrada, 0)

    p_ini, p_fim, total_fin = (
        tabela_price(financiado, juros, prazo_f)
        if sistema == "Price"
        else tabela_sac(financiado, juros, prazo_f)
    )

    taxa_efetiva_fin = (total_fin / financiado - 1) if financiado > 0 else 0

    with f2:
        st.metric("Valor financiado", f"R$ {financiado:,.2f}")
        st.metric("Parcela inicial", f"R$ {p_ini:,.2f}")
        st.metric("Parcela final", f"R$ {p_fim:,.2f}")
        st.metric("Total pago", f"R$ {total_fin:,.2f}")
        st.metric("Taxa efetiva", f"{taxa_efetiva_fin*100:.2f}%")

# =========================
# COMPARATIVO
# =========================
with tab_comp:
    st.subheader("📊 Comparativo por Cenários")

    vencedor_taxa = score_taxa(res_c["Taxa Efetiva"], taxa_efetiva_fin)
    vencedor_parcela = "CONSÓRCIO" if res_c["Parcela Pós"] < p_ini else "FINANCIAMENTO"
    vencedor_custo = "CONSÓRCIO" if res_c["Custo Total"] < total_fin else "FINANCIAMENTO"

    st.metric("🔢 Melhor por Taxa", vencedor_taxa)
    st.metric("💸 Melhor por Parcela", vencedor_parcela)
    st.metric("🏁 Melhor por Custo Total", vencedor_custo)

# =========================
# DIDÁTICA
# =========================
with tab_did:
    st.markdown("""
### 📘 Como ler os cenários

**Taxa efetiva**
- Mede o custo percentual do dinheiro

**Parcela**
- Impacto no fluxo mensal

**Custo total**
- Quanto dinheiro sai do bolso no final

👉 Cada cenário responde uma pergunta diferente.
""")

















































