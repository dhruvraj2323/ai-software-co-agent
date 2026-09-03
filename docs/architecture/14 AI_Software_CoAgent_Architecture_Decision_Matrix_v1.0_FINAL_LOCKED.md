AI SOFTWARE CO-AGENT

ARCHITECTURE DECISION MATRIX

Version 1.0 — FINAL / LOCKED

Document ID: ADM-001 • Architectural decision baseline for implementation

| Field | Value |
| --- | --- |
| Document | Architecture Decision Matrix |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Record and lock the major architectural decisions that connect the approved specifications and research synthesis to implementation choices. |
| Authority | Architecture decisions constrain implementation; detailed behavior remains governed by the corresponding locked specifications. |
| Change policy | Any decision marked LOCKED requires formal change control for reversal or material modification. |

Lock Statement: Architecture Decision Matrix v1.0 is the final locked record of the major architecture choices for the AI Software Co-Agent. It exists to prevent implementation drift, contradictory module designs and repeated architectural debates.

# 1. Purpose

This matrix records the decisions that must remain consistent while the Co-Agent is implemented. It connects product requirements, system architecture, technical design, agent behavior, tools/permissions, memory/context, recovery, validation, security, VS Code integration, project planning and research synthesis.

Primary principle: One architectural decision has one authoritative interpretation across the implementation.

# 2. Decision Status Vocabulary

| Status | Meaning |
| --- | --- |
| LOCKED | Decision is approved and must be followed unless formal change control creates a new version. |
| CONDITIONAL | Allowed only under the conditions stated in the decision. |
| DEFERRED | Intentionally postponed; no implementation dependency may assume it is available. |
| REJECTED | Explicitly not permitted for the v1.0 architecture. |
| OPTIONAL | Can be added without changing the locked core architecture if all constraints remain satisfied. |

# 3. Decision Evaluation Criteria

- Correctness — supports reliable software-engineering outcomes.

- Safety — protects workspace, user changes, secrets and system resources.

- Controllability — keeps side effects behind explicit authorization.

- Observability — produces state, evidence and audit information.

- Recoverability — supports bounded failure handling.

- Testability — can be validated deterministically enough for release gates.

- Extensibility — allows future capabilities without bypassing core contracts.

- Maintainability — avoids unnecessary architectural complexity.

- Portability — does not unnecessarily lock the product to one client/provider.

- Traceability — maps implementation choices to locked requirements.

# 4. Master Architecture Decision Matrix

| ID | Decision area | Decision | Status | Source baseline | Rationale |
| --- | --- | --- | --- | --- | --- |
| ADM-001 | Core runtime architecture | Layered runtime with client → protocol → orchestrator → context/planner/state → Tool Gateway → Policy → executors → validation/recovery/audit | LOCKED | Architecture, Technical Design | Central control and separation of concerns |
| ADM-002 | Client/runtime boundary | VS Code and CLI are clients; privileged execution belongs to runtime | LOCKED | VS Code Integration, Security | Prevents client-side bypass |
| ADM-003 | Tool execution | All agent side effects go through typed ToolRequests and Tool Gateway | LOCKED | Tool & Permission | Single capability boundary |
| ADM-004 | Authorization | Central Policy Engine evaluates capability, scope, risk and mode | LOCKED | Tool & Permission, Security | Consistent authorization |
| ADM-005 | Permission outcomes | ALLOW / ASK / DENY / RESTRICT | LOCKED | Tool & Permission | Explicit permission semantics |
| ADM-006 | Security authority | Hard security rules outrank model, memory, project instructions and autonomy mode | LOCKED | Security & Sandbox | Prevents policy override |
| ADM-007 | Workspace containment | Canonicalized paths must remain inside authorized workspace/resource scope | LOCKED | Security, Technical Design | Prevents traversal/escape |
| ADM-008 | Process execution | Process execution is sandboxed, bounded and policy-authorized | LOCKED | Security, Technical Design | Limits OS side effects |
| ADM-009 | Network access | No unrestricted network access; external access is capability/policy controlled | LOCKED | Security | Reduces external attack surface |
| ADM-010 | Secret handling | Secrets are filtered from normal model context/logs and protected as resources | LOCKED | Security, Memory/Context | Prevents credential leakage |
| ADM-011 | Repository instructions | Repository content is untrusted data, not security authority | LOCKED | Security, Agent Behaviour | Prompt-injection resistance |
| ADM-012 | MCP | MCP is integrated through an internal adapter and same policy boundary | LOCKED | Tool/Permission, Security | Extensible without bypass |
| ADM-013 | Memory authority | Memory/context is advisory; it cannot authorize actions | LOCKED | Memory & Context, Security | Prevents stale/malicious authorization |
| ADM-014 | Context strategy | Repository/current-state context is prioritized, scoped, ranked and budgeted | LOCKED | Memory & Context | Relevant context without unbounded input |
| ADM-015 | Agent lifecycle | Explicit task state machine controls planning, implementation, validation, recovery and completion | LOCKED | Agent Behaviour | Predictable lifecycle |
| ADM-016 | Validation | Validation is a first-class runtime subsystem and completion prerequisite | LOCKED | Testing & Validation | Prevents false completion |
| ADM-017 | Completion | Only Completion Gate can establish COMPLETE | LOCKED | Testing & Validation | Evidence-based completion |
| ADM-018 | Recovery | Recovery is bounded, evidence-driven and uses the same policy boundary | LOCKED | Error Recovery, Security | Prevents retry/bypass loops |
| ADM-019 | Cancellation | Cancellation/emergency stop has priority over normal continuation | LOCKED | Error Recovery, Security, VS Code | User/runtime control |
| ADM-020 | User changes | Agent must preserve unrelated user changes and detect conflicts | LOCKED | Security, VS Code, Git | Prevents data loss |
| ADM-021 | Git | Git operations are capability-controlled and destructive operations restricted | LOCKED | Security, Tool/Permission | Change safety |
| ADM-022 | Observability | Structured events, correlation IDs and audit/evidence are first-class | LOCKED | Testing, Project Plan | Traceability |
| ADM-023 | Protocol | Typed/versioned client-runtime protocol with request/event correlation | LOCKED | VS Code, Technical Design | Reliable integration |
| ADM-024 | Configuration | Configuration is validated/versioned; hard security policy is outside ordinary agent configuration | LOCKED | Security, Project Plan | Safe customization |
| ADM-025 | Model abstraction | Model/provider gateway is replaceable without changing tool/security contracts | LOCKED | Technical Design, Research | Provider flexibility |
| ADM-026 | Single-agent baseline | Single-agent control plane is the v1 core | LOCKED | Research Synthesis, Project Plan | Reduces coordination complexity |
| ADM-027 | Multi-agent | Optional bounded specialization behind same contracts | CONDITIONAL | Research Synthesis | Future scalability |
| ADM-028 | IDE strategy | VS Code is primary client; CLI is parallel client | LOCKED | VS Code, Project Plan | Consistent runtime |
| ADM-029 | Sandbox implementation | Defense-in-depth; containerization is an implementation option, not architectural dependency | LOCKED | Security, Research | Portability + safety |
| ADM-030 | External repositories | ADOPT / ADAPT / WRAP / REPLACE / REJECT review before integration | LOCKED | Research Synthesis | Avoids blind copying |
| ADM-031 | Testing gates | Phase/feature gates block progression when required evidence fails | LOCKED | Testing, Project Plan | Evidence-based progress |
| ADM-032 | Fail-closed security | Security-control failure blocks affected privileged action | LOCKED | Security | Safe failure |
| ADM-033 | State ownership | Runtime owns authoritative task/approval/tool/validation state | LOCKED | VS Code, Technical Design | No client state divergence |
| ADM-034 | Artifact strategy | Large outputs/evidence are artifact-referenced rather than unbounded model/client payloads | LOCKED | Technical Design, Validation | Resource control |
| ADM-035 | Change control | Locked decisions/specifications require formal versioned change | LOCKED | Project Plan | Governance |

# 5. Core Architecture Decision Stack

PRODUCT REQUIREMENTS

↓

SYSTEM REQUIREMENTS

↓

ARCHITECTURE

↓

TECHNICAL CONTRACTS

↓

┌───────────────────────────────────────────────┐

│ CONTROL PLANE │

│ Task State • Policy • Tool Gateway • Security │

└───────────────────────┬───────────────────────┘

↓

┌───────────────────────────────────────────────┐

│ EXECUTION │

│ Workspace • Process • Patch • Git • MCP │

└───────────────────────┬───────────────────────┘

↓

