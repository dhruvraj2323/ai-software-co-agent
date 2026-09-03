AI SOFTWARE CO-AGENT

TECHNICAL DESIGN DOCUMENT

Version 1.0 — FINAL / LOCKED

Document ID: TDD-001 • Derived from PRD, SRS and System Architecture v1.0

| Field | Value |
| --- | --- |
| Document | Technical Design Document |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD v1.0 + SRS v1.0 + System Architecture v1.0 |
| Technology baseline | Technology & Implementation Decision Specification v1.0 |
| Repository baseline | Master Repository / Folder & File Blueprint v1.0 |
| Purpose | Define implementation-level modules, interfaces, data contracts, execution boundaries and technical behavior |

Lock Statement: This Technical Design v1.0 is the final locked implementation-level design baseline. Code must conform to its module boundaries, contracts, security path and execution model unless a formal change-control decision is approved.

# 1. Technical Design Objectives

This document translates the locked logical architecture into an implementable technical design for the local MVP. It defines package responsibilities, dependency direction, core contracts, persistence, execution, IPC, validation, recovery, observability and testing boundaries.

- Build a project-owned modular Python Agent Runtime.

- Use TypeScript only for the VS Code client boundary.

- Keep model/provider code behind an LLM Gateway.

- Keep all tools behind a single Tool Gateway and deterministic Policy Engine.

- Use Pydantic v2 for domain/tool/event validation.

- Use SQLite for local task/project/memory/index persistence.

- Use Tree-sitter and ripgrep for repository intelligence.

- Use subprocess + PowerShell behind controlled execution.

- Use Git CLI behind a controlled adapter.

- Use pytest, ruff and incremental mypy as engineering quality gates.

- Keep the MVP local and avoid unnecessary distributed infrastructure.

# 2. Technology Baseline

| Area | MVP technology/design | Boundary |
| --- | --- | --- |
| Core runtime | Python 3.12+ | src/ runtime only |
| Package/build | uv + pyproject.toml | Project environment |
| Models | Pydantic v2 | Domain/tool/event contracts |
| LLM | Custom LLM Gateway + provider adapter | Provider isolated |
| Initial provider | OpenAI-compatible adapter | Exact production model SKU remains runtime/config decision |
| Parsing | Tree-sitter | Language adapters |
| Search | ripgrep + structured index | Repository intelligence |
| Index/state | SQLite | Repository/task/project/memory state |
| Policy | Custom deterministic Python engine | Authoritative security boundary |
| Terminal | Python subprocess + PowerShell | Controlled executor |
| Sandbox | Windows workspace/process restrictions + pluggable interface | Execution boundary |
| Git | Git CLI adapter | Controlled Git access |
| Testing | pytest | Validation |
| Quality | ruff + incremental mypy | Static quality |
| Logging | Python logging + structured JSON events | Audit/observability |
| CLI | Typer | Headless client |
| VS Code | TypeScript extension | Thin client |
| VS Code IPC | Local process JSON-RPC over stdio | Runtime/client boundary |
| MCP | MCP-compatible adapter | Must enter Tool Gateway |
| Docs | Markdown source + approved DOCX artifacts | Versioned documentation |
| CI | GitHub Actions when hosted | Automated validation |

The technology baseline explicitly defers vector/semantic retrieval until evaluation demonstrates that lexical/structural retrieval is insufficient. The exact production model SKU remains configurable rather than permanently hard-coded.

# 3. Physical Module Mapping

ai-software-co-agent/

├── src/

│ ├── agent/ # orchestration, roles, state, lifecycle

│ ├── task/ # task domain and persistence services

│ ├── repository/ # scanner, search, index, symbols, map

│ ├── context/ # providers, ranking, budgeting, provenance

│ ├── llm/ # gateway, providers, capabilities

│ ├── tools/ # contracts, registry, gateway, built-ins

│ ├── policy/ # policy model, evaluator, decisions

│ ├── execution/ # workspace/process/sandbox executors

│ ├── testing/ # discovery, runner, results, completion gate

│ ├── recovery/ # errors, classifier, diagnosis, repair

│ ├── git/ # status/diff/checkpoint/rollback

│ ├── memory/ # task/project/session state

│ ├── audit/ # structured events/logging

│ └── reporting/ # final report generation

