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
# FUNÇÕES
# =========================
def calcular_consorcio(
    credito, prazo, taxa_adm, fundo_reserva, meses_contemplacao,
    lance_embutido_pct, lance_fixo_pct, recurso_proprio,
    redutor_pct, administradora
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    categoria = credito * (1 + taxa_total)

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor_pct / 100)
    parcela_pos = parcela_base

    if administradora == "Porto":
        base_rep = categoria
    else:
        base_rep = credito

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_fixo = base_rep * (lance_fixo_pct / 100)
    lance_livre = recurso_proprio

    lance_total = lance_embutido + lance_fixo + lance_livre
    representatividade = (lance_total / base_rep) * 100 if base_rep > 0 else 0

    return {
        "Crédito": credito,
        "Categoria": categoria,
        "Parcela Pós": parcela_pos,
        "Lance Total": lance_total,
        "Representatividade": representatividade,
        "Taxa Efetiva": taxa_total,
        "Custo Total": categoria
    }

def faixa_contemplacao(rep):
    if rep < 10:
        return "🔴 Muito baixa"
    elif rep < 20:
        return "🟠 Baixa"
    elif rep < 30:
        return "🟡 Média"
    elif rep < 40:
        return "🟢 Alta"
    else:
        return "🟢🟢 Muito alta"

def ranking_estimado(rep, total=100):
    pos = int(total - (rep / 100) * total)
    return max(1, pos)

# =========================
# INTERFACE
# =========================
st.title("💎 Intelligence Banking – Simulador Profissional")

tabs = st.tabs([
    "🤝 Consórcio",
    "🎯 Faixa de Contemplação",
    "📊 Ranking do Grupo",
    "🧠 Lance Ideal",
    "📄 Proposta"
])

# =========================
# CONSÓRCIO
# =========================
with tabs[0]:
    c1, c2 = st.columns(2)

    with c1:
        credito = st.number_input("Crédito (R$)", 300000.0)
        prazo = st.number_input("Prazo (meses)", 180)
        taxa_adm = st.number_input("Taxa Administração (%)", 15.0)
        fundo = st.number_input("Fundo Reserva (%)", 2.0)
        meses = st.number_input("Meses até contemplação", 12)
        redutor = st.number_input("Redutor pré (%)", 0.0)
        recurso = st.number_input("Recurso próprio (R$)", 0.0)
        adm = st.selectbox("Administradora", ["CNP", "Itaú", "Porto"])
        le = st.number_input("Lance embutido (%)", 20.0)
        lf = st.number_input("Lance fixo (%)", 0.0)

    res = calcular_consorcio(
        credito, prazo, taxa_adm, fundo, meses,
        le, lf, recurso, redutor, adm
    )

    with c2:
        st.metric("Lance Total", f"R$ {res['Lance Total']:,.2f}")
        st.metric("Representatividade", f"{res['Representatividade']:.2f}%")
        st.metric("Parcela Pós", f"R$ {res['Parcela Pós']:,.2f}")
        st.metric("Taxa Efetiva", f"{res['Taxa Efetiva']*100:.2f}%")

# =========================
# FAIXA DE CONTEMPLAÇÃO
# =========================
with tabs[1]:
    faixa = faixa_contemplacao(res["Representatividade"])
    st.subheader("🎯 Faixa estimada de contemplação")
    st.success(f"Faixa atual: **{faixa}**")

# =========================
# RANKING DO GRUPO
# =========================
with tabs[2]:
    pos = ranking_estimado(res["Representatividade"])
    st.subheader("📊 Ranking estimado no grupo")
    st.metric("Posição aproximada", f"{pos}º de 100 participantes")

# =========================
# LANCE IDEAL
# =========================
with tabs[3]:
    st.subheader("🧠 Recomendação automática de lance")

    alvo_media = 25
    alvo_alta = 35

    base = res["Categoria"] if adm == "Porto" else credito
    lance_atual = res["Lance Total"]

    lance_media = base * alvo_media / 100
    lance_alta = base * alvo_alta / 100

    falta_media = max(0, lance_media - lance_atual)
    falta_alta = max(0, lance_alta - lance_atual)

    st.write(f"🔹 Para faixa **MÉDIA (≈25%)** → adicionar **R$ {falta_media:,.2f}**")
    st.write(f"🔹 Para faixa **ALTA (≈35%)** → adicionar **R$ {falta_alta:,.2f}**")

# =========================
# PROPOSTA
# =========================
with tabs[4]:
    texto = f"""
PROPOSTA INTELLIGENCE BANKING

Crédito: R$ {res['Crédito']:,.2f}
Lance Total: R$ {res['Lance Total']:,.2f}
Representatividade: {res['Representatividade']:.2f}%
Faixa de Contemplação: {faixa}

Parcela Pós: R$ {res['Parcela Pós']:,.2f}
Taxa Efetiva: {res['Taxa Efetiva']*100:.2f}%

Ranking Estimado: {pos}º de 100
"""
    st.download_button("⬇️ Baixar Proposta TXT", texto, "proposta_consorcio.txt")



























































