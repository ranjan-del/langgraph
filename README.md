# langgraph

| | |
|---|---|
| **What it is** | Ten LangGraph patterns, one folder per pattern, built to be read as much as run |
| **Stack** | Python · LangGraph · deterministic stand-ins instead of a model provider |
| **Run it** | `python <pattern>/graph.py` for any of the ten; no API key |
| **Tests** | 32 (pytest), run in CI on every push |
| **Read first** | `simple-graph/`, then `conditional-graph/`, then `human-approval/` |

**Why it is written this way:** each folder holds one self-contained `graph.py` and a README with a mermaid diagram of the flow, so a pattern can be understood without tracing shared helpers. Running offline and deterministically means a graph's behaviour is a property of its structure rather than of what a model happened to say that day.

A teaching collection of ten LangGraph patterns, one folder per pattern, built to be read as
much as run. Every folder holds a single self-contained `graph.py` and a README that explains
the architecture, draws the flow as a mermaid diagram, and walks through the idea. The whole
repository runs offline and deterministically: there is no model provider, no API key and no
network call anywhere in it. That is a deliberate teaching choice. When a graph's "model" is a
five-line Python function you can predict exactly, the only thing left to study is LangGraph
itself, which is the point. It exists because the mechanics of LangGraph (state schemas,
reducers, conditional edges, checkpointers, interrupts, `ToolNode`, stream modes) are hard to
see through the noise of a real LLM, and because a deterministic example can be pinned down by
a test.

## Concepts demonstrated

- **State graphs**: a `TypedDict` state schema, node functions that return partial updates, and
  the `START` / `END` sentinels.
- **Reducers**: `Annotated[list, operator.add]` to accumulate across steps instead of
  overwriting, and why the choice of reducer is a design decision.
- **Conditional edges**: routing functions that pick the next node at runtime, and the same
  mechanism used to build bounded loops.
- **Persistence**: compiling with a checkpointer, `thread_id`-scoped state, and thread
  isolation across a single compiled graph.
- **Human in the loop**: `interrupt_before`, inspecting a paused run with `get_state`, editing
  it with `update_state`, and resuming with `invoke(None, config)`.
- **Orchestration shapes**: centralized routing (supervisor), plan then execute (planner),
  self critique (reflection), and peer handoff (multi-agent).
- **Tool calling**: real `@tool` definitions, real `AIMessage.tool_calls`, the prebuilt
  `ToolNode`, and `tools_condition` closing the ReAct loop.
- **Streaming**: `graph.stream` with `stream_mode="custom"` via `get_stream_writer`, and
  `stream_mode="updates"` for per-node deltas.
- **Loop safety**: every cycle in this repository has an explicit termination condition and,
  where a critic could stall, a hard iteration cap.
- **Testing graphs**: loading hyphenated pattern folders with `importlib`, unit testing router
  functions in isolation, and asserting on a full run trace.

## Architecture

The repository has no shared runtime. Each pattern is an island that imports only from
`langgraph` and `langchain_core`. The one thing that spans folders is the test suite, which
loads each `graph.py` by file path.

```mermaid
graph TD
    subgraph Core["Foundations"]
        A["simple-graph<br/>StateGraph, nodes, edges"]
        B["conditional-graph<br/>routing function"]
        C["memory<br/>MemorySaver, thread_id"]
        D["human-approval<br/>interrupt_before"]
    end
    subgraph Orch["Orchestration shapes"]
        E["supervisor<br/>central router"]
        F["planner<br/>plan then execute"]
        G["reflection<br/>generate / critique"]
        H["multi-agent<br/>peer handoff"]
    end
    subgraph Agentic["Agent runtime"]
        I["tool-calling<br/>ToolNode, tools_condition"]
        J["streaming<br/>stream modes"]
    end

    A --> B
    B --> C
    C --> D
    B --> E
    B --> F
    B --> G
    B --> H
    B --> I
    A --> J

    T["tests/test_patterns.py"] -. "importlib loads every graph.py" .-> Core
    T -. "" .-> Orch
    T -. "" .-> Agentic
    R["requirements.txt"] -. "langgraph + langchain-core" .-> Core
```

Arrows mean "teaches a prerequisite for", not "imports". Every folder is independently
runnable, and no folder imports another.

