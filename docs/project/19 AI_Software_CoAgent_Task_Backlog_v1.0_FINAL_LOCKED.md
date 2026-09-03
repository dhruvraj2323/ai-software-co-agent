AI SOFTWARE CO-AGENT

TASK BACKLOG

Version 1.0 — FINAL / LOCKED

Document ID: TBL-001 • Implementation-ready work-item baseline

| Field | Value |
| --- | --- |
| Document | Task Backlog |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Convert the locked architecture and implementation plan into an ordered, traceable backlog of implementation, testing, security, documentation and release work. |
| Authority | Task sequencing and dependencies are governed here; detailed behavior remains governed by the applicable locked specifications. |
| Change policy | Material scope, dependency, priority or acceptance changes require versioned backlog/change control. |

Lock Statement: Task Backlog v1.0 is the canonical implementation backlog baseline. Tasks may be broken into smaller implementation tickets without changing their locked intent, dependencies or acceptance conditions.

# 1. Backlog Mission

The backlog turns the approved architecture into executable work. It prioritizes safety-critical foundations before autonomy, keeps work traceable to locked documents, and makes each task independently reviewable through explicit acceptance criteria and evidence.

Backlog principle: No task is considered Done because code exists; it is Done only when its required evidence and acceptance criteria pass.

# 2. Backlog Status Model

| Status | Meaning |
| --- | --- |
| BACKLOG | Approved work not yet started. |
| READY | Dependencies satisfied and implementation can begin. |
| IN PROGRESS | Active implementation. |
| BLOCKED | Dependency, decision or gate prevents progress. |
| READY FOR REVIEW | Implementation and required tests complete. |
| GATE REVIEW | Evidence is being checked against the phase gate. |
| DONE | Acceptance criteria and required evidence passed. |
| DEFERRED | Intentionally moved outside current implementation scope. |
| REJECTED | Explicitly removed by approved decision/change control. |

# 3. Priority Model

| Priority | Meaning |
| --- | --- |
| P0 | Critical foundation/security/release blocker. |
| P1 | Required for core usable system. |
| P2 | Important capability or quality improvement. |
| P3 | Optional enhancement; not required for v1 core. |

# 4. Work Item Types

| Type | Use |
| --- | --- |
| EPIC | Major implementation area containing related tasks. |
| TASK | Concrete implementation work. |
| SPIKE | Time-bounded investigation/benchmark producing evidence. |
| TEST | Dedicated validation/security/reliability work. |
| DOC | Documentation/traceability work. |
| OPS | Build/CI/release/operational work. |
| ADR | Formal architecture/technology decision work. |

# 5. Master Backlog Structure

EPIC-01 Foundation

EPIC-02 Core Contracts & State

EPIC-03 Security & Workspace

EPIC-04 Tools, Policy & Approval

EPIC-05 Controlled Execution

EPIC-06 Repository Intelligence

EPIC-07 Context & Memory

EPIC-08 Model Gateway & Agent

EPIC-09 Validation, Completion & Recovery

EPIC-10 Audit, Artifacts & Observability

EPIC-11 VS Code & CLI

EPIC-12 E2E, Security & Performance

EPIC-13 Release

EPIC-14 Deferred Technology / Research

# 6. Epic Summary

| Epic | Outcome | Priority | Phase |
| --- | --- | --- | --- |
| EPIC-01 | Reproducible repository/tooling baseline | P0 | P0 |
| EPIC-02 | Stable types, state and protocol | P0 | P1 |
| EPIC-03 | Safe scope and security primitives | P0 | P2 |
| EPIC-04 | Single capability authorization path | P0 | P3 |
| EPIC-05 | Bounded real-world execution | P0 | P4 |
| EPIC-06 | Repository understanding | P1 | P5 |
| EPIC-07 | Scoped context and memory | P1 | P5 |
| EPIC-08 | Controlled model-driven agent | P1 | P6 |
| EPIC-09 | Evidence-based completion and recovery | P0 | P7 |
| EPIC-10 | Traceability and evidence | P1 | P8 |
| EPIC-11 | Developer clients | P1 | P9 |
| EPIC-12 | Hardening | P0 | P10 |
| EPIC-13 | Release package | P0 | P11 |
| EPIC-14 | Deferred evidence-driven choices | P2/P3 | As triggered |

