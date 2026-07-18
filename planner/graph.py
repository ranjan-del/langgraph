"""planner — plan-and-execute.

Scaffold only. See MEMORY.md: "supervisor/planner/reflection" in the Goal.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # TODO: define fields; e.g. objective, plan (list of steps), results.
    objective: str
    plan: list
    results: list


def planner(state: State) -> dict:
    # TODO: decompose the objective into an ordered list of steps.
    raise NotImplementedError("planner is a scaffold stub")


def executor(state: State) -> dict:
    # TODO: execute the current step and record its result.
    raise NotImplementedError("executor is a scaffold stub")


def route_after_step(state: State) -> str:
    """Decide whether to continue executing, replan, or finish."""
    # TODO: return "executor" | "planner" | END
    raise NotImplementedError("route_after_step is a scaffold stub")


def build_graph():
    """Build and compile the plan-and-execute graph."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("planner", planner)
    # TODO: builder.add_node("executor", executor)
    # TODO: builder.add_edge(START, "planner")
    # TODO: builder.add_edge("planner", "executor")
    # TODO: builder.add_conditional_edges("executor", route_after_step)
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("planner scaffold — not yet implemented")
