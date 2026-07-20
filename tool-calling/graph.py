"""tool-calling — bind tools and route through a ToolNode.

A ReAct-style loop: the agent decides whether a tool is needed; if so, the real
``ToolNode`` executes the tool call and the result flows back to the agent,
which then produces a final answer. The "model" here is a deterministic rule
that emits genuine tool-call messages, so the example runs with no API key.
"""

import ast
import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression and return the result."""
    node = ast.parse(expression, mode="eval")
    allowed = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
        ast.USub, ast.UAdd,
    )
    for sub in ast.walk(node):
        if not isinstance(sub, allowed):
            raise ValueError(f"unsupported expression: {expression!r}")
    return str(eval(compile(node, "<calc>", "eval")))  # noqa: S307 - AST-validated


TOOLS = [calculator]


class State(TypedDict):
    messages: Annotated[list, operator.add]


def agent(state: State) -> dict:
    """Deterministic 'model': request the calculator, then finalize the answer."""
    last = state["messages"][-1]
    # If the tool already produced a result, wrap it as the final answer.
    if last.__class__.__name__ == "ToolMessage":
        return {"messages": [AIMessage(content=f"The answer is {last.content}.")]}
    # Otherwise, treat the human input as an arithmetic query and call the tool.
    expression = last.content
    call = {"name": "calculator", "args": {"expression": expression}, "id": "call_1"}
    return {"messages": [AIMessage(content="", tool_calls=[call])]}


def build_graph():
    """Build and compile the tool-calling (ReAct-style) graph."""
    builder = StateGraph(State)
    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({"messages": [HumanMessage(content="6 * 7")]})
    for msg in result["messages"]:
        print(f"  {msg.__class__.__name__}: {msg.content!r} tool_calls={getattr(msg, 'tool_calls', [])}")
    print("tool-calling final:", result["messages"][-1].content)