# 7. EPIC-01 — Foundation Backlog

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T001 | TASK | Create canonical repository tree from Repository Blueprint. | P0 | — | Required root/module structure exists. |
| T002 | TASK | Create Python package/build configuration. | P0 | T001 | Clean environment installs/builds successfully. |
| T003 | TASK | Create test, scripts, configs and docs skeleton. | P0 | T001 | Expected directories and baseline files exist. |
| T004 | OPS | Create CI smoke workflow. | P0 | T002,T003 | CI installs and runs baseline checks. |
| T005 | OPS | Add lint/format baseline. | P1 | T002 | Quality command runs reproducibly. |
| T006 | OPS | Add static type-check baseline. | P1 | T002 | Canonical type checker runs without configuration drift. |
| T007 | OPS | Add dependency/security scanning. | P0 | T004 | CI performs required scans. |
| T008 | OPS | Add secret/config safety checks. | P0 | T003 | Secrets are not accepted in source-controlled config. |
| T009 | DOC | Record bootstrap/run instructions. | P1 | T001–T004 | New developer can reproduce baseline setup. |
| T010 | GATE | Pass G0 Foundation Gate. | P0 | T001–T009 | G0 evidence package approved. |

# 8. EPIC-02 — Core Contracts & State

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T011 | TASK | Implement stable IDs/correlation identifiers. | P0 | T002 | Session/task/request/event IDs are generated and propagated. |
| T012 | TASK | Implement common result/error/event types. | P0 | T011 | Typed contracts cover success/failure/event envelopes. |
| T013 | TASK | Implement session state model. | P0 | T011,T012 | Session lifecycle transitions are tested. |
| T014 | TASK | Implement task state machine. | P0 | T013 | Invalid transitions are rejected. |
| T015 | TASK | Implement versioned client/runtime protocol. | P0 | T012 | Messages validate and version correctly. |
| T016 | TASK | Implement protocol error envelopes. | P1 | T015 | Malformed/unsupported requests produce typed errors. |
| T017 | TEST | Create contract/serialization test suite. | P0 | T015,T016 | Contract tests pass. |
| T018 | TEST | Create state-transition test suite. | P0 | T014 | Valid/invalid transitions pass. |
| T019 | TASK | Implement minimal runtime health/task command. | P1 | T014,T015 | Runtime accepts a safe task command. |
| T020 | GATE | Pass G1 Contracts Gate. | P0 | T011–T019 | G1 evidence package approved. |

# 9. EPIC-03 — Security & Workspace

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T021 | TASK | Implement canonical workspace identity/scope. | P0 | T014 | Task scope is explicit. |
| T022 | TASK | Implement canonical path resolution. | P0 | T021 | Paths resolve deterministically. |
| T023 | TASK | Implement traversal/symlink escape protection. | P0 | T022 | Out-of-scope access is blocked. |
| T024 | TASK | Implement protected-path policy. | P0 | T022 | Protected targets require correct policy outcome. |
| T025 | TASK | Implement resource/time/concurrency limits. | P0 | T014 | Limits are enforced. |
| T026 | TASK | Implement secret filtering/redaction primitives. | P0 | T012 | Known secret patterns are filtered from outputs/events. |
| T027 | TASK | Implement sandbox interface. | P0 | T025 | Executors can require sandbox guarantees. |
| T028 | TEST | Build security boundary/adversarial fixtures. | P0 | T021–T027 | Fixtures cover escape/bypass cases. |
| T029 | TEST | Run fail-closed security-control tests. | P0 | T025–T027 | Affected privileged actions block on control failure. |
| T030 | GATE | Pass G2 Security/Scope Gate. | P0 | T021–T029 | G2 evidence package approved. |

