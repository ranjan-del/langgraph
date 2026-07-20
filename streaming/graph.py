"""streaming — stream tokens and graph events.

The graph is designed to be consumed with ``.stream()``. A node emits word-by-
word "tokens" through a custom stream writer, and node-level state updates are
observable via ``stream_mode="updates"``. Fully offline and deterministic — no
model calls, no API keys.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.config import get_stream_writer


class State(TypedDict):
    prompt: str
    answer: str


def respond(state: State) -> dict:
    """Emit each word as a custom stream token, then return the full answer."""
    writer = get_stream_writer()
    words = f"echo: {state['prompt']}".split()
    for word in words:
        writer({"token": word})
    return {"answer": " ".join(words)}


def build_graph():
    """Build and compile a graph intended to be consumed via .stream()."""
    builder = StateGraph(State)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile()


def stream_tokens(prompt: str) -> list:
    """Run the graph and collect the streamed custom tokens in order."""
    graph = build_graph()
    tokens = []
    for chunk in graph.stream(
        {"prompt": prompt, "answer": ""}, stream_mode="custom"
    ):
        tokens.append(chunk["token"])
    return tokens


if __name__ == "__main__":
    graph = build_graph()
    print("streaming custom tokens:")
    for chunk in graph.stream(
        {"prompt": "hello world", "answer": ""}, stream_mode="custom"
    ):
        print("  token:", chunk["token"])
    print("streaming updates:")
    for chunk in graph.stream(
        {"prompt": "hello world", "answer": ""}, stream_mode="updates"
    ):
        print("  update:", chunk)
