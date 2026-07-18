"""conditional-graph — routing with conditional edges.

Scaffold only. See MEMORY.md: "conditionals" in the Goal section.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define fields; include whatever the router keys off of.
    value: int


def branch_a(state: State) -> dict:
    # TODO: implement branch A.
    raise NotImplementedError("branch_a is a scaffold stub")


def branch_b(state: State) -> dict:
    # TODO: implement branch B.
    raise NotImplementedError("branch_b is a scaffold stub")


def route(state: State) -> str:
    """Return the name of the next node based on state."""
    # TODO: return "branch_a" or "branch_b" depending on state.
    raise NotImplementedError("route is a scaffold stub")


def build_graph():
    """Build and compile the conditional graph."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("branch_a", branch_a)
    # TODO: builder.add_node("branch_b", branch_b)
    # TODO: builder.add_conditional_edges(START, route)
    # TODO: builder.add_edge("branch_a", END)
    # TODO: builder.add_edge("branch_b", END)
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("conditional-graph scaffold — not yet implemented")