# 10. EPIC-04 — Tools, Policy & Approval

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T031 | TASK | Define canonical ToolRequest/ToolResult contracts. | P0 | T012,T015 | Typed tool contracts validate. |
| T032 | TASK | Implement Tool Registry. | P0 | T031 | Capabilities are explicitly registered. |
| T033 | TASK | Implement Tool Gateway. | P0 | T031,T032 | All registered tool calls route through gateway. |
| T034 | TASK | Implement PolicyRequest/PolicyDecision. | P0 | T031,T033 | Policy produces ALLOW/ASK/DENY/RESTRICT. |
| T035 | TASK | Implement approval lifecycle. | P0 | T034,T015 | ASK requests are explicit and correlated. |
| T036 | TASK | Implement policy scope/risk evaluation. | P0 | T021,T025,T034 | Target/risk/scope influence decision. |
| T037 | TEST | Build policy decision matrix tests. | P0 | T034–T036 | Expected decisions pass. |
| T038 | TEST | Build tool/policy bypass tests. | P0 | T033–T036 | Alternate authorization paths fail. |
| T039 | TASK | Implement audit hook for material tool decisions. | P1 | T033,T034 | Decision is traceable. |
| T040 | GATE | Pass G3 Capability Control Gate. | P0 | T031–T039 | G3 evidence package approved. |

# 11. EPIC-05 — Controlled Execution

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T041 | TASK | Implement scoped filesystem executor. | P0 | T033,T036,T027 | Authorized file operations work; escapes fail. |
| T042 | TASK | Implement bounded process executor. | P0 | T033,T036,T027 | Timeout/resource/cancellation controls work. |
| T043 | TASK | Implement patch/change engine. | P0 | T041 | Patch conflicts are detected. |
| T044 | TASK | Implement user-change protection. | P0 | T041,T043 | Unrelated user edits are preserved. |
| T045 | TASK | Implement Git adapter. | P1 | T033,T036,T043 | Git operations use controlled capability path. |
| T046 | TASK | Implement cancellation propagation. | P0 | T042,T014 | Cancellation stops affected work. |
| T047 | TEST | Execution integration/security tests. | P0 | T041–T046 | Representative execution suite passes. |
| T048 | TEST | Process/resource abuse tests. | P0 | T042 | Excessive runtime/output/concurrency is bounded. |
| T049 | GATE | Pass G4 Execution Gate. | P0 | T041–T048 | G4 evidence package approved. |

# 12. EPIC-06 — Repository Intelligence

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T050 | TASK | Implement repository root/discovery service. | P1 | T021,T041 | Repository scope is identified safely. |
| T051 | TASK | Implement file/content search adapter. | P1 | T041 | Search respects scope. |
| T052 | TASK | Implement repository map/index abstraction. | P1 | T050,T051 | Relevant repository structure can be represented. |
| T053 | TASK | Implement symbol intelligence interface. | P2 | T052 | Symbol provider contract exists. |
| T054 | TEST | Repository intelligence scope tests. | P1 | T050–T053 | No out-of-scope repository access. |
| T055 | TEST | Representative repository benchmark. | P1 | T052,T053 | Baseline relevance/performance evidence recorded. |

# 13. EPIC-07 — Context & Memory

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T056 | TASK | Implement ContextProvider interface. | P1 | T012,T052 | Providers return typed context items. |
| T057 | TASK | Implement context ranking/filtering. | P1 | T056 | Relevant items rank within budget. |
| T058 | TASK | Implement context budget manager. | P0 | T057 | Unbounded context is prevented. |
| T059 | TASK | Implement Context Manifest/provenance. | P1 | T057 | Context source/freshness metadata is available. |
| T060 | TASK | Implement MemoryStore interface. | P1 | T012 | Memory persistence is abstracted. |
| T061 | TASK | Implement scoped memory manager. | P1 | T060,T021 | Memory is task/project scoped. |
| T062 | TASK | Implement stale-memory handling. | P1 | T061,T059 | Current repository state can outrank stale memory. |
| T063 | TEST | Context/memory security tests. | P0 | T056–T062 | Memory cannot authorize and secrets are filtered. |
| T064 | TEST | Context relevance/budget benchmark. | P1 | T057,T058 | Representative tasks fit context budget. |
| T065 | GATE | Pass G5 Context Gate. | P1 | T056–T064 | G5 evidence package approved. |