## Tech stack

| Component | Technology | Why this choice |
| --- | --- | --- |
| Graph runtime | `langgraph` (1.2.9) | The subject of the repository. Supplies `StateGraph`, `START` / `END`, `add_conditional_edges`, `compile()` and the `.stream()` API used by every pattern. |
| Stream writer | `langgraph.config.get_stream_writer` (part of `langgraph`) | Lets `streaming/graph.py` emit custom token chunks from inside a node without a real LLM, so `stream_mode="custom"` can be demonstrated offline. |
| Checkpointing | `langgraph-checkpoint` (4.1.1) | Provides `MemorySaver`, the in-process checkpointer that `memory/` and `human-approval/` compile with. In-memory keeps the examples dependency free, with no database to run. |
| Prebuilt agent parts | `langgraph-prebuilt` (1.1.0) | Supplies the genuine `ToolNode` and `tools_condition` used in `tool-calling/`, so that example shows the real ReAct wiring rather than a hand rolled imitation. |
| Message and tool types | `langchain-core` (1.4.9) | The `@tool` decorator plus `HumanMessage` / `AIMessage` / `ToolMessage`. These are the types `ToolNode` actually consumes, so the tool-calling trace is real. |
| State schema | `typing.TypedDict` and `typing.Annotated` (standard library) | LangGraph reads reducers off `Annotated` metadata. Using the standard library instead of Pydantic keeps each file readable in one screen. |
| Reducers | `operator.add` (standard library) | The accumulate-instead-of-overwrite reducer for list channels. No custom reducer code to explain. |
| Safe arithmetic | `ast` (standard library) | `tool-calling/graph.py` parses and allowlists AST node types before evaluating, so the calculator tool is a real tool without being a code execution hole. |
| Tests | `pytest` (9.1.1) | Parametrized coverage over all ten patterns plus per-pattern edge cases. |
| Test loading | `importlib.util` (standard library) | Folder names contain hyphens and so are not importable module names. Loading by file path is what makes the hyphenated, self-contained folder layout possible. |
| CI | GitHub Actions | Runs the same `pytest -q` on Python 3.11 and 3.12 on every push and pull request. |

Version numbers are the versions this README was verified against. `requirements.txt` pins
compatible ranges rather than exact versions.

## Folder structure

```
langgraph/
├── README.md                  # this index and walkthrough
├── LICENSE                    # MIT
├── requirements.txt           # langgraph, langgraph-checkpoint, langgraph-prebuilt, langchain-core, pytest
├── .env.example               # documents that no API key is needed, and where one would go
├── .gitignore                 # venv, caches, .env (but not .env.example)
├── .github/
│   └── workflows/ci.yml       # pytest on Python 3.11 and 3.12
├── tests/
│   └── test_patterns.py       # the entire suite: 32 tests across all ten patterns
├── simple-graph/              # minimal linear StateGraph: START -> node -> END
│   ├── README.md              # architecture, mermaid flow diagram, explanation
│   └── graph.py               # State, node, build_graph, runnable demo
├── conditional-graph/         # branching with add_conditional_edges and a router
│   ├── README.md
│   └── graph.py               # branch_even, branch_odd, route
├── memory/                    # persistence with MemorySaver keyed by thread_id
│   ├── README.md
│   └── graph.py               # respond node, operator.add history reducer
├── human-approval/            # pause with interrupt_before, resume after a decision
│   ├── README.md
│   └── graph.py               # prepare_action, execute_action, run_demo
├── supervisor/                # one router node dispatching to worker nodes
│   ├── README.md
│   └── graph.py               # supervisor, worker_upper, worker_reverse
├── planner/                   # decompose an objective, then execute step by step
│   ├── README.md
│   └── graph.py               # planner, executor, route_after_step
├── reflection/                # generate, critique, revise, with an iteration cap
│   ├── README.md
│   └── graph.py               # generate, reflect, route_after_reflect
├── multi-agent/               # researcher -> writer -> reviewer with a revision handoff
│   ├── README.md
│   └── graph.py               # agent_researcher, agent_writer, agent_reviewer
├── tool-calling/              # real ToolNode and tools_condition ReAct loop
│   ├── README.md
│   └── graph.py               # @tool calculator, agent, build_graph
└── streaming/                 # custom token stream and per-node update stream
    ├── README.md
    └── graph.py               # respond with get_stream_writer, stream_tokens
```

