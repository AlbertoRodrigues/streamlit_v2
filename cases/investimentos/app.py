import uuid

import streamlit as st
import streamlit.components.v1 as components
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

    for item in agent_outputs:
        with st.expander(item["label"], expanded=False):
            st.markdown(item["content"])


def render_graph_mermaid():
    mermaid_code = """
    flowchart TD
        A([START]) --> B{classify_intent}
        B -->|conceitos_investimentos| C[conceitos_agent]
        B -->|produtos_investimentos| D[produtos_agent]
        C --> E([END])
        D --> E
    """

    mermaid_html = f"""
    <div style="
        border: 1px solid rgba(157, 178, 214, 0.14);
        border-radius: 22px;
        padding: 1rem;
        background: linear-gradient(180deg, rgba(13,21,37,0.96), rgba(16,25,43,0.96));
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
    ">
        <div style="
            font-family: Manrope, sans-serif;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #79a8ff;
            margin-bottom: 0.5rem;
        ">Fluxo do grafo</div>
        <div style="
            font-family: Manrope, sans-serif;
            font-size: 1rem;
            font-weight: 800;
            color: #eef4ff;
            margin-bottom: 0.8rem;
        ">Visualização Mermaid do LangGraph</div>
        <div class="mermaid">
            {mermaid_code}
        </div>
    </div>

    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'base',
            securityLevel: 'loose',
            themeVariables: {{
                background: '#0d1525',
                primaryColor: '#132848',
                primaryBorderColor: '#4c84f7',
                primaryTextColor: '#eef4ff',
                lineColor: '#79a8ff',
                secondaryColor: '#10213a',
                tertiaryColor: '#0f1c33',
                clusterBkg: '#0d1525',
                clusterBorder: '#4c84f7',
                edgeLabelBackground: '#132848',
                fontFamily: 'Manrope, sans-serif'
            }}
        }});
    </script>
    """

    components.html(mermaid_html, height=360)


def render_graph_mermaid_large():
    mermaid_code = """
    flowchart TD
        A([START]) --> B{classify_intent}
        B -->|conceitos_investimentos| C[conceitos_agent]
        B -->|produtos_investimentos| D[produtos_agent]
        C --> E([END])
        D --> E
    """

    mermaid_html = f"""
    <div style="
        border: 1px solid rgba(157, 178, 214, 0.16);
        border-radius: 26px;
        padding: 1.4rem 1.4rem 0.8rem 1.4rem;
        background: linear-gradient(180deg, rgba(13,21,37,0.98), rgba(16,25,43,0.98));
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
    ">
        <div class="mermaid">
            {mermaid_code}
        </div>
    </div>

    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'base',
            securityLevel: 'loose',
            themeVariables: {{
                background: '#0d1525',
                primaryColor: '#132848',
                primaryBorderColor: '#4c84f7',
                primaryTextColor: '#eef4ff',
                lineColor: '#79a8ff',
                secondaryColor: '#10213a',
                tertiaryColor: '#0f1c33',
                clusterBkg: '#0d1525',
                clusterBorder: '#4c84f7',
                edgeLabelBackground: '#132848',
                fontFamily: 'Manrope, sans-serif'
            }}
        }});
    </script>
    """

    components.html(mermaid_html, height=760)


chat_tab, graph_tab = st.tabs(["Chat", "Arquitetura do Fluxo"])

with chat_tab:
    st.markdown(
        """
        <section class="hero-card">
            <div class="eyebrow">LangGraph Demo</div>
            <h1 class="hero-title">Fluxo LangGraph de Dúvidas sobre investimentos</h1>
        </section>
        """,
        unsafe_allow_html=True,
    )

    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        avatar = ":material/account_circle:" if role == "user" else ":material/verified:"
        with st.chat_message(role, avatar=avatar):
            if isinstance(msg, AIMessage):
                agent_outputs = msg.additional_kwargs.get("agent_outputs", [])
                if agent_outputs:
                    render_agent_outputs(agent_outputs)
            st.markdown(msg.content)

