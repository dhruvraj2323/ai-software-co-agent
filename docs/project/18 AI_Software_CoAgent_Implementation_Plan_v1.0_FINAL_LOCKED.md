AI SOFTWARE CO-AGENT

IMPLEMENTATION PLAN

Version 1.0 — FINAL / LOCKED

Document ID: IPL-001 • Execution roadmap and delivery-gate baseline

| Field | Value |
| --- | --- |
| Document | Implementation Plan |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Convert the locked architecture/specification set into an ordered, dependency-aware implementation program with deliverables, gates, tests and Definition of Done. |
| Authority | Implementation sequencing and gates are governed here; subsystem behavior remains governed by the relevant locked specifications. |
| Change policy | Material phase, dependency or gate changes require formal versioned change control. |

Lock Statement: Implementation Plan v1.0 is the final locked execution roadmap. Implementation may proceed in iterations, but it must preserve the phase dependencies, security gates, validation gates, traceability and completion rules defined here.

# 1. Implementation Mission

Build the AI Software Co-Agent incrementally from its safest foundations upward: contracts and state first, then security and capability control, then controlled execution, software understanding, agent intelligence, validation/recovery, observability and clients. The plan deliberately prevents premature autonomy.

Implementation principle: Build the control boundary before increasing agent capability.

# 2. Implementation Goals

- Create a runnable core before adding broad autonomous behavior.

- Establish one authoritative runtime and one authorization path.

- Make every side effect observable, bounded and testable.

- Keep VS Code and CLI as clients, not privileged runtimes.

- Introduce context/memory only after repository and security foundations exist.

- Make validation and recovery first-class before claiming autonomous completion.

- Use research-derived components only through internal contracts.

- Reach a reproducible local developer workflow before optional scale technologies.

# 3. Master Implementation Sequence

P0 FOUNDATION & REPOSITORY

↓

P1 CORE CONTRACTS + STATE + PROTOCOL

↓

P2 SECURITY + WORKSPACE SCOPE

↓

P3 TOOL GATEWAY + POLICY + APPROVAL

↓

P4 CONTROLLED EXECUTION + PATCH + GIT

↓

P5 REPOSITORY INTELLIGENCE + CONTEXT + MEMORY

↓

P6 MODEL GATEWAY + AGENT ORCHESTRATION

↓

P7 VALIDATION + COMPLETION + RECOVERY

↓

P8 AUDIT + ARTIFACTS + OBSERVABILITY

↓

P9 VS CODE + CLI INTEGRATION

↓

P10 E2E + SECURITY + PERFORMANCE HARDENING

↓

P11 RELEASE READINESS

# 4. Phase Overview

| Phase | Primary outcome | Exit gate |
| --- | --- | --- |
| P0 | Repository/tooling baseline | G0 Foundation |
| P1 | Stable runtime contracts/state/protocol | G1 Contracts |
| P2 | Safe scope and security primitives | G2 Security/Scope |
| P3 | Single tool authorization path | G3 Capability Control |
| P4 | Bounded real-world execution | G4 Execution |
| P5 | Repository-aware context/memory | G5 Context |
| P6 | Controlled agent reasoning/orchestration | G6 Agent |
| P7 | Evidence-based completion + recovery | G7 Quality |
| P8 | Traceability/evidence/observability | G8 Evidence |
| P9 | Usable VS Code + CLI clients | G9 Clients |
| P10 | Hardening and release confidence | G10 Hardening |
| P11 | Release package | G11 Release |

# 5. Global Phase Rules

- Later phases may not bypass earlier gates.

- Security gates are release-blocking.

- Every phase has explicit entry criteria, deliverables, tests and exit criteria.

- Phase completion means evidence exists, not merely code exists.

- Failed mandatory gates pause progression.

- Prototype code must not silently become production authority.

- All privileged behavior must use the same Tool Gateway/Policy path.

- Architecture drift requires change control before continuation.

# 6. P0 — Foundation & Repository