├── apps/

│ ├── cli/

│ └── vscode-extension/

├── tests/

│ ├── unit/

│ ├── integration/

│ ├── e2e/

│ ├── security/

│ └── evaluation/

├── config/

├── scripts/

├── examples/

├── artifacts/

└── docs/

The physical tree follows the repository blueprint: documentation, runtime source, clients, tests, configuration, scripts, examples and generated artifacts are separated. Implementation files should be introduced as their capability enters the active build phase.

# 4. Dependency Direction & Layer Rules

apps → runtime interfaces

agent/task → context/llm/tools/testing/recovery services

context → repository/memory/task sources

tools → policy + execution interfaces

policy → validated configuration/risk models (never LLM authority)

execution → OS/sandbox adapters

testing → execution/tool interfaces + validation contracts

recovery → testing/context/agent services

git → repository/OS adapter

memory → storage adapter

audit/reporting → domain events + persisted evidence

llm/providers → LLM gateway contracts

MCP adapter → Tool Gateway

VS Code → runtime client protocol

- No lower layer may call around the Policy Engine to obtain side effects.

- Model/provider adapters do not execute tools.

- MCP adapters do not directly call filesystem/process APIs.

- VS Code does not implement a second privileged execution path.

- Recovery does not bypass Tool Gateway, patch validation or Completion Gate.

- Rules/configuration cannot override hard security policy.

# 5. Core Domain Contracts

| Contract | Required fields / concepts | Validation |
| --- | --- | --- |
| Task | id, requirement, scope, acceptance_criteria, state, budgets, timestamps, outcome | Pydantic |
| Plan | task_id, steps, expected_changes, dependencies, risks, validation_gates | Pydantic |
| ToolDefinition | name, description, input_schema, capability, risk, side_effects, scope | Pydantic |
| ToolRequest | request_id, task_id, tool_name, arguments, correlation_id | Pydantic + tool schema |
| PolicyDecision | decision, rule_id, reason, scope, risk, approval requirement | Pydantic |
| ToolResult | request_id, success, output, error, duration, evidence_ref | Pydantic |
| ContextItem | source, content/reference, relevance, provenance, freshness | Pydantic |
| Patch | task_id, files, operations, base_hash/version, expected_scope | Pydantic |
| ValidationResult | gate, command, status, exit_code, stdout/stderr refs, duration | Pydantic |
| ErrorRecord | error_id, category, source, message, evidence_ref, context_ref | Pydantic |
| RecoveryAttempt | failure, diagnosis, repair_plan, patch_ref, result, attempt_no | Pydantic |
| GitState | baseline, status, diff_ref, checkpoint_ref, rollback_ref | Pydantic |
| AuditEvent | event_id, correlation_id, actor, action, target, result, timestamp | Pydantic |
| FinalReport | task, outcome, changes, validation, recovery, Git, blockers, evidence | Pydantic |

# 6. Task State Machine Implementation

| State | Entry | Allowed transitions |
| --- | --- | --- |
| CREATED | Task accepted | PLANNING, CANCELLED |
| PLANNING | Requirement/context/plan work | READY, BLOCKED, FAILED, CANCELLED |
| READY | Plan and prerequisites ready | IMPLEMENTING, BLOCKED, CANCELLED |
| IMPLEMENTING | Authorized mutation begins | VALIDATING, BLOCKED, FAILED, CANCELLED |
| VALIDATING | Required checks execute | COMPLETE, RECOVERING, FAILED, BLOCKED, CANCELLED |
| RECOVERING | Bounded diagnosis/repair | VALIDATING, BLOCKED, FAILED, CANCELLED |
| BLOCKED | Approval/dependency/safety block | READY, IMPLEMENTING, CANCELLED |
| FAILED | Unrecoverable failure | RECOVERING only if explicit recovery remains |
| COMPLETE | All required gates passed | Terminal |
| CANCELLED | Cancellation completed | Terminal |

State transitions are implemented by a dedicated state-machine/lifecycle service. Components must request transitions rather than mutating task state directly.

# 7. Agent Runtime & Orchestrator

The MVP uses one Agent Runtime process. Planner, Coder and Reviewer are logical roles implemented behind interfaces; they are not separate autonomous processes.