## Codebase walkthrough

Every pattern file follows the same three-part shape, so once you have read one you can skim
the rest: a `State` `TypedDict` at the top, plain node functions in the middle, and a
`build_graph()` that wires and compiles them, followed by an `if __name__ == "__main__"` demo.
Nodes always return a partial dict, never a full state. `build_graph()` is the single public
entry point of every module, which is what lets the test suite treat all ten uniformly.

### `simple-graph/graph.py`

The reference shape with nothing else in it. `State` has one field, `message`. `node(state)`
returns `{"message": f"Hello, {state['message']}!"}`, demonstrating that a node returns only
the keys it wants merged. `build_graph()` creates a `StateGraph(State)`, calls `add_node`, adds
`START -> node` and `node -> END` edges, and returns `builder.compile()`. Data flow: the dict
passed to `invoke` becomes the initial state, the node's return value is merged into it (a
plain overwrite, since `message` has no reducer), and the merged state is returned.

### `conditional-graph/graph.py`

Introduces runtime branching. `State` carries `value: int` and `label: str`. Two node functions,
`branch_even` and `branch_odd`, write a label. The important function is `route(state)`, which
is not a node at all: it returns the string name of the node to run next. `build_graph()` wires
it with `add_conditional_edges(START, route, {...})`, where the mapping translates the router's
return value into a node name, and both branches then edge to `END`. Because `route` is an
ordinary function of state, it is unit tested directly in
`test_conditional_graph_router_picks_the_branch_name` without building a graph at all. That
separation, routers as pure functions, is used by every later pattern.

### `memory/graph.py`

The first pattern with a reducer and a checkpointer. `State.history` is declared
`Annotated[list, operator.add]`, which tells LangGraph to concatenate rather than replace when
a node returns a `history` key. `respond(state)` reads `history[-1]` as the newest user message,
increments `turns`, and returns a one-element list that the reducer appends. The difference from
`simple-graph` is in `build_graph()`: it returns `builder.compile(checkpointer=MemorySaver())`.
Data flow across calls: each `invoke({"history": [msg]}, config)` merges the new message into the
snapshot restored from `config["configurable"]["thread_id"]`, runs the node, and writes a new
snapshot back. The `__main__` demo sends three messages on one thread and the history grows to
six entries (three user, three replies). `test_memory_threads_are_isolated` proves the other
half of the contract: a second `thread_id` on the same compiled graph starts from empty.

### `human-approval/graph.py`

Builds directly on the checkpointer. The graph itself is a plain two-node line,
`prepare_action -> execute_action`, with the pause supplied at compile time by
`compile(checkpointer=MemorySaver(), interrupt_before=["execute_action"])`. `prepare_action`
drafts the sensitive action into `proposed_action`; `execute_action` reads the `approved` flag
and writes either an `EXECUTED:` or a `CANCELLED:` outcome. `run_demo(approve, thread_id)` is
the piece worth reading, because it shows the full three-step human loop: the first
`invoke(initial_state, config)` runs `prepare_action` and stops, `graph.update_state(config,
{"approved": approve})` writes the human's decision into the paused snapshot, and
`graph.invoke(None, config)` resumes. Passing `None` is what tells LangGraph "no new input,
continue from the checkpoint". `test_human_approval_actually_pauses_before_executing` asserts
the middle state directly, checking that `graph.get_state(config).next == ("execute_action",)`
and that no outcome has been written yet.

### `supervisor/graph.py`

Centralized routing. `State` holds the working `text`, a `pending` list of worker names, an
accumulating `results` list, and a `next` slot the supervisor writes its decision into. The
`supervisor` node pops the head of `pending` into `next`, or writes `"FINISH"` when the queue is
empty. `worker_upper` and `worker_reverse` each transform `text` and append a line to `results`.
`route_supervisor(state)` translates `next` into either a worker name or the `END` sentinel, and
is wired with `add_conditional_edges("supervisor", route_supervisor, {...})`. Both workers edge
back to `supervisor`, which is what creates the loop. Data flow: START goes to the supervisor,
which dispatches, the worker mutates `text` and returns, and control comes back for the next
decision. Because each worker feeds the next one's input through `text`, the demo output
`OLLEH` is `hello` uppercased and then reversed, in that order.

