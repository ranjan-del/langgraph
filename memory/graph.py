"""memory — persistence via a checkpointer.

A single node appends to a running history. A `MemorySaver` checkpointer keyed
by ``thread_id`` makes state persist across separate ``invoke`` calls, so the
graph "remembers" earlier turns. Fully offline and deterministic — no model
calls, no API keys.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    # ``operator.add`` reducer appends each turn instead of overwriting.
    history: Annotated[list, operator.add]
    turns: int


def respond(state: State) -> dict:
    """Read the latest user message and append an echoed response."""
    latest = state["history"][-1] if state["history"] else "(nothing)"
    turn = state.get("turns", 0) + 1
    return {"history": [f"turn {turn} reply: heard '{latest}'"], "turns": turn}


def build_graph():
    """Build and compile the graph with an in-memory checkpointer."""
    builder = StateGraph(State)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    graph = build_graph()
    config = {"configurable": {"thread_id": "demo"}}
    for user_msg in ("hello", "how are you", "bye"):
        state = graph.invoke({"history": [user_msg]}, config)
        print("memory result:", state)
    print("final history length:", len(state["history"]))