| Service | Technical responsibility | Dependencies |
| --- | --- | --- |
| TaskService | Create/load/update task, acceptance criteria, budgets | Task repository, models |
| Orchestrator | Execute state-driven engineering loop | Task, context, LLM, tools, validation, recovery |
| Planner | Generate structured plan | LLM Gateway, Context Engine |
| Coder | Generate patch/change proposal | LLM Gateway, Context Engine, patch contract |
| Reviewer | Review scope/diff/validation | Git, validation, context |
| LifecycleService | Enforce legal state transitions | Task state model |
| BudgetService | Enforce time/attempt/scope limits | Task/config |

- The Orchestrator is the only component that coordinates the complete lifecycle.

- The Orchestrator never directly calls OS APIs.

- Role outputs are validated before being consumed.

- An invalid model output is treated as an error, not as executable authority.

# 8. Repository Intelligence Design

| Module | Implementation | Responsibilities |
| --- | --- | --- |
| scanner | pathlib/filesystem adapter | Authorized tree/file discovery |
| search | ripgrep adapter | Fast lexical search |
| parser | Tree-sitter adapters | Syntax-aware parsing |
| symbols | Tree-sitter queries + language adapters | Classes/functions/modules |
| index | SQLite repository index | Persistent structural metadata |
| map | Custom repository-map service | Compact project representation |
| relationships | Index queries | Imports/references where supported |
| watch/invalidation | File metadata/hash tracking | Invalidate affected context/index data |

Repository indexing is incremental where practical. Language support expands through adapters; Tree-sitter is not a requirement that every language be supported on day one.

# 9. Context Engine Design

| Component | Technical behavior |
| --- | --- |
| Provider interface | All context sources return normalized ContextItem objects. |
| Repository provider | Queries repository map/search/symbol/index data. |
| Task provider | Provides requirement, scope, plan and acceptance criteria. |
| Git provider | Provides relevant status/diff/checkpoint context. |
| Validation provider | Provides test/build/lint/error evidence. |
| Memory provider | Provides enabled task/project/decision history. |
| Ranker | Scores/selects task-relevant items. |
| Budgeter | Enforces model-context budget. |
| Provenance | Records source and freshness metadata. |
| Invalidation | Marks stale items after relevant changes. |

The MVP uses lexical + structural retrieval. A semantic/vector provider may be added later behind the same interface only if evaluation shows measurable benefit.

# 10. LLM Gateway Design

| Layer | Responsibility |
| --- | --- |
| LLMClient interface | Provider-neutral request/response contract. |
| ProviderAdapter | Maps internal request to provider SDK/API. |
| CapabilityRegistry | Records model capabilities such as tool calling/structured output. |
| StructuredOutputValidator | Validates model output against Pydantic contracts. |
| ToolCallParser | Converts valid model tool calls into ToolRequest objects. |
| Retry/Timeout | Handles bounded provider failures. |
| Telemetry | Records model/provider/prompt/version metadata where configured. |

- Model SKU is configuration, not architecture.

- Provider adapters cannot execute tools.

- LLM output is untrusted input until schema and policy checks succeed.

- Prompt/version tracking supports reproducibility.

# 11. Tool System Design

ToolDefinition

↓

ToolRegistry

↓

ToolRequest validation

↓

ToolGateway

↓

PolicyEngine

├── ALLOW ──→ Executor

├── ASK ──→ ApprovalService ──→ Executor if approved

├── DENY ──→ Audit + Result

└── RESTRICT ──→ constrained executor/path

↓

Normalized ToolResult

| Built-in tool family | MVP examples | Execution boundary |
| --- | --- | --- |
| Workspace | read_file, list_files, create_file, apply_patch | WorkspaceExecutor |
| Search | search_text, repository_map | Repository adapters |
| Terminal | run_process, run_powershell | Process/PowerShell Executor |
| Testing | run_test, run_lint, run_build | Validation Executor |
| Git | status, diff, checkpoint, rollback | Git Adapter |
| MCP | external MCP tool invocation | MCP Adapter → Tool Gateway |

# 12. Policy Engine Design

