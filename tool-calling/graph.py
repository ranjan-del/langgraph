"""tool-calling — bind tools and route through a ToolNode.

Scaffold only. See MEMORY.md: "tool calling" in the Goal section.
"""

from typing import TypedDict

# TODO: from langgraph.graph import StateGraph, START, END
# TODO: from langgraph.prebuilt import ToolNode, tools_condition
# TODO: from langchain_core.tools import tool


# TODO: @tool
def example_tool(query: str) -> str:
    """Example tool the model can call."""
    # TODO: implement a real tool (search, calculator, etc.).
    raise NotImplementedError("example_tool is a scaffold stub")


class State(TypedDict):
    # TODO: define fields; typically a message list for the agent loop.
    messages: list


def agent(state: State) -> dict:
    # TODO: call the tool-bound model and return its message.
    raise NotImplementedError("agent is a scaffold stub")


def build_graph():
    """Build and compile the tool-calling (ReAct-style) graph."""
    # TODO: tools = [example_tool]
    # TODO: builder = StateGraph(State)
    # TODO: builder.add_node("agent", agent)
    # TODO: builder.add_node("tools", ToolNode(tools))
    # TODO: builder.add_edge(START, "agent")
    # TODO: builder.add_conditional_edges("agent", tools_condition)
    # TODO: builder.add_edge("tools", "agent")
    # TODO: return builder.compile()
    raise NotImplementedError("build_graph is a scaffold stub")


if __name__ == "__main__":
    print("tool-calling scaffold — not yet implemented")
