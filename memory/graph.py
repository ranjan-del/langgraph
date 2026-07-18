"""memory — persistence via a checkpointer.

Scaffold only. See MEMORY.md: "memory" in the Goal, and
"Shared env/deps (API keys via .env)".
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END
# TODO: from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    # TODO: define fields; e.g. an accumulating message history.
    history: list


def respond(state: State) -> dict:
    # TODO: read prior state and return an update (appended to history).
    raise NotImplementedError("respond is a scaffold stub")


def build_graph():
    """Build and compile the graph with a checkpointer."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("respond", respond)
    # TODO: builder.add_edge(START, "respond")
    # TODO: builder.add_edge("respond", END)
    # TODO: checkpointer = MemorySaver()
    # TODO: return builder.compile(checkpointer=checkpointer)
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    # TODO: graph = build_graph()
    # TODO: config = {"configurable": {"thread_id": "demo"}}
    # TODO: graph.invoke({"history": []}, config)
    print("memory scaffold — not yet implemented")
