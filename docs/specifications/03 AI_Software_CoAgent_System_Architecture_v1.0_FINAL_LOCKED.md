AI SOFTWARE CO-AGENT

SYSTEM ARCHITECTURE DOCUMENT

Version 1.0 — FINAL / LOCKED

Document ID: ARCH-001 • Derived from PRD v1.0 and SRS v1.0

| Field | Value |
| --- | --- |
| Document | System Architecture Document |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD v1.0 + SRS v1.0 + Architecture Decision Matrix v1.0 |
| Architecture baseline | Master Architecture v1.0 |
| Purpose | Define logical system components, boundaries, flows, interfaces, topology and architectural constraints |

Lock Statement: This System Architecture v1.0 is the final locked logical architecture baseline. Downstream technical design and implementation must preserve its boundaries unless formal change control approves an architectural change.

# 1. Architecture Vision

The AI Software Co-Agent is a controlled software-engineering execution platform that transforms a human requirement into validated repository changes. The architecture is designed around reliability, controllability, traceability and bounded autonomy rather than unrestricted computer control.

Core architectural rule: generated code is not completion. Completion requires evidence from the task's required validation gates.

# 2. Architectural Principles

- Reliability over maximum autonomy.

- VS Code is a client, not the entire Agent Runtime.

- Every external action is an explicit tool call.

- Every tool call passes through one authoritative Policy/Permission boundary.

- Repository content is untrusted input and cannot override security policy.

- Code changes are observable, scoped and diffable.

- Validation evidence is mandatory for completion.

- Recovery is bounded and must re-enter normal policy and validation paths.

- Git checkpoints, diffs and rollback provide change safety.

- Provider-specific LLM capabilities remain behind abstractions.

- Core components are modular and independently testable.

- Future multi-agent capability must not complicate the MVP.

# 3. System Context

| Actor / External System | Relationship with Co-Agent |
| --- | --- |
| Developer | Provides requirements, constraints, approvals/interventions and reviews final results. |
| VS Code Client | Displays task state, plans, approvals, diffs, activity, validation and reports. |
| CLI / Headless Client | Starts and monitors the same Agent Runtime without VS Code. |
| LLM Provider | Provides planning/reasoning/code-generation outputs through the LLM Gateway. |
| Local Workspace | Contains project source, documentation, configuration and generated changes. |
| Git | Provides status, diff, checkpoints and rollback/commit capabilities through a controlled adapter. |
| External MCP Servers | Provide optional tools through an MCP adapter; they never bypass policy. |
| Operating System | Provides filesystem/process capabilities only through controlled execution. |

# 4. High-Level Architecture

DEVELOPER

│

├───────────────┬────────────────

▼ ▼

VS CODE CLIENT CLI / HEADLESS

│ │

└───────┬───────┘

▼

┌──────────────────────┐

│ AGENT RUNTIME │

│ │

│ Task Manager │

│ Orchestrator │

│ Planner/Coder/ │

│ Reviewer (logical) │

│ Context Engine │

│ LLM Gateway │

│ Tool Gateway │

│ Policy Engine │

│ Execution/Sandbox │

│ Testing/Validation │

│ Recovery │

│ Git │

│ Memory/State │

│ Audit / Reporting │

└──────────┬───────────┘

│

CONTROLLED TOOL PATH

│

Tool Gateway

│

Policy Engine

│

Authorized Executor

┌──────┼──────┐

▼ ▼ ▼

Workspace Testing Git

│

▼

Validation Gate

│ │

│ fail │ pass

▼ ▼

Error Recovery COMPLETE

│

└──→ Retest

│

▼

REPORT

The diagram expresses logical boundaries; physical process/package boundaries are defined by the Technical Design and Technology Decision specifications.

# 5. Core Components & Responsibilities