| Policy input | Required evaluation |
| --- | --- |
| Autonomy mode | CHAT/PLAN/ASSISTED IMPLEMENT/SUPERVISED AUTO/AUTONOMOUS/RESTRICTED |
| Tool | Capability identity and category |
| Arguments | Argument-aware risk/scope checks |
| Workspace | Authorized root and protected paths |
| Resource | Target file/process/network/resource as applicable |
| Risk | Read/write/execute/destructive/sensitive classification |
| Policy precedence | Hard security rules override lower-level configuration |
| Approval | ASK requires human approval path |

Policy representation: YAML/JSON configuration validated into typed policy models. Runtime evaluation is owned by the project. Decisions are ALLOW, ASK, DENY or RESTRICT.

- Policy evaluation must be deterministic for identical inputs.

- Policy cannot be changed through normal agent tools.

- Policy decision records include reason and rule identity.

- Security tests cover bypass attempts, malicious arguments, path traversal and autonomy escalation.

# 13. Execution & Sandbox Design

| Executor | Responsibilities | Required controls |
| --- | --- | --- |
| WorkspaceExecutor | Authorized filesystem operations | Root restriction, path normalization, protected paths |
| ProcessExecutor | Generic process execution | Command/argument validation, cwd, timeout, output limits |
| PowerShellExecutor | PowerShell-specific execution | Interpreter capability, command policy, environment filtering |
| SandboxExecutor | Pluggable isolation boundary | Resource/workspace/process restrictions |

- Execution receives only authorized requests.

- Executors do not decide policy.

- Sensitive environment variables are filtered.

- Working directory is constrained.

- Timeout and output limits are enforced.

- Destructive operations require policy approval or denial.

- Sandbox implementation remains replaceable.

# 14. Patch & File Editing Design

Repository Context

↓

Coder / Patch Generator

↓

Patch Schema Validation

↓

Expected Scope Check

↓

Base File Hash / Version Check

↓

Conflict Detection

↓

Dry Run (where applicable)

↓

Policy Check

↓

Apply

↓

Diff + Actual Scope Check

- Patch operations are explicit and file-scoped.

- Stale file hashes cause patch rejection rather than silent overwrite.

- Unexpected files are flagged.

- Actual diff becomes validation/report evidence.

- Patch application must preserve unrelated user changes.

# 15. Testing & Validation Technical Design

| Layer | Implementation boundary | Examples |
| --- | --- | --- |
| Unit | Individual services/models | State machine, policy evaluator, patch validator |
| Integration | Component interactions | Tool Gateway→Policy→Executor, repository index |
| Security | Adversarial fixtures | Path escape, policy bypass, malicious tool args, prompt injection |
| E2E | Complete local loop | Requirement→plan→edit→test→repair→report |
| Evaluation | Curated task benchmark | Representative software-engineering tasks |

Validation Runner executes configured commands and returns structured ValidationResult objects. Completion Gate consumes required gates and evidence. It does not infer success from model claims.

| Evidence | Captured data |
| --- | --- |
| Command evidence | Command, working directory, exit code, duration |
| Output evidence | stdout/stderr references or bounded captured output |
| Test evidence | Gate name, status, test summary where available |
| Change evidence | Diff and expected-vs-actual scope |
| Recovery evidence | Attempt number, diagnosis, patch and retest result |
| Git evidence | Baseline/status/diff/checkpoint/rollback state |

# 16. Error Recovery Technical Design

| Stage | Service | Output |
| --- | --- | --- |
| Normalize | ErrorNormalizer | ErrorRecord |
| Classify | ErrorClassifier | Category + recovery eligibility |
| Context | FailureContextBuilder | Relevant evidence/context |
| Diagnose | DiagnosisService | Root-cause hypothesis |
| Repair plan | RepairPlanner | RepairPlan |
| Repair patch | RepairPatchGenerator | Validated Patch |
| Re-policy | Policy Engine | Decision |
| Apply | Patch Executor | Change result |
| Retest | Validation Runner | ValidationResult |
| Stop | RecoveryController | Retry/blocked/failed/complete path |

- Recovery uses the same Tool Gateway and Policy Engine as normal execution.

- Recovery is bounded by attempt, time and scope budgets.

- Repeated identical failures should be detected where practical to avoid wasteful loops.

- Security/policy failures are not automatically repaired by changing security rules.

- Recovery exhaustion results in non-complete status and an evidence-backed report.

# 17. Git Integration Technical Design

