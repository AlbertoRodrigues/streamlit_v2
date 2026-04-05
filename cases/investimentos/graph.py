from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState


SYSTEM_PROMPT = """
Você é um assistente especializado em investimentos.

Regras:
- Seja claro, direto e técnico quando necessário
- Não forneça aconselhamento financeiro personalizado
- Sempre destaque riscos quando falar de estratégias
- Prefira explicações educacionais em vez de recomendações diretas
- Se não souber, diga explicitamente que não sabe
- Seja breve e simples na sua respostas. Não use mais do que 3 frases.
"""


CLASSIFIER_PROMPT = """
Classifique a pergunta do usuário em apenas uma destas intenções:
- conceitos_investimentos
- produtos_investimentos

Use:
- conceitos_investimentos: quando o usuário quer entender definições, fundamentos, riscos,
  indicadores, estratégias, funcionamento do mercado ou educação financeira em geral.
- produtos_investimentos: quando o usuário pergunta sobre tipos de produtos financeiros,
  compara produtos, quer saber como funciona um produto específico, vantagens, desvantagens
  ou características de produtos como CDB, Tesouro Direto, fundos, ações, FIIs etc.

Responda apenas com uma das duas opções exatas.
"""


CONCEITOS_PROMPT = """
Você é um agente especializado em conceitos de investimentos.
Explique conceitos, fundamentos e funcionamento do mercado de forma clara e educacional.
Não forneça recomendações personalizadas.
Sempre destaque riscos quando relevante.
"""


PRODUTOS_PROMPT = """
Você é um agente especializado em produtos de investimentos.
Explique produtos financeiros, suas características, diferenças, riscos, liquidez, tributação
e cenários de uso de forma educacional.
Não forneça recomendações personalizadas.
Sempre destaque riscos quando relevante.
"""


class InvestmentState(MessagesState):
    intent: str
    selected_agent: str


def create_graph():
    llm = ChatOpenAI(
        model="gpt-5.4-mini",
        temperature=0,
    )

    def get_last_human_message(messages):
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message
        return None

    def classify_intent(state: InvestmentState):
        last_human_message = get_last_human_message(state["messages"])

        if last_human_message is None:
            return {"intent": "conceitos_investimentos"}

        response = llm.invoke(
            [
                SystemMessage(content=CLASSIFIER_PROMPT),
                HumanMessage(content=last_human_message.content),
            ]
        )

        intent = response.content.strip()
        if intent not in {"conceitos_investimentos", "produtos_investimentos"}:
            intent = "conceitos_investimentos"

        return {"intent": intent}

    def conceitos_agent(state: InvestmentState):
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                SystemMessage(content=CONCEITOS_PROMPT),
                *state["messages"],
            ]
        )
        return {
            "selected_agent": "conceitos_agent",
            "messages": [response],
        }

    def produtos_agent(state: InvestmentState):
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                SystemMessage(content=PRODUTOS_PROMPT),
                *state["messages"],
            ]
        )
        return {
            "selected_agent": "produtos_agent",
            "messages": [response],
        }

    def route_intent(
        state: InvestmentState,
    ) -> Literal["conceitos_agent", "produtos_agent"]:
        if state["intent"] == "produtos_investimentos":
            return "produtos_agent"
        return "conceitos_agent"

    builder = StateGraph(InvestmentState)

    builder.add_node("classify_intent", classify_intent)
    builder.add_node("conceitos_agent", conceitos_agent)
    builder.add_node("produtos_agent", produtos_agent)

    builder.add_edge(START, "classify_intent")
    builder.add_conditional_edges("classify_intent", route_intent)
    builder.add_edge("conceitos_agent", END)
    builder.add_edge("produtos_agent", END)

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph
