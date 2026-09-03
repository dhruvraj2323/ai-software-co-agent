AI SOFTWARE CO-AGENT

MASTER ARCHITECTURE

Version 1.0 — FINAL / LOCKED

Document ID: MAR-001 • Consolidated implementation architecture for the AI Software Co-Agent

| Field | Value |
| --- | --- |
| Document | Master Architecture |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Provide one consolidated architectural map from client entry to planning, context, policy, execution, validation, recovery, evidence and completion. |
| Authority | Consolidates the locked Architecture, Technical Design and Architecture Decision Matrix; detailed subsystem specifications remain authoritative for their respective behavior. |
| Change policy | Material architecture changes require formal versioned change control. |

Lock Statement: Master Architecture v1.0 is the final locked architectural map of the AI Software Co-Agent. It is the implementation north star: modules, boundaries, ownership, data flow, authority and lifecycle must remain consistent with this document unless formally changed.

# 1. Architecture Mission

The AI Software Co-Agent is designed as a controlled software-engineering runtime in which the model provides reasoning and proposals, while explicit runtime components control context, task state, tools, permissions, secure execution, validation, recovery and evidence.

Master principle: Intelligence proposes; the controlled runtime decides, executes, validates and records.

# 2. Architecture Goals

- Reliable repository-aware software engineering.

- Explicit separation of reasoning from side effects.

- Centralized tool authorization.

- Defense-in-depth execution security.

- Scoped, fresh and budgeted context.

- Observable task lifecycle.

- Bounded error recovery.

- Evidence-based validation and completion.

- Preservation of user changes.

- Replaceable model/client/external-tool integrations.

- Extensible architecture without weakening core invariants.

- Implementation simplicity where specialization is not justified.

# 3. Master System Context

USER

│

┌─────────┴─────────┐

│ │

VS CODE CLI

│ │

└─────────┬─────────┘

│

CLIENT PROTOCOL

│

▼

┌───────────────────┐

│ CO-AGENT CORE │

│ Session / Task │

│ Orchestrator │

└─────────┬─────────┘

│

┌─────────────────┼─────────────────┐

▼ ▼ ▼

Context Planning State

│ │ │

└─────────────────┼─────────────────┘

▼

TOOL GATEWAY

│

POLICY ENGINE

│

┌──────────────────┼──────────────────┐

▼ ▼ ▼

Workspace Process MCP

Sandbox Sandbox Adapter

│ │ │

└──────────────────┼──────────────────┘

▼

VALIDATION RUNNER

│

RECOVERY CONTROLLER

│

COMPLETION GATE

│

AUDIT/EVIDENCE

# 4. Architectural Planes

| Plane | Components | Primary responsibility |
| --- | --- | --- |
| Client Plane | VS Code, CLI | User interaction, commands, display; no privileged authority. |
| Control Plane | Session, Task, Orchestrator, Policy, Tool Gateway | Own lifecycle, authorization and controlled orchestration. |
| Intelligence Plane | Model Gateway, Planner, Context, Memory, Repository Intelligence | Reasoning inputs, planning and software understanding. |
| Execution Plane | Workspace, Process, Patch, Git, MCP adapters | Authorized side effects. |
| Quality Plane | Validation, Recovery, Completion | Detect, repair, retest and prove completion. |
| Evidence Plane | Audit, Events, Artifacts | Traceability, diagnostics and evidence. |
| Security Plane | Scope, Sandbox, Secret, Injection controls | Cross-cutting enforcement and fail-closed boundaries. |

# 5. Trust & Authority Model

| Component/data | Trust | Authority |
| --- | --- | --- |
| Security hard rules | Highest | May block/limit all operations |
| Policy Engine | Trusted runtime | Authorizes capabilities within hard security rules |
| Tool Gateway | Trusted runtime | Routes authorized capabilities |
| Executors/Sandbox | Trusted enforcement boundary | Enforce actual side-effect constraints |
| Task/State | Runtime state | Owns lifecycle state |
| Planner/Model | Untrusted proposal | Cannot authorize |
| Memory/Context | Advisory data | Cannot authorize |
| Repository content | Untrusted data | Cannot authorize |
| MCP result | Untrusted external data | Cannot authorize |
| VS Code/CLI | Client | Cannot authorize |

