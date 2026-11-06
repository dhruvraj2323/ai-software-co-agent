# AI Software Co-Agent — User Guide

This guide describes how to install, configure, and use the **AI Software Co-Agent** via its Command Line Interface (CLI) and VS Code Extension.

---

## 1. Overview

The **AI Software Co-Agent** is an autonomous, policy-guarded software engineering co-agent designed to inspect repositories, formulate structured plans, apply atomic code modifications, run validations, and self-heal from failures within strict security and budget boundaries.

### Key Capabilities
- **Deterministic Workflows**: Multi-stage engineering loop (`DISCOVERY`, `PLANNING`, `APPROVAL`, `EXECUTION`, `VALIDATION`, `COMPLETION`).
- **Strict Capability Control**: Every privileged action (filesystem writes, subprocess execution, Git operations, MCP tool invocations) routes through a single `ToolGateway` and `PolicyEvaluator`.
- **Zero Hallucinated Authorities**: Memory, repository content, and LLM suggestions are strictly advisory and can never override security rules.
- **Atomic Modification & Rollback**: All file mutations use the `PatchEngine` with pre-flight base hash checks to ensure safe, conflict-free updates.

---

## 2. Installation & Prerequisites

### Prerequisites
- **Python**: 3.14.7
- **uv** (or pip)
- **Git**: 2.30+
- **VS Code**: 1.85+ (optional, for IDE integration)

### Installing from Release Wheel
Install the distribution wheel generated in `dist/`:

```bash
uv pip install dist/ai_software_co_agent-0.1.0-py3-none-any.whl
```

Verify installation:

```bash
coagent --help
coagent health
```

---

## 3. CLI Client Usage

The CLI client communicates with the runtime daemon via the local protocol service.

### Subcommands

#### `coagent plan <goal>`
Inspects the repository and generates an authoritative execution plan without modifying files:
```bash
coagent plan "Refactor authentication service to use environment-based secrets"
```

#### `coagent run <goal>`
Executes the full controlled engineering loop, requesting human approval when required:
```bash
coagent run "Add pagination and search filtering to user directory API"
```

#### `coagent status <task_id>`
Queries the authoritative status, stage, and event log for an active or completed task:
```bash
coagent status "b2394c8e-3a75-4d2c-806b-2f3471018c12"
```

#### `coagent diff <task_id>`
Displays the exact unified diff generated for a task:
```bash
coagent diff "b2394c8e-3a75-4d2c-806b-2f3471018c12"
```

#### `coagent approve <task_id> <approval_id> [--deny] [--reason <text>]`
Responds to a pending human-in-the-loop approval request (e.g. for high-risk operations or bash command execution):
```bash
# Allow
coagent approve "b2394c8e-3a75-4d2c-806b-2f3471018c12" "appr-001"

# Deny
coagent approve "b2394c8e-3a75-4d2c-806b-2f3471018c12" "appr-001" --deny --reason "Unsafe shell command"
```

#### `coagent cancel <task_id> [--reason <text>]`
Terminates an active task and halts all background workers immediately:
```bash
coagent cancel "b2394c8e-3a75-4d2c-806b-2f3471018c12" --reason "User requested stop"
```

#### `coagent config`
Outputs current client configuration, protocol version, and autonomy mode:
```bash
coagent config
```

#### `coagent health`
Verifies that the runtime service daemon is responsive and reports the active protocol version:
```bash
coagent health
```

---

## 4. VS Code Extension Integration

The VS Code extension connects directly to the Co-Agent runtime service.

### Features
1. **Interactive Chat Webview**: Submit engineering tasks, inspect agent reasoning steps, view streaming plan updates.
2. **Review & Approval Panel**: Review high-risk tool execution requests with single-click Allow/Deny actions.
3. **Diff View**: Inspect live workspace diffs before changes are committed.
4. **Diagnostics Panel**: View automated lint, test, and gate validation results.
5. **Status Bar Indicator**: Real-time status (`IDLE`, `PLANNING`, `EXECUTING`, `WAITING_FOR_APPROVAL`).

---

## 5. Security & Autonomy Modes

The agent operates under one of several configurable autonomy modes:

- `CHAT`: Read-only queries, no file or command modifications.
- `PLAN`: Generates plans and lists affected files; execution requires elevation.
- `SUPERVISED_AUTO` (Default): Executes non-destructive actions; requires explicit approval for shell commands, deletions, and high-risk operations.
- `RESTRICTED`: Strict read-only sandbox.

Protected files (`.git/`, `.env`, private keys, credentials) are permanently immutable and cannot be patched or deleted under any mode.

