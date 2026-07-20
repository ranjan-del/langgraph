"""supervisor — supervisor routing to worker nodes.

A supervisor node inspects the remaining work and dispatches to a specialized
worker; each worker returns control to the supervisor, which eventually signals
FINISH. Fully offline and deterministic — no model calls, no API keys.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    text: str
    pending: list            # worker names still to run, in order
    results: Annotated[list, operator.add]
    next: str


def supervisor(state: State) -> dict:
    """Pick the next worker from the pending queue, or FINISH when empty."""
    pending = state["pending"]
    if not pending:
        return {"next": "FINISH"}
    return {"next": pending[0], "pending": pending[1:]}


def worker_upper(state: State) -> dict:
    """Worker A: uppercase the text."""
    result = state["text"].upper()
    return {"text": result, "results": [f"upper -> {result}"]}


def worker_reverse(state: State) -> dict:
    """Worker B: reverse the text."""
    result = state["text"][::-1]
    return {"text": result, "results": [f"reverse -> {result}"]}


def route_supervisor(state: State) -> str:
    """Return the next worker name, or the END sentinel."""
    return END if state["next"] == "FINISH" else state["next"]


def build_graph():
    """Build and compile the supervisor graph."""
    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor)
    builder.add_node("worker_upper", worker_upper)
    builder.add_node("worker_reverse", worker_reverse)
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {"worker_upper": "worker_upper", "worker_reverse": "worker_reverse", END: END},
    )
    builder.add_edge("worker_upper", "supervisor")
    builder.add_edge("worker_reverse", "supervisor")
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke(
        {
            "text": "hello",
            "pending": ["worker_upper", "worker_reverse"],
            "results": [],
            "next": "",
        }
    )
    print("supervisor result:", result)
