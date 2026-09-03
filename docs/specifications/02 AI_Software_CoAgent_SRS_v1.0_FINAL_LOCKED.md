AI SOFTWARE CO-AGENT

SOFTWARE REQUIREMENTS SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: SRS-001 • Derived from PRD v1.0

| Field | Value |
| --- | --- |
| Document | Software Requirements Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baseline | PRD v1.0 FINAL / LOCKED |
| Purpose | Detailed software requirements and acceptance baseline for implementation |

Lock Statement: This SRS v1.0 is the final locked software-requirements baseline. Implementation must satisfy these requirements unless changed through formal change control.

# 1. Introduction

## 1.1 Purpose

This SRS converts the product-level requirements of PRD v1.0 into detailed, testable software requirements for the AI Software Co-Agent. It defines system behavior, interfaces, data, security, operational constraints, validation requirements, and acceptance conditions.

## 1.2 Product Scope

The system is a local-first, policy-controlled AI software engineering co-agent. It accepts software requirements, understands a repository, plans implementation, performs scoped code changes, executes controlled tools, validates the result, diagnoses failures, performs bounded repair/retest cycles, maintains traceability, and produces a final evidence-backed report.

## 1.3 Intended Audience

- Product owner and project stakeholders

- Software engineers

- Architecture/design reviewers

- Security reviewers

- Test/QA engineers

- VS Code extension developers

- Future maintainers and contributors

# 2. System Context

| Actor / System | Interaction |
| --- | --- |
| Developer | Provides requirements, constraints, approvals, intervention, and reviews results. |
| VS Code Client | Creates/monitors tasks and displays plans, approvals, diffs, activity, validation and reports. |
| CLI / Headless Client | Starts and monitors the same Agent Runtime without VS Code. |
| LLM Provider | Supplies planning, reasoning, structured outputs and code-generation results through the LLM Gateway. |
| Local Workspace | Contains project source, documentation, configuration and generated changes. |
| Git | Provides repository status, diff, checkpoint and rollback/commit capabilities. |
| External MCP Servers | Provide optional tools through an adapter; never bypass the central policy path. |
| Operating System | Provides filesystem/process capabilities only through controlled executors. |

## 2.1 System Boundary

- Inside system boundary: Agent Runtime, task lifecycle, orchestration, repository intelligence, context, LLM Gateway, Tool Gateway, Policy Engine, execution boundary, testing/validation, recovery, Git integration, memory, audit and reporting.

- Outside but integrated: VS Code client, CLI client, LLM provider, Git executable/repository, OS, optional MCP servers.

- Security boundary: all AI-requested side effects must pass through Tool Gateway → Policy Engine → authorized Executor.

- Repository files and repository instructions are treated as untrusted data.

# 3. Architectural Requirements

- AR-001 The Agent Runtime shall operate independently of VS Code.

- AR-002 VS Code shall be a client/adapter and shall not implement a privileged parallel execution path.

- AR-003 Every AI-requested external action shall use an explicit tool contract.

- AR-004 Every tool invocation shall pass through one authoritative Tool Gateway.

- AR-005 Every tool invocation shall be evaluated by the Policy/Permission Engine before execution.

- AR-006 Built-in and MCP tools shall share the same authorization path.

- AR-007 Code changes shall be observable, scoped, diffable and, where practical, patch-based.

- AR-008 Validation evidence shall be available to the Completion Gate.

- AR-009 Recovery shall be bounded and shall not bypass normal policy or validation.

- AR-010 Provider-specific model integrations shall remain behind an abstraction.

- AR-011 Major components shall expose testable interfaces and avoid unnecessary coupling.

- AR-012 Future multi-agent capability shall not be required for MVP.

# 4. Detailed Functional Requirements

## 4.1 Requirement & Task Management

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-001 | Accept requirement | The system shall accept a natural-language software requirement from a supported client. |
| REQ-002 | Normalize requirement | The system shall convert the requirement into a structured task representation. |
| REQ-003 | Acceptance criteria | A task shall contain explicit acceptance criteria or an identified need to derive them. |
| REQ-004 | Task scope | A task shall maintain intended scope, constraints and expected outcomes. |
| REQ-005 | Task state | The system shall maintain lifecycle state including planning, implementation, validation, recovery, blocked, cancelled, failed and complete states as applicable. |
| REQ-006 | Execution budgets | The system shall maintain configurable time, retry/attempt and scope budgets. |
| REQ-007 | Cancellation | A running task shall support cancellation and transition safely to a non-complete terminal/interrupted state. |

