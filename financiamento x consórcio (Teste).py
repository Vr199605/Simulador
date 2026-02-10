import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Consórcio x Financiamento", layout="wide")

# ======================
# FUNÇÕES AUXILIARES
# ======================

def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def taxa_efetiva_consorcio(taxa_adm, fundo_reserva, prazo):
    custo_total = taxa_adm + fundo_reserva
    return (custo_total / prazo) * 12

def taxa_efetiva_financiamento(juros_anual):
    return juros_anual

def score_taxas(t_cons, t_fin):
    if t_cons < t_fin * 0.8:
        return "🟢 Consórcio muito vantajoso"
    elif t_cons < t_fin:
        return "🟡 Consórcio levemente melhor"
    elif t_cons == t_fin:
        return "⚖️ Empate técnico"
    else:
        return "🔴 Financiamento mais vantajoso"

# ======================
# TABS
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
    st.header("🏦 Simulação de Consórcio")

    administradora = st.selectbox("Administradora", ["CNP", "Itaú", "Porto"])

    grupo = None
    if administradora == "CNP":
        grupo = st.selectbox("Grupo", ["1021", "1053", "Demais Grupos"])

    credito = st.number_input("Crédito desejado", min_value=0.0, step=1000.0)
    prazo = st.number_input("Prazo (meses)", min_value=1)
    meses_contemplacao = st.number_input("Meses para contemplação", min_value=0)
    taxa_adm = st.number_input("Taxa de administração (%)", min_value=0.0)
    fundo_reserva = st.number_input("Fundo reserva (%)", min_value=0.0)
    redutor = st.number_input("Redutor na parcela pré (%)", min_value=0.0)

    categoria = credito * (1 + (taxa_adm + fundo_reserva) / 100)

    base_lance = "crédito"
    if administradora == "CNP" and grupo in ["1021", "1053"]:
        base_lance = "categoria"
    elif administradora == "Porto":
        base_lance = "categoria"

    base_valor = categoria if base_lance == "categoria" else credito

    lance_fixo = base_valor * 0.3
    lance_livre = base_valor * 0.2

    parcela_base = categoria / prazo
    parcela_pre = parcela_base * (1 - redutor / 100)
    parcela_pos = parcela_base

    credito_liquido = credito

    prob = min(90, 20 + (lance_fixo / base_valor) * 100)

    st.subheader("📌 Resultados")
    st.write("Crédito original:", formatar(credito))
    st.write("Crédito líquido (sem embutido):", formatar(credito_liquido))
    st.write("Parcela pré-contemplação:", formatar(parcela_pre))
    st.write("Parcela pós-contemplação:", formatar(parcela_pos))
    st.write("Lance fixo:", formatar(lance_fixo))
    st.write("Lance livre:", formatar(lance_livre))
    st.write(f"🎯 Probabilidade estimada de contemplação: **{prob:.0f}%**")

    taxa_cons = taxa_efetiva_consorcio(taxa_adm, fundo_reserva, prazo)

# ======================
# FINANCIAMENTO
# ======================
with tabs[1]:
    st.header("💰 Simulação de Financiamento")

    valor_bem = st.number_input("Valor do bem", min_value=0.0)
    entrada = st.number_input("Entrada", min_value=0.0)
    prazo_fin = st.number_input("Prazo (meses)", min_value=1)
    juros_anual = st.number_input("Juros anual (%)", min_value=0.0)
    sistema = st.selectbox("Sistema", ["PRICE", "SAC"])

    saldo = valor_bem - entrada
    juros_mensal = (juros_anual / 100) / 12

    if saldo > 0 and prazo_fin > 0:
        if sistema == "PRICE":
            parcela = saldo * (juros_mensal * (1 + juros_mensal)**prazo_fin) / ((1 + juros_mensal)**prazo_fin - 1)
        else:
            amort = saldo / prazo_fin
            parcela = amort + saldo * juros_mensal
    else:
        parcela = 0

    st.subheader("📌 Resultados")
    st.write("Saldo financiado:", formatar(saldo))
    st.write("Parcela inicial:", formatar(parcela))

    taxa_fin = taxa_efetiva_financiamento(juros_anual)

# ======================
# COMPARATIVO
# ======================
with tabs[2]:
    st.header("📊 Comparativo Inteligente")

    st.write("### Comparação de Taxas Efetivas")
    st.write("Taxa efetiva Consórcio:", f"{taxa_cons:.2f}% a.a")
    st.write("Taxa efetiva Financiamento:", f"{taxa_fin:.2f}% a.a")

    resultado = score_taxas(taxa_cons, taxa_fin)
    st.success(resultado)

    if taxa_cons < taxa_fin:
        st.write("✅ Até esta taxa, **Consórcio tende a ser melhor investimento**.")
    else:
        st.write("✅ A partir desta taxa, **Financiamento tende a ser melhor opção**.")

# ======================
# DIDÁTICA
# ======================
with tabs[3]:
    st.header("📘 Explicação Didática")

    st.markdown("""
### 🏦 Consórcio
- Não há juros, apenas taxas administrativas.
- O custo real é diluído no prazo.
- O redutor diminui apenas a parcela antes da contemplação.
- Lance pode ser sobre crédito ou categoria, conforme administradora.

### 💰 Financiamento
- Possui juros compostos.
- PRICE mantém parcela fixa.
- SAC reduz parcela ao longo do tempo.

### 📊 Comparativo
- Transformamos taxas em valores anuais equivalentes.
- Comparamos custo do dinheiro no tempo.
- Criamos um score simples e objetivo para decisão.
""")

# ======================
# PROPOSTA CLIENTE
# ======================
with tabs[4]:
    st.header("📄 Proposta para o Cliente")

    texto = f"""
PROPOSTA PERSONALIZADA

🔹 CONSÓRCIO
Crédito: {formatar(credito)}
Parcela pré: {formatar(parcela_pre)}
Parcela pós: {formatar(parcela_pos)}

🔹 FINANCIAMENTO
Parcela inicial: {formatar(parcela)}

🔹 CONCLUSÃO
{resultado}
"""

    st.text_area("Prévia da proposta", texto, height=300)

    st.download_button(
        "⬇️ Baixar proposta em TXT",
        texto,
        file_name="proposta_cliente.txt"
    )









