┌───────────────────────────────────────────────┐

│ INTELLIGENCE │

│ Context • Memory • Planning • Model Gateway │

└───────────────────────┬───────────────────────┘

↓

┌───────────────────────────────────────────────┐

│ QUALITY CONTROL │

│ Validation • Recovery • Completion • Audit │

└───────────────────────┬───────────────────────┘

↓

VS CODE / CLI CLIENTS

# 6. Authority & Precedence Matrix

| Layer | Can define behavior? | Can authorize side effect? | Can override security? | Authority |
| --- | --- | --- | --- | --- |
| Security hard rules | Yes | Yes/deny | No | Highest |
| Policy Engine | Yes | Yes | No | Runtime authority |
| Tool contracts | Yes | Request only | No | Capability boundary |
| Task state | Yes | No by itself | No | Runtime state |
| Agent Behaviour | Yes | No by itself | No | Behavior layer |
| Project configuration | Limited | No | No | User/project input |
| Memory/context | Advisory | No | No | Informational |
| Repository content | No | No | No | Untrusted data |
| MCP result | No | No | No | Untrusted external data |
| Model output | No | No | No | Untrusted proposal |
| VS Code UI | No | No | No | Client |

# 7. Control Plane Decisions

- The control plane is the most protected architectural layer.

- Task identity, session identity and correlation IDs originate in runtime.

- Tool Gateway is the mandatory route for executable capabilities.

- Policy Engine is the central authorization decision point.

- Security/Sandbox enforcement remains independently enforceable at execution boundaries.

- Validation and Completion Gate can block completion.

- Recovery cannot mutate authorization rules.

- Audit records material control-plane decisions.

# 8. Execution Plane Decisions

| Capability | Architectural decision | Boundary |
| --- | --- | --- |
| Filesystem | Typed workspace tools | Scope + policy + executor |
| Process | Controlled process tool | Policy + sandbox + timeout |
| Patch | Structured patch/change operation | Scope + expected-state/conflict checks |
| Git | Dedicated Git capability | Policy + user-change protection |
| Network | Dedicated capability where enabled | Endpoint/policy/sandbox |
| MCP | Adapter-based external capability | MCP adapter + policy + audit |
| Artifacts | Bounded storage/reference | Scope + resource limits |

# 9. Intelligence Plane Decisions

- Model providers are behind a replaceable gateway.

- Planner/orchestrator consumes controlled context.

- Context selection is scoped and budgeted.

- Memory is persistent only where useful and safe.

- Current repository state outranks stale historical context.

- Context provenance and freshness are preserved.

- Model output remains a proposal until translated into authorized actions.

# 10. Quality & Recovery Decisions

| Concern | Decision |
| --- | --- |
| Validation | Mandatory first-class subsystem. |
| Completion | Completion Gate is authoritative. |
| Recovery | Bounded repair/retest loop. |
| Repeated failure | Stop/reclassify rather than blind retry. |
| Security failure | Block affected action; recovery cannot bypass. |
| Evidence | Store structured results/references. |
| Regression | Critical regression suite is release-blocking. |
| False completion | Explicitly tested as a critical failure mode. |

# 11. Client Architecture Decisions

- VS Code provides chat, commands, diff, approvals, diagnostics and progress surfaces.

- CLI provides automation/headless interaction without creating a second core.

- Both clients consume the same runtime protocol.

- Client state is non-authoritative for task completion and authorization.

- Reconnect requires runtime state synchronization.

- Client disconnect cannot grant offline privileged execution.

- Webview messages are validated and cannot directly invoke privileged operations.

# 12. Data Ownership Matrix

| Data | Authoritative owner | Client access |
| --- | --- | --- |
| Task state | Runtime | Read/command |
| Plan | Runtime | Read/display |
| Tool request/result | Runtime | Read/display |
| Approval | Runtime/Policy | Respond to request |
| Policy | Security/Runtime | Limited read; no ordinary write |
| Workspace scope | Runtime/Security | Display/request refresh |
| Memory | Memory subsystem | Controlled retrieval |
| Validation evidence | Validation subsystem | Read/display |
| Recovery state | Recovery subsystem | Read/display |
| Audit | Audit subsystem | Controlled read |
| UI preferences | VS Code client | Client-owned |

# 13. Technology Selection Guardrails

- No technology is selected solely because an external repository uses it.