# 14. EPIC-08 — Model Gateway & Agent

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T066 | TASK | Implement ModelGateway interface. | P1 | T012 | Provider is replaceable. |
| T067 | TASK | Implement model adapter contract/conformance tests. | P1 | T066 | Provider adapter conforms. |
| T068 | TASK | Implement planner interface. | P1 | T056,T066 | Planner consumes controlled context. |
| T069 | TASK | Implement agent behavior state loop. | P1 | T014,T033,T068 | Agent lifecycle is explicit. |
| T070 | TASK | Implement task/tool/recovery budgets. | P0 | T025,T069 | Loops are bounded. |
| T071 | TASK | Implement observation/result incorporation. | P1 | T069,T056 | Tool results refresh task context. |
| T072 | TEST | Agent tool-use behavior suite. | P0 | T069–T071 | No direct executor bypass. |
| T073 | TEST | Model failure/cancellation tests. | P0 | T066,T069,T070 | Failures stop safely. |
| T074 | SPIKE | Benchmark candidate model/provider options. | P2 | T066 | Evidence covers quality/cost/latency/security. |
| T075 | GATE | Pass G6 Agent Gate. | P1 | T066–T074 | G6 evidence package approved. |

# 15. EPIC-09 — Validation, Completion & Recovery

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T076 | TASK | Implement Validation Runner. | P0 | T041,T069 | Checks can be executed through controlled tools. |
| T077 | TASK | Implement validation evidence model. | P0 | T012,T076 | Results are structured and traceable. |
| T078 | TASK | Implement Completion Gate. | P0 | T077 | Only required evidence can establish COMPLETE. |
| T079 | TASK | Implement failure classifier. | P0 | T077 | Failures receive bounded categories. |
| T080 | TASK | Implement Recovery Controller. | P0 | T033,T079 | Recovery actions use normal policy path. |
| T081 | TASK | Implement recovery budgets/retry limits. | P0 | T025,T080 | Repeated failures stop. |
| T082 | TASK | Implement retest workflow. | P0 | T076,T080 | Repair is followed by validation. |
| T083 | TEST | False-completion adversarial suite. | P0 | T078 | Missing/invalid evidence cannot complete. |
| T084 | TEST | Recovery failure/loop suite. | P0 | T080–T082 | Recovery stops safely on exhaustion. |
| T085 | TEST | End-to-end coding task validation. | P0 | T069,T076,T078,T082 | Representative task passes with evidence. |
| T086 | GATE | Pass G7 Quality Gate. | P0 | T076–T085 | G7 evidence package approved. |

# 16. EPIC-10 — Audit, Artifacts & Observability

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T087 | TASK | Implement structured event envelope. | P1 | T012 | Events carry correlation metadata. |
| T088 | TASK | Implement audit recorder. | P0 | T087,T039 | Material actions are recorded. |
| T089 | TASK | Implement artifact store/reference model. | P1 | T012,T077 | Large evidence is referenced safely. |
| T090 | TASK | Implement output redaction layer. | P0 | T026,T087 | Sensitive output is filtered. |
| T091 | TASK | Implement task trace/reconstruction view. | P1 | T088,T089 | Representative task can be reconstructed. |
| T092 | TEST | Audit completeness/correlation tests. | P1 | T087–T091 | Event chains remain correlated. |
| T093 | TEST | Secret leakage tests. | P0 | T090 | Known secrets do not appear in ordinary evidence. |
| T094 | GATE | Pass G8 Evidence Gate. | P1 | T087–T093 | G8 evidence package approved. |