| Component | Primary responsibility | Key output |
| --- | --- | --- |
| Task Manager | Task lifecycle, scope, acceptance criteria, budgets and state | Task state, task scope, lifecycle events |
| Agent Orchestrator | Controls the engineering loop and stage transitions | Next stage/action |
| Planner | Breaks requirements into executable plan | Plan, expected changes, validation requirements |
| Coder | Generates proposed code changes from approved plan | Patch/proposed edits |
| Reviewer | Checks changes, scope and quality | Review findings |
| Repository Intelligence | Understands project structure and relationships | Repository map, search, symbols, metadata |
| Context Engine | Selects task-relevant information within budget | Context package + provenance |
| LLM Gateway | Abstracts provider/model interaction | Structured model outputs |
| Tool Registry | Registers tools and capability metadata | Discoverable tool definitions |
| Tool Gateway | Single controlled route for tool invocation | Validated tool request/result |
| Policy Engine | Evaluates permissions/risk/scope/autonomy | ALLOW / ASK / DENY / RESTRICT |
| Execution / Sandbox | Performs authorized filesystem/process actions | Execution results/evidence |
| Testing / Validation | Runs required checks and produces evidence | Validation results |
| Completion Gate | Determines whether required gates passed | Complete / non-complete decision |
| Error Recovery | Normalizes, diagnoses, repairs and retests failures | Recovery attempt/result |
| Git Integration | Status, diff, checkpoint and rollback | Git state/change evidence |
| Memory / Project State | Persists task/project/session/decision/failure information | Context/state records |
| Audit Log | Records important activity and security decisions | Structured events |
| Reporting | Builds final implementation report | Final report |

# 6. Foundational Architectural Boundaries

| Boundary | Responsibility | Non-negotiable rule |
| --- | --- | --- |
| Agent Boundary | Decides what engineering step should occur | Cannot bypass security/tool boundaries. |
| Context Boundary | Controls what repository/task information reaches the model | Context is selected, budgeted and provenance-aware. |
| Tool Boundary | Represents executable capabilities | Every external action is an explicit tool. |
| Policy Boundary | Authorizes tool actions | No tool execution before policy decision. |
| Execution Boundary | Performs authorized side effects | Only authorized, scoped operations execute. |
| Validation Boundary | Determines evidence-backed completion | No COMPLETE without required validation evidence. |

Fundamental chain: Human Requirement → Agent Plan → Context → Tool Request → Policy → Execution → Validation → Recovery → Completion Gate → Report

# 7. Primary Data Flow

| Stage | Name | Architectural behavior |
| --- | --- | --- |
| 1 | Requirement | Client submits natural-language requirement. |
| 2 | Normalize | Task Manager creates structured task, scope and acceptance criteria. |
| 3 | Discover | Repository Intelligence inspects authorized workspace and relevant Git state. |
| 4 | Context | Context Engine selects ranked, budgeted, provenance-aware context. |
| 5 | Plan | Planner creates implementation plan, expected changes and validation gates. |
| 6 | Policy | Required actions are represented as tool requests and evaluated. |
| 7 | Implement | Coder produces validated patch/change proposals; authorized changes are applied. |
| 8 | Validate | Testing/Validation runs configured gates and records evidence. |
| 9 | Diagnose | Failures are normalized/classified and relevant context is assembled. |
| 10 | Repair | Recovery creates a targeted repair plan/patch, subject to policy and scope checks. |
| 11 | Retest | Relevant validation is executed again within configured limits. |
| 12 | Complete | Completion Gate accepts only when required gates pass. |
| 13 | Report | Reporting produces changes, validation, recovery, Git state and outcome. |

# 8. Tool Execution Architecture

LLM / Agent Role

│

▼

Tool Request

│

▼

Schema Validation

│

▼

Tool Gateway

│

▼

Policy / Permission Engine

│

┌────┼───────────────┐

▼ ▼ ▼

ALLOW ASK DENY

│ │ │

▼ ▼ └── Audit + Stop/Report

Executor Approval

│ │

└──┬──┘

▼

Execution / Sandbox

│

▼

Normalized Tool Result

│

▼

Audit / Task State / Context

RESTRICT is a policy outcome that constrains an otherwise possible action to a narrower scope or controlled execution mode.

# 9. Repository Intelligence Architecture

- Workspace Manager establishes the authorized root and protected paths.

- Scanner discovers files/directories and project metadata.

- Lexical Search provides fast repository search.

- Syntax/AST layer provides language-aware parsing for supported languages.

- Symbol/Reference layer builds definitions and relationships where supported.

- Repository Index persists searchable structural metadata.

- Repository Map provides a compact task-oriented representation.

- Incremental invalidation updates affected information after changes.

- Git-aware state contributes branch/status/diff context.