# 6. Component Inventory

| ID | Component | Role | Authority | Depends on |
| --- | --- | --- | --- | --- |
| C01 | Client Protocol | Typed client/runtime communication | None | Runtime session |
| C02 | Session Manager | Session identity/lifecycle | Runtime | Core contracts |
| C03 | Task Manager | Task state and ownership | Runtime | State contracts |
| C04 | Orchestrator | Coordinates task lifecycle | Runtime behavior | Task/context/tools/validation |
| C05 | Planner | Creates task plans | Proposal only | Context + model |
| C06 | Model Gateway | Provider abstraction | None | Model provider |
| C07 | Context Engine | Selects/ranks context | Advisory | Repository + memory |
| C08 | Memory Manager | Scoped persistence | Advisory | Storage + provenance |
| C09 | Repository Intelligence | Maps/searches repository | Read capability | Workspace |
| C10 | Tool Gateway | Single capability route | Runtime | Registry + policy |
| C11 | Tool Registry | Tool schemas/capabilities | Descriptive | Contracts |
| C12 | Policy Engine | ALLOW/ASK/DENY/RESTRICT | Authorization | Security + scope |
| C13 | Workspace Executor | Authorized filesystem changes | Execution | Sandbox + scope |
| C14 | Process Executor | Authorized process execution | Execution | Sandbox + policy |
| C15 | Patch Engine | Safe code changes | Execution | Workspace + conflict checks |
| C16 | Git Adapter | Version/change operations | Execution | Policy + repository |
| C17 | MCP Adapter | External tools | Execution | Policy + MCP |
| C18 | Validation Runner | Tests/checks/gates | Quality | Execution + evidence |
| C19 | Recovery Controller | Bounded diagnosis/repair/retest | Quality | Validation + tools |
| C20 | Completion Gate | Authoritative completion decision | Quality | Validation + evidence |
| C21 | Audit/Event System | Structured events/evidence | Evidence | All material components |
| C22 | Artifact Store | Large output/evidence | Evidence | Scope + storage |
| C23 | Security/Sandbox | Cross-cutting enforcement | Highest | OS/runtime |

# 7. Component Dependency Graph

C01 Client Protocol

↓

C02 Session Manager → C03 Task Manager

↓

C04 Orchestrator

↙ ↓ ↘

C05 Planner C07 Context C18 Validation

↓ ↓ ↓

C06 Model C08 Memory C19 Recovery

↑ ↓

C09 Repository C20 Completion

↓ ↓

C10 Tool Gateway

↓

C12 Policy Engine

↓

┌────────────┼────────────┐

↓ ↓ ↓

C13 C14 C17

Workspace Process MCP

↓ ↓ ↓

C15 C16 C22

Patch Git Artifacts

└────────────┬────────────┘

↓

C21 Audit/Event

↑

C23 Security

# 8. Core Request Flow

USER REQUEST

↓

SESSION / TASK IDENTIFICATION

↓

CONTEXT ASSEMBLY

↓

PLANNING / AGENT REASONING

↓

TOOL REQUEST

↓

SCHEMA + SCOPE + RISK VALIDATION

↓

POLICY DECISION

├── DENY → BLOCK + AUDIT

├── ASK → USER APPROVAL → RE-EVALUATE

├── RESTRICT → CONSTRAIN → EXECUTE

└── ALLOW → EXECUTE

↓

TOOL RESULT

↓

CONTEXT REFRESH

↓

VALIDATION

├── PASS → COMPLETION GATE

└── FAIL → RECOVERY → RETEST

↓

EVIDENCE / AUDIT

↓

DONE

# 9. Tool Authorization Flow

| Step | Component | Action |
| --- | --- | --- |
| 1 | Agent/Planner | Proposes structured ToolRequest. |
| 2 | Tool Gateway | Validates request schema. |
| 3 | Scope Resolver | Resolves canonical resource scope. |
| 4 | Policy Engine | Evaluates capability, target, risk and mode. |
| 5 | Approval Manager | Requests exact user approval if required. |
| 6 | Security/Sandbox | Applies hard runtime restrictions. |
| 7 | Executor | Performs authorized operation. |
| 8 | Output Filter | Filters sensitive/unbounded output. |
| 9 | Audit | Records material decision/execution. |
| 10 | Agent | Consumes result as untrusted evidence/data. |

