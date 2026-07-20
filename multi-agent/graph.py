"""multi-agent — collaborating agents with handoffs.

Two agents share a message list: a researcher gathers facts, then hands off to
a writer that composes a summary from those facts. Fully offline and
deterministic — no model calls, no API keys.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END

# A tiny deterministic "knowledge base" the researcher draws from.
_FACTS = {
    "python": ["created by Guido van Rossum", "released in 1991", "dynamically typed"],
    "langgraph": ["builds stateful graphs", "supports conditional edges"],
}


class State(TypedDict):
    topic: str
    messages: Annotated[list, operator.add]
    facts: list
    summary: str


def agent_researcher(state: State) -> dict:
    """Researcher: look up facts about the topic and record them."""
    facts = _FACTS.get(state["topic"].lower(), ["no facts found"])
    return {
        "facts": facts,
        "messages": [f"researcher: found {len(facts)} fact(s)"],
    }


def agent_writer(state: State) -> dict:
    """Writer: compose a one-line summary from the researcher's facts."""
    summary = f"{state['topic']}: " + "; ".join(state["facts"])
    return {"summary": summary, "messages": ["writer: summary composed"]}


def route_handoff(state: State) -> str:
    """After the writer produces a summary, the collaboration is finished."""
    return END if state.get("summary") else "agent_writer"


def build_graph():
    """Build and compile the multi-agent graph."""
    builder = StateGraph(State)
    builder.add_node("agent_researcher", agent_researcher)
    builder.add_node("agent_writer", agent_writer)
    builder.add_edge(START, "agent_researcher")
    builder.add_edge("agent_researcher", "agent_writer")
    builder.add_conditional_edges(
        "agent_writer", route_handoff, {"agent_writer": "agent_writer", END: END}
    )
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke(
        {"topic": "python", "messages": [], "facts": [], "summary": ""}
    )
    for msg in result["messages"]:
        print(" ", msg)
    print("multi-agent summary:", result["summary"])
