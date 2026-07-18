"""multi-agent — collaborating agents with handoffs.

Scaffold only. See MEMORY.md: "multi-agent" in the Goal section.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define shared fields; e.g. an appended message list.
    messages: list


def agent_researcher(state: State) -> dict:
    # TODO: implement the researcher agent role.
    raise NotImplementedError("agent_researcher is a scaffold stub")


def agent_writer(state: State) -> dict:
    # TODO: implement the writer agent role.
    raise NotImplementedError("agent_writer is a scaffold stub")


def route_handoff(state: State) -> str:
    """Decide the next agent (or finish) based on shared state."""
    # TODO: return "agent_researcher" | END
    raise NotImplementedError("route_handoff is a scaffold stub")


def build_graph():
    """Build and compile the multi-agent graph."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("agent_researcher", agent_researcher)
    # TODO: builder.add_node("agent_writer", agent_writer)
    # TODO: builder.add_edge(START, "agent_researcher")
    # TODO: builder.add_edge("agent_researcher", "agent_writer")
    # TODO: builder.add_conditional_edges("agent_writer", route_handoff)
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("multi-agent scaffold — not yet implemented")