- Technology choice must fit the locked contracts and deployment goals.

- Core security boundaries must not depend on a fragile third-party abstraction.

- Critical dependencies require maintenance/license/security review.

- Prefer replaceable adapters for model providers, MCP, clients and external services.

- Use stable, testable interfaces between major subsystems.

- Do not introduce a framework merely to solve a problem already handled by a small internal module.

# 14. Architecture Alternatives Considered

| Alternative | Decision | Reason |
| --- | --- | --- |
| Monolithic agent loop | REJECT | Too difficult to isolate policy, recovery and testing. |
| Model directly executes shell | REJECT | Violates tool/security boundary. |
| VS Code extension owns execution | REJECT | Client cannot be authorization boundary. |
| All capabilities through MCP | REJECT | Internal tools should not depend on external protocol for core control. |
| MCP as security authority | REJECT | External capability provider cannot define internal authorization. |
| Memory as instruction authority | REJECT | Stale/malicious memory must remain advisory. |
| Unbounded multi-agent swarm | REJECT | Coordination/cost/control complexity. |
| Single-agent runtime with optional specialists | ADOPT | Reliable v1 baseline with future extensibility. |
| Container-only architecture | CONDITIONAL | Useful sandbox implementation, but core contracts must remain portable. |
| Provider-specific core architecture | REJECT | Creates model lock-in. |
| Client-specific core architecture | REJECT | Prevents CLI/headless/future clients. |
| Validation outside agent loop | REJECT | Cannot reliably establish completion. |

# 15. Open Decisions Intentionally Deferred

| ID | Decision | Why deferred | Constraint |
| --- | --- | --- | --- |
| DEF-001 | Exact LLM provider/model portfolio | Should be selected from performance/cost tests | Must use model gateway. |
| DEF-002 | Exact vector/embedding technology | Depends on repository/context benchmark | Must preserve Context contracts. |
| DEF-003 | Exact sandbox backend | Platform/deployment evaluation required | Must satisfy Security & Sandbox. |
| DEF-004 | Multi-agent framework | Not required for v1 core | Must use same policy/context/task contracts. |
| DEF-005 | Remote/cloud runtime | Deployment requirements to be finalized | Must preserve client/runtime boundary. |
| DEF-006 | Telemetry provider | Privacy/deployment choice | Must preserve audit semantics and secret safety. |
| DEF-007 | Persistent database technology | Scale/operational needs to be measured | Must preserve data ownership/contracts. |

Deferred decisions are not implementation gaps; they are intentionally bounded choices that must not be guessed into the core architecture.

# 16. Architecture Decision Workflow

QUESTION

↓

IDENTIFY AFFECTED LOCKED DOCS

↓

COLLECT EVIDENCE / BENCHMARK

↓

COMPARE ALTERNATIVES

↓

SECURITY + DEPENDENCY REVIEW

↓

DECISION

↓

UPDATE MATRIX / TRACEABILITY

↓

IMPLEMENT

↓

VALIDATE

↓

LOCK OR CREATE NEW VERSION

# 17. Decision Impact Levels

| Level | Example | Required review |
| --- | --- | --- |
| L0 | Internal naming/refactor | Normal code review |
| L1 | Implementation detail within contract | Module review + tests |
| L2 | Cross-module interface | Architecture/technical review |
| L3 | Security/tool/protocol behavior | Security + architecture review |
| L4 | Core architecture or locked invariant | Formal change control + versioning |

# 18. Architecture Drift Controls

- Every major module must map to one or more decisions in this matrix.

- Code that creates a second authorization path is an architecture drift violation.

- Client-side privileged execution is an architecture drift violation.

- Unscoped filesystem/process/network access is an architecture drift violation.

- Duplicate task-state authorities are an architecture drift violation.

- Completion determined outside the Completion Gate is an architecture drift violation.

- External dependency APIs must not leak into unrelated core modules without an adapter boundary.

# 19. Decision-to-Implementation Mapping