with graph_tab:
    render_graph_mermaid_large()

    st.markdown(
        """
        <section class="shell-card" style="margin-top: 1rem;">
            <div class="section-kicker">Leitura informal</div>
            <div class="section-title">O que cada parte do grafo faz</div>
            <div class="section-copy">
                Aqui a ideia é simples: entra uma pergunta, o classificador decide o tema,
                o especialista certo responde e o fluxo encerra com a resposta pronta para o chat.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    desc_col1, desc_col2 = st.columns(2, gap="large")

    with desc_col1:
        st.markdown(
            """
            <section class="shell-card">
                <div class="section-kicker">START</div>
                <div class="section-title">Entrada da pergunta</div>
                <div class="section-copy">
                    É o ponto em que o fluxo recebe a última mensagem do usuário e prepara tudo para começar a decisão.
                </div>
                <div class="section-copy" style="margin-top: 0.8rem;">
                    Exemplo:
                    <br><code>"Qual a diferença entre CDB e Tesouro Selic?"</code>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <section class="shell-card" style="margin-top: 1rem;">
                <div class="section-kicker">classify_intent</div>
                <div class="section-title">O triador do fluxo</div>
                <div class="section-copy">
                    Esse nó lê a pergunta e decide se ela é mais sobre conceito de investimentos
                    ou sobre produto financeiro.
                </div>
                <div class="section-copy" style="margin-top: 0.8rem;">
                    Exemplo de saída:
                    <br><code>{"intent": "produtos_investimentos"}</code>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <section class="shell-card" style="margin-top: 1rem;">
                <div class="section-kicker">conceitos_agent</div>
                <div class="section-title">Especialista em fundamentos</div>
                <div class="section-copy">
                    Entra quando a pergunta é mais educativa: risco, liquidez, inflação, juros,
                    diversificação e funcionamento do mercado.
                </div>
                <div class="section-copy" style="margin-top: 0.8rem;">
                    Exemplo de saída:
                    <br><code>{"selected_agent": "conceitos_agent", "messages": ["Liquidez é a facilidade de converter um ativo em dinheiro..."]}</code>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    with desc_col2:
        st.markdown(
            """
            <section class="shell-card">
                <div class="section-kicker">produtos_agent</div>
                <div class="section-title">Especialista em produtos</div>
                <div class="section-copy">
                    Entra quando a dúvida fala de CDB, Tesouro Direto, fundos, ações, FIIs
                    ou comparação entre tipos de investimento.
                </div>
                <div class="section-copy" style="margin-top: 0.8rem;">
                    Exemplo de saída:
                    <br><code>{"selected_agent": "produtos_agent", "messages": ["O Tesouro Selic é um título público com baixa volatilidade e liquidez diária..."]}</code>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <section class="shell-card" style="margin-top: 1rem;">
                <div class="section-kicker">END</div>
                <div class="section-title">Saída final do fluxo</div>
                <div class="section-copy">
                    É o encerramento. Nessa etapa a resposta já foi produzida e está pronta para aparecer na conversa.
                </div>
                <div class="section-copy" style="margin-top: 0.8rem;">
                    Exemplo de saída final:
                    <br><code>"CDB e Tesouro Selic são investimentos de renda fixa, mas têm emissores, garantias e comportamentos diferentes."</code>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <section class="shell-card" style="margin-top: 1rem;">
                <div class="section-kicker">Roteamento</div>
                <div class="section-title">Como ele decide para onde ir</div>
                <div class="section-copy">
                    Se o classificador devolver <code>conceitos_investimentos</code>, o fluxo segue para
                    <code>conceitos_agent</code>. Se devolver <code>produtos_investimentos</code>, ele vai para
                    <code>produtos_agent</code>.
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

with chat_tab:
    user_input = st.chat_input("Digite uma pergunta sobre investimentos")

if user_input:
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    with chat_tab:
        with st.chat_message("user", avatar=":material/account_circle:"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar=":material/verified:"):
            with st.spinner("Analisando a solicitação e preparando a resposta..."):
                answer_placeholder = st.empty()
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
                            answer_placeholder.markdown(final_ai_msg.content)
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
                            answer_placeholder.markdown(final_ai_msg.content)
                            agent_outputs.append(
                                {
                                    "label": f"Saída do {AGENT_LABELS.get(selected_agent, selected_agent)}",
                                    "content": final_ai_msg.content,
                                }
                            )

                final_result = graph.get_state(config={"configurable": {"thread_id": THREAD_ID}})

                if final_ai_msg is None and final_result and final_result.values.get("messages"):
                    final_ai_msg = final_result.values["messages"][-1]
                    answer_placeholder.markdown(final_ai_msg.content)

                if agent_outputs:
                    render_agent_outputs(agent_outputs)

                if final_ai_msg is not None:
                    ai_msg_to_store = AIMessage(
                        content=final_ai_msg.content,
                        additional_kwargs={"agent_outputs": agent_outputs},
                    )
                    st.session_state.messages.append(ai_msg_to_store)
