import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="Avaliação de Modelos", layout="centered")

CSV_PATH = "respostas.csv"

# -----------------------------
# Dados simulando arquivo externo
# -----------------------------
perguntas = {
    "Pergunta 1": [
        {"texto": "Resposta A", "modelo": "Modelo A", "latencia": 120},
        {"texto": "Resposta B", "modelo": "Modelo B", "latencia": 95},
        {"texto": "Resposta C", "modelo": "Modelo C", "latencia": 140},
    ],
    "Pergunta 2": [
        {"texto": "Resposta D", "modelo": "Modelo A", "latencia": 110},
        {"texto": "Resposta E", "modelo": "Modelo B", "latencia": 105},
        {"texto": "Resposta F", "modelo": "Modelo C", "latencia": 130},
    ],
    "Pergunta 3": [
        {"texto": "Resposta G", "modelo": "Modelo A", "latencia": 90},
        {"texto": "Resposta H", "modelo": "Modelo B", "latencia": 100},
        {"texto": "Resposta I", "modelo": "Modelo C", "latencia": 115},
    ],
    "Pergunta 4": [
        {"texto": "Resposta J", "modelo": "Modelo A", "latencia": 125},
        {"texto": "Resposta K", "modelo": "Modelo B", "latencia": 98},
        {"texto": "Resposta L", "modelo": "Modelo C", "latencia": 135},
    ],
    "Pergunta 5": [
        {"texto": "Resposta M", "modelo": "Modelo A", "latencia": 102},
        {"texto": "Resposta N", "modelo": "Modelo B", "latencia": 97},
        {"texto": "Resposta O", "modelo": "Modelo C", "latencia": 108},
    ],
}

# -----------------------------
# Estado
# -----------------------------
if "respostas" not in st.session_state:
    st.session_state.respostas = {}

if "ordem" not in st.session_state:
    st.session_state.ordem = {}

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

# -----------------------------
# Salvar CSV
# -----------------------------
def salvar_csv():
    linhas = []

    for pergunta, lista_respostas in st.session_state.respostas.items():
        for item in lista_respostas:
            linhas.append({
                "pergunta": pergunta,
                "modelo": item["modelo"],
                "resposta": item["texto"],
                "valor": item["valor"],
                "latencia": item["latencia"]
            })

    df = pd.DataFrame(linhas)
    df.to_csv(CSV_PATH, index=False)

# -----------------------------
# Abas
# -----------------------------
aba1, aba2 = st.tabs(["📝 Coleta", "📊 Resultados"])

# ==================================================
# ABA 1 - COLETA
# ==================================================
with aba1:

    st.title("📊 Avaliação de Perguntas")

    # -----------------------------
    # RESET
    # -----------------------------
    col1, col2 = st.columns([6, 1])

    with col2:
        if st.button("🔄 Reset"):
            st.session_state.confirm_reset = True

    if st.session_state.confirm_reset:
        st.warning("Tem certeza que deseja apagar todas as respostas?")

        col_confirm, col_cancel = st.columns(2)

        with col_confirm:
            if st.button("✅ Confirmar reset"):
                st.session_state.respostas = {}
                st.session_state.ordem = {}

                for key in list(st.session_state.keys()):
                    if key.startswith("input_"):
                        del st.session_state[key]

                if os.path.exists(CSV_PATH):
                    os.remove(CSV_PATH)

                st.session_state.confirm_reset = False
                st.success("Dados resetados com sucesso!")
                st.rerun()

        with col_cancel:
            if st.button("❌ Cancelar"):
                st.session_state.confirm_reset = False

    # -----------------------------
    # PROGRESSO
    # -----------------------------
    total = len(perguntas)
    respondidas = len(st.session_state.respostas)

    st.progress(respondidas / total)
    st.caption(f"{respondidas} de {total} perguntas respondidas")

    # -----------------------------
    # CONTROLE DE ÍNDICE
    # -----------------------------
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    lista_perguntas = list(perguntas.keys())

    labels = [
        f"✅ {p}" if p in st.session_state.respostas else p
        for p in lista_perguntas
    ]

    # -----------------------------
    # SELECTBOX
    # -----------------------------
    selected_label = st.selectbox(
        "Escolha uma pergunta:",
        labels,
        index=st.session_state.current_index
    )

    st.session_state.current_index = labels.index(selected_label)
    pergunta_selecionada = lista_perguntas[st.session_state.current_index]

    # -----------------------------
    # NAVEGAÇÃO (isolada)
    # -----------------------------
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])

    with nav_col1:
        if st.button("⬅️ Anterior"):
            if st.session_state.current_index > 0:
                st.session_state.current_index -= 1
                st.rerun()

    with nav_col3:
        if st.button("➡️ Próxima"):
            if st.session_state.current_index < len(lista_perguntas) - 1:
                st.session_state.current_index += 1
                st.rerun()

    st.markdown("---")  # 🔥 quebra de layout (essencial)

    # -----------------------------
    # INTERFACE DA PERGUNTA
    # -----------------------------
    if pergunta_selecionada:

        st.subheader(pergunta_selecionada)

        itens_originais = perguntas[pergunta_selecionada]

        # -----------------------------
        # SHUFFLE CONTROLADO
        # -----------------------------
        if pergunta_selecionada not in st.session_state.ordem:
            indices = list(range(len(itens_originais)))
            random.shuffle(indices)
            st.session_state.ordem[pergunta_selecionada] = indices

        indices = st.session_state.ordem[pergunta_selecionada]
        itens_embaralhados = [itens_originais[i] for i in indices]

        # -----------------------------
        # RECUPERAR VALORES SALVOS
        # -----------------------------
        valores_anteriores = {}

        if pergunta_selecionada in st.session_state.respostas:
            for r in st.session_state.respostas[pergunta_selecionada]:
                valores_anteriores[r["texto"]] = r["valor"]

        valores = []

        # -----------------------------
        # INPUTS
        # -----------------------------
        for i, item in enumerate(itens_embaralhados):
            valor = st.number_input(
                item["texto"],
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.1f",
                value=valores_anteriores.get(item["texto"], 0.0),
                key=f"input_{pergunta_selecionada}_{i}"
            )
            valores.append(valor)

        # -----------------------------
        # ENVIO
        # -----------------------------
        if st.button("🚀 Enviar dados"):

            respostas_finais = []

            for i, idx_original in enumerate(indices):
                item_original = itens_originais[idx_original]

                respostas_finais.append({
                    "texto": item_original["texto"],
                    "modelo": item_original["modelo"],
                    "latencia": item_original["latencia"],
                    "valor": valores[i],
                })

            st.session_state.respostas[pergunta_selecionada] = respostas_finais

            salvar_csv()

            st.success("Dados salvos com sucesso!")

# ==================================================
# ABA 2 - RESULTADOS
# ==================================================
with aba2:

    st.title("📊 Resultados")

    if not os.path.exists(CSV_PATH):
        st.warning("Nenhum dado encontrado ainda.")
    else:
        df = pd.read_csv(CSV_PATH)

        st.subheader("📋 Resultados detalhados")
        st.dataframe(df)

        # -----------------------------
        # Agregações
        # -----------------------------
        st.subheader("📊 Agregação por modelo")

        agg_df = df.groupby("modelo").agg(
            media_nota=("valor", "mean"),
            mediana_nota=("valor", "median"),
            media_latencia=("latencia", "mean"),
            mediana_latencia=("latencia", "median"),
        ).reset_index()

        st.dataframe(agg_df)