## 4.2 Repository Intelligence

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-008 | Workspace discovery | The system shall identify and operate against an explicitly authorized workspace root. |
| REQ-009 | Repository scan | The system shall inspect repository structure before implementation when repository context is required. |
| REQ-010 | File discovery | The system shall provide structured file and directory information. |
| REQ-011 | Lexical search | The system shall support fast text/code search. |
| REQ-012 | Syntax analysis | The system shall support syntax/symbol-aware analysis for supported languages. |
| REQ-013 | Repository map | The system shall maintain a repository representation containing relevant files, symbols, relationships, metadata, documentation and change state. |
| REQ-014 | Incremental update | Repository information shall support invalidation/update after relevant file changes. |
| REQ-015 | Git-aware context | Repository understanding shall be able to incorporate relevant Git state. |

## 4.3 Context Management

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-016 | Context providers | The system shall obtain context from repository, task, Git, validation/error and memory sources. |
| REQ-017 | Relevance ranking | The system shall rank/select context according to task relevance. |
| REQ-018 | Budget enforcement | Context assembly shall respect configured token/output/resource budgets. |
| REQ-019 | Provenance | Context items shall retain enough provenance to identify their source. |
| REQ-020 | Stale context | Relevant context shall be invalidated or refreshed when underlying content changes. |

## 4.4 Planning

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-021 | Implementation plan | The system shall generate a structured implementation plan for tasks requiring planning. |
| REQ-022 | Expected changes | The plan shall identify expected files, folders, modules or other changes. |
| REQ-023 | Dependencies | The plan shall identify material implementation dependencies when known. |
| REQ-024 | Validation plan | The plan shall identify required validation activities. |
| REQ-025 | Risk information | The plan shall identify relevant risks/blockers when known. |

## 4.5 Code Creation & Editing

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-026 | Create files | The system shall create new files/folders only within authorized scope. |
| REQ-027 | Modify files | The system shall modify existing files only through authorized execution paths. |
| REQ-028 | Patch representation | Changes shall preferably be represented as structured/validated patches or diffs. |
| REQ-029 | Expected scope | The system shall record expected change scope before mutation where practical. |
| REQ-030 | Version/hash check | Before patch application, the system shall detect stale file versions using an appropriate version/hash mechanism. |
| REQ-031 | Conflict detection | The system shall detect patch/application conflicts and fail safely rather than silently overwrite. |
| REQ-032 | Dry run | The system shall support dry-run validation before mutation where applicable. |
| REQ-033 | Actual vs expected | After mutation, actual changed files shall be compared with expected scope. |
| REQ-034 | Reviewer | A reviewer step shall be available to report scope/quality findings. |

## 4.6 Tool System

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-035 | Tool contract | Every executable capability exposed to the agent shall have an explicit tool contract. |
| REQ-036 | Tool registry | The system shall register/discover available tools and capability metadata. |
| REQ-037 | Tool gateway | All AI-requested tool calls shall pass through the Tool Gateway. |
| REQ-038 | Argument validation | Tool arguments shall be schema-validated before execution. |
| REQ-039 | Normalized results | Tool execution shall return normalized structured results. |
| REQ-040 | Tool metadata | Tools shall expose relevant capability, risk, side-effect and scope metadata. |
| REQ-041 | Audit | Important tool requests/results shall be auditable. |

## 4.7 Policy & Permission

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-042 | Pre-execution policy | Every tool invocation shall be evaluated before execution. |
| REQ-043 | Decision types | The policy layer shall support ALLOW, ASK, DENY and RESTRICT outcomes. |
| REQ-044 | Argument-aware rules | Policy shall consider tool identity and arguments. |
| REQ-045 | Scope-aware rules | Policy shall consider workspace/resource scope. |
| REQ-046 | Autonomy-aware rules | Policy shall consider configured autonomy mode. |
| REQ-047 | Risk-aware rules | Policy shall consider operation risk and side effects. |
| REQ-048 | Precedence | Higher-priority security restrictions shall not be overridden by lower-priority configuration or model output. |
| REQ-049 | Approval | ASK decisions shall provide a human approval path when applicable. |
| REQ-050 | No self-bypass | The agent shall not be able to rewrite/disable its own security policy through normal tools. |

