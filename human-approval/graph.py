"""human-approval — human-in-the-loop interrupt.

Scaffold only. See MEMORY.md: "human-in-the-loop" in the Goal section.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END
# TODO: from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    # TODO: define fields; e.g. the proposed action awaiting approval.
    proposed_action: str
    approved: bool


def prepare_action(state: State) -> dict:
    # TODO: draft the action that requires human approval.
    raise NotImplementedError("prepare_action is a scaffold stub")


def execute_action(state: State) -> dict:
    # TODO: execute only after human approval.
    raise NotImplementedError("execute_action is a scaffold stub")


def build_graph():
    """Build and compile the graph with an interrupt before execution."""
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("prepare_action", prepare_action)
    # TODO: builder.add_node("execute_action", execute_action)
    # TODO: builder.add_edge(START, "prepare_action")
    # TODO: builder.add_edge("prepare_action", "execute_action")
    # TODO: builder.add_edge("execute_action", END)
    # TODO: checkpointer = MemorySaver()
    # TODO: return builder.compile(
    # TODO:     checkpointer=checkpointer,
    # TODO:     interrupt_before=["execute_action"],
    # TODO: )
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("human-approval scaffold — not yet implemented")