| Item | Plan |
| --- | --- |
| Objective | Create canonical repository, development tooling, CI skeleton and documentation baseline. |
| Inputs | Docs 01–17, Repository Blueprint, Master Architecture. |
| Build | Repository tree, pyproject, package skeleton, configs, scripts, docs, test skeleton. |
| Tests | Build/import, lint, type baseline, test runner, CI smoke. |
| Security | Secret scanning and safe config baseline. |
| Deliverable | Reproducible developer bootstrap. |
| Exit | Clean checkout can install, test and run a minimal health command. |

- Do not implement autonomous execution in P0.

- Create placeholder interfaces only where needed to establish contracts.

- Pin/constraint tool versions reproducibly.

# 7. P1 — Core Contracts, State & Protocol

| Item | Plan |
| --- | --- |
| Objective | Establish stable internal types and runtime/client contracts. |
| Build | IDs, errors, results, events, task/session state, protocol messages, versioning. |
| Tests | Contract tests, serialization, state-transition tests, invalid-message tests. |
| Security | Reject malformed/unknown privileged requests. |
| Deliverable | Minimal runtime accepting safe task/session commands. |
| Exit | State and protocol behavior are deterministic and contract-tested. |

Client → Protocol → Session → Task → Orchestrator

↓

Typed State Machine

# 8. P2 — Security & Workspace Scope

| Item | Plan |
| --- | --- |
| Objective | Build non-bypassable scope and security primitives. |
| Build | Canonical path resolution, workspace scope, policy primitives, secret filters, sandbox interface, resource limits. |
| Tests | Traversal, symlink/junction escape, protected paths, secret leakage, limit enforcement. |
| Security | Fail closed for security-control failures. |
| Deliverable | Safe workspace/resource boundary. |
| Exit | Security boundary tests pass; no privileged executor exists outside approved boundary. |

# 9. P3 — Tool Gateway, Policy & Approval

| Item | Plan |
| --- | --- |
| Objective | Create the one mandatory capability authorization route. |
| Build | Tool definitions, registry, ToolRequest/Result, Gateway, Policy Engine, ALLOW/ASK/DENY/RESTRICT, approval lifecycle. |
| Tests | Policy matrix, bypass tests, approval replay, malformed requests, scope mismatch. |
| Security | Client/model/memory/repository cannot authorize directly. |
| Deliverable | Controlled tool invocation framework. |
| Exit | Every registered privileged tool reaches the same authorization path. |

# 10. P4 — Controlled Execution, Patch & Git

| Item | Plan |
| --- | --- |
| Objective | Enable safe, bounded side effects. |
| Build | Filesystem, process, patch, Git adapters; timeouts, output limits, cancellation, conflict detection. |
| Tests | Safe reads/writes, process timeout, cancellation, output bounds, patch conflicts, Git safety. |
| Security | No privilege escalation; workspace containment; user-change protection. |
| Deliverable | Agent-independent safe execution substrate. |
| Exit | Representative tool operations pass security + integration tests. |

# 11. P5 — Repository Intelligence, Context & Memory

| Item | Plan |
| --- | --- |
| Objective | Make the runtime repository-aware without making memory authoritative. |
| Build | Repository map/search/symbol interfaces, ContextProviders, ranking, budget, Context Manifest, MemoryStore/Manager, provenance. |
| Tests | Context relevance, scope, stale-memory handling, secret filtering, budget enforcement. |
| Security | Memory/context cannot authorize. |
| Deliverable | Controlled repository context pipeline. |
| Exit | Representative repositories produce useful bounded context without bypassing scope. |

# 12. P6 — Model Gateway & Agent Orchestration

| Item | Plan |
| --- | --- |
| Objective | Introduce model reasoning and controlled task orchestration. |
| Build | ModelGateway, planner, behavior loop, task budgets, observation/result handling. |
| Tests | Tool selection, invalid plan handling, bounded loops, cancellation, model failure. |
| Security | Model output is proposal only. |
| Deliverable | Agent can reason and request authorized tools. |
| Exit | Representative coding tasks reach validation without direct execution bypass. |

