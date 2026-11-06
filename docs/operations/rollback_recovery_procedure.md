# AI Software Co-Agent — Rollback & Recovery Procedure (T118)

This document establishes the operational procedures for reverting state, rolling back workspace modifications, and recovering from runtime corruptions.

---

## 1. Rollback Architecture & Primitives

The system maintains three independent state boundaries, each with deterministic rollback capabilities:

```
[ Workspace Filesystem ] <--- Atomic rollback via PatchEngine & GitAdapter
[ Task & Memory SQLite ] <--- Transaction rollback & Snapshot restore
[ Runtime Event Log    ] <--- Append-only audit trail
```

---

## 2. Standard Rollback Procedures

### Procedure 1: Workspace Modification Rollback (Patch Conflict or Task Failure)
When a patch application fails midway or is cancelled by a user:

1. **Automatic Mechanism**:
   The `PatchEngine` validates all target file hashes before applying modifications. If any file hash fails or a protected path violation occurs, **zero files are touched**.
2. **Manual Git Restoration**:
   If an in-progress task leaves unwanted files in the workspace:
   ```bash
   # Discard all unstaged modifications in workspace
   git restore .
   
   # Remove untracked files created by the task
   git clean -fd
   ```
3. **Verification**:
   Run `git status` to verify `working tree clean`.

---

### Procedure 2: Persistent SQLite Store Disaster Recovery
In the event of process crash during disk write, power loss, or database file corruption (`state.db`):

1. **Snapshot Backup**:
   The runtime automatically creates daily snapshots of `state.db` at `.coagent/backups/state_<timestamp>.db`.
2. **Recovery Steps**:
   ```bash
   # 1. Stop the runtime service
   coagent cancel --all
   
   # 2. Quarantine corrupted database
   mv .coagent/state.db .coagent/state_corrupted_<timestamp>.db
   
   # 3. Restore the latest known-good snapshot
   cp .coagent/backups/state_latest.db .coagent/state.db
   
   # 4. Restart runtime service and verify health
   coagent health
   ```
3. **Automated Verification**:
   Verified by `tests/release/test_rollback_procedure.py::test_sqlite_store_snapshot_disaster_recovery`.

---

### Procedure 3: Task Abort & Emergency Termination
To cleanly terminate an active execution loop:

1. **Via CLI**:
   ```bash
   coagent cancel <task_id> --reason "User requested immediate halt"
   ```
2. **Runtime Actions**:
   - `TaskStateMachine` transitions task state to `CANCELLED`.
   - Running subprocesses receive `SIGTERM` (or `TerminateProcess` on Windows).
   - In-flight patches are aborted.
   - Event log records `TASK_CANCELLED` with audit metadata.

---

## 3. Disaster Recovery Testing Matrix

| Component | Failure Mode | Recovery Mechanism | Verifying Test Suite |
|---|---|---|---|
| **PatchEngine** | Base hash conflict | Atomic abort prior to disk write | `test_atomic_patch_engine_rollback_on_conflict` |
| **SqliteStore** | File corruption | Snapshot restoration | `test_sqlite_store_snapshot_disaster_recovery` |
| **Git Working Tree** | Dirty tree on startup | Immediate execution halt | `test_git_working_tree_rollback_safeguards` |
| **Subprocess** | Hang / Infinite loop | Timeout enforcement & kill | `test_process_execution_timeout_enforced` |