| Capability | Design |
| --- | --- |
| Status | Git CLI adapter returns structured status. |
| Baseline | Capture relevant HEAD/worktree/index state before mutation. |
| Diff | Generate task-scoped diff and actual-change evidence. |
| Checkpoint | Create task recovery point according to configured strategy. |
| Rollback | Revert task-owned changes without discarding unrelated user changes. |
| Conflict | Detect risky worktree/index conditions and block when necessary. |
| Commit | Optional and policy/approval-controlled; not required for core MVP. |

Git operations are tools and therefore pass through the same Tool Gateway/Policy Engine. The agent must not use destructive reset/clean behavior as an implicit recovery shortcut.

# 18. Persistence & Memory Design

| Store | Technology | Primary contents |
| --- | --- | --- |
| Task store | SQLite | Tasks, states, acceptance criteria, budgets, outcomes |
| Project store | SQLite | Project metadata/conventions |
| Repository index | SQLite | Files, symbols, relationships, hashes/metadata |
| Memory store | SQLite | Task/project/decision/failure/session records |
| Audit metadata | SQLite + structured files | Event metadata and evidence references |
| Raw logs/artifacts | Files | Large command/test outputs, reports, diffs as appropriate |
| Secrets | OS/environment secret mechanism | Never normal Git storage |

- Domain services depend on repository interfaces rather than direct SQL where practical.

- Memory is contextual/advisory and cannot override policy.

- Schema migrations must be versioned.

- Large raw outputs should be stored as artifacts and referenced from structured records.

# 19. VS Code ↔ Runtime IPC Design

For the MVP, the VS Code extension launches/connects to the local Agent Runtime as a thin client. The technical design fixes a simple local process boundary using JSON-RPC 2.0 messages over stdio.

| Message class | Examples |
| --- | --- |
| Request | create_task, get_task, plan_task, run_task, approve, cancel, get_diff, get_report |
| Notification | task_state_changed, tool_requested, validation_started, validation_completed, recovery_started, activity_event |
| Response | request id, success/error, typed result |
| Error | code, message, structured details |

- The extension must not receive direct filesystem/process privileges from the runtime beyond normal client behavior.

- Approval messages are runtime policy decisions surfaced to the user.

- Protocol messages are versioned and schema-validated.

- Runtime remains independently usable by CLI/headless mode.

- Future IPC/API transport can be added behind the client interface without changing core domain contracts.

# 20. CLI Technical Design

| Command | Purpose |
| --- | --- |
| agent plan | Normalize requirement, inspect repository and produce plan. |
| agent run | Execute the controlled engineering loop. |
| agent status | Show task state and current stage. |
| agent diff | Show actual task diff. |
| agent test | Run configured validation. |
| agent report | Show/export final evidence-backed report. |

Typer is the CLI framework. CLI commands call the same runtime services used by VS Code; they must not duplicate orchestration or security logic.

# 21. Configuration Design

| Configuration category | Examples | Authority |
| --- | --- | --- |
| Runtime | workspace root, budgets, logging | Runtime config |
| LLM | provider, model, endpoint, limits | Provider adapter config |
| Policy | autonomy rules, tool risk/scope rules | Policy Engine; hard rules highest |
| Validation | test/build/lint commands, required gates | Task/project configuration |
| Repository | ignore patterns, supported language adapters | Repository subsystem |
| Sandbox | limits/restrictions | Execution/Sandbox; hard security wins |
| VS Code | runtime command/protocol settings | Client config |

- Secrets are not stored in normal project configuration.

- Configuration is validated before use.

- Configuration cannot disable hard security rules.

- Project configuration is untrusted input with respect to security.

# 22. Logging, Audit & Observability

| Event | Minimum information |
| --- | --- |
| task.created | task ID, timestamp, client |
| task.state_changed | task ID, from/to, reason |
| tool.requested | request ID, tool, task, correlation ID |
| policy.decided | request ID, decision, rule, reason |
| approval | request ID, approver/action, result |
| tool.completed | request ID, result, duration |
| patch.applied | task, files, scope/diff reference |
| validation.completed | gate, status, command, evidence |
| recovery.attempted | task, error, attempt number |
| git.changed | status/checkpoint/diff references |
| completion.decided | task, gate results, decision |
| report.generated | task, report reference |