Multi-agent: Remain single-agent for the v1 core. Specialist agents are not required for P6 exit.

# 13. P7 — Validation, Completion & Recovery

| Item | Plan |
| --- | --- |
| Objective | Make correctness and recovery first-class. |
| Build | Validation Runner, checks, evidence, Completion Gate, failure classifier, Recovery Controller, budgets. |
| Tests | False completion, test failure, repair/retest, repeated failure, recovery budget, security-blocked recovery. |
| Security | Recovery uses normal policy/tool path. |
| Deliverable | Evidence-based task completion. |
| Exit | No supported path can mark COMPLETE without required evidence. |

# 14. P8 — Audit, Artifacts & Observability

| Item | Plan |
| --- | --- |
| Objective | Make task execution reconstructable. |
| Build | Event envelopes, correlation IDs, audit recorder, artifact references, redaction, local diagnostics. |
| Tests | Event completeness, correlation, redaction, artifact integrity/reference behavior. |
| Security | No secret leakage; audit cannot become authorization bypass. |
| Deliverable | Traceable task/evidence chain. |
| Exit | Representative task can be reconstructed from events/evidence. |

# 15. P9 — VS Code & CLI Integration

| Item | Plan |
| --- | --- |
| Objective | Expose the runtime through primary clients. |
| Build | VS Code extension, chat/commands, approval UI, diff/diagnostics/progress, CLI commands. |
| Tests | Protocol compatibility, reconnect, approval UX, client state synchronization, headless task execution. |
| Security | Clients cannot invoke privileged executors directly. |
| Deliverable | Usable developer-facing Co-Agent. |
| Exit | Same runtime behavior works through VS Code and CLI. |

# 16. P10 — E2E, Security & Performance Hardening

| Item | Plan |
| --- | --- |
| Objective | Validate the complete system under realistic and adversarial conditions. |
| Build | E2E fixtures, security attack suites, performance benchmarks, failure injection. |
| Tests | Architecture Decision tests, security suite, representative coding tasks, regression, resource limits. |
| Security | Injection, scope escape, tool bypass, MCP boundary, secret exposure, recovery abuse. |
| Deliverable | Release candidate. |
| Exit | All mandatory release gates pass with documented evidence. |

# 17. P11 — Release Readiness

- Freeze release candidate.

- Run clean-environment installation/build.

- Run full automated test suite.

- Run mandatory security/dependency scans.

- Verify documentation/version consistency.

- Verify artifact and evidence packaging.

- Review open risks/deferred decisions.

- Confirm no unresolved architecture drift.

- Generate release notes and rollback procedure.

- Tag/version only after G11 approval.

# 18. Work Breakdown Structure

| WBS | Workstream | Primary outputs |
| --- | --- | --- |
| 1.0 | Foundation | Repo/tooling/CI |
| 2.0 | Contracts | Types/state/protocol |
| 3.0 | Security | Scope/sandbox/secrets |
| 4.0 | Tools | Gateway/registry/policy/approval |
| 5.0 | Execution | Filesystem/process/patch/Git |
| 6.0 | Intelligence | Repository/context/memory |
| 7.0 | Agent | Model gateway/planner/orchestrator |
| 8.0 | Quality | Validation/completion/recovery |
| 9.0 | Evidence | Audit/artifacts/observability |
| 10.0 | Clients | VS Code/CLI |
| 11.0 | Hardening | E2E/security/performance |
| 12.0 | Release | Packaging/release/rollback |

# 19. Critical Path

Repository

→ Contracts/State

→ Security/Scope

→ Tool Gateway/Policy

→ Execution

→ Context

→ Agent

→ Validation/Completion

→ Recovery

→ Clients

→ E2E/Security

→ Release

Critical-path rule: A downstream feature cannot create its own substitute for a missing upstream boundary.