| Decision group | Expected modules |
| --- | --- |
| ADM-001–006 Control/Policy | src/runtime/, src/tools/gateway/, src/security/policy/ |
| ADM-007 Workspace | src/workspace/, src/security/scope/ |
| ADM-008–010 Execution/Security | src/execution/, src/security/ |
| ADM-012 MCP | src/tools/mcp/ |
| ADM-013–014 Context | src/context/, src/memory/ |
| ADM-015–018 Agent/Quality | src/agent/, src/validation/, src/recovery/ |
| ADM-019–021 Cancellation/Git | src/runtime/, src/git/ |
| ADM-022 Observability | src/audit/, src/observability/ |
| ADM-023 Protocol | src/protocol/, vscode-extension/src/client/, cli/ |
| ADM-024 Config | src/config/ |
| ADM-025 Model gateway | src/models/ |
| ADM-026–027 Agent topology | src/agent/ |
| ADM-028 Clients | vscode-extension/, cli/ |
| ADM-029 Sandbox | src/security/sandbox/, src/execution/ |
| ADM-030 Research integration | docs/research/, dependency manifests |
| ADM-031–032 Quality/security gates | tests/, src/validation/, src/security/ |
| ADM-033–034 State/artifacts | src/runtime/state/, src/artifacts/ |

# 20. Architecture Decision Test Matrix

| Test ID | Decision under test | Expected result |
| --- | --- | --- |
| ADM-T01 | Tool bypass | No privileged action can execute outside Tool Gateway. |
| ADM-T02 | Policy bypass | Client/model/memory/repository cannot convert DENY to ALLOW. |
| ADM-T03 | Workspace escape | Traversal/symlink/out-of-scope access is blocked. |
| ADM-T04 | Client bypass | VS Code/CLI cannot invoke privileged executor directly. |
| ADM-T05 | Completion bypass | Client/model cannot mark task COMPLETE. |
| ADM-T06 | Recovery bypass | Recovery cannot weaken policy. |
| ADM-T07 | MCP bypass | MCP cannot bypass internal policy. |
| ADM-T08 | Memory authority | Memory cannot authorize tool execution. |
| ADM-T09 | User-change protection | Unrelated user edits remain preserved. |
| ADM-T10 | Reconnect replay | Reconnect does not duplicate side effects. |
| ADM-T11 | Security fail-closed | Security-control failure blocks affected privileged operation. |
| ADM-T12 | Provider substitution | Changing model provider does not alter tool/security contracts. |
| ADM-T13 | Multi-agent boundary | Sub-agent cannot exceed parent task permissions. |
| ADM-T14 | Artifact bounds | Large output is bounded/artifact-referenced. |
| ADM-T15 | Architecture drift | No alternate core authority path exists. |

# 21. Research Alignment

| Research lesson | Architecture decision |
| --- | --- |
| IDE-native coding agents | VS Code is a client with deep UX integration. |
| Tool-driven coding agents | Typed Tool Gateway is mandatory. |
| MCP-enabled systems | MCP is adopted behind an internal security boundary. |
| Multi-agent frameworks | Specialization is conditional, not the v1 default. |
| Sandbox-oriented agent systems | Execution isolation is first-class. |
| Context-provider systems | Context is scoped/ranked/budgeted. |
| Iterative coding workflows | Validation and bounded recovery are first-class. |
| Configuration-driven agents | Profiles/configuration are supported without security authority. |
| External repository research | Patterns are adopted only through internal contracts. |

# 22. Alignment With Project Plan

| Project phase | Primary decisions required |
| --- | --- |
| P0 Foundation | ADM-023, ADM-024, ADM-033–035 |
| P1 Contracts | ADM-003, ADM-005, ADM-015, ADM-017, ADM-022–023 |
| P2 Repository | ADM-007, ADM-014, ADM-020 |
| P3 Tools/Permissions | ADM-003–006, ADM-009–012, ADM-032 |
| P4 Execution | ADM-008, ADM-020–021, ADM-029, ADM-034 |
| P5 Context | ADM-013–014, ADM-025 |
| P6 Behaviour | ADM-015, ADM-026–027 |
| P7 Validation/Recovery | ADM-016–019, ADM-031–032 |
| P8 Observability | ADM-022, ADM-034 |
| P9 VS Code | ADM-002, ADM-023, ADM-028, ADM-033 |
| P10 Hardening | ADM-006–012, ADM-016–021, ADM-031–032 |
| P11 Release | ADM-031–035 |

# 23. Locked Architecture Invariants

- AD1: There is one authoritative runtime control plane.

- AD2: There is one mandatory policy authorization path for agent capabilities.

- AD3: No model output directly authorizes execution.

- AD4: No client directly owns privileged execution.