## 4.8 Terminal / Execution / Sandbox

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-051 | Controlled execution | Filesystem and process side effects shall occur only through controlled executors. |
| REQ-052 | PowerShell | The Windows-first MVP shall support controlled PowerShell/process execution. |
| REQ-053 | Working directory | Process execution shall be constrained to an authorized working directory unless explicitly approved. |
| REQ-054 | Protected paths | Protected paths shall be blocked or specially controlled. |
| REQ-055 | Environment protection | Sensitive environment data shall not be exposed by default. |
| REQ-056 | Timeout | Process execution shall support configurable timeouts where practical. |
| REQ-057 | Output limits | Process output shall support practical size limits. |
| REQ-058 | Sandbox boundary | Execution shall use a pluggable sandbox/isolation interface. |
| REQ-059 | Destructive operations | Destructive/sensitive actions shall be approval-controlled or denied according to policy. |

## 4.9 Testing & Validation

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-060 | Command configuration | The system shall support configured project validation commands. |
| REQ-061 | Test execution | The system shall execute applicable unit/integration/e2e tests. |
| REQ-062 | Lint/build | The system shall support configured lint and build validation. |
| REQ-063 | Result capture | Validation shall capture applicable command, exit code, stdout, stderr and duration. |
| REQ-064 | Structured evidence | Validation results shall be represented as structured evidence. |
| REQ-065 | Required gates | Each task shall identify required validation gates appropriate to its acceptance criteria. |
| REQ-066 | Completion Gate | The system shall prevent completion unless all required gates pass. |
| REQ-067 | False completion | A missing/failed required gate shall result in non-complete status. |

## 4.10 Error Recovery

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-068 | Normalize errors | Validation/execution failures shall be converted to structured errors. |
| REQ-069 | Classify errors | Failures shall be classified for diagnosis/routing. |
| REQ-070 | Failure context | The system shall build relevant failure context for diagnosis. |
| REQ-071 | Diagnosis | The system shall support root-cause hypotheses/diagnosis within available evidence. |
| REQ-072 | Repair plan | The system shall represent a repair plan. |
| REQ-073 | Repair patch | Repairs shall use the normal validated patch/change path. |
| REQ-074 | Re-policy | Repair actions shall pass through normal policy and safety checks. |
| REQ-075 | Retest | A repair attempt shall be followed by relevant retesting. |
| REQ-076 | Bounded loop | Recovery shall obey configurable attempt/time/scope limits. |
| REQ-077 | Stop conditions | Unrecoverable, unsafe, blocked or exhausted conditions shall stop recovery safely. |

## 4.11 Git Safety

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-078 | Baseline | The system shall capture relevant pre-task Git state. |
| REQ-079 | Status | The system shall expose structured Git status. |
| REQ-080 | Diff | The system shall expose actual changes as a diff. |
| REQ-081 | Checkpoint | The system shall support task checkpoints. |
| REQ-082 | Rollback | The system shall support safe rollback of task-owned changes. |
| REQ-083 | User changes | Pre-existing unrelated user changes shall be detected and preserved. |
| REQ-084 | Commit | Commit operations shall remain policy/approval-controlled. |
| REQ-085 | No silent discard | The system shall never silently discard user changes. |

## 4.12 Memory, Audit & Reporting

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-086 | Task state persistence | Relevant task state shall persist for the configured lifecycle. |
| REQ-087 | Project memory | The system shall support project-level context/conventions where enabled. |
| REQ-088 | Task memory | The system shall support task-specific memory. |
| REQ-089 | Decision memory | The system shall support recorded decisions. |
| REQ-090 | Failure history | The system shall support useful failure/recovery history. |
| REQ-091 | Memory authority | Memory shall not override security policy. |
| REQ-092 | Audit events | Important task/tool/policy/change/validation/recovery/Git/completion events shall be recorded. |
| REQ-093 | Final report | The system shall produce a final report. |
| REQ-094 | Report evidence | The final report shall identify changes, validation, retries/recovery, Git state, blockers/failures and outcome. |

## 4.13 Clients, MCP & LLM Abstraction

| ID | Requirement | Detailed requirement |
| --- | --- | --- |
| REQ-095 | CLI/headless | The same Agent Runtime shall operate through a CLI/headless client. |
| REQ-096 | VS Code client | The VS Code client shall support task creation, plan display, approvals, diffs, progress/activity, cancellation and final results. |
| REQ-097 | Client separation | VS Code shall not become a second privileged execution path. |
| REQ-098 | MCP adapter | The system shall support MCP through an adapter. |
| REQ-099 | MCP policy | MCP tools shall pass through the same Tool Gateway and Policy Engine. |
| REQ-100 | LLM abstraction | The Agent Runtime shall use an LLM provider abstraction. |
| REQ-101 | Initial provider | The MVP shall support an initial provider through the abstraction without making the core runtime permanently provider-specific. |
| REQ-102 | Structured output | The LLM boundary shall support structured outputs needed for plans, tool requests and other contracts. |

