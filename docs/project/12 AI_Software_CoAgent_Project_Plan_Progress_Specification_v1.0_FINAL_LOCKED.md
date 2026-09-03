AI SOFTWARE CO-AGENT

PROJECT PLAN & PROGRESS SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: PPP-001 • Implementation control baseline for the AI Software Co-Agent

| Field | Value |
| --- | --- |
| Document | Project Plan & Progress Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Control implementation sequencing, dependencies, milestones, progress, risks, decisions, validation and release readiness |
| Planning authority | This document governs project execution order; locked architecture/specification documents govern technical behavior |

Lock Statement: Project Plan & Progress Specification v1.0 is the final locked implementation-control baseline. It prevents phase skipping, undocumented scope expansion, dependency violations and false progress. Technical specifications remain authoritative for system behavior.

# 1. Purpose & Planning Mission

This document converts the locked specification set into a controlled implementation roadmap. It defines what must be built, in what order, what evidence marks progress, which dependencies must be satisfied, and how implementation is stopped or re-planned when blockers arise.

Primary planning principle: Never mark work complete merely because code exists; completion requires the defined evidence and validation gates.

# 2. Planning Principles

- Specifications are the source of truth for intended system behavior.

- Implementation follows dependency order, not convenience order.

- Each phase has entry criteria, deliverables, validation and exit criteria.

- Do not skip security or validation gates to accelerate progress.

- Keep implementation scope aligned with the locked baseline.

- Track blockers explicitly; do not hide them as partial completion.

- Prefer small, testable increments.

- Integrate borrowed/open-source patterns only after architectural fit and license/security review.

- Every material implementation decision is recorded.

- Progress must be evidence-based.

- Changes to locked behavior require change control.

- Keep repository structure and documentation synchronized.

- Do not start broad optimization before correctness and safety are established.

# 3. Master 19-Document Baseline

| # | Document / Baseline | Role in implementation | Status |
| --- | --- | --- | --- |
| 01 | PRD v1.0 | Product goals, scope, users, success criteria | FINAL / LOCKED |
| 02 | SRS v1.0 | Functional/non-functional requirements | FINAL / LOCKED |
| 03 | System Architecture v1.0 | System boundaries and components | FINAL / LOCKED |
| 04 | Technical Design v1.0 | Detailed technical contracts/design | FINAL / LOCKED |
| 05 | Agent Behaviour v1.0 | Agent lifecycle and behavior invariants | FINAL / LOCKED |
| 06 | Tool & Permission v1.0 | Capability/authorization model | FINAL / LOCKED |
| 07 | Memory & Context v1.0 | Context/memory contracts and authority | FINAL / LOCKED |
| 08 | Error Recovery v1.0 | Failure/recovery lifecycle | FINAL / LOCKED |
| 09 | Testing & Validation v1.0 | Quality and completion gates | FINAL / LOCKED |
| 10 | Security & Sandbox v1.0 | Security authority and isolation | FINAL / LOCKED |
| 11 | VS Code Integration v1.0 | Primary client integration | FINAL / LOCKED |
| 12 | Project Plan & Progress v1.0 | Implementation control | FINAL / LOCKED |
| 13 | Repository / Module Blueprint | Physical code organization | Planned dependency |
| 14 | Data / Schema Specification | Persistent/runtime data contracts | Planned dependency |
| 15 | API / Protocol Specification | Service/client/tool contracts | Planned dependency |
| 16 | Configuration Specification | Runtime/configuration contracts | Planned dependency |
| 17 | Observability & Audit Specification | Telemetry/audit/reporting | Planned dependency |
| 18 | Deployment / Operations Specification | Build/install/runtime operations | Planned dependency |
| 19 | Release & Maintenance Specification | Release, upgrade and lifecycle | Planned dependency |

# 4. Implementation Dependency Principle

PRD

↓

SRS

↓

Architecture

↓

Technical Design

↓

Behaviour + Tool/Permission + Memory/Context + Security