# 10. Workspace Architecture

- Workspace identity is explicit.

- Canonical paths are resolved before authorization.

- Workspace scope is task-bound.

- Protected paths are policy-controlled.

- Symlink/junction escape is prevented.

- User changes are detected/preserved.

- Repository intelligence reads through controlled workspace interfaces.

- Workspace expansion requires explicit policy/authorization.

# 11. Process Architecture

| Control | Master rule |
| --- | --- |
| Program | Must be authorized. |
| Arguments | Structured/validated; no blind command execution. |
| Working directory | Within authorized scope. |
| Environment | Filtered/allowlisted; secrets protected. |
| Network | Restricted unless authorized. |
| Timeout | Mandatory bounded lifetime. |
| Output | Bounded capture/artifact reference. |
| Privileges | No escalation by default. |
| Cancellation | Propagated to process control. |
| Cleanup | Processes/resources cleaned safely. |

# 12. Context & Memory Architecture

Repository State ─┐

Current Files ────┤

Search/Symbols ───┤

Task History ─────┼→ Context Providers → Rank/Filter → Budget

Memory ───────────┤ ↓

Tool Results ─────┘ Context Manifest

↓

Planner/Model

- Current authoritative repository state has priority over stale memory.

- Every context item has provenance where practical.

- Context is scoped to task/project.

- Memory cannot authorize tools.

- Secrets are filtered.

- Large content is summarized/artifact-referenced.

# 13. Agent Behaviour Architecture

UNDERSTAND

↓

PLAN

↓

EXECUTE

↓

OBSERVE

↓

VALIDATE

├── PASS → COMPLETE

└── FAIL → DIAGNOSE

↓

RECOVER

↓

RETEST

├── PASS → COMPLETE

└── FAIL → STOP / ESCALATE

- Every loop is bounded by task/time/tool/recovery budgets.

- Security/policy checks occur before side effects.

- Completion is evidence-driven.

- User approval pauses execution when required.

- Cancellation overrides normal continuation.

# 14. Validation & Completion Architecture

| Layer | Purpose |
| --- | --- |
| Unit | Component correctness. |
| Component | Subsystem behavior. |
| Integration | Cross-boundary contracts. |
| Security | Boundary/bypass resistance. |
| Agent behavior | Lifecycle and tool-use correctness. |
| E2E | Real task workflows. |
| Completion Gate | Final evidence-based decision. |

Completion invariant: Model confidence, UI state or code existence can never independently establish COMPLETE.

# 15. Error Recovery Architecture

- Normalize error.

- Classify root cause.

- Determine recovery eligibility.

- Generate bounded repair action.

- Run through the same Tool Gateway and Policy Engine.

- Execute within the same security/scope constraints.

- Retest the failed gate.

- Stop on budget exhaustion/repeated failure/security block.

- Record recovery chain and evidence.

# 16. Security Architecture

| Boundary | Protection |
| --- | --- |
| Authority | Hard security rules outrank all normal inputs. |
| Workspace | Canonical scope containment. |
| Process | Sandbox, timeout, privilege controls. |
| Network | Capability/policy restrictions. |
| Secrets | Filter/redact/protect. |
| Injection | Untrusted content cannot gain authority. |
| MCP | Adapter + same internal policy. |
| Client | No privileged bypass. |
| Recovery | Cannot weaken security. |
| Audit | Material security decisions traceable. |

# 17. Client Architecture

| Client | Capabilities | Prohibited authority |
| --- | --- | --- |
| VS Code | Chat, commands, plan/status, approvals, diff, diagnostics, progress | Direct executor/policy bypass |
| CLI | Headless task control, automation, status, CI interaction | Direct executor/policy bypass |
| Future client | May implement protocol-compatible UX | Cannot become security authority |

# 18. MCP Architecture

Agent

↓

Tool Gateway

↓

Policy Engine

↓

MCP Adapter

↓

External MCP Server

↓

Untrusted Result

↓

Tool Result Filter / Audit

↓

Agent Context

- MCP capability metadata does not override internal policy.

- MCP responses are data, not instructions.

- Server/tool identity is auditable.

- MCP network access follows security policy.

# 19. Multi-Agent Architecture