# 5. Non-Functional Requirements

| ID | Quality attribute | Requirement |
| --- | --- | --- |
| NFR-001 | Reliability | State transitions, failure states and completion decisions shall be deterministic and testable. |
| NFR-002 | Security | No unrestricted AI-to-OS access; central policy, workspace controls and protected secrets are mandatory. |
| NFR-003 | Auditability | Security-relevant and task-relevant actions shall be traceable. |
| NFR-004 | Modularity | Core components shall have clear boundaries and independently testable interfaces. |
| NFR-005 | Extensibility | LLM providers, tools, MCP, clients and future multi-agent capabilities shall be replaceable/extensible. |
| NFR-006 | Testability | Major capabilities shall have appropriate unit, integration, security, e2e or evaluation tests. |
| NFR-007 | Performance | Repository/context operations shall use practical incremental and budgeted approaches for local projects. |
| NFR-008 | User control | Autonomy shall be configurable and policy-backed; high-risk decisions shall not rely only on model instructions. |
| NFR-009 | Recoverability | Changes shall be inspectable and reversible through diff/checkpoint mechanisms. |
| NFR-010 | Portability | The core runtime shall not require VS Code and shall support CLI/headless operation. |
| NFR-011 | Maintainability | Implementation shall favor small, documented modules and explicit contracts. |
| NFR-012 | Observability | Task progress, tool activity, validation and recovery shall produce structured activity/evidence. |
| NFR-013 | Data integrity | Persisted task, memory and audit records shall have validated schemas. |
| NFR-014 | Deterministic policy | Security policy evaluation shall be deterministic for identical policy inputs. |
| NFR-015 | Bounded execution | Long-running/recovery operations shall be bounded by configurable controls. |

# 6. Data & Information Requirements

| Data object | Required information |
| --- | --- |
| Task | ID, requirement, scope, acceptance criteria, state, budgets, timestamps, outcome. |
| Plan | Task ID, steps, expected files/changes, dependencies, risks, validation gates. |
| Tool | Name, description, schema, capability, risk, side effects, scope requirements, version/metadata. |
| Tool Request | Task/correlation ID, tool, validated arguments, policy decision, approval state. |
| Tool Result | Success/failure, normalized output, exit/process metadata where applicable, evidence reference. |
| Policy Decision | Decision type, rule/policy ID, tool/action, scope, reason/evidence, timestamp. |
| Context Item | Source, content/reference, relevance, provenance, freshness/version metadata. |
| Patch/Change | Files, operations, expected scope, source/version/hash, validation state, diff reference. |
| Validation Result | Gate, command, exit code, stdout/stderr references, duration, status, evidence. |
| Error | Error ID, category, source, message, evidence, context reference, recovery status. |
| Recovery Attempt | Failure, diagnosis, repair plan, patch, result, attempt count, stop condition. |
| Git State | Baseline, current status, diff/checkpoint/rollback information. |
| Memory Record | Scope, key/value or structured content, provenance, timestamp, confidence/validity metadata as appropriate. |
| Audit Event | Event ID, correlation ID, actor/component, action, target, result, timestamp. |
| Final Report | Task outcome, requirement/plan summary, changes, tests, recovery, Git state, blockers and evidence. |

# 7. Task Lifecycle Requirements

| State | Entry condition | Permitted next states |
| --- | --- | --- |
| CREATED | Task accepted | PLANNING, CANCELLED |
| PLANNING | Planning started | READY, BLOCKED, FAILED, CANCELLED |
| READY | Plan/requirements ready | IMPLEMENTING, BLOCKED, CANCELLED |
| IMPLEMENTING | Authorized change work begins | VALIDATING, BLOCKED, FAILED, CANCELLED |
| VALIDATING | Validation running | COMPLETE, RECOVERING, FAILED, BLOCKED, CANCELLED |
| RECOVERING | Bounded diagnosis/repair running | VALIDATING, BLOCKED, FAILED, CANCELLED |
| BLOCKED | Approval/dependency/safety blocker | READY, IMPLEMENTING, CANCELLED |
| FAILED | Unrecoverable failure | RECOVERING only if policy permits/retry remains; otherwise terminal |
| COMPLETE | All required gates passed | Terminal |
| CANCELLED | User/system cancellation | Terminal |