# 17. EPIC-11 — VS Code & CLI

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T095 | TASK | Implement CLI runtime client. | P1 | T015,T019 | CLI uses protocol only. |
| T096 | TASK | Implement VS Code extension shell. | P1 | T015 | Extension connects to runtime. |
| T097 | TASK | Implement chat/task UI. | P1 | T096 | User can submit and monitor tasks. |
| T098 | TASK | Implement approval UI. | P1 | T035,T096 | Approval responses map to exact requests. |
| T099 | TASK | Implement diff/change presentation. | P1 | T043,T096 | Changes are reviewable. |
| T100 | TASK | Implement diagnostics/progress/status. | P1 | T087,T096 | Runtime state is visible. |
| T101 | TASK | Implement reconnect/state synchronization. | P1 | T015,T013,T096 | Client reconnect does not duplicate side effects. |
| T102 | TEST | Client protocol compatibility suite. | P0 | T095–T101 | CLI and VS Code interoperate with same runtime. |
| T103 | TEST | Client bypass/security tests. | P0 | T095–T101 | Clients cannot bypass runtime/policy. |
| T104 | GATE | Pass G9 Client Gate. | P1 | T095–T103 | G9 evidence package approved. |

# 18. EPIC-12 — E2E, Security & Performance

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T105 | TEST | Run complete architecture decision test suite. | P0 | T104 | Applicable ADM tests pass. |
| T106 | TEST | Run injection/untrusted-content suite. | P0 | T069,T103 | Repository/MCP/memory content cannot gain authority. |
| T107 | TEST | Run workspace/process escape suite. | P0 | T041,T042 | Escape/resource attacks are blocked. |
| T108 | TEST | Run MCP policy-boundary suite. | P0 | T033,T067 | MCP cannot bypass internal policy. |
| T109 | TEST | Run user-change protection suite. | P0 | T044 | Unrelated changes remain safe. |
| T110 | TEST | Run failure-injection/recovery suite. | P0 | T080–T082 | Failures recover or stop within budgets. |
| T111 | TEST | Run representative repository E2E suite. | P0 | T085,T104 | Core coding workflows succeed. |
| T112 | TEST | Run performance/resource benchmark suite. | P1 | T064,T074 | Baseline metrics are recorded. |
| T113 | TEST | Run dependency/license/security review. | P0 | T007,T074 | Release dependencies approved. |
| T114 | GATE | Pass G10 Hardening Gate. | P0 | T105–T113 | Release-candidate evidence approved. |

# 19. EPIC-13 — Release

| ID | Type | Task | Pri | Depends | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T115 | OPS | Create reproducible release build. | P0 | T114 | Clean environment produces release artifact. |
| T116 | OPS | Verify package/install/startup workflow. | P0 | T115 | Fresh install passes smoke test. |
| T117 | DOC | Finalize user/developer/security documentation. | P0 | T114 | Documentation matches implementation. |
| T118 | OPS | Create rollback/recovery procedure. | P0 | T115 | Known-good rollback is documented/tested. |
| T119 | DOC | Generate release notes and traceability report. | P1 | T114 | Changes map to backlog/specs. |
| T120 | GATE | Pass G11 Release Gate. | P0 | T115–T119 | Release approval recorded. |

# 20. EPIC-14 — Deferred Technology / Research

| ID | Type | Task | Pri | Trigger | Acceptance |
| --- | --- | --- | --- | --- | --- |
| T121 | SPIKE | Evaluate specific LLM/provider candidates. | P2 | Need/provider benchmark | Decision backed by quality/cost/latency/security evidence. |
| T122 | SPIKE | Evaluate vector/embedding retrieval. | P2 | Context benchmark gap | Adopt only if material measured benefit. |
| T123 | SPIKE | Evaluate container sandbox backend. | P1 | Deployment/security need | Isolation/resource evidence passes. |
| T124 | SPIKE | Evaluate telemetry backend. | P3 | Operational need | Privacy/value review passes. |
| T125 | SPIKE | Evaluate multi-agent framework. | P3 | Measured coordination need | Benefit + isolation + budget evidence. |
| T126 | SPIKE | Evaluate remote database/runtime. | P3 | Scale/deployment trigger | Architecture compatibility proven. |
| T127 | ADR | Record approved deferred technology decision. | P1 | After evidence | ADR and affected docs updated. |