### `planner/graph.py`

Separates deciding from doing. `_PLAYBOOK` is a module-level dict standing in for an LLM
planner, mapping a known objective to concrete steps. `planner(state)` looks the objective up
and falls back to a generic `analyze / act / verify` plan, returning `plan` and resetting
`cursor` to 0. `executor(state)` runs exactly the step at `cursor`, advances the cursor by one,
and appends to the accumulating `results`. The loop is `add_conditional_edges("executor",
route_after_step, ...)` where `route_after_step` returns `"executor"` while
`cursor < len(plan)` and `END` otherwise. The termination argument is easy to state, which is
why the pattern is written this way: `cursor` strictly increases and `plan` never changes, so
the loop is bounded by `len(plan)`.

### `reflection/graph.py`

A self-critique loop with an explicit cap. Two module constants, `TARGET_WORDS` and
`MAX_ITERATIONS`, define the goal and the safety limit. `generate(state)` appends one more
detail word to the draft and increments `iterations`; it is deliberately a weak generator so
several passes are needed. `reflect(state)` counts words and writes either `"OK"` or a
`"too short (n/N words)"` critique. `route_after_reflect(state)` sends control back to
`generate` unless the critique is `"OK"` or `iterations >= MAX_ITERATIONS`. That second clause
is the whole lesson: a critic that never approves must not be able to spin the graph forever.
`test_reflection_respects_the_iteration_cap` raises `TARGET_WORDS` beyond what the generator can
ever reach and asserts the run stops at `MAX_ITERATIONS` with a still-failing critique.

### `multi-agent/graph.py`

Peer handoff rather than central routing, and the one pattern with a genuine multi-pass loop
between two agents. `_FACTS` is a small offline knowledge base. `agent_researcher` fills `facts`
and posts to the shared `messages` list (itself an `operator.add` channel, which is how the
agents "see" each other). `agent_writer` joins the facts into a `summary`; if `review_note` is
non-empty it also appends the citation marker and reports that it revised. `agent_reviewer`
checks whether the summary contains `"(N facts)"` for the current fact count, and either
approves by clearing `review_note` or writes a note asking for the citation.
`route_handoff(state)` sends the work back to `agent_writer` while `review_note` is set and
`revisions < MAX_REVISIONS`, otherwise `END`. Because the first draft never carries the
citation, the reviewer always rejects once and approves on the second pass, so the conditional
edge is exercised on every single run instead of being decoration. `initial_state(topic)` is a
small helper that builds a complete starting dict, used by the demo and by both tests.

### `tool-calling/graph.py`

The only pattern that uses LangChain message objects, because `ToolNode` requires them.
`calculator` is a real `@tool`: it parses the expression with `ast.parse(..., mode="eval")`,
walks the tree and rejects any node type outside an arithmetic allowlist, then compiles and
evaluates. That allowlist is why a calculator tool can be shipped in a teaching repo at all, and
`test_tool_calling_rejects_unsafe_expressions` pins it by asserting that
`__import__('os').getcwd()` raises. `State.messages` is an `operator.add` list. The `agent` node
is a deterministic stand-in for a model: if the last message is a `ToolMessage` it wraps the
result as a final `AIMessage`, otherwise it emits an `AIMessage` with an actual `tool_calls`
entry naming the calculator. `build_graph()` then wires the genuine prebuilt pieces:
`ToolNode(TOOLS)` as the `tools` node, `add_conditional_edges("agent", tools_condition)` to
decide between the tool node and `END`, and a static `tools -> agent` edge to close the loop.
Data flow for one run: `HumanMessage("6 * 7")` goes to `agent`, which emits a tool call,
`tools_condition` routes to `ToolNode`, `ToolNode` executes the real tool and appends a
`ToolMessage("42")`, control returns to `agent`, which now sees a `ToolMessage` and answers, and
`tools_condition` finds no tool calls and routes to `END`.

### `streaming/graph.py`

