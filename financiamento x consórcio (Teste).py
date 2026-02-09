import streamlit as st
import pandas as pd

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

    parcela_padrao = categoria / prazo
    parcela_pre = parcela_padrao * (1 - redutor_pct / 100)

    saldo_atual = categoria - (parcelas_pagas * parcela_pre)
    saldo_atual = max(saldo_atual, 0)

    lance_embutido = credito * (lance_embutido_pct / 100)
    lance_livre = categoria * (lance_livre_pct / 100)
    lance_fixo = categoria * (lance_fixo_pct / 100)

    lance_total = lance_embutido + lance_livre + lance_fixo
    credito_liquido = credito - lance_embutido

    saldos = []
    saldo_tmp = categoria
    for _ in range(prazo):
        saldo_tmp -= parcela_padrao
        saldos.append(max(saldo_tmp, 0))

    df_saldo = pd.DataFrame({
        "Parcela": range(1, prazo + 1),
        "Saldo Devedor": saldos
    })

    return {
        "Categoria": categoria,
        "Parcela Padrão": parcela_padrao,
        "Parcela Pré": parcela_pre,
        "Saldo Atual": saldo_atual,
        "Lance Total": lance_total,
        "Crédito Líquido": credito_liquido,
        "DataFrame": df_saldo
    }


def calcular_financiamento(valor, juros_anual, prazo, modelo):
    taxa_mensal = (1 + juros_anual) ** (1 / 12) - 1
    saldo = valor
    parcelas = []

    if modelo == "SAC":
        amortizacao = valor / prazo
        for _ in range(prazo):
            juros = saldo * taxa_mensal
            parcela = amortizacao + juros
            parcelas.append(parcela)
            saldo -= amortizacao
    else:  # PRICE
        if taxa_mensal == 0:
            parcela_fixa = valor / prazo
        else:
            parcela_fixa = valor * (taxa_mensal * (1 + taxa_mensal) ** prazo) / ((1 + taxa_mensal) ** prazo - 1)

        for _ in range(prazo):
            juros = saldo * taxa_mensal
            amortizacao = parcela_fixa - juros
            parcelas.append(parcela_fixa)
            saldo -= amortizacao

    return parcelas[0], parcelas[-1], sum(parcelas)


def score_simples(total_pago, prazo, parcela):
    score = 100
    score -= total_pago / 150000
    score -= parcela / 2500
    score -= prazo / 15
    return max(0, round(score, 1))

# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_cons, tab_fin, tab_comp = st.tabs(
    ["🤝 Consórcio", "🏦 Financiamento", "🔄 Comparação"]
)

# =========================
# CONSÓRCIO
# =========================
with tab_cons:
    st.header("Simulador de Consórcio")

    c1, c2 = st.columns([1, 2])

    with c1:
        credito = st.number_input("Crédito contratado (R$)", 50000.0, 3000000.0, 300000.0, key="cred")
        prazo_c = st.number_input("Prazo (meses)", 60, 240, 180, step=12, key="prazo_c")

        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0, key="adm")
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0, key="fr")

        parcelas_pagas = st.number_input(
            "Parcelas pagas pré-contemplação",
            0, prazo_c, 0, key="pp"
        )

        st.subheader("🎯 Lances")
        lance_embutido_pct = st.number_input("Lance Embutido (% crédito)", 0.0, 100.0, 20.0, key="le")
        lance_livre_pct = st.number_input("Lance Livre (% categoria)", 0.0, 100.0, 5.0, key="ll")
        lance_fixo_pct = st.number_input("Lance Fixo (% categoria)", 0.0, 100.0, 0.0, key="lf")

        redutor_pct = st.number_input("Redutor parcela pré (%)", 0.0, 50.0, 0.0, key="red")

    res_c = calcular_consorcio(
        credito, prazo_c, taxa_adm, fundo_reserva,
        parcelas_pagas, lance_embutido_pct,
        lance_livre_pct, lance_fixo_pct, redutor_pct
    )

    with c2:
        st.markdown(f"""
        **Categoria:** R$ {res_c['Categoria']:,.2f}  
        **Parcela padrão:** R$ {res_c['Parcela Padrão']:,.2f}  
        **Parcela pré:** R$ {res_c['Parcela Pré']:,.2f}  
        **Saldo atual:** R$ {res_c['Saldo Atual']:,.2f}  
        **Lance total:** R$ {res_c['Lance Total']:,.2f}  
        **Crédito líquido:** R$ {res_c['Crédito Líquido']:,.2f}
        """)

        st.subheader("📉 Saldo Devedor")
        st.line_chart(res_c["DataFrame"].set_index("Parcela"))

# =========================
# FINANCIAMENTO
# =========================
with tab_fin:
    st.header("Simulador de Financiamento")

    f1, f2 = st.columns([1, 2])

    with f1:
        valor_bem = st.number_input("Valor do bem (R$)", 100000.0, 5000000.0, 500000.0, key="vb")
        entrada = st.number_input("Entrada (R$)", 0.0, valor_bem * 0.9, valor_bem * 0.2, key="ent")
        prazo_f = st.number_input("Prazo (meses)", 12, 420, 240, step=12, key="pf")

        juros_anual = st.number_input("Juros anual (%)", 0.0, 30.0, 12.0, key="ja") / 100
        modelo = st.selectbox("Sistema", ["Price", "SAC"], key="mod")

    valor_fin = valor_bem - entrada

    p_ini, p_fim, total_pago_fin = calcular_financiamento(
        valor_fin, juros_anual, prazo_f, modelo
    )

    with f2:
        st.markdown(f"""
        **Valor financiado:** R$ {valor_fin:,.2f}  
        **Parcela inicial:** R$ {p_ini:,.2f}  
        **Parcela final:** R$ {p_fim:,.2f}  
        **Total pago:** R$ {total_pago_fin:,.2f}
        """)

# =========================
# COMPARAÇÃO
# =========================
with tab_comp:
    st.header("🔄 Comparação Inteligente")

    score_cons = score_simples(res_c["Categoria"], prazo_c, res_c["Parcela Pré"])
    score_fin = score_simples(total_pago_fin, prazo_f, p_ini)

    st.metric("Score Consórcio", score_cons)
    st.metric("Score Financiamento", score_fin)

    if score_cons > score_fin:
        st.success("🎯 Estratégia recomendada: CONSÓRCIO")
    else:
        st.success("🎯 Estratégia recomendada: FINANCIAMENTO")

# =========================
# RODAPÉ
# =========================
st.markdown(
    "<center>Desenvolvido por Victor • Intelligence Banking 2026</center>",
    unsafe_allow_html=True
)