The exact internal state model may contain additional sub-states, but no state transition may bypass required policy or validation gates.

# 8. External & Internal Interface Requirements

## 8.1 Client Interface

- Clients shall submit tasks and receive structured task state.

- Clients shall receive plans, approval requests, progress/activity, diffs, validation status and final reports.

- Clients shall be able to request cancellation.

- Client protocols shall be versioned/capability-aware.

## 8.2 LLM Interface

- The LLM Gateway shall hide provider-specific request/response details.

- Model outputs used for tools or structured decisions shall be schema-validated.

- Provider errors shall be normalized.

- Prompt/model/version information required for reproducibility shall be recordable.

## 8.3 Tool Interface

- Tool inputs and outputs shall use explicit schemas.

- Tools shall declare side effects and risk/capability metadata.

- Tool invocation shall require a policy decision before execution.

- Tool results shall be normalized.

## 8.4 Execution Interface

- Executors shall receive only authorized requests.

- Execution shall return exit/result metadata and evidence.

- Execution shall not decide policy; authorization belongs to Policy Engine.

- Execution shall not silently broaden scope.

# 9. Security Requirements

- SEC-001 Repository content shall be treated as untrusted input.

- SEC-002 Repository instructions shall never outrank system security policy.

- SEC-003 Secrets and credentials shall be protected and normally unreadable to the agent.

- SEC-004 Destructive commands, production actions, live-system actions, live trading and deployment shall receive special restrictions.

- SEC-005 Security policy shall not be rewritable through normal agent tools.

- SEC-006 Workspace boundaries shall be enforced below the prompt/rules layer.

- SEC-007 MCP tools shall not bypass the Tool Gateway/Policy Engine.

- SEC-008 VS Code shall not create a privileged bypass.

- SEC-009 Recovery shall not bypass policy, patch validation or Completion Gate.

- SEC-010 Emergency stop/cancellation shall be available for running execution.

- SEC-011 Important approvals and policy decisions shall be auditable.

- SEC-012 The system shall support security testing using malicious repository/tool fixtures.

# 10. Autonomy & Approval Requirements

| Mode | Expected behavior |
| --- | --- |
| CHAT | No mutation/execution; explanation and discussion. |
| PLAN | Read/search/context and planning; no mutation. |
| ASSISTED IMPLEMENT | Controlled implementation with user involvement for actions requiring approval. |
| SUPERVISED AUTO | Low-risk policy-approved actions may proceed automatically; risky actions require approval. |
| AUTONOMOUS | Longer bounded execution remains subject to policy, sandbox, budgets and completion gates. |
| RESTRICTED | Sensitive contexts default to deny or approval-only for high-risk actions. |

Autonomy mode is an input to policy evaluation, not a replacement for policy.

# 11. Validation & Completion Requirements

A task may be reported COMPLETE only when all required acceptance and validation gates have passed.

| Gate | Required evidence |
| --- | --- |
| Requirement | Structured task and acceptance criteria exist. |
| Plan | Implementation plan exists when required. |
| Scope | Expected changes are identified. |
| Change | Actual changes/diff are available. |
| Execution | Required commands have structured results. |
| Validation | Required lint/build/test checks have passed. |
| Recovery | If recovery occurred, the final validation after repair passed. |
| Security | Required policy/sandbox/security gates passed. |
| Git | Required baseline/diff/checkpoint conditions are satisfied. |
| Report | Final report contains evidence and outcome. |

Hard requirement: generated code alone is never sufficient evidence of completion.

# 12. Error Handling Requirements

| Error class | Required behavior |
| --- | --- |
| Input/requirement error | Explain/normalize; do not begin unsafe execution. |
| Repository access error | Record error, identify affected scope, stop or request intervention. |
| LLM/provider error | Normalize, apply bounded retry policy, then stop safely if exhausted. |
| Tool validation error | Reject request before execution. |
| Policy DENY | Do not execute; record reason. |
| Approval timeout/rejection | Remain blocked/cancelled according to policy. |
| Execution error | Capture evidence, classify and route to recovery if allowed. |
| Test/build failure | Enter diagnosis/recovery path if configured. |
| Patch conflict | Reject application and require refreshed context/patch. |
| Git conflict/user-change risk | Preserve user changes and stop for intervention. |
| Recovery exhaustion | Stop safely and report failure. |
| Security violation attempt | Deny, audit and prevent bypass. |

