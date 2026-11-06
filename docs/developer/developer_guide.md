# AI Software Co-Agent — Developer Guide

This guide explains the architecture, layering principles, development workflow, and testing practices for contributors to the **AI Software Co-Agent** codebase.

---

## 1. System Architecture & Layering

The system enforces strict unidirectional dependencies and layer isolation. Components at lower layers never depend on or take direction from higher or external layers.

### The 8 Authority Layers (L0 to L7)

Precedence is numeric (`L0 = 100` down to `L7 = 10`):

| Layer | Priority | Name | Description |
|---|---|---|---|
| **L0** | `100` | **Security / Sandbox** | Hard system constraints, path containment, shell injection prevention, protected files (`.git`, `.env`). Cannot be bypassed. |
| **L1** | `90` | **Task State** | Authoritative lifecycle states (`TaskRecord`, `TaskState`). Transitions are strictly monotonic. |
| **L2** | `80` | **Repository Truth** | Files on disk inside the verified workspace scope. Read via `RepositoryDiscoveryService`. |
| **L3** | `70` | **Git State** | Branch, commit, and index clean/dirty status verified via `GitAdapter`. |
| **L4** | `60` | **Validation & Gates** | Authoritative quality gates (`ValidationRunner`, `CompletionGate`). Dictates task completion. |
| **L5** | `40` | **Project Memory** | Persistent memory records (`SqliteMemoryStore`). Strictly non-authoritative advisory context. |
| **L6** | `30` | **Task Memory** | Ephemeral, task-scoped scratchpad and plan steps. Non-authoritative. |
| **L7** | `10` | **External / Model** | LLM responses, user chat prompts, MCP external tools. Always treated as untrusted data. |

> [!IMPORTANT]
> External data (L7) or memory records (L5/L6) can never override repository state (L2) or security rules (L0).

---

## 2. Package Structure

```
src/coagent/
  agent/        # Core agent loop, state machine, and reasoning cycle
  artifacts/    # Artifact store and integrity verification
  context/      # Context packager, token budget manager, and relevance ranker
  core/         # Foundation types, error contracts, and event bus
  execution/    # Bounded filesystem, process runner, and atomic patch engine
  git/          # Safe Git inspection and staging adapter
  memory/       # SQLite persistent memory store and typed records
  models/       # Common Pydantic data contracts
  policy/       # Tool policy evaluator and human approval store
  recovery/     # Failure classifier and bounded auto-repair loop
  repo/         # Repository indexing, discovery, and AST symbol extraction
  runtime/      # Client-facing protocol service and event streamer
  security/     # Path security, shell sanitizer, and protected path policies
  tools/        # Tool registry, ToolGateway, and MCP adapter
  workspace/    # Workspace scope and path canonicalization

cli/coagent_cli/ # Rich terminal CLI client

vscode-extension/ # TypeScript VS Code Extension client
```

---

## 3. Extending the System

### Adding a New Tool
1. Define the tool's input/output schemas and register it in `ToolRegistry`:
   ```python
   tool_def = ToolDefinition(
       tool_id="custom.analyzer",
       version="1.0",
       input_schema={"type": "object", "properties": {"target": {"type": "string"}}},
       output_schema={"type": "object"},
       capability=ToolCapability.FILESYSTEM_READ,
       risk_level=ToolRiskLevel.LOW,
       side_effects=[ToolSideEffect.READ],
       resource_scope=ToolScope.WORKSPACE,
       approval_profile="auto",
       executor="custom_executor",
       origin=ToolOrigin.INTERNAL,
       enabled=True,
   )
   ```
2. Route tool execution strictly through `ToolGateway.route(request)`. Never invoke executors directly from agent logic.

### Adding an MCP Server
1. Use `McpAdapter.register_server(config)` and `McpAdapter.register_tool(tool_def, handler)`.
2. All MCP tools are assigned `ToolOrigin.MCP` and execute through the standard `ToolGateway` with audit hooks enabled.

---

## 4. Development Workflow & Verification

### Running Tests
Execute the entire regression suite:
```bash
uv run --no-sync pytest tests/ -q
```

Run a specific suite:
```bash
uv run --no-sync pytest tests/release/ -v
```

### Static Analysis & Linter
```bash
uv run --no-sync ruff check .
uv run --no-sync mypy src cli
```

### Automated CI Pipeline
Run the consolidated verification pipeline:
```bash
uv run --no-sync python scripts/ci/verify.py
```
This executes:
1. Ruff format and lint check
2. Mypy strict type check
3. Secret and security boundary scan
4. License & dependency review
5. Full release packaging (Wheel, Sdist, VS Code)
6. Isolated release verification and smoke test