# 20. Parallel Workstreams

| Can run in parallel | Constraint |
| --- | --- |
| Documentation cleanup + P0 tooling | Must not change locked decisions. |
| Protocol contract tests + core state tests | Shared contract version must remain stable. |
| Security test fixtures + security implementation | Fixtures must model real boundaries. |
| VS Code UX prototyping + runtime work | UI cannot invent runtime authority. |
| Repository intelligence research + P4 execution | Production integration waits for contracts. |
| Performance benchmark harness + feature implementation | Benchmarks must use stable scenarios. |
| Dependency/license review + module development | No unreviewed dependency enters release. |

# 21. Phase Deliverable Matrix

| Phase | Code | Tests | Docs/Evidence | Gate |
| --- | --- | --- | --- | --- |
| P0 | Repo/tooling | CI smoke | Bootstrap evidence | G0 |
| P1 | Core/protocol/state | Contract tests | Protocol/state evidence | G1 |
| P2 | Security/workspace | Security boundary tests | Threat/evidence | G2 |
| P3 | Tools/policy | Policy/bypass tests | Capability matrix | G3 |
| P4 | Executors/Git | Integration/security | Execution evidence | G4 |
| P5 | Context/memory/repo | Context tests | Context evidence | G5 |
| P6 | Agent/model | Behavior tests | Agent evidence | G6 |
| P7 | Validation/recovery | Quality tests | Completion evidence | G7 |
| P8 | Audit/artifacts | Traceability tests | Event/evidence package | G8 |
| P9 | Clients | Protocol/E2E client tests | UX/integration evidence | G9 |
| P10 | Hardening | Full suites | Release candidate evidence | G10 |
| P11 | Release | Clean-build/full suite | Release package | G11 |

# 22. Definition of Done — Universal

- Implementation matches the applicable locked specification.

- Code is in the correct Repository Blueprint module.

- Types/contracts are explicit.

- Unit/component tests pass.

- Relevant integration/security tests pass.

- Logging/events do not leak secrets.

- Errors are handled according to Error Recovery.

- Documentation/traceability is updated.

- No architecture invariant is violated.

- Code review/diff is clean.

- Acceptance evidence is recorded.

- Phase gate criteria are satisfied.

# 23. Definition of Done — Security-Critical Work

- Threat/abuse cases identified.

- Fail-closed behavior tested.

- Bypass tests attempted.

- Scope enforcement tested.

- Secret handling verified.

- Relevant sandbox/resource limits verified.

- Audit/evidence generated.

- Security review completed before gate approval.

# 24. Definition of Done — Agent Feature

- Agent behavior is explicitly specified.

- Tool requests use canonical schemas.

- Authorization occurs through Policy Engine.

- Context is scoped/budgeted.

- Task/recovery budgets exist.

- Validation gate is defined.

- False-completion scenario is tested.

- Cancellation behavior is tested.

- Representative E2E task passes.

# 25. Gate Criteria

| Gate | Mandatory conditions |
| --- | --- |
| G0 | Reproducible repository/tooling + CI smoke. |
| G1 | Contracts/state/protocol versioned and contract-tested. |
| G2 | Security/scope primitives pass boundary tests. |
| G3 | One tool authorization path; bypass tests pass. |
| G4 | Execution is bounded, scoped, cancellable and tested. |
| G5 | Context/memory are bounded and non-authoritative. |
| G6 | Agent uses tools only through runtime boundaries. |
| G7 | Completion requires evidence; recovery is bounded. |
| G8 | Material actions traceable through events/evidence. |
| G9 | VS Code/CLI use same runtime without bypass. |
| G10 | Full E2E/security/performance/regression evidence passes. |
| G11 | Release package reproducible, documented and approved. |

# 26. Risk & Mitigation Plan

