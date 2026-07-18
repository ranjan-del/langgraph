"""reflection — generate / critique / revise loop.

Scaffold only. See MEMORY.md: "supervisor/planner/reflection" in the Goal.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define fields; e.g. draft, critique, iteration count.
    draft: str
    critique: str
    iterations: int


def generate(state: State) -> dict:
    # TODO: produce or revise the draft (using critique if present).
    raise NotImplementedError("generate is a scaffold stub")


def reflect(state: State) -> dict:
    # TODO: critique the current draft against the goal.
    raise NotImplementedError("reflect is a scaffold stub")


def route_after_reflect(state: State) -> str:
    """Loop back to generate, or finish, based on the critique / iteration cap."""
    # TODO: return "generate" | END
    raise NotImplementedError("route_after_reflect is a scaffold stub")


def build_graph():
    """Build and compile the reflection graph."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("generate", generate)
    # TODO: builder.add_node("reflect", reflect)
    # TODO: builder.add_edge(START, "generate")
    # TODO: builder.add_edge("generate", "reflect")
    # TODO: builder.add_conditional_edges("reflect", route_after_reflect)
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("reflection scaffold — not yet implemented")
