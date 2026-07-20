"""Deterministic tests for every LangGraph pattern.

Each pattern folder is named with a hyphen, so its ``graph.py`` is loaded by
file path via ``importlib`` rather than a normal import. Every test runs a graph
end to end and asserts on its output — no API keys, no network.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

PATTERNS = [
    "simple-graph",
    "conditional-graph",
    "memory",
    "human-approval",
    "supervisor",
    "planner",
    "reflection",
    "multi-agent",
    "tool-calling",
    "streaming",
]


def load(pattern: str):
    """Load a pattern's graph.py as a module object."""
    path = REPO_ROOT / pattern / "graph.py"
    spec = importlib.util.spec_from_file_location(f"{pattern}_graph", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("pattern", PATTERNS)
def test_build_graph_is_implemented(pattern):
    """Every pattern exposes a build_graph() that compiles without raising."""
    module = load(pattern)
    graph = module.build_graph()
    assert graph is not None


def test_simple_graph():
    graph = load("simple-graph").build_graph()
    result = graph.invoke({"message": "world"})
    assert result["message"] == "Hello, world!"


def test_conditional_graph_even_and_odd():
    graph = load("conditional-graph").build_graph()
    assert graph.invoke({"value": 4, "label": ""})["label"] == "4 is even"
    assert graph.invoke({"value": 7, "label": ""})["label"] == "7 is odd"


def test_memory_persists_across_invokes():
    graph = load("memory").build_graph()
    config = {"configurable": {"thread_id": "t1"}}
    graph.invoke({"history": ["hello"]}, config)
    state = graph.invoke({"history": ["again"]}, config)
    assert state["turns"] == 2
    # History accumulates: 2 user messages + 2 replies.
    assert len(state["history"]) == 4


def test_human_approval_approved_and_rejected():
    module = load("human-approval")
    approved = module.run_demo(True, "yes-thread")
    rejected = module.run_demo(False, "no-thread")
    assert approved["outcome"].startswith("EXECUTED")
    assert rejected["outcome"].startswith("CANCELLED")


def test_supervisor_runs_all_workers():
    graph = load("supervisor").build_graph()
    result = graph.invoke(
        {
            "text": "hello",
            "pending": ["worker_upper", "worker_reverse"],
            "results": [],
            "next": "",
        }
    )
    assert result["next"] == "FINISH"
    assert result["results"] == ["upper -> HELLO", "reverse -> OLLEH"]
    assert result["text"] == "OLLEH"


def test_planner_executes_full_plan():
    graph = load("planner").build_graph()
    result = graph.invoke(
        {"objective": "make tea", "plan": [], "cursor": 0, "results": []}
    )
    assert len(result["plan"]) == 4
    assert len(result["results"]) == 4
    assert result["cursor"] == 4


def test_reflection_converges():
    graph = load("reflection").build_graph()
    result = graph.invoke(
        {"topic": "cats", "draft": "", "critique": "", "iterations": 0}
    )
    assert result["critique"] == "OK"
    assert len(result["draft"].split()) >= 5
    assert result["iterations"] <= 5


def test_multi_agent_handoff():
    graph = load("multi-agent").build_graph()
    result = graph.invoke(
        {"topic": "python", "messages": [], "facts": [], "summary": ""}
    )
    assert "created by Guido van Rossum" in result["summary"]
    assert len(result["messages"]) == 2


def test_tool_calling_uses_toolnode():
    module = load("tool-calling")
    from langchain_core.messages import HumanMessage

    graph = module.build_graph()
    result = graph.invoke({"messages": [HumanMessage(content="6 * 7")]})
    final = result["messages"][-1]
    assert final.content == "The answer is 42."
    # A genuine ToolMessage must appear in the trace.
    assert any(m.__class__.__name__ == "ToolMessage" for m in result["messages"])


def test_streaming_emits_tokens_in_order():
    module = load("streaming")
    tokens = module.stream_tokens("hello world")
    assert tokens == ["echo:", "hello", "world"]
