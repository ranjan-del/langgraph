"""supervisor — supervisor routing to worker nodes.

Scaffold only. See MEMORY.md: "supervisor/planner/reflection" in the Goal.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define fields; e.g. task, accumulated results, next worker.
    task: str
    results: list


def supervisor(state: State) -> dict:
    # TODO: decide which worker runs next (or signal FINISH).
    raise NotImplementedError("supervisor is a scaffold stub")


def worker_a(state: State) -> dict:
    # TODO: implement worker A capability.
    raise NotImplementedError("worker_a is a scaffold stub")


def worker_b(state: State) -> dict:
    # TODO: implement worker B capability.
    raise NotImplementedError("worker_b is a scaffold stub")


def route_supervisor(state: State) -> str:
    """Return the next worker name, or END sentinel, based on supervisor state."""
    # TODO: return "worker_a" | "worker_b" | END
    raise NotImplementedError("route_supervisor is a scaffold stub")


def build_graph():
    """Build and compile the supervisor graph."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("supervisor", supervisor)
    # TODO: builder.add_node("worker_a", worker_a)
    # TODO: builder.add_node("worker_b", worker_b)
    # TODO: builder.add_edge(START, "supervisor")
    # TODO: builder.add_conditional_edges("supervisor", route_supervisor)
    # TODO: builder.add_edge("worker_a", "supervisor")
    # TODO: builder.add_edge("worker_b", "supervisor")
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("supervisor scaffold — not yet implemented")
