from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

# =========================
# CONFIG
# =========================

SYSTEM_PROMPT = """
Você é um assistente especializado em investimentos.

Regras:
- Seja claro, direto e técnico quando necessário
- Não forneça aconselhamento financeiro personalizado
- Sempre destaque riscos quando falar de estratégias
- Prefira explicações educacionais em vez de recomendações diretas
- Se não souber, diga explicitamente que não sabe
"""

def create_graph():
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )

    def llm_node(state: MessagesState):
        messages = state["messages"]

        full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        response = llm.invoke(full_messages)

        return {
            "messages": [response]
        }

    builder = StateGraph(MessagesState)

    builder.add_node("llm_node", llm_node)
    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", END)

    memory = MemorySaver()

    graph = builder.compile(checkpointer=memory)

    return graph