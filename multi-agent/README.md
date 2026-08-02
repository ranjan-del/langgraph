# multi-agent

Multiple specialized **agents collaborate**, handing off control and sharing state to solve a
task no single agent owns end to end.

## Architecture

- Each agent is a node (often itself a small sub-graph) with a distinct role.
- Agents communicate through shared state: an appended `messages` list plus the working
  artifacts (`facts`, `summary`, `review_note`).
- Handoff edges (static or conditional) pass control between agents.
- A `MAX_REVISIONS` cap bounds the writer/reviewer loop so it always terminates.

## Flow Diagram

```mermaid
graph TD
    START((START)) --> A[agent_researcher]
    A --> B[agent_writer]
    B --> C[agent_reviewer]
    C --> H{review_note set<br/>and under cap?}
    H -->|yes: revise| B
    H -->|no: approved or capped| END((END))
```

## Explanation

Where the supervisor pattern centralizes routing, a multi-agent graph distributes it: agents
hand off directly to one another, each contributing its specialty (research, writing, review,
and so on) and reading the shared conversation state. Handoffs can be fixed pipelines or
conditional, allowing agents to send work back for revision. This models collaborative
workflows and is the basis for more elaborate agent networks.

Concretely: `agent_researcher` fills `facts`, `agent_writer` turns them into a `summary`, and
`agent_reviewer` checks that the summary cites how many facts it rests on. The first draft
never carries that citation, so the reviewer always sends the work back once; the writer sees
a non-empty `review_note` and adds the citation, and the second review approves. Running
`graph.py` therefore shows five messages and two writer passes, which is the handoff loop
made visible rather than described.