# 21. Cross-Cutting Backlog

| ID | Work | Priority | Rule |
| --- | --- | --- | --- |
| X001 | Maintain traceability from task → spec → architecture decision. | P0 | Required for material work. |
| X002 | Maintain security regression suite. | P0 | Security regressions block release. |
| X003 | Maintain architecture drift checks. | P0 | No alternate authority path. |
| X004 | Maintain dependency/license inventory. | P0 | Required for production dependencies. |
| X005 | Maintain test fixtures for adversarial repositories. | P1 | Use controlled, reproducible fixtures. |
| X006 | Maintain evidence/artifact retention rules. | P1 | No uncontrolled sensitive output. |
| X007 | Update progress/evidence after each gate. | P0 | Gate status must be reconstructable. |
| X008 | Review deferred decisions before release when triggered. | P1 | No hidden unresolved dependency. |

# 22. Dependency Graph

T001–T010 Foundation

↓

T011–T020 Contracts/State

↓

T021–T030 Security/Scope

↓

T031–T040 Tools/Policy

↓

T041–T049 Execution

↓

T050–T065 Repository/Context/Memory

↓

T066–T075 Model/Agent

↓

T076–T086 Validation/Recovery

↓

T087–T094 Evidence

↓

T095–T104 Clients

↓

T105–T114 Hardening

↓

T115–T120 Release

# 23. Critical Path Tasks

| Critical ID | Why critical |
| --- | --- |
| T002 | Build/install foundation. |
| T014 | Authoritative task lifecycle. |
| T021–T023 | Safe workspace boundary. |
| T033–T036 | Single tool authorization path. |
| T041–T042 | Controlled side effects. |
| T058 | Context resource control. |
| T069–T070 | Bounded agent lifecycle. |
| T078 | Authoritative completion. |
| T080–T082 | Bounded recovery. |
| T085 | Representative E2E proof. |
| T105–T114 | Release-blocking hardening. |
| T120 | Final release gate. |

# 24. Parallelizable Work

- Security test fixture development may run alongside security implementation.

- Protocol contract tests may run alongside state implementation.

- VS Code UI prototyping may run alongside runtime development, provided it cannot define authority.

- Repository-intelligence benchmarks may run alongside execution work.

- Dependency/license review may run in parallel with module implementation.

- Performance harness development may precede final performance measurements.

- Documentation updates may proceed continuously without altering locked specifications.

# 25. Task-Level Definition of Ready

- Task has a unique ID and clear scope.

- Applicable specification/baseline is identified.

- Dependencies are known.

- Acceptance criteria are testable.

- Security impact is identified.

- Expected repository location is known.

- Required evidence is identified.

- No unresolved architecture contradiction blocks implementation.

# 26. Task-Level Definition of Done

- Implementation is in the correct repository module.

- Applicable contracts/specifications are satisfied.

- Required automated tests pass.

- Security tests pass where applicable.

- Errors/cancellation follow the recovery model.

- Audit/evidence behavior is implemented where required.

- No locked invariant is violated.

- Documentation/traceability is updated.

- Review is complete.

- Acceptance evidence is recorded.

# 27. Security-Critical Task Rules

- Security-critical tasks are P0.

- Security tests are release-blocking.

- Security-control failure must fail closed for affected privileged operations.

- Security fixes cannot be replaced by model prompts or documentation.

- Policy, sandbox, secret and scope changes require explicit review.

- Security bypass findings must create a tracked remediation task.

# 28. Bug / Defect Workflow

DEFECT

↓

CLASSIFY: SECURITY / CORRECTNESS / RELIABILITY / UX / PERFORMANCE

