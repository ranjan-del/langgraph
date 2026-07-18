"""simple-graph — minimal linear StateGraph.

Scaffold only. See MEMORY.md checklist:
  - "Each folder: runnable graph code + Architecture + Flow Diagram + Explanation"
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define the fields carried through the graph.
    message: str


def node(state: State) -> dict:
    """Single node: read state, return a partial update."""
    # TODO: implement the node logic (return a dict merged into State).
    raise NotImplementedError("simple-graph node is a scaffold stub")


def build_graph():
    """Build and compile the minimal linear graph (START -> node -> END)."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("node", node)
    # TODO: builder.add_edge(START, "node")
    # TODO: builder.add_edge("node", END)
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    # TODO: graph = build_graph()
    # TODO: print(graph.invoke({"message": "hello"}))
    print("simple-graph scaffold — not yet implemented")