Structured JSON events are the primary audit representation. Correlation IDs connect task → tool → policy → execution → validation → recovery → report.

# 23. Security Implementation Controls

- Canonical path normalization before workspace authorization.

- Workspace-root containment check for file operations.

- Protected-path deny/approval rules.

- Argument-aware process/PowerShell policy.

- Environment-variable filtering.

- Explicit capability/risk metadata for every tool.

- Central Tool Gateway enforcement.

- Policy precedence independent of model output.

- Repository prompt-injection isolation.

- MCP adapter isolation.

- VS Code client separation.

- Recovery policy re-check.

- False-completion tests.

- Emergency cancellation/stop path.

# 24. Performance & Resource Controls

| Resource | Control |
| --- | --- |
| LLM calls | Timeouts, bounded retries, configurable token/context budget |
| Repository indexing | Incremental updates and cached index |
| Search | ripgrep and bounded result sets |
| Context | Ranking + token budget |
| Process | Timeout and output-size limits |
| Recovery | Attempt/time/scope budgets |
| Logs | Large output stored as artifacts rather than unlimited memory |
| Task runtime | Cancellation and bounded execution |

# 25. Module-Level Test Boundary

| Production area | Minimum test boundary |
| --- | --- |
| agent/state/lifecycle | Transition matrix + invalid transition tests |
| task | Model/CRUD/budget tests |
| repository | Scanner/search/parser/index/map tests |
| context | Ranking/budget/provenance/staleness tests |
| llm | Adapter contract/structured output/error tests |
| tools | Schema/registry/gateway tests |
| policy | Decision matrix + bypass/security tests |
| execution | Path/command/env/timeout/output security tests |
| testing | Runner/evidence/completion tests |
| recovery | Classification/retry/stop/retest tests |
| git | Baseline/diff/rollback/user-change preservation tests |
| memory | Persistence/schema/authority tests |
| audit | Event schema/correlation tests |
| reporting | Evidence completeness/report tests |
| CLI | Command integration tests |
| VS Code | Protocol/client/non-bypass integration tests |

# 26. Technical Build Order

1. Project/bootstrap contracts

2. Domain models + schemas

3. Task state machine + runtime shell

4. Tool contracts + registry

5. Policy Engine + policy tests

6. Workspace/search/repository intelligence

7. Context Engine

8. LLM Gateway + provider adapter

9. Patch/change engine

10. Controlled execution + sandbox boundary

11. Validation Runner + Completion Gate

12. Error Recovery

13. Git integration

14. Memory + audit + reporting

15. CLI end-to-end

16. VS Code client

17. Security/evaluation hardening

This order preserves the implementation-plan dependency gates: autonomous terminal execution follows the Policy Engine; automatic repair follows Testing + Completion Gate; broad MCP execution follows Tool Gateway policy enforcement; VS Code does not become a prerequisite for core runtime validation.

# 27. Error & Result Taxonomy

| Prefix | Meaning | Examples |
| --- | --- | --- |
| TASK- | Task lifecycle | TASK_INVALID_STATE, TASK_CANCELLED |
| CTX- | Context | CTX_BUDGET_EXCEEDED, CTX_STALE |
| LLM- | Model/provider | LLM_TIMEOUT, LLM_INVALID_OUTPUT |
| TOOL- | Tool contract | TOOL_UNKNOWN, TOOL_SCHEMA_INVALID |
| POL- | Policy | POL_DENIED, POL_APPROVAL_REQUIRED |
| EXEC- | Execution | EXEC_TIMEOUT, EXEC_OUTPUT_LIMIT |
| PATH- | Workspace safety | PATH_OUTSIDE_WORKSPACE, PATH_PROTECTED |
| PATCH- | Patch | PATCH_STALE, PATCH_CONFLICT, PATCH_SCOPE |
| TEST- | Validation | TEST_FAILED, TEST_COMMAND_INVALID |
| REC- | Recovery | RECOVERY_LIMIT, RECOVERY_STOPPED |
| GIT- | Git | GIT_DIRTY_CONFLICT, GIT_ROLLBACK_FAILED |
| MEM- | Persistence | MEM_SCHEMA, MEM_WRITE_FAILED |
| REPORT- | Reporting | REPORT_EVIDENCE_MISSING |
| SEC- | Security | SECURITY_POLICY_BYPASS |

