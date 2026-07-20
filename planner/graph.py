"""planner — plan-and-execute.

A planner node decomposes an objective into an ordered list of steps; an
executor runs one step per turn and loops until the plan is exhausted. Fully
offline and deterministic — no model calls, no API keys.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    objective: str
    plan: list
    cursor: int
    results: Annotated[list, operator.add]


# A tiny deterministic "planner": maps known objectives to concrete steps.
_PLAYBOOK = {
    "make tea": ["boil water", "add tea leaves", "steep 3 min", "pour"],
}


def planner(state: State) -> dict:
    """Decompose the objective into an ordered list of steps."""
    steps = _PLAYBOOK.get(
        state["objective"].lower(),
        [f"analyze '{state['objective']}'", "act", "verify"],
    )
    return {"plan": steps, "cursor": 0}


def executor(state: State) -> dict:
    """Execute the step at the current cursor and advance."""
    idx = state["cursor"]
    step = state["plan"][idx]
    return {"cursor": idx + 1, "results": [f"step {idx + 1}: done '{step}'"]}


def route_after_step(state: State) -> str:
    """Continue executing while steps remain, otherwise finish."""
    return "executor" if state["cursor"] < len(state["plan"]) else END


def build_graph():
    """Build and compile the plan-and-execute graph."""
    builder = StateGraph(State)
    builder.add_node("planner", planner)
    builder.add_node("executor", executor)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_conditional_edges(
        "executor", route_after_step, {"executor": "executor", END: END}
    )
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke(
        {"objective": "make tea", "plan": [], "cursor": 0, "results": []}
    )
    print("planner objective:", result["objective"])
    print("planner plan:", result["plan"])
    for line in result["results"]:
        print(" ", line)
