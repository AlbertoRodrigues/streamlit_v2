import os
import random
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Avaliação de Modelos", layout="wide")

CSV_PATH = Path(__file__).with_name("respostas.csv")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Instrument+Serif:ital@0;1&display=swap');

    :root {
        --bg: #09111f;
        --panel: rgba(13, 22, 39, 0.86);
        --panel-strong: #0d1728;
        --line: rgba(169, 192, 230, 0.14);
        --text: #eef4ff;
        --muted: #95a8c7;
        --accent: #79a8ff;
        --accent-2: #9cc6ff;
        --accent-soft: rgba(121, 168, 255, 0.14);
        --shadow: 0 22px 60px rgba(0, 0, 0, 0.38);
        --radius-xl: 28px;
        --radius-lg: 22px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(84, 127, 214, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(27, 66, 140, 0.22), transparent 24%),
            linear-gradient(180deg, #07111f 0%, #0b1528 100%);
        color: var(--text);
        font-family: "Space Grotesk", sans-serif;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2.4rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, label, p, div, span {
        font-family: "Space Grotesk", sans-serif;
        color: var(--text);
    }

    [data-testid="stTabs"] {
        margin-top: 1.2rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.75rem;
        background: transparent;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        height: 52px;
        border-radius: 999px;
        padding: 0 1.3rem;
        background: rgba(16, 27, 46, 0.92);
        border: 1px solid rgba(169, 192, 230, 0.12);
        box-shadow: none;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(135deg, #5f8ff0 0%, #396fd8 100%);
    }

    [data-testid="stTabs"] [aria-selected="true"] p {
        color: #f5f9ff;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 1rem 1.1rem;
        box-shadow: var(--shadow);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--text);
    }

    div[data-testid="stSelectbox"],
    div[data-testid="stDataFrame"] {
        background: transparent;
    }

    div[data-baseweb="select"] > div {
        background: rgba(12, 21, 36, 0.96);
        border-radius: 16px;
        border: 1px solid rgba(169, 192, 230, 0.12);
    }

    .stButton > button {
        border-radius: 16px;
        border: 1px solid rgba(169, 192, 230, 0.10);
        background: rgba(12, 21, 36, 0.96);
        color: var(--text);
        font-weight: 600;
        min-height: 48px;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.24);
    }

    .stButton > button:hover {
        border-color: rgba(121, 168, 255, 0.44);
        transform: translateY(-1px);
    }

    .hero-card {
        position: relative;
        overflow: hidden;
        padding: 2rem;
        border-radius: var(--radius-xl);
        background: linear-gradient(135deg, rgba(12,22,40,0.96) 0%, rgba(18,36,67,0.96) 56%, rgba(27,54,102,0.94) 100%);
        border: 1px solid rgba(169, 192, 230, 0.10);
        box-shadow: var(--shadow);
    }

    .hero-card::after {
        content: "";
        position: absolute;
        inset: auto -60px -80px auto;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(156,198,255,0.28) 0%, rgba(156,198,255,0) 72%);
    }

    .eyebrow {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--accent-2);
        font-weight: 700;
        margin-bottom: 0.7rem;
    }

    .hero-title {
        font-family: "Instrument Serif", serif;
        font-size: clamp(2.4rem, 4vw, 4.8rem);
        line-height: 0.92;
        margin: 0;
        max-width: 14ch;
    }

    .hero-subtitle {
        margin-top: 1rem;
        max-width: 72ch;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.6;
    }

    .panel-card {
        padding: 1.1rem 1.25rem;
        border-radius: var(--radius-lg);
        background: linear-gradient(180deg, rgba(11,20,35,0.94), rgba(16,27,46,0.92));
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }

    .question-card {
        padding: 1.5rem;
        border-radius: var(--radius-xl);
        background: linear-gradient(135deg, rgba(10,19,34,0.98), rgba(18,31,55,0.96));
        border: 1px solid rgba(169, 192, 230, 0.12);
        box-shadow: var(--shadow);
        margin-top: 1rem;
    }

    .question-title {
        font-size: 1.9rem;
        line-height: 1.1;
        margin: 0;
    }

    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 1rem;
    }

    .pill {
        padding: 0.55rem 0.9rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: #b8d5ff;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .response-shell {
        margin-bottom: 1rem;
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(9,18,32,0.98), rgba(15,27,48,0.95));
        border: 1px solid rgba(169, 192, 230, 0.10);
    }

    .response-model {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--accent-2);
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .response-copy {
        color: var(--text);
        line-height: 1.65;
        font-size: 0.98rem;
    }

    [data-testid="stPills"] button {
        background: rgba(121, 168, 255, 0.08);
        border: 1px solid rgba(121, 168, 255, 0.18);
        border-radius: 14px;
        color: var(--text);
    }

    [data-testid="stPills"] button[aria-pressed="true"] {
        background: rgba(121, 168, 255, 0.18);
        border-color: rgba(121, 168, 255, 0.42);
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .section-copy {
        color: var(--muted);
        font-size: 0.96rem;
        line-height: 1.55;
    }

    .dataframe-shell {
        padding: 1rem;
        border-radius: var(--radius-xl);
        background: linear-gradient(180deg, rgba(10,19,34,0.96), rgba(17,29,50,0.94));
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }

    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #7db0ff 0%, #3f79eb 100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


perguntas = {
    "Como explicar Tesouro Selic para um investidor iniciante?": [
        {
            "texto": "Tesouro Selic costuma ser visto como uma opção conservadora. Ele acompanha a taxa básica de juros e tende a oscilar pouco no dia a dia. Para quem está começando, passa uma sensação de simplicidade e segurança.",
            "modelo": "gpt-4.1",
            "latencia": 1.4,
        },
        {
            "texto": "Tesouro Selic é frequentemente usado como porta de entrada para investidores iniciantes. Ele oferece liquidez diária e um risco de crédito percebido como baixo. O tom aqui tenta ser didático sem ficar excessivamente técnico.",
            "modelo": "gpt-5.2",
            "latencia": 1.1,
        },
        {
            "texto": "Se a ideia é começar com algo previsível, o Tesouro Selic costuma aparecer primeiro. Ele ajuda na reserva de emergência e tem uma leitura mais estável para o investidor comum. A resposta procura soar confiante e acolhedora ao mesmo tempo.",
            "modelo": "gpt-5.4",
            "latencia": 0.9,
        },
    ],
    "Qual é a diferença entre CDB e poupança?": [
        {
            "texto": "A poupança é mais conhecida e fácil de entender para quase todo mundo. Já o CDB costuma oferecer rendimento potencialmente maior em muitos cenários. Essa resposta tenta resumir a comparação de forma direta e objetiva.",
            "modelo": "gpt-4.1",
            "latencia": 1.5,
        },
        {
            "texto": "Enquanto a poupança prioriza simplicidade, o CDB costuma entregar mais eficiência para quem aceita comparar opções. Os dois podem ter perfis diferentes de liquidez e rentabilidade. O estilo aqui busca equilíbrio entre clareza e autoridade.",
            "modelo": "gpt-5.2",
            "latencia": 1.2,
        },
        {
            "texto": "Poupança normalmente é escolhida pela familiaridade, mas o CDB entra na conversa quando o foco é rendimento. A diferença principal costuma aparecer no retorno e nas condições do produto. O texto foi escrito para soar firme, mas acessível.",
            "modelo": "gpt-5.4",
            "latencia": 1.0,
        },
    ],
    "Como descrever diversificação de carteira em um tom confiante?": [
        {
            "texto": "Diversificar é uma forma de evitar concentração excessiva em um único ativo. Isso ajuda a carteira a reagir melhor a diferentes cenários de mercado. O tom foi pensado para ser racional e seguro.",
            "modelo": "gpt-4.1",
            "latencia": 1.6,
        },
        {
            "texto": "Uma carteira diversificada tende a distribuir risco com mais inteligência. Em vez de depender de uma única aposta, ela combina fontes diferentes de retorno. A resposta quer transmitir confiança com uma linguagem mais consultiva.",
            "modelo": "gpt-5.2",
            "latencia": 1.3,
        },
        {
            "texto": "Diversificação não é dispersão aleatória, é construção de equilíbrio. Quando os ativos se complementam, a carteira ganha mais estabilidade ao longo do tempo. O estilo aqui foi escrito para parecer assertivo e estratégico.",
            "modelo": "gpt-5.4",
            "latencia": 1.0,
        },
    ],
}


if "respostas" not in st.session_state:
    st.session_state.respostas = {}

if "ordem" not in st.session_state:
    st.session_state.ordem = {}

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False


def carregar_respostas_salvas():
    if st.session_state.respostas or not os.path.exists(CSV_PATH):
        return

    df = pd.read_csv(CSV_PATH)
    if df.empty:
        return

    perguntas_validas = set(perguntas.keys())
    modelos_validos = {
        item["modelo"]
        for lista_respostas in perguntas.values()
        for item in lista_respostas
    }

    df = df[df["pergunta"].isin(perguntas_validas) & df["modelo"].isin(modelos_validos)]
    if df.empty:
        return

    respostas_carregadas = {}

    for pergunta, grupo in df.groupby("pergunta", sort=False):
        respostas_carregadas[pergunta] = []

        for _, row in grupo.iterrows():
            respostas_carregadas[pergunta].append(
                {
                    "texto": row["resposta"],
                    "modelo": row["modelo"],
                    "latencia": float(row["latencia"]),
                    "valor": float(row["valor"]),
                }
            )

    st.session_state.respostas = respostas_carregadas


def salvar_csv():
    linhas = []

    for pergunta, lista_respostas in st.session_state.respostas.items():
        for item in lista_respostas:
            linhas.append(
                {
                    "pergunta": pergunta,
                    "modelo": item["modelo"],
                    "resposta": item["texto"],
                    "valor": item["valor"],
                    "latencia": item["latencia"],
                }
            )

    df = pd.DataFrame(linhas)
    df.to_csv(CSV_PATH, index=False)


carregar_respostas_salvas()

total = len(perguntas)
respondidas = len(st.session_state.respostas)
pendentes = total - respondidas
progresso = respondidas / total if total else 0

st.markdown(
    """
    <section class="hero-card">
        <h1 class="hero-title">Avaliação de respostas sobre tom de voz em investimentos.</h1>
    </section>
    """,
    unsafe_allow_html=True,
)

hero_col1, hero_col2, hero_col3 = st.columns([1.2, 1, 1])
with hero_col1:
    st.metric("Perguntas respondidas", f"{respondidas}/{total}")
with hero_col2:
    st.metric("Taxa de conclusão", f"{progresso * 100:.0f}%")
with hero_col3:
    st.metric("Pendências", pendentes)

aba1, aba2 = st.tabs(["Coleta", "Resultados"])


with aba1:
    header_col, reset_col = st.columns([5.4, 1.1])

    with header_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Coleta</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with reset_col:
        if st.button("Resetar base"):
            st.session_state.confirm_reset = True

    if st.session_state.confirm_reset:
        st.warning("Tem certeza que deseja apagar todas as respostas?")

        col_confirm, col_cancel = st.columns(2)

        with col_confirm:
            if st.button("Confirmar reset"):
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
            if st.button("Cancelar reset"):
                st.session_state.confirm_reset = False

    st.progress(progresso)
    st.caption(f"{respondidas} de {total} perguntas respondidas")

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    lista_perguntas = list(perguntas.keys())
    labels = [f"Concluída • {p}" if p in st.session_state.respostas else p for p in lista_perguntas]

    select_col, status_col = st.columns([3.2, 0.8])
    with select_col:
        selected_label = st.selectbox(
            "Pergunta",
            labels,
            index=st.session_state.current_index,
            label_visibility="collapsed",
        )

    st.session_state.current_index = labels.index(selected_label)
    pergunta_selecionada = lista_perguntas[st.session_state.current_index]

    with status_col:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="section-title">{st.session_state.current_index + 1}/{len(lista_perguntas)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    nav_col1, nav_col2, nav_col3 = st.columns([1, 3.4, 1])
    with nav_col1:
        if st.button("Anterior"):
            if st.session_state.current_index > 0:
                st.session_state.current_index -= 1
                st.rerun()

    with nav_col3:
        if st.button("Próxima"):
            if st.session_state.current_index < len(lista_perguntas) - 1:
                st.session_state.current_index += 1
                st.rerun()

    if pergunta_selecionada:
        st.markdown(
            f"""
            <section class="question-card">
                <h2 class="question-title">{pergunta_selecionada}</h2>
                <div class="pill-row">
                    <span class="pill">Tom de voz</span>
                    <span class="pill">Notas 1 a 3</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        itens_originais = perguntas[pergunta_selecionada]

        if pergunta_selecionada not in st.session_state.ordem:
            indices = list(range(len(itens_originais)))
            random.shuffle(indices)
            st.session_state.ordem[pergunta_selecionada] = indices

        indices = st.session_state.ordem[pergunta_selecionada]
        itens_embaralhados = [itens_originais[i] for i in indices]

        valores_anteriores = {}
        if pergunta_selecionada in st.session_state.respostas:
            for r in st.session_state.respostas[pergunta_selecionada]:
                valores_anteriores[r["texto"]] = r["valor"]

        valores = []
        for i, item in enumerate(itens_embaralhados):
            valor_anterior = valores_anteriores.get(item["texto"], 1.0)
            opcoes = [1, 2, 3]
            valor_padrao = int(valor_anterior) if int(valor_anterior) in opcoes else 1

            st.markdown(
                f"""
                <div class="response-shell">
                    <div class="response-model">Tom de Voz {i + 1}</div>
                    <div class="response-copy">{item["texto"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            valor = st.pills(
                label=f"Nota para Tom de Voz {i + 1}",
                options=opcoes,
                default=valor_padrao,
                key=f"input_{pergunta_selecionada}_{i}",
                label_visibility="collapsed",
            )
            valores.append(valor)

        if st.button("Salvar avaliação"):
            respostas_finais = []

            for i, idx_original in enumerate(indices):
                item_original = itens_originais[idx_original]
                respostas_finais.append(
                    {
                        "texto": item_original["texto"],
                        "modelo": item_original["modelo"],
                        "latencia": item_original["latencia"],
                        "valor": valores[i],
                    }
                )

            st.session_state.respostas[pergunta_selecionada] = respostas_finais
            salvar_csv()
            st.success("Dados salvos com sucesso!")


with aba2:
    st.markdown(
        """
        <div class="panel-card">
            <div class="section-title">Resultados</div>
            <div class="section-copy">Modelo e latência ficam visíveis nesta etapa para análise comparativa.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not os.path.exists(CSV_PATH):
        st.warning("Nenhum dado encontrado ainda.")
    else:
        df = pd.read_csv(CSV_PATH)
        perguntas_validas = set(perguntas.keys())
        modelos_validos = {
            item["modelo"]
            for lista_respostas in perguntas.values()
            for item in lista_respostas
        }
        df = df[df["pergunta"].isin(perguntas_validas) & df["modelo"].isin(modelos_validos)]

        if df.empty:
            st.warning("Nenhum dado compatível com o conjunto atual de perguntas foi encontrado.")
            st.stop()

        resultado_col1, resultado_col2, resultado_col3 = st.columns(3)
        with resultado_col1:
            st.metric("Linhas avaliadas", len(df))
        with resultado_col2:
            st.metric("Modelos presentes", df["modelo"].nunique())
        with resultado_col3:
            media_geral = df["valor"].mean() if not df.empty else 0
            st.metric("Média geral", f"{media_geral:.2f}")

        st.markdown(
            """
            <div class="dataframe-shell" style="margin-top: 1rem;">
                <div class="section-title">Resultados detalhados</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(df, width="stretch")

        agg_df = (
            df.groupby("modelo")
            .agg(
                media_nota=("valor", "mean"),
                mediana_nota=("valor", "median"),
                media_latencia=("latencia", "mean"),
                mediana_latencia=("latencia", "median"),
            )
            .reset_index()
        )

        st.markdown(
            """
            <div class="dataframe-shell" style="margin-top: 1.25rem;">
                <div class="section-title">Agregação por modelo</div>
                <div class="section-copy">Resumo consolidado das notas e latências por modelo.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(agg_df, width="stretch")