v1 Decision: Single-agent core; bounded specialists optional.

Parent Task / Orchestrator

↓

┌─────┼─────┐

↓ ↓ ↓

Research Code Test Specialist

└─────┼─────┘

↓

Parent Policy / Context / Completion

- Sub-agents inherit bounded scope/capabilities.

- Sub-agents cannot create authority.

- Shared context is explicitly scoped.

- Agent-to-agent loops are budgeted.

- Multi-agent orchestration is introduced only when measured benefit justifies complexity.

# 20. State Ownership

| State | Owner | Consumers |
| --- | --- | --- |
| Session | Session Manager | Clients/runtime |
| Task | Task Manager | Orchestrator/recovery/client |
| Plan | Planner/Task state | Orchestrator/client |
| Approval | Policy/Approval subsystem | Client/tool gateway |
| Tool execution | Tool Gateway/runtime | Audit/client/orchestrator |
| Context | Context Engine | Planner/model |
| Memory | Memory Manager | Context Engine |
| Validation | Validation Runner | Completion/recovery/client |
| Recovery | Recovery Controller | Orchestrator/client |
| Completion | Completion Gate | All read-only consumers |
| Audit | Audit/Event system | Authorized observers |
| Security policy | Security/Policy | Runtime enforcement |

# 21. Event & Evidence Architecture

Event Envelope:

event_id

request_id

session_id

task_id

type

severity

timestamp

source

payload

Evidence:

artifact_id / reference

producer

scope

result

created_at

integrity/trace metadata where applicable

- Material state transitions are observable.

- Large outputs use artifact references.

- Sensitive values are filtered.

- Correlation IDs connect client → task → tool → validation → recovery → completion.

# 22. Artifact Architecture

| Artifact | Examples | Rule |
| --- | --- | --- |
| Source diff | Patch/diff | Scoped and reviewable. |
| Tool output | Command/test output | Bounded; large output referenced. |
| Validation evidence | Test reports | Authoritative for completion. |
| Recovery evidence | Diagnosis/repair/retest | Linked to failure chain. |
| Audit evidence | Policy/tool/security events | Protected from normal mutation. |
| Research evidence | Repo notes/benchmarks | Traceable to source/decision. |

# 23. Configuration Architecture

Hard Security Policy

↓

Runtime Configuration

↓

Project Configuration

↓

Behavior/Profile Configuration

↓

Task Inputs

- Lower layers cannot override hard security rules.

- Configuration is schema-validated.

- Security-sensitive configuration changes are protected/audited.

- Model/provider configuration is replaceable.

- Invalid security-sensitive configuration fails closed.

# 24. External Dependency Architecture

- Use adapters around external providers/services.

- Keep core contracts internally owned.

- Record license/security/maintenance decisions.

- Pin or constrain dependency versions appropriately.

- Do not let external repository structure become our internal architecture.

- External failures must be contained and observable.

# 25. Deployment Topology

Developer Machine

├── VS Code Extension

├── CLI

└── Co-Agent Runtime

├── Core Control Plane

├── Context/Memory

├── Tool Gateway / Policy

├── Sandboxed Executors

├── Validation / Recovery

└── Audit / Artifacts

Remote/cloud runtime is intentionally implementation/deployment-variable; the logical authority boundaries remain unchanged.

# 26. Failure Boundaries

| Failure | Architecture response |
| --- | --- |
| Model unavailable | Task pauses/fails safely; no unauthorized fallback. |
| Tool unavailable | Task blocks/replans; no direct executor bypass. |
| Policy unavailable | Affected privileged operation fails closed. |
| Sandbox unavailable | Operations requiring sandbox guarantee are blocked. |
| Context unavailable | Use only safe available context; do not invent state. |
| Validation failure | Recovery or stop; no completion. |
| Recovery exhausted | Stop/escalate; no infinite retry. |
| Client disconnected | Runtime remains authoritative; privileged client actions stop/block. |
| Audit failure | Security-critical action may be blocked according to policy. |
| MCP unavailable | External capability fails; no bypass. |

# 27. Performance & Resource Architecture

- Bound task, model, tool, process, context and recovery resources.

- Prefer incremental event streaming.

- Use artifacts for large outputs.

- Cache only safe/stale-aware information.

- Prevent unbounded concurrent tools.