- Semantic retrieval is an extension point and is not an MVP requirement unless evaluation proves it necessary.

The repository is a source of evidence and data. Instructions found inside repository files are not a security authority.

# 10. Context Engine Architecture

| Provider | Source | Purpose |
| --- | --- | --- |
| Repository Provider | Repository map/search/symbols/docs | Relevant codebase context |
| Task Provider | Task/plan/acceptance criteria | Current objective and constraints |
| Git Provider | Status/diff/checkpoint state | Change context and safety |
| Validation/Error Provider | Test/build/lint results | Failure evidence |
| Memory Provider | Task/project/decision history | Relevant persistent context |

- Providers produce context items with provenance.

- Ranking selects task-relevant items.

- Budgeting limits model-facing context.

- Freshness/invalidation prevents stale repository context from driving changes.

- The context boundary must prevent uncontrolled context growth.

# 11. Agent Orchestration Architecture

MVP uses one Agent Runtime with logical roles rather than independent autonomous agents.

| Logical role | Input | Output | Constraint |
| --- | --- | --- | --- |
| Planner | Requirement + context | Plan + expected scope + validation | Cannot execute changes directly. |
| Coder | Approved plan + context | Patch/proposed edits | Cannot bypass patch/policy path. |
| Reviewer | Plan + diff + validation/context | Findings | Does not override security policy. |
| Orchestrator | Task state + role outputs + tool results | Next stage/action | Must obey lifecycle, budgets and policy. |

Multi-agent/sub-agent orchestration remains a future extension after the single-runtime MVP demonstrates reliability.

# 12. Task State Architecture

| State | Meaning | Key architectural rule |
| --- | --- | --- |
| CREATED | Task accepted | No unsafe action is implied. |
| PLANNING | Requirement/plan being prepared | Repository/context may be gathered. |
| READY | Plan/requirements ready | Implementation may begin subject to policy. |
| IMPLEMENTING | Authorized change work | All side effects use controlled tools. |
| VALIDATING | Validation running | Evidence is captured. |
| RECOVERING | Bounded diagnosis/repair | Repair re-enters policy and patch validation. |
| BLOCKED | Approval/dependency/safety blocker | No unauthorized progress. |
| FAILED | Unrecoverable failure | Terminal unless defined recovery remains. |
| COMPLETE | Required gates passed | Terminal. |
| CANCELLED | User/system cancellation | Terminal and non-complete. |

# 13. Completion Gate Architecture

Completion Gate is a first-class architectural component, not merely a UI status.

- It consumes task acceptance criteria and required validation gates.

- It consumes structured validation evidence.

- It verifies that required gates have passed.

- It verifies required recovery validation after repair when recovery occurred.

- It verifies required security/Git conditions where configured.

- It prevents false COMPLETE status.

- It produces an auditable completion decision.

Hard rule: If required validation evidence is missing or failed, the task remains non-complete.

# 14. Error Recovery Architecture

Validation / Execution Failure

↓

Error Normalization

↓

Error Classification

↓

Failure Context Assembly

↓

Diagnosis / Root-Cause Hypothesis

↓

Repair Plan

↓

Policy + Patch Validation

↓

Apply Repair

↓

Retest

↓

┌────────┴─────────┐

PASS FAIL

│ │

Completion Retry within budget

│

Stop when exhausted

- Recovery must have attempt/time/scope budgets.

- Recovery cannot bypass the Tool Gateway or Policy Engine.

- Recovery cannot declare completion without validation evidence.

- Exhausted or unsafe recovery transitions to a non-complete state.

# 15. Git Safety Architecture

- Capture relevant baseline state before task-owned mutations.

- Detect pre-existing unrelated changes.

- Expose status and diff.

- Create task checkpoints.

- Support safe rollback of task-owned changes.

- Preserve unrelated user changes.

- Keep commit operations policy/approval-controlled.

- Never silently execute destructive reset/clean behavior.

# 16. Memory, State & Audit Architecture

| Store / service | Purpose | Authority limit |
| --- | --- | --- |
| Task State | Lifecycle, scope, budgets, outcome | Cannot override security policy. |
| Project Memory | Project conventions/context | Advisory/context only. |
| Task Memory | Task-specific facts/history | Advisory/context only. |
| Decision Records | Recorded choices and rationale | Traceability only. |
| Failure History | Prior failures/recovery evidence | Advisory; never security authority. |
| Audit Log | Tool/policy/change/validation/recovery/Git events | Append-oriented evidence. |
| Report Store | Final task evidence/report | Derived from recorded evidence. |

