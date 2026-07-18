"""streaming — stream tokens and graph events.

Scaffold only. See MEMORY.md: "streaming" in the Goal section.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define fields; e.g. a message list to stream tokens from.
    messages: list


def respond(state: State) -> dict:
    # TODO: produce output suitable for token streaming.
    raise NotImplementedError("respond is a scaffold stub")


def build_graph():
    """Build and compile a graph intended to be consumed via .stream()."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("respond", respond)
    # TODO: builder.add_edge(START, "respond")
    # TODO: builder.add_edge("respond", END)
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    # TODO: graph = build_graph()
    # TODO: for chunk in graph.stream({"messages": []}, stream_mode="messages"):
    # TODO:     print(chunk)
    print("streaming scaffold — not yet implemented")
