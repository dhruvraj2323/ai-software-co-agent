# AI Software Co-Agent — Security Threat Model & Operations Runbook

This document details the threat modeling, defensive controls, and operational security incident runbook for the **AI Software Co-Agent** runtime.

---

## 1. Threat Model & Attack Vectors

| Threat Vector | Attack Scenario | Mitigation Control | Spec Reference |
|---|---|---|---|
| **Prompt Injection** | Adversarial comments or README text attempting to instruct the model to exfiltrate files or execute unauthorized commands. | Non-authoritative repository provenance (`AuthorityLayer.L7_EXTERNAL`). LLM prompt outputs cannot grant permissions or modify policies. | ST-INJ-001, ADM-014 |
| **Workspace Escape / Path Traversal** | Patches or read requests targeting `../../etc/passwd` or `C:\Windows\System32`. | Strict `require_path_within_workspace` canonicalization and symlink target resolution. Escape attempts raise `WorkspaceEscapeError`. | ST-SBX-001, ADM-008 |
| **Shell Chaining & Command Injection** | Command execution arguments containing `;`, `&&`, `|`, `` ` ``, `$()`, or interpreter escapes (`python -c`). | `ProcessExecutor` tokenizes all commands via `shlex`. Shell chaining syntax and interpreter switching are rejected with `SHELL_CHAINING_DISALLOWED`. | ST-EXE-001, ADM-010 |
| **Protected File Tampering** | Agent modifying `.git/`, `.env`, SSH keys, or cloud credentials. | `ProtectedPathPolicy` blocks any read/write/modify/delete on sensitive path patterns, returning `FS_PROTECTED_PATH`. | ST-SBX-003, ADM-024 |
| **MCP Authority Elevation** | Compromised MCP server returning payloads claiming filesystem or process authority. | `McpAdapter` treats all tool output as untrusted external data (`ToolOrigin.MCP`). All invocations route through `ToolGateway` with audit hooks. | ST-MCP-001, ADM-012 |
| **User Change Overwrite** | Agent overwriting uncommitted user modifications or stash. | Pre-flight dirty tree check in `GitAdapter` and base hash checking in `PatchEngine`. Conflicting patches are aborted with `PATCH_STALE_HASH`. | ST-GIT-001, ADM-020 |
| **Recovery Infinite Loop** | Persistent build failure triggering infinite self-healing loops. | Hard budget limits in `FailureRecoveryService` (max retry count = 3, max token budget). Violations halt with `BUDGET_EXHAUSTED`. | ADM-018, Gate G7 |

---

## 2. Invariant Security Policies

1. **Single Tool Gateway**: No tool, script, or model can execute side effects without passing through `ToolGateway.route()` and `PolicyEvaluator.evaluate()`.
2. **Fail Closed**: Any ambiguous, unclassifiable, or malformed request is rejected immediately with an audit log entry.
3. **Audit Trail**: Every tool invocation records request UUID, correlation ID, tool ID, arguments, outcome, and timestamp in structured event logs.

---

## 3. Security Incident Response Runbook

### Scenario A: Unintended Command Execution Attempt
1. **Detection**: `PolicyEvaluator` denies request or logs `APPROVAL_DENIED`.
2. **Action**: The runtime raises `PolicyViolationError`, increments task error count, and halts the task.
3. **Verification**: Inspect `.coagent/audit.jsonl` for the task UUID to review command arguments and source.

### Scenario B: Dirty Working Tree Detection
1. **Detection**: `GitAdapter.get_status().is_clean == False`.
2. **Action**: Runtime halts task execution before applying patches.
3. **Resolution**: Direct the user to commit or stash local edits (`git stash`) before running Co-Agent tasks.

### Scenario C: Emergency Abort
1. **CLI Abort**:
   ```bash
   coagent cancel <task_id> --reason "Emergency security stop"
   ```
2. **Process Kill**: If the runtime daemon is unresponsive, terminate the process.
3. **Workspace Verification**: Inspect `git status` to confirm no partial patches remain uncommitted.