↓

Data/Protocol/Repository/Configuration contracts

↓

Core Runtime

↓

Validation + Recovery + Observability

↓

VS Code / CLI clients

↓

Integration / E2E

↓

Deployment / Release

The exact ordering of parallel implementation streams may vary, but no stream may violate a higher-level locked dependency or security boundary.

# 5. Master Implementation Phases

| Phase | Name | Primary outcome | Exit gate |
| --- | --- | --- | --- |
| P0 | Foundation & Repository | Buildable repository, tooling, conventions, CI skeleton | Foundation Gate |
| P1 | Core Contracts & State | Models, IDs, schemas, task/session state | Contract Gate |
| P2 | Workspace & Repository Intelligence | Safe workspace binding, map/search/context inputs | Repository Gate |
| P3 | Tool Gateway & Permissions | Typed tools + Policy Engine + authorization | Security Gate A |
| P4 | Execution & Patch Engine | Filesystem/process/patch/Git controlled execution | Execution Gate |
| P5 | Memory & Context | Context providers, ranking, budgets, provenance | Context Gate |
| P6 | Agent Orchestration & Behaviour | Planner/orchestrator/lifecycle | Behaviour Gate |
| P7 | Validation & Error Recovery | Validation Runner, Completion Gate, Recovery Controller | Recovery/Validation Gate |
| P8 | Observability & Audit | Events, evidence, reports, diagnostics | Audit Gate |
| P9 | VS Code Integration | Client protocol/UI/approvals/diff/progress | Client Gate |
| P10 | End-to-End Hardening | Security, regression, reliability, performance | E2E Gate |
| P11 | Deployment & Release | Packaging, install, operations, release candidate | Release Gate |

# 6. Phase P0 — Foundation & Repository

- Create canonical repository structure.

- Pin language/runtime/tooling versions.

- Establish lint/type-check/test configuration.

- Create CI skeleton.

- Create configuration/environment separation.

- Create secure local development workflow.

- Add baseline documentation and contribution/change-control files.

- Create test fixture framework.

| Entry | Deliverables | Validation | Exit |
| --- | --- | --- | --- |
| Locked 01–12 baselines | Repository skeleton, CI, tooling, config baseline | Clean build + basic test + lint | Foundation reproducible |

# 7. Phase P1 — Core Contracts & State

- Define IDs/correlation IDs.

- Define Task/Session/Plan/Step state models.

- Define ToolRequest/ToolResult.

- Define PolicyDecision.

- Define ContextItem/MemoryRecord.

- Define ErrorRecord/Recovery state.

- Define ValidationResult/Completion evidence.

- Define event envelope and protocol primitives.

| Entry | Deliverables | Validation | Exit |
| --- | --- | --- | --- |
| P0 PASS | Typed contracts + serialization tests | Unit/contract tests | All core contracts stable |

# 8. Phase P2 — Workspace & Repository Intelligence

- Workspace discovery/binding.

- Canonical path/scope resolution.

- Repository map/index.

- File/search/symbol interfaces.

- Current-state refresh/invalidation.

- Safe repository context extraction.

- Repository fixture suite.

| Entry | Deliverables | Validation | Exit |
| --- | --- | --- | --- |
| P1 contracts + Security rules | Workspace manager + repository intelligence | Security path tests + repository tests | Current repository can be safely understood |

# 9. Phase P3 — Tool Gateway & Permissions

- Tool registry and schemas.

- Tool Gateway.

- Policy Engine.

- ALLOW/ASK/DENY/RESTRICT decisions.

- Approval correlation/expiry.

- Scope and risk evaluation.

- Security audit events.

- Registered initial tool set.

Hard gate: No privileged executor is integrated as an agent capability until this phase passes Security Gate A.

# 10. Phase P4 — Execution & Patch Engine

- Workspace/file operations.

- Process execution controls.

- Patch application.

- Diff/scope verification.

- Git adapter/checkpoint behavior.