| Risk | When | Mitigation |
| --- | --- | --- |
| Scope creep | All phases | Gate backlog; defer optional features. |
| Premature autonomy | P6 | Keep model proposal-only; enforce policy. |
| Architecture drift | All | ADM + Master Architecture checks. |
| Security bypass | P2–P10 | Dedicated adversarial tests. |
| Provider lock-in | P6 | Model Gateway + benchmark selection. |
| Framework lock-in | P1–P10 | Internal contracts/state machine. |
| Context overload | P5–P6 | Budget/ranking/artifacts. |
| False completion | P7+ | Completion Gate + adversarial tests. |
| Recovery loop | P7 | Budgets + repeated-failure stop. |
| Client bypass | P9 | Protocol boundary + tests. |
| Dependency vulnerability | All | Scanning + pinned versions. |
| Schedule pressure | All | Never skip security/release gates. |

# 27. Research Integration Plan

- Use researched repositories as pattern references, not authorities.

- Extract useful patterns into internal contracts.

- Record ADOPT / ADAPT / WRAP / REPLACE / REJECT decisions.

- Do not copy security-sensitive behavior without local review.

- Benchmark frameworks before making them core dependencies.

- Keep research artifacts in docs/research and dependency review records.

- Any borrowed code must pass license/security review.

# 28. Deferred Technology Integration

| Technology | When considered | Required evidence |
| --- | --- | --- |
| Specific LLM/provider | P6 | Task success/cost/latency/security benchmark |
| Vector/embeddings | P5/P10 | Retrieval benchmark showing material gain |
| Container backend | P2/P10 | Isolation/resource benchmark |
| Telemetry backend | P8/P10 | Operational value/privacy review |
| Multi-agent framework | Post-v1 or controlled P10 experiment | Measured task benefit + isolation |
| Remote database | Post-v1 or scale trigger | Scale/operability evidence |
| Web client | Post-v1 | Product need + security/client architecture review |

# 29. Progress Tracking Model

| Status | Definition |
| --- | --- |
| NOT STARTED | No implementation work accepted. |
| IN PROGRESS | Active implementation with identified owner/work item. |
| BLOCKED | Cannot proceed due to dependency/decision/gate. |
| READY FOR REVIEW | Implementation and required tests complete. |
| GATE REVIEW | Evidence under formal phase review. |
| DONE | Gate passed and evidence recorded. |
| DEFERRED | Intentionally moved outside current phase. |
| REJECTED | Explicitly removed from implementation. |

# 30. Progress Evidence Package

- Commit/change reference.

- Specification references.

- Architecture Decision IDs where applicable.

- Test results.

- Security test results where applicable.

- Validation evidence.

- Known limitations.

- Dependency changes.

- Artifacts/log references.

- Reviewer/gate approval record.

# 31. Change Management

CHANGE REQUEST

↓

IMPACT ANALYSIS

↓

CHECK LOCKED DOCS / ADM / MASTER ARCHITECTURE

↓

SECURITY + DEPENDENCY REVIEW

↓

APPROVE / REJECT / DEFER

↓

UPDATE VERSIONED PLAN/SPEC

↓

IMPLEMENT + TEST

↓

RE-GATE

- Implementation pressure is not a reason to bypass locked architecture.

- Any changed dependency sequence must be documented.

- Emergency security fixes may block normal sequencing until validated.

# 32. Release Strategy

| Stage | Rule |
| --- | --- |
| Development | Feature branches/controlled changes. |
| Integration | Contract + integration tests. |
| Release candidate | Full mandatory suite. |
| Security review | Mandatory before release. |
| Packaging | Reproducible build. |
| Release | Versioned artifact + notes. |
| Rollback | Known-good prior version and recovery procedure. |
| Post-release | Monitor errors/evidence; no silent architecture changes. |

# 33. Implementation Invariants

- IP1: Security/scope foundations precede autonomous execution.

- IP2: Tool Gateway precedes production agent tool use.

- IP3: Policy precedes privileged execution.

- IP4: Validation precedes autonomous completion.

- IP5: Recovery uses the same authorization boundary.

