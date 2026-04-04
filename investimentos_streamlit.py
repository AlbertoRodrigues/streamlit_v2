import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from graph import create_graph

load_dotenv()


INTENT_LABELS = {
    "conceitos_investimentos": "Conceitos de investimentos",
    "produtos_investimentos": "Produtos de investimentos",
}

AGENT_LABELS = {
    "conceitos_agent": "Agente de conceitos",
    "produtos_agent": "Agente de produtos",
}


if "graph" not in st.session_state:
    st.session_state.graph = create_graph()

graph = st.session_state.graph

st.set_page_config(page_title="Chatbot Investimentos", layout="centered")
st.title("Chatbot de Investimentos")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

THREAD_ID = st.session_state.thread_id

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        if isinstance(msg, AIMessage):
            steps = msg.additional_kwargs.get("execution_steps", [])
            if steps:
                with st.expander("Passo a passo do grafo", expanded=False):
                    for step in steps:
                        st.markdown(step)
        st.markdown(msg.content)


user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Executando o grafo..."):
            steps_placeholder = st.empty()
            answer_placeholder = st.empty()

            current_steps = ["1. Última mensagem do histórico capturada"]
            final_result = None
            final_ai_msg = None

            for update in graph.stream(
                {"messages": [human_msg]},
                config={"configurable": {"thread_id": THREAD_ID}},
                stream_mode="updates",
            ):
                if "classify_intent" in update:
                    intent = update["classify_intent"].get("intent", "")
                    intent_label = INTENT_LABELS.get(intent, intent)
                    current_steps.append(f"2. Intenção classificada: `{intent_label}`")
                    steps_placeholder.markdown("\n".join(current_steps))

                if "conceitos_agent" in update:
                    selected_agent = update["conceitos_agent"].get("selected_agent", "conceitos_agent")
                    current_steps.append(f"3. Agente acionado: `{AGENT_LABELS.get(selected_agent, selected_agent)}`")
                    messages = update["conceitos_agent"].get("messages", [])
                    if messages:
                        final_ai_msg = messages[-1]
                        answer_placeholder.markdown(final_ai_msg.content)
                    steps_placeholder.markdown("\n".join(current_steps))

                if "produtos_agent" in update:
                    selected_agent = update["produtos_agent"].get("selected_agent", "produtos_agent")
                    current_steps.append(f"3. Agente acionado: `{AGENT_LABELS.get(selected_agent, selected_agent)}`")
                    messages = update["produtos_agent"].get("messages", [])
                    if messages:
                        final_ai_msg = messages[-1]
                        answer_placeholder.markdown(final_ai_msg.content)
                    steps_placeholder.markdown("\n".join(current_steps))

            final_result = graph.get_state(config={"configurable": {"thread_id": THREAD_ID}})

            if final_ai_msg is None and final_result and final_result.values.get("messages"):
                final_ai_msg = final_result.values["messages"][-1]
                answer_placeholder.markdown(final_ai_msg.content)

            current_steps.append("4. Resposta final gerada")

            with st.expander("Passo a passo do grafo", expanded=True):
                for step in current_steps:
                    st.markdown(step)

            if final_ai_msg is not None:
                ai_msg_to_store = AIMessage(
                    content=final_ai_msg.content,
                    additional_kwargs={"execution_steps": current_steps},
                )
                st.session_state.messages.append(ai_msg_to_store)