- Timeout/cancellation.

- Output/artifact capture.

- User-change preservation.

| Entry | Validation | Exit |
| --- | --- | --- |
| P3 Security Gate A | Sandbox, path, process, patch, Git and cancellation tests | Controlled execution works without boundary violations |

# 11. Phase P5 — Memory & Context

- Context providers.

- Context ranking.

- Context budget.

- Context Manifest.

- Memory persistence and isolation.

- Freshness/invalidation.

- Provenance.

- Secret filtering.

- Current-evidence precedence.

| Entry | Validation | Exit |
| --- | --- | --- |
| P4 execution + Memory/Context baseline | Context/memory unit, integration and security tests | Safe, bounded, current context available to orchestration |

# 12. Phase P6 — Agent Orchestration & Behaviour

- Task lifecycle state machine.

- Request understanding.

- Planning.

- Execution loop.

- Tool request generation.

- Approval pauses.

- Validation transitions.

- Completion Gate integration.

- Cancellation handling.

- Agent Behaviour invariant enforcement.

| Entry | Validation | Exit |
| --- | --- | --- |
| P1–P5 required contracts/services | Behavior tests + controlled E2E workflow | Agent can perform bounded repository task lifecycle |

# 13. Phase P7 — Validation & Error Recovery

- Validation Runner.

- Gate registry.

- Evidence collection.

- Error normalization/classification.

- Recovery eligibility.

- Diagnosis/repair planning.

- Bounded retry/attempt budgets.

- Repeated-failure detection.

- Retest loop.

- Completion evidence.

Hard gate: The agent cannot be considered implementation-ready until it can safely fail, recover, retest and stop.

# 14. Phase P8 — Observability & Audit

- Structured runtime events.

- Task/tool/policy/validation/recovery audit.

- Correlation across client/runtime.

- Safe diagnostic logs.

- Evidence artifact indexing.

- Task progress reporting.

- Security audit protection.

# 15. Phase P9 — VS Code Integration

- Extension activation.

- Runtime client/protocol.

- Chat interface.

- Task/sidebar/status views.

- Approval UI.

- Diff/editor integration.

- Diagnostics.

- Progress/cancellation.

- Reconnect/resynchronization.

- Client security tests.

Boundary rule: VS Code remains a client. It must never become a direct executor or authorization bypass.

# 16. Phase P10 — End-to-End Hardening

- Full E2E workflows.

- Security attack/bypass suite.

- Prompt-injection scenarios.

- MCP boundary tests.

- Recovery stress/failure injection.

- Restart/disconnect/cancellation.

- Large repository/context tests.

- Performance benchmarks.

- Regression suite.

- False-completion testing.

# 17. Phase P11 — Deployment & Release

- Build/package.

- Installation workflow.

- Configuration validation.

- Runtime startup/shutdown.

- Upgrade/migration strategy.

- Release notes/changelog.

- Security release checklist.

- Evidence archive.

- Release candidate acceptance.

# 18. Phase Gates

| Gate | Required evidence | Failure result |
| --- | --- | --- |
| Foundation Gate | Build/tooling/CI baseline | Phase remains open |
| Contract Gate | Schema/state contract tests | Phase remains open |
| Repository Gate | Workspace/repository tests | Phase remains open |
| Security Gate A | Tool/policy/sandbox tests | Privileged execution blocked |
| Execution Gate | Execution/patch/Git tests | Agent implementation blocked |
| Context Gate | Memory/context tests | Orchestration context blocked |
| Behaviour Gate | Lifecycle/behavior tests | E2E blocked |
| Recovery/Validation Gate | Recovery + completion tests | Completion blocked |
| Audit Gate | Traceability/event tests | Release evidence incomplete |
| Client Gate | VS Code integration/security tests | Client release blocked |
| E2E Gate | End-to-end/security/reliability tests | Release blocked |
| Release Gate | All mandatory release conditions | Release prohibited |

# 19. Work Item Structure