# 17. Client Architecture

- VS Code and CLI/headless clients connect to the same Agent Runtime.

- Clients request actions and display state; they do not directly execute privileged operations.

- Approval requests are represented by runtime state/policy decisions.

- Diffs, validation evidence and reports are returned from runtime services.

- Client protocol must be versioned and capability-aware.

- Future clients can reuse the same runtime boundary.

# 18. MCP Architecture

- MCP is an extensibility mechanism, not a security boundary.

- MCP servers are treated as external/untrusted tool sources.

- MCP tools are adapted into the internal Tool model.

- Every MCP invocation passes through the Tool Gateway.

- Every MCP invocation passes through the Policy Engine.

- MCP identity/capability and relevant invocation outcomes are auditable.

- MCP must never create a second execution path around the policy boundary.

# 19. LLM Gateway Architecture

- The Agent Runtime communicates with models through an LLM Gateway.

- Provider-specific SDK/request/response details remain inside provider adapters.

- Structured outputs are schema-validated.

- Tool requests generated by the model become explicit validated Tool Request objects.

- Provider failures are normalized into runtime errors.

- Model/provider information needed for reproducibility can be recorded.

- The architecture supports future provider/model expansion without rewriting the core runtime.

# 20. Security Zones

| Zone | Trust posture | Controls |
| --- | --- | --- |
| Client Zone | User-facing | No privileged execution path. |
| Agent/Reasoning Zone | Model-influenced | Treat model output as untrusted; explicit contracts. |
| Context Zone | Repository-derived | Repository content is untrusted data. |
| Tool Zone | Capability boundary | Schema validation + Tool Gateway. |
| Policy Zone | Authoritative security decision | Deterministic authorization and precedence. |
| Execution Zone | Privileged side effects | Authorized executor + workspace/sandbox controls. |
| Validation Zone | Evidence | Structured results and Completion Gate. |
| Persistence Zone | State/evidence | Validated schemas and auditability. |

# 21. Dependency Direction

Clients

↓

Agent Runtime / Task / Orchestrator

↓

Context + LLM + Tool contracts

↓

Tool Gateway

↓

Policy Engine

↓

Execution / Sandbox

↓

OS / Workspace / Process

Validation / Recovery / Git / Memory / Audit / Reporting

↕

Agent Runtime state and evidence

Provider adapters → LLM Gateway

MCP adapters → Tool Gateway

VS Code → Runtime client boundary

No component below the Policy Boundary may be used by model-facing code as an alternate route to side effects.

# 22. Runtime Topology

| Runtime element | MVP topology |
| --- | --- |
| VS Code | Separate client process/extension. |
| CLI | Separate client process. |
| Agent Runtime | Primary local process/runtime. |
| LLM Provider | External service/provider accessed through gateway. |
| Workspace | Local controlled filesystem. |
| Git | Local Git repository/CLI through adapter. |
| MCP | Optional external/local servers through adapter. |
| Persistent state | Local SQLite-backed stores/files as selected by technology baseline. |
| Sandbox | Execution boundary behind pluggable interface. |

The exact IPC protocol and packaging topology are defined at technical-design/implementation level; this architecture requires client/runtime separation.

# 23. Future Extension Points

- Multiple LLM providers/models.

- Semantic/vector retrieval if evaluation justifies it.

- Additional language parsers.

- Advanced sandbox implementations.

- Additional clients.

- MCP ecosystem expansion.

- Specialist agents/sub-agents.

- Background/autonomous workers.

- Multi-project management.

- Remote/distributed execution.

These extension points must not be introduced into the MVP in ways that weaken the core boundaries.

# 24. Research-Derived Architecture Decisions