# 28. Technical Design Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| TDD-A01 | Module boundaries | Physical modules map cleanly to locked architecture responsibilities. |
| TDD-A02 | Dependency direction | No model-facing component has a direct privileged OS path. |
| TDD-A03 | Policy enforcement | All tool execution routes through Tool Gateway → Policy Engine. |
| TDD-A04 | Provider isolation | Provider-specific code remains behind LLM Gateway. |
| TDD-A05 | Repository intelligence | Scanner/search/parser/index/map have explicit interfaces. |
| TDD-A06 | Patch safety | Stale/conflicting changes are rejected safely. |
| TDD-A07 | Execution safety | Workspace/process/PowerShell controls are explicit. |
| TDD-A08 | Validation | Validation evidence and Completion Gate are first-class. |
| TDD-A09 | Recovery | Recovery is bounded and reuses normal policy/validation paths. |
| TDD-A10 | Git safety | User changes are preserved and rollback is controlled. |
| TDD-A11 | Persistence | SQLite-backed state/memory/index boundaries are explicit. |
| TDD-A12 | Client separation | CLI and VS Code use same runtime; VS Code has no privileged bypass. |
| TDD-A13 | Auditability | Important actions are correlated and auditable. |
| TDD-A14 | Testing | Every major subsystem has a defined test boundary. |
| TDD-A15 | MVP discipline | Deferred vector search, multi-agent, cloud/distributed execution are not mandatory dependencies. |

# 29. Traceability

| Source | Technical design responsibility |
| --- | --- |
| PRD v1.0 | Product vision, MVP, safety and completion principles. |
| SRS v1.0 | Detailed functional, non-functional and security requirements. |
| System Architecture v1.0 | Logical components, boundaries, flows and topology. |
| Architecture Decision Matrix v1.0 | Research-derived architectural choices. |
| Master Architecture v1.0 | Runtime component and flow baseline. |
| Technology Decision v1.0 | Python/TypeScript, Pydantic, Tree-sitter, SQLite, policy, execution, testing and client technology. |
| Repository Blueprint v1.0 | Physical module/folder organization. |
| Implementation Plan v1.0 | Phase/dependency order. |
| Task Backlog v1.0 | Implementation tasks, dependencies and acceptance criteria. |

# 30. Locked Technical Constraints

- Python 3.12+ is the MVP Agent Runtime language.

- TypeScript is the VS Code extension language.

- uv + pyproject.toml is the Python environment/build baseline.

- Pydantic v2 is the primary contract validation mechanism.

- SQLite is the MVP local persistence/index store.

- Tree-sitter + ripgrep are the initial repository intelligence technologies.

- Policy Engine is custom, deterministic and project-owned.

- PowerShell/process execution is controlled by policy and executor boundaries.

- Git is accessed through a controlled adapter.

- CLI and VS Code share the same Agent Runtime.

- JSON-RPC over local stdio is the MVP VS Code/runtime IPC design.

- MCP cannot bypass Tool Gateway/Policy Engine.

- Vector/semantic retrieval is deferred until evaluation justifies it.

- Multi-agent orchestration is deferred until single-runtime reliability is demonstrated.

- Cloud/distributed infrastructure is not required for the MVP.

- Completion Gate is mandatory and evidence-based.

# 31. Technical Change Control

- Changes to locked module boundaries require architecture review.

- Changes to security enforcement require security review and regression tests.

- Changes to tool contracts require tool/policy regression tests.

- Changes to patching require stale/conflict tests.

- Changes to Completion Gate require false-completion tests.

- Changes to recovery require retry/stop-condition tests.

- Changes to Git behavior require user-change preservation tests.

- New requirements discovered during coding become backlog/change-control items; they are not silently inserted into existing scope.

# 32. Final Status

STATUS: FINAL / LOCKED — v1.0

This Technical Design v1.0 is the authoritative implementation-level design for the AI Software Co-Agent. It translates the locked product, requirements and logical architecture into concrete module boundaries, technology usage, contracts, persistence, execution controls, IPC, validation, recovery, Git, observability and testing boundaries.

— END OF TECHNICAL DESIGN v1.0 —