Shows that streaming is a consumption concern, not a build concern: the graph here is the same
one-node line as `simple-graph`. Inside `respond(state)`, `get_stream_writer()` returns a writer
callable, and the node pushes one `{"token": word}` chunk per word before returning the joined
answer. Those chunks surface through `stream_mode="custom"`. `stream_tokens(prompt)` is a small
helper that builds the graph, iterates `graph.stream(..., stream_mode="custom")` and collects
the tokens in order, which is what the test asserts on. The `__main__` block runs the same
compiled graph twice under two different modes to make the contrast concrete: `"custom"` yields
the three word tokens, `"updates"` yields a single per-node delta
`{'respond': {'answer': 'echo: hello world'}}`.

### `tests/test_patterns.py`

One file, no conftest, no fixtures. `load(pattern)` uses
`importlib.util.spec_from_file_location` to execute a `graph.py` by path, which is required
because folder names like `simple-graph` are not legal module names. Every call to `load`
re-executes the module, so tests that mutate a module constant (the reflection cap test) cannot
leak into others. The suite has three layers: a `@pytest.mark.parametrize` over all ten
`PATTERNS` asserting `build_graph()` compiles, one happy-path test per pattern asserting the
real output, and a second block of per-pattern tests covering the branch, loop or safety
behaviour the happy path skips (thread isolation, the paused interrupt state, an empty
supervisor queue, the planner fallback plan, the reflection cap, the multi-agent revision loop
and an unknown topic, the calculator allowlist and ReAct loop termination, and the second
stream mode).

## Installation

Requires Python 3.11 or newer. Verified on Python 3.14.6, and CI runs 3.11 and 3.12.

```bash
# 1. Clone
git clone https://github.com/ranjan-del/langgraph.git
cd langgraph

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run any pattern
python simple-graph/graph.py

# 5. Run the test suite
pytest -q
```

There is no `.env` to fill in and no API key to obtain. `.env.example` exists only to document
that fact and to show where a key would go if you later swap a deterministic stand-in for a
real provider.

## Usage

Each pattern is a script. Run it directly and read the output next to the source. The output
below was captured from an actual run of each file.

```
$ python simple-graph/graph.py
simple-graph result: {'message': 'Hello, world!'}

$ python conditional-graph/graph.py
conditional-graph result: {'value': 4, 'label': '4 is even'}
conditional-graph result: {'value': 7, 'label': '7 is odd'}
```

Memory, showing state accumulating across three separate `invoke` calls on one `thread_id`:

```
$ python memory/graph.py
memory result: {'history': ['hello', "turn 1 reply: heard 'hello'"], 'turns': 1}
memory result: {'history': ['hello', "turn 1 reply: heard 'hello'", 'how are you', "turn 2 reply: heard 'how are you'"], 'turns': 2}
memory result: {'history': ['hello', "turn 1 reply: heard 'hello'", 'how are you', "turn 2 reply: heard 'how are you'", 'bye', "turn 3 reply: heard 'bye'"], 'turns': 3}
final history length: 6
```

Human approval, running the same graph twice with opposite human decisions:

```
$ python human-approval/graph.py
human-approval result (approved): {'proposed_action': "delete file 'notes.txt'", 'approved': True, 'outcome': "EXECUTED: delete file 'notes.txt'"}
human-approval result (rejected): {'proposed_action': "delete file 'notes.txt'", 'approved': False, 'outcome': "CANCELLED: delete file 'notes.txt'"}
```

Supervisor and planner, the two orchestration loops:

```
$ python supervisor/graph.py
supervisor result: {'text': 'OLLEH', 'pending': [], 'results': ['upper -> HELLO', 'reverse -> OLLEH'], 'next': 'FINISH'}

$ python planner/graph.py
planner objective: make tea
planner plan: ['boil water', 'add tea leaves', 'steep 3 min', 'pour']
  step 1: done 'boil water'
  step 2: done 'add tea leaves'
  step 3: done 'steep 3 min'
  step 4: done 'pour'
```

Reflection, looping until the critique passes:

```
$ python reflection/graph.py
reflection iterations: 5
reflection critique: OK
reflection draft: cats-detail1 cats-detail2 cats-detail3 cats-detail4 cats-detail5
```

Multi-agent, where the reviewer sends the draft back once before approving:

```
$ python multi-agent/graph.py
  researcher: found 3 fact(s)
  writer: summary composed
  reviewer: cite how many facts the summary is based on
  writer: revised for 'cite how many facts the summary is based on'
  reviewer: approved
multi-agent revisions: 2
multi-agent summary: python: created by Guido van Rossum; released in 1991; dynamically typed (3 facts)
```

Tool calling, printing the full message trace so the real `ToolMessage` is visible:

```
$ python tool-calling/graph.py
  HumanMessage: '6 * 7' tool_calls=[]
  AIMessage: '' tool_calls=[{'name': 'calculator', 'args': {'expression': '6 * 7'}, 'id': 'call_1', 'type': 'tool_call'}]
  ToolMessage: '42' tool_calls=[]
  AIMessage: 'The answer is 42.' tool_calls=[]
tool-calling final: The answer is 42.
```

Streaming, the same compiled graph consumed under two stream modes:

```
$ python streaming/graph.py
streaming custom tokens:
  token: echo:
  token: hello
  token: world
streaming updates:
  update: {'respond': {'answer': 'echo: hello world'}}
```

To use a pattern from your own code, import its `build_graph()` and invoke the compiled graph:

```python
import importlib.util

spec = importlib.util.spec_from_file_location("planner_graph", "planner/graph.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

graph = module.build_graph()
result = graph.invoke({"objective": "make tea", "plan": [], "cursor": 0, "results": []})
print(result["plan"])
```

## API reference

This repository is a reference collection, not a service. It exposes no HTTP API, no CLI flags
and no network listener, so there is no endpoint table to give. The public surface is the
`build_graph()` function in each folder plus a few per-pattern helpers.

| Pattern | Public surface | Invoke with | Returns |
| --- | --- | --- | --- |
| simple-graph | `build_graph()`, `node()` | `{"message": str}` | State with the greeting in `message` |
| conditional-graph | `build_graph()`, `route()` | `{"value": int, "label": ""}` | State with `label` set by the chosen branch |
| memory | `build_graph()` | `{"history": [str]}` plus a `config` with `thread_id` | State with accumulated `history` and `turns` |
| human-approval | `build_graph()`, `run_demo(approve, thread_id)` | `{"proposed_action": str, "approved": bool}` plus a `config` | State with `outcome` prefixed `EXECUTED:` or `CANCELLED:` |
| supervisor | `build_graph()` | `{"text", "pending", "results", "next"}` | State with `next == "FINISH"` and `results` per worker |
| planner | `build_graph()` | `{"objective", "plan", "cursor", "results"}` | State with the full `plan` and one result per step |
| reflection | `build_graph()` | `{"topic", "draft", "critique", "iterations"}` | State with the final `draft` and `critique` |
| multi-agent | `build_graph()`, `initial_state(topic)` | `initial_state("python")` | State with `summary`, `messages` and `revisions` |
| tool-calling | `build_graph()`, `calculator` | `{"messages": [HumanMessage(...)]}` | State whose `messages` end in the final `AIMessage` |
| streaming | `build_graph()`, `stream_tokens(prompt)` | `{"prompt": str, "answer": ""}` | Consumed with `.stream()`; `stream_tokens` returns a token list |

Compiling with a checkpointer (memory and human-approval) means those two graphs require a
`config` containing `{"configurable": {"thread_id": ...}}` on every call. The other eight do
not take a config.

## Testing

```bash
pytest -q
```

Observed result on the current tree:

```
$ .venv/bin/python -m pytest -q
................................                                         [100%]
32 passed in 0.22s
```

That is 32 tests: 10 from the parametrized compile check, 10 happy-path tests (one per
pattern), and 12 edge-case tests covering branching, looping, isolation and safety behaviour.
Every pattern has at least three tests against it. The suite needs no network and no API key,
and it also passes from a clean virtual environment built only from `requirements.txt`, which
was verified before publishing these numbers.

CI runs the same command on Python 3.11 and 3.12 via
[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) on every push and pull request to
`main`.

## Design decisions and trade-offs

**Deterministic stand-ins instead of a real LLM.** Every "model" in this repository is a small
Python function. The benefit is that examples run offline in milliseconds, are byte-for-byte
reproducible, and can be asserted on precisely, so the tests actually test LangGraph wiring
rather than tolerating model variance. The cost is honesty about scope: you learn the graph
mechanics here, not prompt engineering, and nothing in these files tells you how a real model
behaves when it decides not to call the tool you expected.

