from __future__ import annotations

from typing import TypedDict, Literal, Any
from sqlalchemy.orm import Session

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from crewai import Agent, Task, Crew
import autogen

from app.chat.tools import get_hours, get_location, search_menu, get_item
from app.chat.memory import load_state, save_state
from app.settings import settings

class ChatState(TypedDict, total=False):
    user_id: int
    conversation_id: int
    intent: Literal["delivery", "reservation", "info", "menu"]
    input: str
    messages: list[Any]
    response: str

def _llm():
    return ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)

def classify_intent(state: ChatState) -> ChatState:
    llm = _llm()
    prompt = (
        "Classify intent into one of: delivery, reservation, info, menu.\n"
        f"User message: {state['input']}\nReturn only the label."
    )
    label = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
    if label not in {"delivery", "reservation", "info", "menu"}:
        label = "info"
    state["intent"] = label  # type: ignore
    return state

def route(state: ChatState) -> str:
    return state.get("intent", "info")  # type: ignore

def handle_info(state: ChatState) -> ChatState:
    llm = _llm()
    ctx = f"Hours: {get_hours()}\nLocation: {get_location()}\n"
    msg = f"{ctx}\nUser: {state['input']}\nAnswer briefly and accurately."
    out = llm.invoke([HumanMessage(content=msg)]).content
    state["response"] = out
    return state

def handle_menu(state: ChatState, db: Session) -> ChatState:
    llm = _llm()
    # Lightweight tool use via LLM instruction (kept deterministic)
    items = search_menu(db, query=state["input"])
    msg = (
        "You are a restaurant assistant. Use the following menu search results.\n"
        f"Results: {items}\n"
        "Recommend up to 3 items and ask a clarification if needed."
    )
    out = llm.invoke([HumanMessage(content=msg)]).content
    state["response"] = out
    return state

def handle_delivery_with_crewai(state: ChatState) -> ChatState:
    # CrewAI can handle sales/upsell language; tools kept server-side in real implementation.
    sales_agent = Agent(
        role="Sales Agent",
        goal="Increase conversions while respecting user preferences.",
        backstory="Expert at upsell combos and confirming order details.",
        verbose=False,
    )
    task = Task(
        description=f"User wants delivery/order help. Message: {state['input']}. "
                    "Ask for missing details: address, items, customizations, payment instructions.",
        expected_output="A clear, step-by-step message confirming cart and next questions.",
        agent=sales_agent,
    )
    crew = Crew(agents=[sales_agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    state["response"] = str(result)
    return state

def handle_reservation_with_autogen(state: ChatState) -> ChatState:
    # AutoGen for negotiation-style dialog; in production, wrap with strict tool calls.
    assistant = autogen.AssistantAgent(
        name="ReservationAgent",
        llm_config={"model": "gpt-4o-mini", "api_key": settings.OPENAI_API_KEY},
        system_message="You book restaurant tables. Ask for date, time, party size, name, phone (optional)."
    )
    user = autogen.UserProxyAgent(name="User", human_input_mode="NEVER")
    user.initiate_chat(assistant, message=state["input"])
    # Take the last assistant message
    last = assistant.chat_messages[user][-1]["content"]
    state["response"] = last
    return state

def build_graph(db: Session, user_id: int, conversation_id: int):
    graph = StateGraph(ChatState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("info", handle_info)
    graph.add_node("delivery", handle_delivery_with_crewai)
    graph.add_node("reservation", handle_reservation_with_autogen)
    graph.add_node("menu", lambda s: handle_menu(s, db))

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges("classify_intent", route, {
        "info": "info",
        "delivery": "delivery",
        "reservation": "reservation",
        "menu": "menu",
    })

    for n in ["info", "delivery", "reservation", "menu"]:
        graph.add_edge(n, END)

    return graph.compile()

def run_chat_turn(db: Session, user_id: int, conversation_id: int, text: str) -> str:
    # Per-user exclusive state in Redis
    state_cache = load_state(user_id, conversation_id)
    messages = state_cache.get("messages", [])
    messages.append({"role": "user", "content": text})

    graph = build_graph(db, user_id, conversation_id)
    out_state = graph.invoke({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "input": text,
        "messages": messages,
    })

    messages.append({"role": "assistant", "content": out_state["response"]})
    save_state(user_id, conversation_id, {"messages": messages})
    return out_state["response"]
