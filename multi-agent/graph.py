"""multi-agent: collaborating agents with handoffs.

Three agents share one message list: a researcher gathers facts, a writer turns
them into a summary, and a reviewer accepts the summary or hands it back to the
writer with a revision note. Fully offline and deterministic, with no model
calls and no API keys.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END

# A tiny deterministic "knowledge base" the researcher draws from.
_FACTS = {
    "python": ["created by Guido van Rossum", "released in 1991", "dynamically typed"],
    "langgraph": ["builds stateful graphs", "supports conditional edges"],
}

# The reviewer insists that a summary cite how many facts it rests on. The
# writer only adds that citation once it has been asked to, which is what makes
# the writer <-> reviewer handoff observable instead of dead code.
CITATION = "({count} facts)"

# Hard cap so a reviewer that never accepts cannot spin the graph forever.
MAX_REVISIONS = 3


class State(TypedDict):
    topic: str
    messages: Annotated[list, operator.add]
    facts: list
    summary: str
    review_note: str
    revisions: int


def _citation(facts: list) -> str:
    """Render the citation marker the reviewer looks for."""
    return CITATION.format(count=len(facts))


def agent_researcher(state: State) -> dict:
    """Researcher: look up facts about the topic and record them."""
    facts = _FACTS.get(state["topic"].lower(), ["no facts found"])
    return {
        "facts": facts,
        "messages": [f"researcher: found {len(facts)} fact(s)"],
    }


def agent_writer(state: State) -> dict:
    """Writer: compose a summary, honouring any note the reviewer sent back."""
    summary = f"{state['topic']}: " + "; ".join(state["facts"])
    if state.get("review_note"):
        # Second pass: the reviewer asked for a source citation, so add one.
        summary = f"{summary} {_citation(state['facts'])}"
        note = f"writer: revised for '{state['review_note']}'"
    else:
        note = "writer: summary composed"
    return {
        "summary": summary,
        "messages": [note],
        "revisions": state.get("revisions", 0) + 1,
    }


def agent_reviewer(state: State) -> dict:
    """Reviewer: accept the summary, or write a note asking for a revision."""
    if _citation(state["facts"]) in state["summary"]:
        return {"review_note": "", "messages": ["reviewer: approved"]}
    note = "cite how many facts the summary is based on"
    return {"review_note": note, "messages": [f"reviewer: {note}"]}


def route_handoff(state: State) -> str:
    """Hand back to the writer while the reviewer objects, else finish."""
    if state["review_note"] and state["revisions"] < MAX_REVISIONS:
        return "agent_writer"
    return END


def build_graph():
    """Build and compile the multi-agent graph."""
    builder = StateGraph(State)
    builder.add_node("agent_researcher", agent_researcher)
    builder.add_node("agent_writer", agent_writer)
    builder.add_node("agent_reviewer", agent_reviewer)
    builder.add_edge(START, "agent_researcher")
    builder.add_edge("agent_researcher", "agent_writer")
    builder.add_edge("agent_writer", "agent_reviewer")
    builder.add_conditional_edges(
        "agent_reviewer", route_handoff, {"agent_writer": "agent_writer", END: END}
    )
    return builder.compile()


def initial_state(topic: str) -> dict:
    """Build a complete starting state for the given topic."""
    return {
        "topic": topic,
        "messages": [],
        "facts": [],
        "summary": "",
        "review_note": "",
        "revisions": 0,
    }


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke(initial_state("python"))
    for msg in result["messages"]:
        print(" ", msg)
    print("multi-agent revisions:", result["revisions"])
    print("multi-agent summary:", result["summary"])