WorkItem {

id

phase

title

objective

specification_refs[]

dependencies[]

owner

status

risk

files_scope[]

tests_required[]

acceptance_criteria[]

evidence_refs[]

blocker_refs[]

decision_refs[]

created_at

updated_at

}

# 20. Progress State Model

| State | Meaning | Transition |
| --- | --- | --- |
| BACKLOG | Identified, not started | → READY |
| READY | Dependencies satisfied | → IN_PROGRESS |
| IN_PROGRESS | Active implementation | → REVIEW / BLOCKED |
| REVIEW | Implementation awaiting review/tests | → DONE / CHANGES_REQUIRED |
| CHANGES_REQUIRED | Review/validation found issue | → IN_PROGRESS |
| BLOCKED | Cannot proceed due dependency/risk/decision | → READY / IN_PROGRESS |
| DONE | Acceptance + evidence satisfied | Terminal for work item |
| CANCELLED | Work intentionally stopped | Terminal unless re-opened by change control |

# 21. Definition of Ready

- Work item has a clear objective.

- Applicable locked specification references are known.

- Dependencies are satisfied or explicitly planned.

- Scope/files are identifiable.

- Acceptance criteria are testable.

- Required security/permission implications are understood.

- Required test strategy is identified.

- No unresolved blocker makes immediate execution unsafe.

# 22. Definition of Done

- Implementation is complete within declared scope.

- Required tests pass.

- Security checks pass where applicable.

- Actual diff matches intended scope.

- Acceptance criteria are satisfied.

- Relevant documentation is updated.

- Evidence references are recorded.

- No unresolved blocking error remains.

- Code is in the expected repository state.

- Completion does not depend on an unverified assumption.

# 23. Dependency Management

- Represent hard dependencies explicitly.

- Do not start a blocked work item merely because it appears next in the list.

- Parallel work is allowed only when interfaces are stable enough.

- Changes to upstream contracts trigger downstream impact review.

- Record dependency blockers with an owner and resolution condition.

- Never silently replace a dependency with an incompatible shortcut.

# 24. Research → Implementation Workflow

RESEARCH

↓

EXTRACT USEFUL PATTERNS

↓

LICENSE / SECURITY / ARCHITECTURE REVIEW

↓

ADOPT / ADAPT / REJECT DECISION

↓

CREATE INTERNAL CONTRACT

↓

IMPLEMENT

↓

TEST

↓

INTEGRATE

↓

RECORD SOURCE + DECISION

- External repositories are references, not authoritative specifications.

- Do not copy code blindly.

- Record why a pattern was adopted and where it maps into our architecture.

- Check license compatibility before integrating source code.

- Security-sensitive patterns require additional review.

# 25. Repository Integration Policy

| Decision | Meaning |
| --- | --- |
| ADOPT | Use the pattern/component with minimal adaptation after review. |
| ADAPT | Use the concept but implement against our contracts. |
| WRAP | Keep external implementation behind our internal interface. |
| REPLACE | Use the idea but select another implementation. |
| REJECT | Do not use because it conflicts with architecture/security/scope/license. |

- Internal interfaces remain authoritative.

- External repository structure does not dictate our architecture.

- Every adopted dependency has ownership/version/license/security information.

# 26. Risk Register

| Risk | Impact | Mitigation | Trigger |
| --- | --- | --- | --- |
| Scope creep | High | Locked specs + change control | Unplanned feature request |
| Architecture drift | High | Traceability + gate review | Implementation conflicts with baseline |
| Security bypass | Critical | Defense-in-depth + security tests | Unauthorized side effect |
| False completion | Critical | Completion Gate | Missing/failed evidence |
| Endless recovery | High | Budgets + repetition detection | Repeated failure |
| Context staleness | High | Refresh/invalidation | Repository changed |
| User data loss | Critical | Git/diff/scope controls | Unrelated change overwritten |
| Dependency instability | Medium | Pin/version/test | Build/runtime drift |
| External repo license issue | High | License review | Incompatible terms |
| Performance regression | Medium | Benchmarks | Target exceeded |
| Client/runtime mismatch | High | Versioned protocol | Protocol incompatibility |
| Test flakiness | Medium | Quarantine/root-cause policy | Unstable gate |

