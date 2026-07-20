"""human-approval — human-in-the-loop interrupt.

The graph prepares an action, then pauses (``interrupt_before``) so a human can
inspect and approve it before it executes. A checkpointer stores the paused
state; the human updates ``approved`` and resumes with ``invoke(None, config)``.
Fully offline and deterministic — no model calls, no API keys.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    proposed_action: str
    approved: bool
    outcome: str


def prepare_action(state: State) -> dict:
    """Draft the action that requires human approval."""
    return {"proposed_action": f"delete file '{state['proposed_action']}'"}


def execute_action(state: State) -> dict:
    """Execute only if the human approved; otherwise record a cancellation."""
    if state.get("approved"):
        return {"outcome": f"EXECUTED: {state['proposed_action']}"}
    return {"outcome": f"CANCELLED: {state['proposed_action']}"}


def build_graph():
    """Build and compile the graph with an interrupt before execution."""
    builder = StateGraph(State)
    builder.add_node("prepare_action", prepare_action)
    builder.add_node("execute_action", execute_action)
    builder.add_edge(START, "prepare_action")
    builder.add_edge("prepare_action", "execute_action")
    builder.add_edge("execute_action", END)
    return builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["execute_action"],
    )


def run_demo(approve: bool, thread_id: str) -> dict:
    """Run the graph, pause at the interrupt, apply a human decision, resume."""
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    # First pass runs up to (but not through) execute_action, then stops.
    graph.invoke({"proposed_action": "notes.txt", "approved": False}, config)
    # Human review: record the decision into the paused state.
    graph.update_state(config, {"approved": approve})
    # Resume: passing None continues from the checkpoint.
    return graph.invoke(None, config)


if __name__ == "__main__":
    print("human-approval result (approved):", run_demo(True, "approve-thread"))
    print("human-approval result (rejected):", run_demo(False, "reject-thread"))
