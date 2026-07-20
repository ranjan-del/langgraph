"""reflection — generate / critique / revise loop.

A generator writes a draft, a reflector critiques it, and the graph loops back
to regenerate until the critique is satisfied or an iteration cap is hit. Fully
offline and deterministic — no model calls, no API keys.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

TARGET_WORDS = 5
MAX_ITERATIONS = 5


class State(TypedDict):
    topic: str
    draft: str
    critique: str
    iterations: int


def generate(state: State) -> dict:
    """Produce or extend the draft, using the prior critique as guidance."""
    words = state["draft"].split() if state["draft"] else []
    # Each pass adds one more detail word about the topic — a deterministic
    # stand-in for an LLM revising toward the critique.
    words.append(f"{state['topic']}-detail{len(words) + 1}")
    return {"draft": " ".join(words), "iterations": state.get("iterations", 0) + 1}


def reflect(state: State) -> dict:
    """Critique the current draft against the length goal."""
    count = len(state["draft"].split())
    if count >= TARGET_WORDS:
        return {"critique": "OK"}
    return {"critique": f"too short ({count}/{TARGET_WORDS} words)"}


def route_after_reflect(state: State) -> str:
    """Loop back to generate, or finish when good enough / capped."""
    if state["critique"] == "OK" or state["iterations"] >= MAX_ITERATIONS:
        return END
    return "generate"


def build_graph():
    """Build and compile the reflection graph."""
    builder = StateGraph(State)
    builder.add_node("generate", generate)
    builder.add_node("reflect", reflect)
    builder.add_edge(START, "generate")
    builder.add_edge("generate", "reflect")
    builder.add_conditional_edges(
        "reflect", route_after_reflect, {"generate": "generate", END: END}
    )
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke(
        {"topic": "cats", "draft": "", "critique": "", "iterations": 0}
    )
    print("reflection iterations:", result["iterations"])
    print("reflection critique:", result["critique"])
    print("reflection draft:", result["draft"])