# 27. Blocker Management

- Every blocker receives a stable ID.

- Record affected phase/work items.

- Record cause, evidence and resolution condition.

- Classify blocker as technical, security, dependency, decision, environment or external.

- Security blockers cannot be downgraded to ordinary technical blockers.

- Blocked work does not count as completed.

- Replanning must preserve locked invariants.

BLOCKED

├── Cause

├── Evidence

├── Impact

├── Resolution condition

├── Owner

└── Next review trigger

# 28. Decision Management

| Decision field | Required content |
| --- | --- |
| Decision ID | Stable identifier |
| Question | What required a decision |
| Options | Meaningful alternatives considered |
| Decision | Selected option |
| Rationale | Evidence/reasoning |
| Impact | Affected docs/modules/phases |
| Reversibility | Easy / Moderate / Hard |
| Approver | If required by governance |
| Date/version | When it became effective |

- Decisions affecting locked behavior trigger change control.

- Temporary implementation decisions must be labeled temporary.

- Rejected alternatives should be recorded for high-impact decisions.

# 29. Change Control

| Change type | Default handling |
| --- | --- |
| Bug fix within locked behavior | Normal implementation + regression test |
| Internal refactor | Normal review if contracts/invariants unchanged |
| New feature in existing scope | Add work item + acceptance/tests |
| Scope expansion | Change request + PRD/SRS impact review |
| Behavior change | Affected specification review + version/change control |
| Security rule change | Security/architecture review |
| Protocol contract change | Protocol versioning + compatibility tests |
| Architecture change | Architecture review + downstream impact |
| Locked document change | Formal change control; new version |

No implementation change may silently redefine a locked requirement.

# 30. Progress Reporting

| Report | Required content | Cadence |
| --- | --- | --- |
| Daily/working status | Completed, in-progress, blocked, next | During active implementation |
| Phase report | Gate status, evidence, risks | At phase boundary |
| Milestone report | Deliverables, deviations, decisions | At milestone |
| Release report | All gates + known issues + evidence | Release candidate |
| Master progress | Overall phase/document/work-item status | Continuous source of truth |

- Progress percentages are secondary to gate status.

- A phase is not complete because a percentage reaches 100%; its exit criteria must pass.

- Blocked items remain visible in progress reporting.

# 31. Master Progress Board

| Phase | Status at baseline | Required evidence | Next action |
| --- | --- | --- | --- |
| P0 Foundation | PLANNED | Foundation Gate | Create implementation repository |
| P1 Contracts | PLANNED | Contract Gate | Implement core models/schemas |
| P2 Repository | PLANNED | Repository Gate | Implement workspace/repository intelligence |
| P3 Tools/Permissions | PLANNED | Security Gate A | Implement Tool Gateway + Policy Engine |
| P4 Execution | PLANNED | Execution Gate | Implement executors/patch/Git |
| P5 Context | PLANNED | Context Gate | Implement Memory & Context |
| P6 Behaviour | PLANNED | Behaviour Gate | Implement orchestration |
| P7 Validation/Recovery | PLANNED | Recovery/Validation Gate | Implement validation + recovery |
| P8 Observability | PLANNED | Audit Gate | Implement events/audit/reporting |
| P9 VS Code | PLANNED | Client Gate | Implement extension/client |
| P10 Hardening | PLANNED | E2E Gate | Run full security/reliability/performance |
| P11 Release | PLANNED | Release Gate | Package and release |

Baseline status is PLANNED because this document establishes the implementation roadmap; actual status must be updated only from implementation evidence.

# 32. Milestones