- AD5: Security authority outranks all ordinary configuration/context.

- AD6: Workspace scope is explicit and enforced.

- AD7: Secrets are protected from ordinary model/client context.

- AD8: MCP cannot bypass internal policy.

- AD9: Memory cannot authorize side effects.

- AD10: Validation is required for completion.

- AD11: Recovery is bounded and policy-constrained.

- AD12: User changes are protected.

- AD13: Runtime state is authoritative over client state.

- AD14: External patterns must enter through internal contracts.

- AD15: Architecture-changing decisions require formal versioned change control.

# 24. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| ADM-A01 | Decision completeness | Major architecture choices have explicit decisions/status. |
| ADM-A02 | Authority | Security and runtime authority are unambiguous. |
| ADM-A03 | Tool boundary | All privileged agent capabilities have a single authorization route. |
| ADM-A04 | Client boundary | VS Code/CLI cannot bypass runtime. |
| ADM-A05 | Execution | Workspace/process/network boundaries are represented. |
| ADM-A06 | Context | Memory/context authority is constrained. |
| ADM-A07 | Agent | Task lifecycle and agent topology are defined. |
| ADM-A08 | Quality | Validation/completion/recovery architecture is explicit. |
| ADM-A09 | Research | Research-derived choices are recorded. |
| ADM-A10 | Alternatives | Major rejected alternatives are documented. |
| ADM-A11 | Deferred | Unresolved choices are explicitly bounded. |
| ADM-A12 | Testing | Architecture decision tests are defined. |
| ADM-A13 | Implementation | Decision-to-module mapping exists. |
| ADM-A14 | Governance | Architecture drift/change controls exist. |
| ADM-A15 | Traceability | Matrix maps to locked specification set and project phases. |

# 25. Traceability to Locked Baselines

| Baseline | Architecture Decision Matrix role |
| --- | --- |
| 01 PRD v1.0 | Ensures architectural choices support product scope/goals. |
| 02 SRS v1.0 | Maps requirements to architectural decisions. |
| 03 System Architecture v1.0 | Records and operationalizes core architectural choices. |
| 04 Technical Design v1.0 | Constrains implementation details and module boundaries. |
| 05 Agent Behaviour v1.0 | Locks lifecycle/topology behavior decisions. |
| 06 Tool & Permission v1.0 | Locks capability and authorization decisions. |
| 07 Memory & Context v1.0 | Locks context/memory authority and data decisions. |
| 08 Error Recovery v1.0 | Locks recovery/cancellation decisions. |
| 09 Testing & Validation v1.0 | Locks architecture validation and completion evidence. |
| 10 Security & Sandbox v1.0 | Locks security authority, isolation and fail-closed decisions. |
| 11 VS Code Integration v1.0 | Locks client/runtime boundary. |
| 12 Project Plan & Progress v1.0 | Maps decisions to implementation phases/gates. |
| 13 Research Synthesis v1.0 | Records research-derived adoption/rejection choices. |

# 26. Implementation Governance

- Before implementing a new core subsystem, identify its relevant ADM IDs.

- Before introducing a new external dependency, check ADM-030 and record the decision.

- Before changing a locked interface, perform L2–L4 impact review as applicable.

- Before changing security behavior, perform mandatory security review.

- Before introducing multi-agent behavior, verify all parent/child capability boundaries.

- Before release, run the architecture decision test matrix for all applicable decisions.

- Any unresolved architecture drift is a release blocker when it affects a locked invariant.

# 27. Final Change-Control Rules

- A locked decision cannot be changed by code implementation preference.

- New evidence may justify a new decision version, but does not retroactively rewrite v1.0.

- Decision reversal requires documenting the problem, alternatives, impact and migration plan.

- Security-critical reversals require explicit security review.

- Protocol/interface reversals require compatibility and migration analysis.

- Architecture changes must update affected specifications and the project plan.

- ADM v1.0 remains the historical baseline even after a future ADM v1.1+ is approved.

# 28. Final Status

STATUS: FINAL / LOCKED — v1.0

Architecture Decision Matrix v1.0 is the authoritative decision record for the AI Software Co-Agent architecture. It locks the control plane, execution boundaries, intelligence plane, validation/recovery model, client/runtime split, research adoption rules, deferred choices, architecture invariants and implementation governance.

— END OF ARCHITECTURE DECISION MATRIX v1.0 —
