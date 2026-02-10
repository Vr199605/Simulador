import streamlit as st

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="Intelligence Banking Pro",
    page_icon="💎",
    layout="wide"
)

# =========================
# CONSÓRCIO
# =========================
def calcular_consorcio(
    credito, prazo, taxa_adm, fundo_reserva, meses_contemplacao,
    lance_embutido_pct, lance_fixo_pct, recurso_proprio,
    redutor_pct, administradora, grupo
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    categoria = credito * (1 + taxa_total)

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor_pct / 100)
    parcela_pos = parcela_base

    saldo_atual = max(categoria - meses_contemplacao * parcela_pre, 0)

    # Base conforme administradora
    if administradora == "Porto":
        base_representatividade = categoria
    else:
        base_representatividade = credito

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_fixo = base_representatividade * (lance_fixo_pct / 100)
    lance_livre = recurso_proprio

    lance_total = lance_embutido + lance_fixo + lance_livre
    credito_liquido = credito - lance_embutido

    representatividade = (lance_total / base_representatividade) * 100 if base_representatividade > 0 else 0

    return {
        "Crédito": credito,
        "Crédito Líquido": credito_liquido,
        "Categoria": categoria,
        "Parcela Pré": parcela_pre,
        "Parcela Pós": parcela_pos,
        "Saldo": saldo_atual,
        "Lance Embutido": lance_embutido,
        "Lance Fixo": lance_fixo,
        "Lance Livre": lance_livre,
        "Lance Total": lance_total,
        "Representatividade": representatividade,
        "Taxa Efetiva": taxa_total,
        "Custo Total": categoria,
        "Base Representatividade": base_representatividade
    }

# =========================
# FINANCIAMENTO
# =========================
def tabela_price(valor, juros_anual, meses):
    i = juros_anual / 100 / 12
    pmt = valor * (i * (1 + i) ** meses) / ((1 + i) ** meses - 1)
    total = pmt * meses
    return pmt, pmt, total

def tabela_sac(valor, juros_anual, meses):
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

tabs = st.tabs([
    "🤝 Consórcio",
    "🏦 Financiamento",
    "📊 Comparativo",
    "📘 Didática",
    "🎯 Faixas de Contemplação",
    "📊 Ranking do Grupo",
    "🧠 Recomendação de Lance",
    "📄 Proposta"
])

tab_cons, tab_fin, tab_comp, tab_did, tab_fx, tab_rank, tab_lance, tab_prop = tabs

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    c1, c2 = st.columns(2)

    with c1:
        credito = st.number_input("Crédito (R$)", value=300000.0)
        prazo = st.number_input("Prazo (meses)", min_value=1, value=180)
        taxa_adm = st.number_input("Taxa Administração (%)", value=15.0)
        fundo = st.number_input("Fundo Reserva (%)", value=2.0)
        meses = st.number_input("Meses até contemplação", min_value=0, value=12)
        redutor = st.number_input("Redutor pré (%)", value=0.0)
        recurso = st.number_input("Recurso próprio (R$)", value=0.0)
        adm = st.selectbox("Administradora", ["CNP", "Itaú", "Porto"])
        grupo = st.selectbox("Grupo", ["1021", "1053", "Demais Grupos"]) if adm == "CNP" else "Demais Grupos"
        le = st.number_input("Lance embutido (%)", value=20.0)
        lf = st.number_input("Lance fixo (%)", value=0.0)

    res_c = calcular_consorcio(
        credito, prazo, taxa_adm, fundo, meses,
        le, lf, recurso, redutor, adm, grupo
    )

    with c2:
        for k, v in res_c.items():
            if k == "Taxa Efetiva":
                st.metric(k, f"{v*100:.2f}%")
            elif k == "Representatividade":
                st.metric(k, f"{v:.2f}%")
            elif isinstance(v, (int, float)):
                st.metric(k, f"R$ {v:,.2f}")

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    f1, f2 = st.columns(2)

    with f1:
        valor = st.number_input("Valor do bem", value=500000.0)
        entrada = st.number_input("Entrada", value=100000.0)
        prazo_f = st.number_input("Prazo (meses)", min_value=1, value=240)
        juros = st.number_input("Juros anual (%)", value=12.0)
        sistema = st.selectbox("Sistema", ["Price", "SAC"])

    financiado = max(valor - entrada, 0)

    if sistema == "Price":
        p_ini, p_fim, total_fin = tabela_price(financiado, juros, prazo_f)
    else:
        p_ini, p_fim, total_fin = tabela_sac(financiado, juros, prazo_f)

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
    vencedor_taxa = "CONSÓRCIO" if res_c["Taxa Efetiva"] < taxa_efetiva_fin else "FINANCIAMENTO"
    vencedor_parcela = "CONSÓRCIO" if res_c["Parcela Pós"] < p_ini else "FINANCIAMENTO"
    vencedor_custo = "CONSÓRCIO" if res_c["Custo Total"] < total_fin else "FINANCIAMENTO"

    st.subheader("📊 Resultado Comparativo")
    st.write(f"🔹 Melhor por taxa: **{vencedor_taxa}**")
    st.write(f"🔹 Melhor por parcela: **{vencedor_parcela}**")
    st.write(f"🔹 Melhor por custo total: **{vencedor_custo}**")

# =========================
# DIDÁTICA
# =========================
with tab_did:
    st.markdown("""
### 📘 Representatividade do Lance
- Resultado automático
- Mede competitividade no grupo
- Base varia por administradora
- Fundamental para estratégia
""")

# =========================
# FAIXA DE CONTEMPLAÇÃO
# =========================
with tab_fx:
    rep = res_c["Representatividade"]
    if rep < 10:
        faixa = "🔴 Muito baixa"
    elif rep < 20:
        faixa = "🟠 Baixa"
    elif rep < 30:
        faixa = "🟡 Média"
    elif rep < 40:
        faixa = "🟢 Alta"
    else:
        faixa = "🟢🟢 Muito alta"

    st.metric("Faixa estimada", faixa)

# =========================
# RANKING DO GRUPO
# =========================
with tab_rank:
    posicao = max(1, int(100 - rep))
    st.metric("Posição estimada no grupo", f"{posicao}º de 100")

# =========================
# RECOMENDAÇÃO DE LANCE
# =========================
with tab_lance:
    base = res_c["Base Representatividade"]
    alvo_media = base * 0.25
    alvo_alta = base * 0.35

    falta_media = max(0, alvo_media - res_c["Lance Total"])
    falta_alta = max(0, alvo_alta - res_c["Lance Total"])

    st.write(f"📌 Para **faixa MÉDIA** → adicionar **R$ {falta_media:,.2f}**")
    st.write(f"📌 Para **faixa ALTA** → adicionar **R$ {falta_alta:,.2f}**")

# =========================
# PROPOSTA
# =========================
with tab_prop:
    texto = f"""
PROPOSTA INTELLIGENCE BANKING

Crédito: R$ {res_c['Crédito']:,.2f}
Lance Total: R$ {res_c['Lance Total']:,.2f}
Representatividade: {res_c['Representatividade']:.2f}%
Parcela Pós: R$ {res_c['Parcela Pós']:,.2f}
Taxa Efetiva Consórcio: {res_c['Taxa Efetiva']*100:.2f}%

Financiamento:
Parcela Inicial: R$ {p_ini:,.2f}
Parcela Final: R$ {p_fim:,.2f}
Taxa Efetiva: {taxa_efetiva_fin*100:.2f}%
"""
    st.download_button("⬇️ Baixar Proposta TXT", texto, "proposta_completa.txt")





























