↓

SEVERITY + PRIORITY

↓

ROOT-CAUSE TASK

↓

FIX

↓

REGRESSION TEST

↓

RE-GATE IF AFFECTED

↓

CLOSE WITH EVIDENCE

# 29. Backlog Change Control

| Change | Rule |
| --- | --- |
| Split task | Allowed if intent, acceptance and traceability are preserved. |
| Reorder task | Allowed only when dependency/gate safety is preserved. |
| Change acceptance | Requires review of affected specification and tests. |
| Change priority | Requires impact/gate review. |
| Add new core capability | Requires scope/architecture/security review. |
| Remove mandatory task | Requires explicit change control. |
| Change locked invariant | Not allowed through normal backlog edit; requires new versioned decision. |
| Defer release blocker | Requires formal approval; security/release gates cannot be silently skipped. |

# 30. Backlog Metrics

| Metric | Purpose |
| --- | --- |
| Ready → Done lead time | Delivery flow. |
| Blocked time | Dependency health. |
| Rework rate | Implementation quality. |
| Gate pass rate | Release readiness. |
| Security defect escape | Security quality. |
| False-completion rate | Agent correctness. |
| Recovery success rate | Resilience. |
| Test pass rate | Regression health. |
| Architecture drift findings | Design integrity. |
| Deferred decision count | Technology uncertainty. |

# 31. Progress Reporting Format

PHASE: Pn

GATE: Gn

STATUS: NOT STARTED / IN PROGRESS / BLOCKED / REVIEW / DONE

COMPLETED: <task IDs>

IN PROGRESS: <task IDs>

BLOCKED: <task IDs + reason>

TESTS: <result>

SECURITY: <result>

EVIDENCE: <artifact references>

RISKS: <active risks>

NEXT: <task IDs>

# 32. Release-Blocking Backlog Items

- T007 dependency/security scanning

- T008 secret/config safety

- T023 workspace escape protection

- T029 fail-closed security tests

- T033 Tool Gateway

- T034–T036 Policy/approval/scope controls

- T042 process limits

- T044 user-change protection

- T078 Completion Gate

- T081 recovery limits

- T083 false-completion tests

- T093 secret leakage tests

- T103 client bypass tests

- T105–T110 adversarial hardening

- T113 dependency/license/security review

- T120 release gate

# 33. Backlog Invariants

- BL1: Every implementation task has a unique stable ID.

- BL2: Every material task maps to a locked baseline.

- BL3: Dependencies cannot be silently bypassed.

- BL4: Security-critical work is release-blocking.

- BL5: Tool side-effect work requires the Tool Gateway/Policy path.

- BL6: Agent tasks cannot create direct executor paths.

- BL7: Completion work requires validation evidence.

- BL8: Recovery work cannot weaken policy/security.

- BL9: Client tasks cannot create privileged runtime authority.

- BL10: Deferred technology is not a hidden prerequisite.

- BL11: Every gate has evidence.

- BL12: Done means acceptance criteria passed.

- BL13: Architecture drift creates remediation/change work.

- BL14: User-change protection remains active throughout implementation.

- BL15: Release requires full mandatory backlog/gate evidence.

# 34. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| BL-A01 | Coverage | All major implementation areas are represented. |
| BL-A02 | Sequence | Backlog follows dependency-aware implementation order. |
| BL-A03 | Security | Security/scope work precedes privileged execution. |
| BL-A04 | Tools | Single Tool Gateway/Policy implementation is explicit. |
| BL-A05 | Execution | Filesystem/process/patch/Git work is represented. |
| BL-A06 | Context | Repository/context/memory work is represented. |
| BL-A07 | Agent | Model/agent work is bounded and testable. |
| BL-A08 | Quality | Validation/completion/recovery work is explicit. |
| BL-A09 | Evidence | Audit/artifact/observability work is explicit. |
| BL-A10 | Clients | VS Code/CLI work uses same runtime. |
| BL-A11 | Hardening | E2E/security/performance work is release-blocking. |
| BL-A12 | Release | Release tasks and gate are explicit. |
| BL-A13 | Deferred | Deferred technology work is trigger/evidence based. |
| BL-A14 | Traceability | Tasks map to locked documents. |
| BL-A15 | Governance | Change, DoR, DoD and progress rules are defined. |