| Milestone | Completion condition |
| --- | --- |
| M0 — Repository Ready | P0 exit gate PASS |
| M1 — Runtime Contracts Ready | P1 exit gate PASS |
| M2 — Repository Understanding Ready | P2 exit gate PASS |
| M3 — Secure Tooling Ready | P3 security gate PASS |
| M4 — Controlled Execution Ready | P4 gate PASS |
| M5 — Context Ready | P5 gate PASS |
| M6 — Agent Core Ready | P6 gate PASS |
| M7 — Safe Self-Recovery Ready | P7 gate PASS |
| M8 — Observable Runtime Ready | P8 gate PASS |
| M9 — VS Code Alpha | P9 gate PASS |
| M10 — Hardened Candidate | P10 gate PASS |
| M11 — Release Candidate | P11 gate PASS |

# 33. Minimum Viable Implementation Order

1. Repository + CI foundation

2. Core typed contracts

3. Workspace/scope/security primitives

4. Tool Gateway + Policy Engine

5. Safe filesystem/process/patch execution

6. Repository intelligence

7. Memory/context

8. Agent orchestration

9. Validation + Completion Gate

10. Error Recovery

11. Observability/audit

12. VS Code integration

13. E2E/security/reliability hardening

14. Deployment/release

This order prioritizes the security and control plane before broad autonomous execution.

# 34. First Implementation Sprint Definition

- Initialize repository and canonical directory structure.

- Set Python/runtime/tool versions.

- Create lint/type-check/test/CI baseline.

- Implement core ID/event/config primitives.

- Create initial unit-test harness.

- Create security test fixture harness.

- Create initial ToolDefinition/ToolRequest/PolicyDecision contracts.

- Create project progress tracker using this document's work-item model.

- Do not enable unrestricted process execution during the foundation sprint.

Sprint exit: Buildable, testable repository with the initial contract/security skeleton—not a partially autonomous agent.

# 35. Progress Evidence Model

ProgressEvidence {

work_item_id

phase_id

status

commit_or_revision

tests_passed[]

security_checks[]

acceptance_results[]

artifact_refs[]

diff_scope

blockers[]

decisions[]

recorded_at

}

- Evidence must correspond to the actual repository state.

- Later changes can invalidate earlier evidence.

- Evidence should be reproducible where practical.

# 36. Project Metrics

| Metric | Meaning |
| --- | --- |
| Phase completion | Phases passing exit gates / total phases |
| Work item completion | DONE items / total planned items |
| Blocked work | BLOCKED items + age |
| Requirement coverage | Requirements mapped to implementation/tests |
| Security gate pass | Mandatory security gate status |
| Regression pass | Critical regression status |
| False completion | Count of invalid completion claims; target zero |
| Recovery success | Recovered failures / eligible failures |
| Test stability | Flaky/unstable test rate |
| Change churn | Reopened/reworked work items |
| Architecture deviations | Approved deviations from baseline |

Metrics are management signals and do not override hard acceptance or security gates.

# 37. Release Readiness Checklist

- All required phases have passed their exit gates.

- All mandatory security tests pass.

- All critical regression tests pass.

- Completion Gate behavior is verified.

- Recovery budgets/repetition detection are verified.

- VS Code client boundary is verified.

- Documentation is version-aligned.

- Known blockers are zero or formally dispositioned.

- Release artifacts are reproducible and traceable.

- Change log/release notes are prepared.

- Security-sensitive changes have required review.

- Evidence archive is complete.

# 38. Project Governance Invariants

- PPP1: Locked specifications are not silently changed during implementation.

- PPP2: A blocked item is not DONE.

- PPP3: A phase cannot close without its exit gate.

- PPP4: Security gates cannot be skipped for schedule reasons.

- PPP5: Progress claims require evidence.

- PPP6: Dependencies are explicit.

- PPP7: Scope expansion requires change control.

- PPP8: External repositories are reviewed before adoption.

- PPP9: User-impacting changes remain traceable.

- PPP10: Current repository state determines implementation evidence.

- PPP11: Earlier PASS evidence may be invalidated by later changes.