| Capability | Research direction | Architecture treatment |
| --- | --- | --- |
| Repository intelligence | Aider + Continue + SWE-agent | Core Repository Intelligence Engine. |
| Context | Aider + Continue + Plandex | Provider/ranking/budget boundary. |
| Editing | Aider + SWE-agent | Validated patch/diff approach. |
| Tool system | SWE-agent + Continue + Goose | Central Tool Registry + Gateway. |
| Permission | Continue + Cline + Roo Code | Deterministic ALLOW/ASK/DENY/RESTRICT policy. |
| Terminal | SWE-agent + OpenHands + Cline | Controlled executor behind policy/sandbox. |
| Testing | Aider + SWE-agent | Lint/build/test/regression validation. |
| Recovery | Aider + SWE-agent + OpenHands | Normalize/classify/diagnose/repair/retest. |
| Git | Aider | Status/diff/checkpoint/rollback. |
| Sandbox | OpenHands | Controlled execution boundary. |
| MCP | Goose | Adapter behind internal Tool Gateway. |
| Logical roles | MetaGPT | Planner/Coder/Reviewer workflow inside one runtime initially. |

These are architecture reuse/adaptation directions derived from the research baseline; the architecture does not require copying any single repository wholesale.

# 25. Architecture Traceability

| Source | Architecture impact |
| --- | --- |
| PRD v1.0 | Product vision, scope, safety, MVP and completion principles. |
| SRS v1.0 | Detailed functional/non-functional/security requirements. |
| Architecture Decision Matrix v1.0 | Research-derived component and boundary decisions. |
| Master Architecture v1.0 | Logical component model and primary data-flow baseline. |
| Technical Design v1.0 | Implementation-level realization of these boundaries. |
| Technology Decision v1.0 | Concrete technology choices within architecture. |
| Repository Blueprint v1.0 | Physical folder/module organization. |
| Implementation Plan v1.0 | Phase sequence. |
| Task Backlog v1.0 | Implementation work items and acceptance criteria. |

# 26. Architecture Constraints

- Windows-first MVP with PowerShell and VS Code.

- Core Agent Runtime must run without VS Code.

- No unrestricted AI-to-OS access.

- All external actions use explicit tools.

- All tool actions use one authoritative policy boundary.

- Repository instructions cannot override security policy.

- Completion requires evidence.

- Recovery is bounded.

- User changes must be preserved.

- Provider-specific implementations stay behind adapters.

- MVP uses one runtime with logical roles before multi-agent architecture.

- Cloud/distributed infrastructure is not required for the local MVP.

# 27. Architecture Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| ARCH-A01 | Component completeness | All core runtime components required by PRD/SRS are represented. |
| ARCH-A02 | Boundary integrity | Agent, Context, Tool, Policy, Execution and Validation boundaries are explicit. |
| ARCH-A03 | Tool safety | No alternate tool execution path exists outside the Tool Gateway/Policy path. |
| ARCH-A04 | Client separation | VS Code/CLI are clients over an independent runtime. |
| ARCH-A05 | Completion integrity | Completion Gate is architecturally separate from code generation. |
| ARCH-A06 | Recovery safety | Recovery re-enters policy, patch validation and testing. |
| ARCH-A07 | Repository intelligence | Repository map/search/symbol/context capabilities are first-class. |
| ARCH-A08 | Git safety | Baseline/diff/checkpoint/rollback concepts are first-class. |
| ARCH-A09 | Extensibility | LLM, MCP, clients and future multi-agent capabilities have defined extension points. |
| ARCH-A10 | Testability | Major components expose testable boundaries. |
| ARCH-A11 | Traceability | Architecture can be traced to requirements and downstream implementation artifacts. |
| ARCH-A12 | MVP discipline | Deferred capabilities do not become mandatory dependencies. |

# 28. Architecture Change Control

- Changes to locked architectural boundaries require a change identifier and impact assessment.

- Security boundary changes require explicit security review.

- Changes to Completion Gate behavior require validation-impact review.

- Changes that add a privileged execution path are prohibited unless the architecture is formally revised and the security model is updated.

- Implementation discoveries that do not change architectural intent belong in the task backlog/technical design rather than silently changing this document.

- Any approved architecture change must update affected downstream documents and traceability.

# 29. Final Status

STATUS: FINAL / LOCKED — v1.0

This System Architecture v1.0 is the authoritative logical architecture baseline for the AI Software Co-Agent. It establishes the component model, security boundaries, execution flow, validation model, client separation, extension points and architectural constraints that downstream technical design and implementation must preserve.

— END OF SYSTEM ARCHITECTURE v1.0 —
