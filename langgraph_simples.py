import uuid
import streamlit as st
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from graph import create_graph

load_dotenv()

# =========================
# INIT GRAPH
# =========================

if "graph" not in st.session_state:
    st.session_state.graph = create_graph()

graph = st.session_state.graph

# =========================
# UI
# =========================

st.set_page_config(page_title="Chatbot Investimentos", layout="centered")
st.title("💬 Chatbot de Investimentos")

# thread_id único por sessão
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

THREAD_ID = st.session_state.thread_id

# histórico visual
if "messages" not in st.session_state:
    st.session_state.messages = []

# render histórico
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# input
user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):

            result = graph.invoke(
                {"messages": [human_msg]},
                config={"configurable": {"thread_id": THREAD_ID}}
            )

            ai_msg = result["messages"][-1]

            st.session_state.messages.append(ai_msg)

            st.markdown(ai_msg.content)