# 35. Traceability to Locked Baselines

| Baseline | Task Backlog role |
| --- | --- |
| 01 PRD v1.0 | Provides product scope/outcomes represented by epics. |
| 02 SRS v1.0 | Provides requirements mapped to implementation and tests. |
| 03 System Architecture v1.0 | Provides phase/component dependency order. |
| 04 Technical Design v1.0 | Provides module-level implementation tasks. |
| 05 Agent Behaviour v1.0 | Drives agent lifecycle and behavior tasks. |
| 06 Tool & Permission v1.0 | Drives Tool Gateway, Policy and approval tasks. |
| 07 Memory & Context v1.0 | Drives repository/context/memory tasks. |
| 08 Error Recovery v1.0 | Drives recovery, cancellation and failure tasks. |
| 09 Testing & Validation v1.0 | Drives validation, completion and quality gates. |
| 10 Security & Sandbox v1.0 | Drives security, scope, sandbox and adversarial tasks. |
| 11 VS Code Integration v1.0 | Drives client/protocol/UI tasks. |
| 12 Project Plan & Progress v1.0 | Provides project governance and phase structure. |
| 13 Research Synthesis v1.0 | Drives research/benchmark/dependency adoption tasks. |
| 14 Architecture Decision Matrix v1.0 | Constrains backlog architecture decisions. |
| 15 Master Architecture v1.0 | Provides master component/dependency map. |
| 16 Repository Blueprint v1.0 | Defines physical locations for implementation. |
| 17 Technology Decisions v1.0 | Defines technology defaults and deferred evaluations. |
| 18 Implementation Plan v1.0 | Provides the phase sequence, gates and Definition of Done operationalized by this backlog. |

# 36. Initial Implementation Start Set

| Order | Start with | Why |
| --- | --- | --- |
| 1 | T001–T010 | Make repository reproducible. |
| 2 | T011–T020 | Create stable contracts/state. |
| 3 | T021–T030 | Establish security boundary. |
| 4 | T031–T040 | Establish one authorization path. |
| 5 | T041–T049 | Enable safe side effects. |

Do not jump directly to agent autonomy. P6 agent work becomes meaningful only after the control, execution and context foundations are working and tested.

# 37. Final Backlog Snapshot

| Area | Tasks | Priority | Gate |
| --- | --- | --- | --- |
| Foundation | T001–T010 | P0/P1 | G0 |
| Contracts/State | T011–T020 | P0/P1 | G1 |
| Security/Scope | T021–T030 | P0 | G2 |
| Tools/Policy | T031–T040 | P0 | G3 |
| Execution | T041–T049 | P0/P1 | G4 |
| Repository | T050–T055 | P1/P2 | G5 |
| Context/Memory | T056–T065 | P0/P1 | G5 |
| Agent/Model | T066–T075 | P0/P1/P2 | G6 |
| Validation/Recovery | T076–T086 | P0 | G7 |
| Evidence | T087–T094 | P0/P1 | G8 |
| Clients | T095–T104 | P0/P1 | G9 |
| Hardening | T105–T114 | P0/P1 | G10 |
| Release | T115–T120 | P0/P1 | G11 |
| Deferred | T121–T127 | P1/P2/P3 | As triggered |

# 38. Final Status

STATUS: FINAL / LOCKED — v1.0

Task Backlog v1.0 is the canonical implementation work-item baseline for the AI Software Co-Agent. It translates the locked specification, architecture, repository, technology and implementation-plan baselines into ordered epics/tasks, dependencies, gates, acceptance criteria, security rules, progress reporting, evidence requirements and release-blocking work.

— END OF TASK BACKLOG v1.0 —