- PPP12: Completion requires validation evidence, not code existence.

- PPP13: Critical security violations block release.

- PPP14: Project replanning cannot weaken locked security/behavior invariants.

- PPP15: Every implementation stream has a known next actionable state.

# 39. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| PPP-A01 | Baseline | Locked document set is represented and traceable. |
| PPP-A02 | Phases | Implementation phases have dependencies, deliverables and gates. |
| PPP-A03 | Work items | Work-item structure supports evidence-based status. |
| PPP-A04 | Ready/Done | Definition of Ready and Done are explicit. |
| PPP-A05 | Security | Security gates precede unrestricted execution. |
| PPP-A06 | Validation | Validation/Completion gates control completion. |
| PPP-A07 | Recovery | Recovery is included as a required implementation capability. |
| PPP-A08 | Research | External repo adoption has review/adaptation policy. |
| PPP-A09 | Risks | Critical project risks have mitigations. |
| PPP-A10 | Blockers | Blockers are explicit and cannot masquerade as progress. |
| PPP-A11 | Decisions | High-impact decisions are traceable. |
| PPP-A12 | Progress | Master progress board exists. |
| PPP-A13 | Evidence | Implementation progress maps to repository state/evidence. |
| PPP-A14 | Release | Release readiness conditions are explicit. |
| PPP-A15 | Change control | Baseline-changing work follows formal change control. |

# 40. Traceability to Locked Baselines

| Baseline | Project-plan impact |
| --- | --- |
| 01 PRD v1.0 | Scope, product goals and success criteria. |
| 02 SRS v1.0 | Requirement implementation and acceptance. |
| 03 System Architecture v1.0 | Phase/component dependencies. |
| 04 Technical Design v1.0 | Module implementation sequence. |
| 05 Agent Behaviour v1.0 | Behavior gate and invariants. |
| 06 Tool & Permission v1.0 | Security-first tool-control phase. |
| 07 Memory & Context v1.0 | Context implementation and gate. |
| 08 Error Recovery v1.0 | Recovery implementation and gate. |
| 09 Testing & Validation v1.0 | Mandatory validation/completion gates. |
| 10 Security & Sandbox v1.0 | Security-first execution boundary. |
| 11 VS Code Integration v1.0 | Client integration phase and gate. |

# 41. Implementation Mapping

| Planning artifact | Expected repository location |
| --- | --- |
| Master plan | docs/project/PROJECT_PLAN_PROGRESS.md |
| Work items | docs/project/work-items/ or tracker |
| Phase reports | docs/project/phases/ |
| Decision log | docs/project/decisions/ |
| Risk register | docs/project/RISK_REGISTER.md |
| Change log | docs/project/CHANGELOG.md |
| Progress evidence | artifacts/project-progress/ |
| Test evidence | artifacts/test-results/ |
| Release evidence | artifacts/release/ |
| CI | .github/workflows/ |

Exact paths may evolve with the Repository/Module Blueprint. The governance model and phase gates remain locked.

# 42. Change Control

- Changing phase order requires dependency-impact review.

- Adding a phase requires updated milestones and traceability.

- Changing an exit gate requires validation review.

- Changing security-first sequencing requires security/architecture review.

- Changing the Definition of Done affects every future work item and requires project-level approval.

- New external repository adoption requires source/license/security decision record.

- Any change to this locked baseline creates a new version; v1.0 remains immutable as historical baseline.

# 43. Final Status

STATUS: FINAL / LOCKED — v1.0

This Project Plan & Progress Specification v1.0 is the authoritative implementation-control baseline for the AI Software Co-Agent. It defines the 19-document baseline, implementation phases P0–P11, dependencies, gates, work-item lifecycle, Definition of Ready/Done, research-to-implementation process, risks, blockers, decisions, progress evidence, milestones, release readiness and governance invariants.

— END OF PROJECT PLAN & PROGRESS SPECIFICATION v1.0 —