- Measure before optimizing.

- Performance optimization cannot weaken security or validation.

# 28. Master Security/Quality Gates

G0 Foundation

↓

G1 Contracts

↓

G2 Repository/Scope

↓

G3 Security + Tool Authorization

↓

G4 Execution

↓

G5 Context

↓

G6 Agent Behaviour

↓

G7 Validation + Recovery

↓

G8 Audit + Client

↓

G9 E2E Hardening

↓

RELEASE

Gate rule: A failed mandatory gate blocks progression and cannot be bypassed by project schedule, model confidence or UI status.

# 29. Master Data Flow

User Intent

→ Task

→ Context Manifest

→ Plan

→ ToolRequest

→ PolicyDecision

→ Authorized Execution

→ ToolResult

→ State/Context Refresh

→ ValidationResult

→ [Recovery → Retest]*

→ CompletionEvidence

→ CompletionDecision

→ Client + Audit

# 30. Master Implementation Package

| Package | Expected modules |
| --- | --- |
| Core | src/core/, src/runtime/ |
| Agent | src/agent/ |
| Context | src/context/, src/memory/ |
| Repository | src/repository/, src/workspace/ |
| Tools | src/tools/ |
| Security | src/security/ |
| Execution | src/execution/, src/git/ |
| Validation | src/validation/ |
| Recovery | src/recovery/ |
| Observability | src/audit/, src/observability/ |
| Artifacts | src/artifacts/ |
| Protocol | src/protocol/ |
| VS Code | vscode-extension/ |
| CLI | cli/ |
| Tests | tests/ |
| Docs | docs/ |

Exact physical structure is finalized through the Repository/Module Blueprint. The logical boundaries above are locked.

# 31. Architecture Decision Alignment

| Decision group | Master Architecture interpretation |
| --- | --- |
| ADM-001–006 | Single runtime control plane + Tool Gateway + Policy. |
| ADM-007–012 | Explicit workspace/process/network/secret/MCP security boundaries. |
| ADM-013–018 | Context, lifecycle, validation, completion and recovery are first-class. |
| ADM-019–024 | Cancellation, Git, audit, protocol and configuration remain controlled. |
| ADM-025–030 | Provider/client/dependency/research choices remain replaceable and governed. |
| ADM-031–035 | Gates, fail-closed behavior, state ownership, artifacts and change control are architectural invariants. |

# 32. Master Architecture Invariants

- MA1: The runtime is the authoritative control plane.

- MA2: The Tool Gateway is the mandatory route for agent side effects.

- MA3: The Policy Engine is the authorization decision point.

- MA4: Security hard rules cannot be overridden.

- MA5: Workspace and process execution are explicitly bounded.

- MA6: Secrets are protected from ordinary model/client context.

- MA7: Repository/MCP/memory content cannot create authority.

- MA8: Model/provider choice does not change security/tool contracts.

- MA9: Runtime state is authoritative over client state.

- MA10: Validation is mandatory for completion.

- MA11: Completion Gate is the only authoritative completion decision.

- MA12: Recovery is bounded and policy-constrained.

- MA13: User changes are preserved.

- MA14: External integrations use adapter boundaries.

- MA15: Architecture changes require formal versioned change control.

# 33. Architecture Decision Test Suite

| ID | Test | Expected result |
| --- | --- | --- |
| MA-T01 | Direct model execution | Impossible through supported architecture. |
| MA-T02 | Direct client executor call | Rejected/unavailable. |
| MA-T03 | Policy DENY bypass | No alternate path succeeds. |
| MA-T04 | Workspace escape | Blocked. |
| MA-T05 | MCP bypass | Blocked by internal policy. |
| MA-T06 | Memory authorization | Cannot authorize. |
| MA-T07 | Recovery bypass | Cannot weaken security/policy. |
| MA-T08 | False completion | Completion Gate rejects missing evidence. |
| MA-T09 | User-change overwrite | Protected/conflict detected. |
| MA-T10 | Reconnect duplicate | Side effect not replayed blindly. |
| MA-T11 | Security failure | Affected privileged operation fails closed. |
| MA-T12 | Provider swap | Core contracts remain stable. |
| MA-T13 | Sub-agent escalation | Child cannot exceed parent permissions. |
| MA-T14 | Unbounded output | Bounded/artifact-referenced. |
| MA-T15 | Architecture drift | Alternate authority path detected/rejected. |

