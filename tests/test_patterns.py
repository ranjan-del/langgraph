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
    module = load("multi-agent")
    result = module.build_graph().invoke(module.initial_state("python"))
    assert "created by Guido van Rossum" in result["summary"]
    # researcher, writer, reviewer (rejects), writer, reviewer (approves).
    assert len(result["messages"]) == 5


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


# ---------------------------------------------------------------------------
# Second test per pattern: the edge case or mechanism the happy path skips.
# The tests above prove each graph produces the right answer once; these prove
# the branching, looping and safety behaviour that makes each pattern a pattern.
# ---------------------------------------------------------------------------


def test_simple_graph_node_is_a_pure_partial_update():
    """The node returns only the keys it changes, not a whole new state."""
    module = load("simple-graph")
    assert module.node({"message": "you"}) == {"message": "Hello, you!"}


def test_conditional_graph_router_picks_the_branch_name():
    """The router is a plain function, so it can be unit tested on its own."""
    module = load("conditional-graph")
    assert module.route({"value": 0, "label": ""}) == "branch_even"
    assert module.route({"value": -3, "label": ""}) == "branch_odd"


def test_memory_threads_are_isolated():
    """Two thread_ids on one compiled graph must not see each other's state."""
    graph = load("memory").build_graph()
    a = {"configurable": {"thread_id": "alice"}}
    b = {"configurable": {"thread_id": "bob"}}
    graph.invoke({"history": ["hi from alice"]}, a)
    graph.invoke({"history": ["hi from alice again"]}, a)
    bob_state = graph.invoke({"history": ["hi from bob"]}, b)
    assert bob_state["turns"] == 1
    assert len(bob_state["history"]) == 2
    assert graph.get_state(a).values["turns"] == 2


def test_human_approval_actually_pauses_before_executing():
    """The first invoke must stop at the interrupt with execute_action pending."""
    graph = load("human-approval").build_graph()
    config = {"configurable": {"thread_id": "pause-thread"}}
    paused = graph.invoke({"proposed_action": "notes.txt", "approved": False}, config)
    # prepare_action ran, execute_action did not, so there is no outcome yet.
    assert paused["proposed_action"] == "delete file 'notes.txt'"
    assert not paused.get("outcome")
    assert graph.get_state(config).next == ("execute_action",)


def test_supervisor_finishes_immediately_when_nothing_is_pending():
    """An empty queue must route straight to END without running a worker."""
    graph = load("supervisor").build_graph()
    result = graph.invoke(
        {"text": "hello", "pending": [], "results": [], "next": ""}
    )
    assert result["next"] == "FINISH"
    assert result["results"] == []
    assert result["text"] == "hello"


def test_planner_falls_back_to_a_generic_plan():
    """An objective missing from the playbook still gets an executable plan."""
    graph = load("planner").build_graph()
    result = graph.invoke(
        {"objective": "ship the feature", "plan": [], "cursor": 0, "results": []}
    )
    assert result["plan"] == ["analyze 'ship the feature'", "act", "verify"]
    assert result["cursor"] == len(result["plan"]) == len(result["results"])


def test_reflection_respects_the_iteration_cap():
    """A target the generator cannot reach must stop at MAX_ITERATIONS."""
    module = load("reflection")
    graph = module.build_graph()
    # One word is added per pass, so an unreachable target forces the cap.
    module.TARGET_WORDS = module.MAX_ITERATIONS + 10
    result = graph.invoke(
        {"topic": "cats", "draft": "", "critique": "", "iterations": 0}
    )
    assert result["iterations"] == module.MAX_ITERATIONS
    assert result["critique"].startswith("too short")


def test_multi_agent_reviewer_sends_the_draft_back_once():
    """The writer/reviewer conditional edge must genuinely fire, not be dead."""
    module = load("multi-agent")
    result = module.build_graph().invoke(module.initial_state("langgraph"))
    # Two writer passes: the initial draft plus one reviewer-requested revision.
    assert result["revisions"] == 2
    assert result["review_note"] == ""
    assert result["summary"].endswith("(2 facts)")
    assert result["messages"][-1] == "reviewer: approved"
    assert result["revisions"] <= module.MAX_REVISIONS


def test_multi_agent_handles_an_unknown_topic():
    """An unknown topic degrades to the placeholder fact, not a crash."""
    module = load("multi-agent")
    result = module.build_graph().invoke(module.initial_state("quantum basketry"))
    assert result["facts"] == ["no facts found"]
    assert result["summary"] == "quantum basketry: no facts found (1 facts)"


def test_tool_calling_rejects_unsafe_expressions():
    """The calculator is AST-validated, so non-arithmetic input must raise."""
    module = load("tool-calling")
    with pytest.raises(ValueError):
        module.calculator.invoke({"expression": "__import__('os').getcwd()"})


def test_tool_calling_loop_terminates_after_one_tool_call():
    """tools_condition must route to END once the agent stops asking for tools."""
    module = load("tool-calling")
    from langchain_core.messages import HumanMessage

    result = module.build_graph().invoke({"messages": [HumanMessage(content="2 + 3")]})
    assert result["messages"][-1].content == "The answer is 5."
    # Human, AI tool request, ToolMessage, final AI: exactly one loop.
    assert [m.__class__.__name__ for m in result["messages"]] == [
        "HumanMessage",
        "AIMessage",
        "ToolMessage",
        "AIMessage",
    ]


def test_streaming_updates_mode_reports_per_node_deltas():
    """The same compiled graph supports a second stream_mode without changes."""
    graph = load("streaming").build_graph()
    chunks = list(
        graph.stream({"prompt": "hi there", "answer": ""}, stream_mode="updates")
    )
    assert chunks == [{"respond": {"answer": "echo: hi there"}}]