**One flat file per pattern.** No shared `common/` package, no base classes, and some
duplication between folders (`State`, `build_graph`, the `__main__` block). Deduplicating would
be better engineering and worse teaching: a reader could not open one file and see the whole
pattern. Independent runnability was an explicit requirement, and it is worth the repetition.

**Hyphenated folder names.** These read better in a listing than `simple_graph`, but they are
not importable, which is why the test suite loads modules by file path with `importlib`. The
trade-off was accepted once, in one helper function, rather than compromising the folder names.

**`TypedDict` over Pydantic for state.** LangGraph supports both. `TypedDict` with
`Annotated[list, operator.add]` shows the reducer mechanism with no extra dependency and no
validation layer between the reader and the state. The trade-off is no runtime validation: pass
a wrong-typed value and it flows straight through.

**`MemorySaver` rather than a SQLite or Postgres checkpointer.** In-process persistence keeps
installation to one `pip install` with no service to run. It also means state vanishes when the
process exits, so the memory and human-approval examples cannot demonstrate a run that pauses
across a restart, which is the more realistic human-in-the-loop scenario.

**Real `ToolNode`, fake model.** In `tool-calling/` the tool, the message types, the `ToolNode`
and `tools_condition` are all genuine LangGraph and LangChain components. Only the model is
substituted. This was chosen over faking the whole loop so the ReAct trace you see printed is
the real one, including a real `ToolMessage`.

**Every loop has a hard cap.** Reflection has `MAX_ITERATIONS`, multi-agent has
`MAX_REVISIONS`, planner and supervisor terminate on a strictly advancing cursor or a draining
queue. Even where a loop provably terminates on its logic, the cap is stated explicitly because
unbounded cycles are the most common way a real LangGraph application fails.

**The multi-agent reviewer always rejects the first draft.** This is contrived on purpose. A
conditional handoff edge that never fires is indistinguishable from a straight pipeline, so the
acceptance criterion was chosen to guarantee the loop is exercised on every run and can be
asserted on in a test.

## Limitations and future improvements

This is teaching material, not a production system, and it should not be treated as one.

- **No real model anywhere.** Swapping any stand-in for an actual provider will change error
  handling, latency, retries, token costs and non-determinism in ways this repository does not
  cover at all.
- **No async.** Everything uses the synchronous `invoke` and `stream` APIs. Real services want
  `ainvoke` and `astream`, and the `messages` stream mode for genuine LLM token streaming is
  never shown, because there are no LLM tokens to stream.
- **No durable persistence.** `MemorySaver` is in-process only. A restart loses every thread,
  so nothing here demonstrates resuming a paused approval hours later, which is the actual
  point of human-in-the-loop in production.
- **No error handling, retries or timeouts.** A node that raises simply propagates. Node
  retry policies, fallbacks and error edges are not demonstrated.
- **The calculator tool is allowlisted but still uses `eval`.** The AST walk restricts node
  types to arithmetic before evaluating, which is sound for the demo, but no attempt has been
  made to harden it against resource exhaustion (for example `9**9**9`).
- **The planner cannot re-plan.** `route_after_step` only loops back to the executor. A real
  plan-and-execute agent revises the plan when a step fails, and adding that edge is the most
  useful next extension.
- **Subgraphs, `Send` and map-reduce fan-out are not covered.** Nor are streaming from within
  subgraphs, node caching, or time-travel via checkpoint history, all of which are real
  LangGraph features a complete tour would include.
- **No type checking or linting in CI.** Only `pytest` runs. Adding `ruff` and `mypy` would
  raise the bar on a repository whose main product is readable code.
- **Diagrams are mermaid source only.** They render on GitHub but not in every markdown
  viewer, and they are maintained by hand, so they can drift from the code if a graph changes.

Candidate next steps, roughly in order of value: add an optional live variant of each pattern
behind an environment flag, add a durable SQLite checkpointer variant of `memory/`, wire the
re-planning edge into `planner/`, add async and `messages`-mode streaming, and add a subgraph
and `Send` fan-out pattern as an eleventh folder.

## License

Released under the [MIT License](./LICENSE).
