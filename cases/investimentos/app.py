import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

try:
    from .graph import create_graph
except ImportError:
    from graph import create_graph

load_dotenv()


INTENT_LABELS = {
    "conceitos_investimentos": "Conceitos de investimentos",
    "produtos_investimentos": "Produtos de investimentos",
}

AGENT_LABELS = {
    "conceitos_agent": "Especialista em conceitos",
    "produtos_agent": "Especialista em produtos",
}

GRAPH_IMAGE_PATH = Path(__file__).with_name("grafo.png")
USER_AVATAR_PATH = Path(__file__).with_name("avatar_humano.svg")
BOT_AVATAR_PATH = Path(__file__).with_name("avatar_robo.svg")


st.set_page_config(page_title="Assistente de Investimentos", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap');

    :root {
        --bg: #0b1220;
        --bg-soft: #111a2c;
        --panel: rgba(13, 21, 37, 0.88);
        --panel-strong: rgba(16, 25, 43, 0.96);
        --text: #eef4ff;
        --muted: #93a2bd;
        --line: rgba(157, 178, 214, 0.14);
        --accent: #79a8ff;
        --accent-2: #4c84f7;
        --accent-soft: rgba(121, 168, 255, 0.14);
        --success: #46c39a;
        --shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
        --radius-xl: 28px;
        --radius-lg: 22px;
        --radius-md: 16px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(76, 132, 247, 0.18), transparent 26%),
            radial-gradient(circle at top right, rgba(45, 88, 184, 0.20), transparent 24%),
            linear-gradient(180deg, #08101d 0%, #0d1627 100%);
        color: var(--text);
        font-family: "Manrope", sans-serif;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, h5, h6, p, li, label, div, span {
        font-family: "Manrope", sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(14,22,38,0.94), rgba(18,28,47,0.92));
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 1rem 1.1rem;
        box-shadow: var(--shadow);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--text);
    }

    [data-testid="stChatMessage"] {
        background: transparent;
    }

    [data-testid="stChatMessageContent"] {
        border-radius: 22px;
        border: 1px solid var(--line);
        background: rgba(14, 22, 38, 0.92);
        box-shadow: var(--shadow);
        padding: 1.05rem 1.15rem;
    }

    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatMessageContent"] span {
        color: var(--text);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, rgba(16,63,145,0.95), rgba(44,107,237,0.92));
        color: #ffffff;
        border-color: rgba(16, 63, 145, 0.18);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] p {
        color: #ffffff;
    }

    .stChatInputContainer {
        background: rgba(8, 14, 25, 0.78);
        border-top: 1px solid rgba(157, 178, 214, 0.10);
        backdrop-filter: blur(10px);
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 18px;
        border: 1px solid rgba(157, 178, 214, 0.14);
        background: rgba(16,25,43,0.96);
        color: var(--text);
    }

    .stExpander {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(14, 22, 38, 0.92);
        box-shadow: var(--shadow);
    }

    .hero-card {
        position: relative;
        overflow: hidden;
        padding: 1.8rem 2rem;
        border-radius: var(--radius-xl);
        background: linear-gradient(135deg, #0f1c33 0%, #132848 58%, #1d3d73 100%);
        box-shadow: 0 26px 70px rgba(0, 0, 0, 0.34);
        color: #f8fbff;
    }

    .hero-card::after {
        content: "";
        position: absolute;
        right: -80px;
        top: -30px;
        width: 260px;
        height: 260px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0) 72%);
    }

    .eyebrow {
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: rgba(232, 240, 255, 0.78);
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-family: "Manrope", sans-serif;
        font-size: clamp(1.8rem, 2.8vw, 2.8rem);
        line-height: 1.05;
        margin: 0;
        max-width: none;
        font-weight: 800;
    }

    .hero-subtitle {
        margin-top: 0.85rem;
        max-width: 72ch;
        font-size: 0.98rem;
        line-height: 1.65;
        color: rgba(240, 245, 255, 0.84);
    }

    .shell-card {
        padding: 1.35rem;
        border-radius: var(--radius-lg);
        background: rgba(13, 21, 37, 0.88);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }

    .section-kicker {
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: var(--accent-2);
        margin-bottom: 0.5rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--text);
        margin-bottom: 0.35rem;
    }

    .section-copy {
        color: var(--muted);
        line-height: 1.65;
        font-size: 0.96rem;
    }

    .status-list {
        display: grid;
        gap: 0.8rem;
    }

    .status-item {
        padding: 0.95rem 1rem;
        border-radius: 16px;
        background: linear-gradient(180deg, rgba(16,25,43,0.96) 0%, rgba(18,29,49,0.94) 100%);
        border: 1px solid rgba(157, 178, 214, 0.12);
    }

    .status-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 0.35rem;
        font-weight: 800;
    }

    .status-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
    }

    .timeline-card {
        margin-top: 1rem;
        padding: 1.2rem;
        border-radius: var(--radius-lg);
        background: rgba(13, 21, 37, 0.92);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }

    .timeline-title {
        font-size: 0.95rem;
        font-weight: 800;
        margin-bottom: 0.85rem;
        color: var(--text);
    }

    .timeline-step {
        display: flex;
        gap: 0.8rem;
        align-items: flex-start;
        padding: 0.8rem 0;
        border-top: 1px solid rgba(22, 32, 51, 0.06);
    }

    .timeline-step:first-of-type {
        border-top: 0;
        padding-top: 0;
    }

    .timeline-index {
        min-width: 34px;
        height: 34px;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.85rem;
    }

    .timeline-text {
        color: var(--muted);
        line-height: 1.55;
        padding-top: 0.15rem;
    }

    .badge-row {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .badge {
        padding: 0.55rem 0.9rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.14);
        color: #edf4ff;
        font-size: 0.88rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "graph" not in st.session_state:
    st.session_state.graph = create_graph()

graph = st.session_state.graph

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

THREAD_ID = st.session_state.thread_id

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_agent_outputs(agent_outputs):
    if not agent_outputs:
        return

    for i, item in enumerate(agent_outputs):
        is_last = i == len(agent_outputs) - 1
        with st.expander(item["label"], expanded=is_last):
            st.markdown(item["content"])



def render_graph_diagram():
    _, center_col, _ = st.columns([0.12, 0.76, 0.12])
    with center_col:
        st.image(str(GRAPH_IMAGE_PATH), use_container_width=True)


chat_tab, graph_tab = st.tabs(["Chat", "Arquitetura do Fluxo"])

with chat_tab:
    st.markdown(
        """
        <section class="hero-card">
            <h1 class="hero-title">Novo Fluxo de Dúvidas - Wealth Specialist</h1>
        </section>
        """,
        unsafe_allow_html=True,
    )

    chat_messages_container = st.container()

    with chat_messages_container:
        for msg in st.session_state.messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            avatar = str(USER_AVATAR_PATH) if role == "user" else str(BOT_AVATAR_PATH)
            with st.chat_message(role, avatar=avatar):
                if isinstance(msg, AIMessage):
                    agent_outputs = msg.additional_kwargs.get("agent_outputs", [])
                    if agent_outputs:
                        render_agent_outputs(agent_outputs)
                    else:
                        st.markdown(msg.content)
                else:
                    st.markdown(msg.content)

with graph_tab:
    render_graph_diagram()


with chat_tab:
    user_input = st.chat_input("Digite uma pergunta sobre investimentos")

if user_input:
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    with chat_tab:
        with chat_messages_container:
            with st.chat_message("user", avatar=str(USER_AVATAR_PATH)):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar=str(BOT_AVATAR_PATH)):
                with st.spinner("Analisando a solicitação e preparando a resposta..."):
                    final_ai_msg = None
                    agent_outputs = []

                    for update in graph.stream(
                        {"messages": [human_msg]},
                        config={"configurable": {"thread_id": THREAD_ID}},
                        stream_mode="updates",
                    ):
                        if "classify_intent" in update:
                            intent = update["classify_intent"].get("intent", "")
                            intent_label = INTENT_LABELS.get(intent, intent or "Não identificada")
                            agent_outputs = [
                                {
                                    "label": "Classificação da intenção",
                                    "content": f"Saída do classificador: `{intent_label}`",
                                }
                            ]

                        if "conceitos_agent" in update:
                            selected_agent = update["conceitos_agent"].get("selected_agent", "conceitos_agent")
                            messages = update["conceitos_agent"].get("messages", [])
                            if messages:
                                final_ai_msg = messages[-1]
                                agent_outputs.append(
                                    {
                                        "label": f"Saída do {AGENT_LABELS.get(selected_agent, selected_agent)}",
                                        "content": final_ai_msg.content,
                                    }
                                )

                        if "produtos_agent" in update:
                            selected_agent = update["produtos_agent"].get("selected_agent", "produtos_agent")
                            messages = update["produtos_agent"].get("messages", [])
                            if messages:
                                final_ai_msg = messages[-1]
                                agent_outputs.append(
                                    {
                                        "label": f"Saída do {AGENT_LABELS.get(selected_agent, selected_agent)}",
                                        "content": final_ai_msg.content,
                                    }
                                )

                    final_result = graph.get_state(config={"configurable": {"thread_id": THREAD_ID}})

                    if final_ai_msg is None and final_result and final_result.values.get("messages"):
                        final_ai_msg = final_result.values["messages"][-1]

                    if agent_outputs:
                        render_agent_outputs(agent_outputs)
                    elif final_ai_msg:
                        st.markdown(final_ai_msg.content)

                    if final_ai_msg is not None:
                        ai_msg_to_store = AIMessage(
                            content=final_ai_msg.content,
                            additional_kwargs={"agent_outputs": agent_outputs},
                        )
                        st.session_state.messages.append(ai_msg_to_store)
