"""conditional-graph — routing with conditional edges.

A router function inspects the state and picks one of two branches. Runs fully
offline and deterministically — no model calls, no API keys.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    value: int
    label: str


def branch_even(state: State) -> dict:
    """Handle the even branch."""
    return {"label": f"{state['value']} is even"}


def branch_odd(state: State) -> dict:
    """Handle the odd branch."""
    return {"label": f"{state['value']} is odd"}


def route(state: State) -> str:
    """Return the name of the next node based on state."""
    return "branch_even" if state["value"] % 2 == 0 else "branch_odd"


def build_graph():
    """Build and compile the conditional graph."""
    builder = StateGraph(State)
    builder.add_node("branch_even", branch_even)
    builder.add_node("branch_odd", branch_odd)
    builder.add_conditional_edges(
        START, route, {"branch_even": "branch_even", "branch_odd": "branch_odd"}
    )
    builder.add_edge("branch_even", END)
    builder.add_edge("branch_odd", END)
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    for value in (4, 7):
        result = graph.invoke({"value": value, "label": ""})
        print("conditional-graph result:", result)
