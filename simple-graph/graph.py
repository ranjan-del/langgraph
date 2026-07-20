"""simple-graph — minimal linear StateGraph.

The smallest possible LangGraph: a single node wired START -> node -> END.
Runs fully offline and deterministically — no model calls, no API keys.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def node(state: State) -> dict:
    """Single node: read the incoming message and return a partial update."""
    return {"message": f"Hello, {state['message']}!"}


def build_graph():
    """Build and compile the minimal linear graph (START -> node -> END)."""
    builder = StateGraph(State)
    builder.add_node("node", node)
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({"message": "world"})
    print("simple-graph result:", result)