- IP6: Clients never become execution authorities.

- IP7: Context/memory never become authorization authorities.

- IP8: External technologies enter through adapters.

- IP9: Every phase produces evidence.

- IP10: Mandatory gates cannot be bypassed for schedule.

- IP11: Deferred choices are not hidden prerequisites.

- IP12: Architecture drift requires formal review.

- IP13: User changes are protected throughout implementation.

- IP14: Security-critical failures fail closed.

- IP15: Release requires complete traceability.

# 34. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| IP-A01 | Sequence | Implementation phases have dependency-aware order. |
| IP-A02 | Foundation | Repository/tooling bootstrap is defined. |
| IP-A03 | Contracts | Core state/protocol work precedes capabilities. |
| IP-A04 | Security | Security/scope precede privileged execution. |
| IP-A05 | Tools | Single Tool Gateway/Policy path is established. |
| IP-A06 | Execution | Execution is bounded and tested. |
| IP-A07 | Context | Context/memory are introduced after safe foundations. |
| IP-A08 | Agent | Agent reasoning is introduced behind contracts. |
| IP-A09 | Quality | Validation/completion/recovery are first-class. |
| IP-A10 | Evidence | Audit/artifacts are integrated. |
| IP-A11 | Clients | VS Code/CLI use same runtime. |
| IP-A12 | Hardening | E2E/security/performance phase exists. |
| IP-A13 | Gates | Every phase has explicit exit criteria. |
| IP-A14 | DoD | Universal/security/agent DoD is defined. |
| IP-A15 | Governance | Change management and release strategy are defined. |

# 35. Traceability to Locked Baselines

| Baseline | Implementation Plan role |
| --- | --- |
| 01 PRD v1.0 | Defines product outcomes delivered through phases. |
| 02 SRS v1.0 | Defines requirements/gates to verify. |
| 03 System Architecture v1.0 | Defines implementation dependency order. |
| 04 Technical Design v1.0 | Defines module-level implementation work. |
| 05 Agent Behaviour v1.0 | Drives P6/P7 behavior and tests. |
| 06 Tool & Permission v1.0 | Drives P3/P4 authorization/execution. |
| 07 Memory & Context v1.0 | Drives P5 context/memory. |
| 08 Error Recovery v1.0 | Drives P7 recovery. |
| 09 Testing & Validation v1.0 | Drives gates and evidence. |
| 10 Security & Sandbox v1.0 | Drives P2/P4/P10 security work. |
| 11 VS Code Integration v1.0 | Drives P9 client work. |
| 12 Project Plan & Progress v1.0 | Provides project governance baseline; this document operationalizes implementation sequencing. |
| 13 Research Synthesis v1.0 | Drives research adoption discipline. |
| 14 Architecture Decision Matrix v1.0 | Constrains architecture and decision gates. |
| 15 Master Architecture v1.0 | Provides master target architecture. |
| 16 Repository Blueprint v1.0 | Defines physical implementation locations. |
| 17 Technology Decisions v1.0 | Defines technology defaults, deferred choices and dependency governance. |

# 36. Final Implementation Readiness Checklist

- 01–17 locked baselines are available to implementation team.

- Repository Blueprint is accepted as canonical structure.

- Master Architecture is accepted as architectural north star.

- Technology Decisions are accepted as v1 baseline.

- Phase gates and evidence requirements are understood.

- Security-first sequence is preserved.

- Implementation tracking mechanism is ready.

- CI can execute baseline checks.

- Change-control process is available.

- Release evidence package format is defined.

# 37. Final Status

STATUS: FINAL / LOCKED — v1.0

Implementation Plan v1.0 is the authoritative execution roadmap for building the AI Software Co-Agent from the locked specification, architecture, repository and technology baselines. It establishes the dependency-aware phase sequence, workstreams, gates, Definition of Done, risk controls, evidence requirements, change management and release path.

— END OF IMPLEMENTATION PLAN v1.0 —