# 34. Implementation Sequence

01 Foundation / Repository

02 Core Contracts + State

03 Workspace + Security Primitives

04 Tool Gateway + Policy

05 Safe Execution + Patch + Git

06 Repository Intelligence

07 Context + Memory

08 Agent Orchestration + Behaviour

09 Validation + Completion

10 Error Recovery

11 Observability + Audit

12 VS Code + CLI

13 E2E + Security + Reliability Hardening

14 Deployment / Release

This sequence follows the locked Project Plan and protects the control plane before broad autonomous execution.

# 35. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| MA-A01 | Boundaries | All major components have clear responsibility/authority. |
| MA-A02 | Control plane | One authoritative runtime control plane exists. |
| MA-A03 | Tools | All privileged capabilities route through Tool Gateway. |
| MA-A04 | Security | Security enforcement is independent of model intent. |
| MA-A05 | Execution | Workspace/process/network boundaries are represented. |
| MA-A06 | Context | Context/memory are scoped, ranked and non-authoritative. |
| MA-A07 | Behaviour | Agent lifecycle is explicit. |
| MA-A08 | Validation | Validation/Completion are first-class. |
| MA-A09 | Recovery | Recovery is bounded and policy-constrained. |
| MA-A10 | Clients | VS Code/CLI are non-authoritative clients. |
| MA-A11 | Evidence | Audit/evidence supports reconstruction. |
| MA-A12 | External | MCP/providers/dependencies use adapters. |
| MA-A13 | Testing | Architecture decision tests exist. |
| MA-A14 | Implementation | Logical architecture maps to repository modules. |
| MA-A15 | Governance | Architecture changes require formal versioning. |

# 36. Traceability to Locked Baselines

| Baseline | Master Architecture role |
| --- | --- |
| 01 PRD v1.0 | Product intent and system scope. |
| 02 SRS v1.0 | System requirements and quality constraints. |
| 03 System Architecture v1.0 | Core architecture source. |
| 04 Technical Design v1.0 | Implementation contracts and component detail. |
| 05 Agent Behaviour v1.0 | Lifecycle and behavior model. |
| 06 Tool & Permission v1.0 | Tool/control authority. |
| 07 Memory & Context v1.0 | Context/memory architecture. |
| 08 Error Recovery v1.0 | Recovery/cancellation architecture. |
| 09 Testing & Validation v1.0 | Quality/completion gates. |
| 10 Security & Sandbox v1.0 | Security authority and isolation. |
| 11 VS Code Integration v1.0 | Client/runtime architecture. |
| 12 Project Plan & Progress v1.0 | Implementation sequence/gates. |
| 13 Research Synthesis v1.0 | External pattern adoption rules. |
| 14 Architecture Decision Matrix v1.0 | Major locked architectural decisions. |

# 37. Implementation Governance

- Every implementation module must map to a Master Architecture component.

- Every privileged capability must map to Tool Gateway + Policy + Security.

- Every completion path must map to Validation + Completion Gate.

- Every recovery path must map to Recovery Controller + same policy path.

- Every client action with side effects must map to a runtime request.

- Every external integration must map to an adapter.

- Every major architectural deviation must create a decision/change record.

- Implementation convenience cannot override a master invariant.

# 38. Final Change Control

- Material component boundary changes require architecture review.

- Changing authority/precedence requires formal change control.

- Adding a direct executor path is prohibited under v1.0.

- Changing completion authority requires Testing/Validation and architecture review.

- Changing security boundaries requires Security/Sandbox review.

- Changing protocol contracts requires compatibility/migration analysis.

- Adding multi-agent orchestration requires capability/isolation review.

- Future approved changes create Master Architecture v1.1+; v1.0 remains immutable.

# 39. Final Status

STATUS: FINAL / LOCKED — v1.0

Master Architecture v1.0 is the consolidated architectural north star for the AI Software Co-Agent. It establishes the client/control/intelligence/execution/quality/evidence/security planes, component boundaries, authority model, request and data flows, lifecycle, security boundaries, validation/recovery, implementation sequence and architectural invariants.

— END OF MASTER ARCHITECTURE v1.0 —