# 13. MVP Requirements Boundary

## 13.1 MVP shall include

- Local workspace/repository.

- One primary Agent Runtime.

- One initial LLM provider behind an abstraction.

- Repository scan/search/repository map.

- Validated file creation/editing.

- Controlled terminal/PowerShell execution.

- Configured lint/build/test validation.

- Failure classification and bounded repair/retest.

- Git status/diff/checkpoint/rollback.

- Task progress and activity/audit.

- Completion Gate and final report.

- CLI/headless core loop.

- Basic VS Code integration after runtime reliability.

## 13.2 Explicitly deferred

- Unrestricted computer/OS control.

- Fully autonomous production deployment.

- Live trading.

- Full multi-agent swarms.

- Complex model routing.

- Broad cloud/remote execution.

- Advanced background autonomy.

- Advanced semantic/vector retrieval unless evaluation proves need.

- Enterprise-scale multi-project controls.

# 14. Requirements Traceability

Every implementation task should map to one or more SRS requirements, and every completion decision should map to validation evidence.

| Traceability level | Expected artifact |
| --- | --- |
| Product | PRD requirement/goal |
| Software requirement | SRS REQ/NFR/SEC/AR identifier |
| Architecture | Component/boundary decision |
| Implementation | Task Backlog task ID |
| Code | Changed module/file |
| Test | Test case/suite |
| Evidence | Validation result/audit event |
| Outcome | Final report |

Traceability must be maintained without silently changing locked requirements.

# 15. SRS Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| SRS-A01 | Requirement coverage | All major PRD product goals are represented by detailed software requirements. |
| SRS-A02 | Testability | Requirements are expressed in verifiable terms wherever practical. |
| SRS-A03 | Security coverage | Tool, policy, workspace, secrets, MCP, recovery and client boundaries are explicitly specified. |
| SRS-A04 | Completion integrity | Completion Gate behavior is explicitly required. |
| SRS-A05 | Recovery | Failure → diagnosis → repair → retest is explicitly bounded. |
| SRS-A06 | Traceability | Requirements can be traced to architecture, implementation and validation. |
| SRS-A07 | MVP boundary | Required MVP capabilities and deferred capabilities are explicit. |
| SRS-A08 | Client independence | CLI/headless and VS Code separation is explicit. |
| SRS-A09 | Data | Core task/tool/policy/context/change/validation/error/memory/audit/report objects are defined. |
| SRS-A10 | Change control | Locked requirements cannot be silently changed. |

# 16. Dependencies & Constraints

- PRD v1.0 is the authoritative product scope.

- Architecture and technical documents define implementation boundaries.

- Technology decisions define the proposed implementation stack but do not override product requirements.

- Repository Blueprint defines physical module organization.

- Testing & Validation Plan defines detailed validation strategy.

- Security & Sandbox Specification defines detailed security/isolation controls.

- Tool & Permission Specification defines detailed tool authorization behavior.

- VS Code Integration Specification defines detailed client behavior.

- Implementation Plan and Task Backlog convert this SRS into execution tasks.

# 17. Assumptions

- The initial target environment is Windows with PowerShell and VS Code.

- The core runtime can run locally without VS Code.

- A Git repository may be present but the system must safely handle repository state conditions defined by implementation.

- Project-specific validation commands may vary; the system therefore requires configurable command discovery/configuration.

- Language-specific repository intelligence will expand incrementally.

- Advanced capabilities are introduced only when their evaluation demonstrates sufficient reliability.

# 18. Change Control

- Any material change to a locked SRS requirement requires a change identifier and impact assessment.

- Changes affecting security boundaries, Completion Gate behavior, MVP scope, or architectural contracts require explicit review.

- Implementation discoveries that do not alter product/software requirements belong in the engineering backlog.

- New requirements discovered during implementation shall not be silently inserted into existing tasks.

- Version increments shall follow the project's documentation/versioning policy.

# 19. Final Status

STATUS: FINAL / LOCKED — v1.0

This SRS is the authoritative detailed software-requirements baseline derived from PRD v1.0. Downstream architecture, technical design, behavior, security, tool, testing, implementation and task artifacts shall remain traceable to this specification.

— END OF SRS v1.0 —
