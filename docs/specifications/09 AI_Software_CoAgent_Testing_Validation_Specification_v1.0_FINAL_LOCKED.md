AI SOFTWARE CO-AGENT

TESTING & VALIDATION SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: TVS-001 • Derived from PRD, SRS, System Architecture, Technical Design, Agent Behaviour, Tool/Permission, Memory/Context & Error Recovery v1.0

| Field | Value |
| --- | --- |
| Document | Testing & Validation Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD + SRS + System Architecture + Technical Design + Agent Behaviour + Tool & Permission + Memory & Context + Error Recovery v1.0 |
| Purpose | Define the complete quality, correctness, security, reliability, regression and release-validation system for the Co-Agent |

Lock Statement: This Testing & Validation Specification v1.0 is the final locked quality baseline. No implementation may declare a task, feature, build or release successful without the applicable validation gates and evidence defined here.

# 1. Purpose & Quality Mission

Testing & Validation establishes objective evidence that the Co-Agent behaves according to its locked product, functional, architectural, security, permission, context, recovery and user-facing requirements. It validates both the Co-Agent itself and the work the Co-Agent performs in a repository.

Primary validation principle: Model confidence is not validation evidence.

# 2. Core Validation Principles

- Test behavior, not implementation assumptions.

- Validate deterministic safety boundaries independently from the model.

- Every material completion claim must be supported by evidence.

- Use the smallest relevant validation gate first, then required broader gates.

- Security tests are mandatory, not optional quality checks.

- Recovery paths must be tested, not only happy paths.

- Tool permissions must be tested at the authorization boundary.

- Context/memory must be tested for freshness, isolation and injection resistance.

- User changes must be preserved under testing and recovery.

- Flaky/unknown results are not equivalent to PASS.

- Tests must be reproducible where practical.

- Test failures must feed the Error Recovery lifecycle.

- Validation itself must respect the same controlled execution and policy path.

- Tests must not weaken production security controls merely to obtain a pass.

# 3. Quality Dimensions

| Dimension | What is validated |
| --- | --- |
| Functional | Required features and behaviors work. |
| Behavioral | Agent follows locked behavior/state rules. |
| Tool/Permission | No unauthorized action can execute. |
| Security | Sandbox, prompt injection, secret handling and boundaries. |
| Repository Intelligence | Search/map/symbol/context correctness. |
| Code Change | Patch correctness, scope and user-change preservation. |
| Validation | Tests/build/lint evidence and completion gates. |
| Recovery | Failure classification, repair and bounded retries. |
| Memory/Context | Freshness, ranking, provenance, isolation and budgets. |
| Integration | Runtime components interact correctly. |
| Client | VS Code/CLI integration behavior. |
| Performance | Latency/resource/output budgets within targets. |
| Reliability | Repeated tasks, failures and restarts behave safely. |
| Observability | Events/evidence are traceable. |
| Release | All mandatory gates and acceptance criteria are satisfied. |

# 4. Testing Pyramid

E2E / RELEASE

┌──────────────┐

│ Full Agent │

│ Workflows │

└──────┬───────┘

Integration / Contract

┌────────────┴────────────┐

│ Tool/Policy/Runtime/MCP │

└────────────┬────────────┘

Component Tests

┌────────────┴────────────┐

│ Context / Recovery / Git│

└────────────┬────────────┘

Unit Tests

┌────────────────┴────────────────┐

│ Models / Rules / Parsers / Utils│

└─────────────────────────────────┘

The suite should maximize fast deterministic unit/component coverage while retaining targeted integration and full workflow tests for boundary behavior.

# 5. Test Environments

| Environment | Purpose | Data |
| --- | --- | --- |
| Unit | Fast isolated logic tests | Synthetic fixtures |
| Component | Single subsystem behavior | Controlled fixtures |
| Integration | Cross-module contracts | Temporary workspace/repository |
| Security | Attack/bypass scenarios | Dedicated malicious fixtures |
| Recovery | Failure/repair lifecycle | Fault-injected fixtures |
| E2E | Realistic user workflows | Ephemeral sample repositories |
| Performance | Latency/resource characterization | Controlled benchmark repos |
| Release/Acceptance | Final locked acceptance | Clean reproducible environment |

- Tests must avoid depending on a developer's personal repository state.

- Tests requiring network/external providers should be isolated and explicitly marked.

- Security tests should be runnable without exposing real secrets.

- Production credentials/data are prohibited in normal test fixtures.

# 6. Test Taxonomy & Naming

| Prefix | Class | Purpose |
| --- | --- | --- |
| UT | Unit Test | Pure/local logic. |
| CT | Component Test | Subsystem behavior. |
| IT | Integration Test | Component contracts. |
| ST | Security Test | Security/bypass resistance. |
| RT | Recovery Test | Failure/recovery behavior. |
| BT | Behavior Test | Agent behavioral invariants. |
| ET | E2E Test | Complete workflow. |
| PT | Performance Test | Latency/resource budgets. |
| RTG | Regression Test | Previously fixed behavior. |
| AT | Acceptance Test | Requirement-level acceptance. |
| REL | Release Gate | Mandatory release criteria. |

Recommended IDs use stable identifiers, e.g. BT-TOOL-001, ST-POL-004, RT-PATCH-002, AT-ABS-006.

# 7. Requirements Traceability

- Every testable SRS requirement must map to one or more tests or an explicit verification method.

- Every locked invariant in Agent Behaviour, Tool/Permission, Memory/Context and Error Recovery must have test coverage.

- Security/Sandbox requirements must have dedicated security tests.

- Acceptance criteria must identify the evidence required for PASS.

- Uncovered requirements must be visible in a coverage report.

| Requirement source | Required verification |
| --- | --- |
| PRD | Acceptance/E2E + product behavior evidence |
| SRS | Requirement-level tests |
| Architecture | Integration/contract tests |
| Technical Design | Component/contract/unit tests |
| Agent Behaviour | Behavior + E2E tests |
| Tool & Permission | Security + policy + integration tests |
| Memory & Context | Unit + integration + security tests |
| Error Recovery | Recovery + integration + E2E tests |
| Security & Sandbox | Dedicated security tests |
| Implementation Plan | Task-level acceptance/regression tests |

# 8. Unit Testing Specification

- Use pytest as the primary Python test framework.

- Unit tests should isolate deterministic logic from filesystem/process/network/model dependencies.

- Use mocks/fakes only where they preserve the contract being tested.

- Cover normal, boundary, invalid and adversarial inputs.

- Policy rules must have explicit positive and negative cases.

- State transitions must test valid and invalid transitions.

- Context ranking/budgeting must test deterministic selection.

- Error classification must test all supported categories.

- Tool schema validation must test malformed arguments.

| Unit area | Minimum coverage focus |
| --- | --- |
| Task/state models | Valid/invalid states and transitions |
| Tool contracts | Schema validation + serialization |
| Policy Engine | ALLOW/ASK/DENY/RESTRICT + precedence |
| Scope resolver | Containment, traversal, protected paths |
| Context ranker | Priority, freshness, dedupe |
| Context budget | Token/item/provider limits |
| Memory lifecycle | Create/update/stale/supersede |
| Error classifier | Category/recoverability |
| Recovery budgets | Attempts/time/scope limits |
| Patch validator | Hashes, conflicts, scope |
| Completion Gate | Evidence and required-gate logic |
| Audit models | Event schema and correlation |

# 9. Component Testing

| Component | Validation |
| --- | --- |
| Agent Orchestrator | Lifecycle coordination, state, stop conditions |
| Planner | Requirement decomposition and plan contract |
| Repository Intelligence | Map/search/symbol correctness |
| Context Engine | Provider integration, ranking, budget, manifest |
| Memory Service | Persistence, isolation, freshness |
| LLM Gateway | Structured output, timeout, provider error handling |
| Tool Gateway | Validation → policy → executor routing |
| Policy Engine | Deterministic decisions and hard-rule precedence |
| Workspace Executor | Safe file operations |
| Process Executor | CWD/timeout/output/cancellation |
| Patch Engine | Stale/conflict/scope checks |
| Validation Runner | Command execution + evidence |
| Recovery Controller | Classification → repair → retest |
| Git Adapter | Status/diff/checkpoint/rollback behavior |
| MCP Adapter | Registration, invocation and policy routing |
| Audit/Reporting | Traceability and evidence generation |

# 10. Integration & Contract Testing

- Verify module interfaces using contract tests.

- Verify Tool Gateway always calls Policy Engine before executor.

- Verify Policy decisions are enforced by executors.

- Verify Context Engine consumes provider contracts correctly.

- Verify Recovery actions return through the normal tool path.

- Verify Validation results feed Completion Gate.

- Verify Git state feeds scope/change safety.

- Verify MCP calls use the same internal authorization path.

- Verify VS Code/CLI clients cannot bypass runtime security boundaries.

| Integration chain | Mandatory assertion |
| --- | --- |
| Agent → Tool Gateway | No direct executor path exists. |
| Tool Gateway → Policy | Every request is evaluated. |
| Policy → Executor | Only authorized operations execute. |
| Executor → Result | Normalized result/evidence returned. |
| Validation → Recovery | Failures become structured recovery inputs. |
| Recovery → Tool Gateway | Repair actions are policy-controlled. |
| Repository → Context | Current state/version is represented. |
| Context → LLM Gateway | Context manifest/budget is enforced. |
| Task → Completion Gate | Completion requires current evidence. |

# 11. Agent Behaviour Testing

| ID | Behavior | Test assertion |
| --- | --- | --- |
| BT-001 | Repository-first | Agent inspects relevant repository context before material change. |
| BT-002 | Plan-first | Material implementation has a plan. |
| BT-003 | Tool discipline | External actions use explicit registered tools. |
| BT-004 | Policy discipline | No tool executes before policy decision. |
| BT-005 | Approval | ASK pauses execution until approval. |
| BT-006 | No false completion | Missing/failed required evidence prevents COMPLETE. |
| BT-007 | User-change preservation | Unrelated dirty changes survive task execution. |
| BT-008 | Current evidence | Current code outranks stale memory. |
| BT-009 | Injection resistance | Repository instructions cannot override policy. |
| BT-010 | Bounded recovery | Recovery stops at configured budgets. |
| BT-011 | Cancellation | Cancellation stops new work and does not become success. |
| BT-012 | No scope creep | Unrelated files are not changed silently. |

# 12. Tool & Permission Testing

- Unknown tools must be rejected.

- Invalid schemas must be rejected before execution.

- DENY must result in zero underlying side effect.

- ASK must result in zero execution until approval.

- RESTRICT must not permit broader scope.

- Tool switching cannot bypass a DENY.

- Recovery cannot bypass policy.

- MCP cannot bypass policy.

- VS Code cannot bypass policy.

- Autonomy mode cannot bypass hard security rules.

| Security test | Expected result |
| --- | --- |
| Unknown tool ID | Rejected |
| Malformed arguments | Rejected |
| Outside-workspace path | Denied/restricted |
| Path traversal | Denied |
| Protected path write | Denied/ASK per policy |
| Denied shell command | No execution |
| Alternate shell bypass | No bypass |
| MCP denied capability | No execution |
| Recovery denied action | No execution |
| Approval rejected | No execution |
| Expired approval replay | No execution |
| Policy config tampering by agent | Rejected/blocked |

# 13. Security & Sandbox Validation

| Area | Required tests |
| --- | --- |
| Filesystem isolation | Traversal, absolute path, symlink/junction, protected paths |
| Process isolation | CWD, environment filtering, timeout, process termination |
| Command security | Shell metacharacters, command chaining, interpreter switching |
| Secret protection | Env/output/log/context redaction |
| Prompt injection | Malicious repository/tool/MCP instructions |
| MCP trust | Untrusted output and capability boundary |
| Policy integrity | Attempted policy modification/bypass |
| Client boundary | VS Code/CLI direct-executor bypass attempts |
| Persistence | Cross-task/project data leakage |
| Audit | Tamper/omission of critical decision evidence |

Security tests must be treated as release-blocking for violations of hard invariants.

# 14. Memory & Context Validation

- Verify provenance is retained for model-facing context.

- Verify current repository content invalidates stale context.

- Verify current validation evidence supersedes older results.

- Verify task/project memory isolation.

- Verify secret filtering.

- Verify context budgets are enforced.

- Verify deterministic ranking under fixed inputs.

- Verify malicious instructions do not gain authority through memory/context.

- Verify Context Manifest reflects selected and omitted items.

| Test | Expected result |
| --- | --- |
| File changes after indexing | Affected context is refreshed/invalidated. |
| Stale decision conflicts with current code | Current evidence wins; conflict is surfaced when material. |
| Cross-project memory query | No unauthorized memory returned. |
| Secret in tool output | Filtered before normal model context. |
| Oversized log | Bounded/summarized/artifact-referenced. |
| Injection in README | Treated as untrusted data. |
| Same inputs/policy | Equivalent ranking/selection behavior. |
| Completion with old PASS only | Rejected without current required evidence. |

# 15. Error Recovery Validation

| ID | Failure | Expected result |
| --- | --- | --- |
| RT-001 | Malformed LLM output | Bounded correction/retry then safe stop if repeated. |
| RT-002 | Test failure | Diagnose → targeted repair → retest. |
| RT-003 | Stale patch | Refresh → regenerate → apply → validate. |
| RT-004 | Patch conflict | Conflict is detected; user changes preserved. |
| RT-005 | Policy DENY | No recovery bypass. |
| RT-006 | Repeated same error | Loop detection stops repeated repair. |
| RT-007 | Timeout | Bounded termination/retry. |
| RT-008 | Recovery scope expansion | Blocked. |
| RT-009 | Recovery budget exhaustion | Non-complete state. |
| RT-010 | Cancellation during recovery | No new attempts; CANCELLED. |
| RT-011 | New failure after repair | New error chain is recorded. |
| RT-012 | Rollback | Only task-owned changes rolled back. |

# 16. Validation Runner Specification

- Validation Runner executes approved validation commands through the Tool Gateway.

- Each gate has a stable ID and expected success semantics.

- Capture command metadata, exit code, duration and bounded output.

- Large output is stored as an artifact and referenced.

- Gate results are immutable evidence records.

- A later relevant change supersedes earlier gate results.

- Timeouts and non-zero exit codes are explicit failures.

- Skipped/not-run gates remain visible.

ValidationResult {

gate_id: string

task_id: UUID

command: string

status: PASS | FAIL | BLOCKED | NOT_RUN | TIMEOUT

exit_code: int | null

duration_ms: int | null

evidence_ref: string | null

captured_at: datetime

source_version: string | null

}

# 17. Validation Gate Hierarchy

| Gate | Purpose | Typical trigger |
| --- | --- | --- |
| G0 — Contract | Schema/model/serialization integrity | Every build/test cycle |
| G1 — Unit | Fast component correctness | Every implementation task |
| G2 — Component | Subsystem behavior | Changed subsystem |
| G3 — Integration | Cross-component contracts | Material architecture/runtime change |
| G4 — Security | Policy/sandbox/injection controls | Security-sensitive or release gate |
| G5 — Regression | Previously fixed critical behavior | Every relevant change/release |
| G6 — E2E | Complete user workflow | Feature completion/release |
| G7 — Performance | Latency/resource budgets | Performance-impacting/release |
| G8 — Acceptance | Requirement-level success | Task/release completion |
| G9 — Release | All mandatory gates + documentation | Release candidate |

# 18. Completion Gate

The Completion Gate is authoritative.

- Verify acceptance criteria are satisfied.

- Verify required validation gates are PASS.

- Verify no required gate is FAIL, BLOCKED or NOT_RUN.

- Verify current code/diff is the code that was validated.

- Verify recovery, if used, ended with successful current validation.

- Verify security gates are satisfied.

- Verify task scope and Git/change state are acceptable.

- Generate completion evidence manifest.

- Only then permit COMPLETE.

COMPLETE =

acceptance_passed

AND required_gates_passed

AND current_state_matches_validated_state

AND security_gates_passed

AND no blocking_error

AND completion_evidence_recorded

# 19. Regression Strategy

- Every production bug/failure that is fixed should receive a regression test when practical.

- Security bypasses require permanent regression fixtures.

- Policy rule changes require both positive and negative regression cases.

- Recovery fixes require repeated-failure and budget regression coverage.

- Context/memory fixes require stale/conflict/security regression coverage.

- Maintain a critical regression suite suitable for every commit/release gate.

# 20. Property & Adversarial Testing

- Use property-based tests for parsers, path normalization, scope resolution and schema boundaries where valuable.

- Use adversarial fixtures for shell arguments, paths, malformed tool requests and prompt injection.

- Test invariants across random valid/invalid state sequences where practical.

- Fuzzing must remain sandboxed and use synthetic data.

- Security fuzz failures are release-blocking until assessed.

# 21. Performance & Resource Validation

| Area | Measure |
| --- | --- |
| Repository discovery | Latency, file count, memory |
| Search | Latency/result count/output size |
| Context assembly | Latency, token count, provider contribution |
| LLM Gateway | Latency, timeout behavior, structured-output success |
| Tool Gateway | Policy evaluation latency |
| Policy Engine | Decision latency under representative rules |
| Patch application | Latency and changed-file scope |
| Validation Runner | Startup/command overhead |
| Recovery | Time/attempt distribution |
| VS Code IPC | Request/response latency |
| Persistence | SQLite read/write latency |
| Memory usage | Peak resident memory |

Performance targets are configured per release profile; a performance regression must be evaluated against the active target rather than a fixed universal number.

# 22. Reliability & Resilience Testing

- Repeat representative workflows multiple times.

- Test process restart and task recovery from persisted state.

- Inject tool timeouts and failures.

- Inject LLM provider failures.

- Inject SQLite/artifact failures.

- Test interrupted/cancelled executions.

- Test partial tool results.

- Test repeated validation failures.

- Verify no unsafe state transition after fault.

# 23. Test Fixtures & Sample Repositories

| Fixture | Purpose |
| --- | --- |
| minimal-python | Simple unit/test workflow |
| multi-module-python | Repository map/symbol/context |
| broken-build | Compiler/build recovery |
| failing-tests | Validation/recovery |
| dirty-git | User-change preservation |
| protected-paths | Security scope tests |
| prompt-injection | Malicious repository instructions |
| large-repository | Performance/context budgeting |
| mcp-mock | External tool integration/security |
| malformed-config | Configuration validation |

- Fixtures must be deterministic and version-controlled.

- Fixtures must contain no real secrets.

- Fixtures should isolate one failure mechanism where possible.

# 24. CI Validation Pipeline

FORMAT / STATIC CHECKS

↓

UNIT TESTS

↓

COMPONENT TESTS

↓

INTEGRATION / CONTRACT

↓

SECURITY SUITE

↓

REGRESSION SUITE

↓

E2E / ACCEPTANCE

↓

PERFORMANCE (release profile)

↓

RELEASE GATE

- Fast checks should fail early.

- Security and critical regression suites are mandatory gates.

- Release candidates require the complete applicable gate set.

- CI must publish machine-readable results and human-readable summaries.

# 25. Coverage & Quality Metrics

| Metric | Purpose |
| --- | --- |
| Requirement coverage | Percentage of testable requirements with verification. |
| Behavior invariant coverage | Locked behavioral invariants tested. |
| Policy rule coverage | Rules exercised by positive/negative tests. |
| Security scenario coverage | Attack/bypass scenarios exercised. |
| Recovery path coverage | Failure classes with tested recovery/stop paths. |
| Code coverage | Implementation-level signal, not sole quality measure. |
| Critical regression pass rate | Stability of critical behaviors. |
| Flaky test rate | Reliability of test suite. |
| Gate pass rate | Release readiness. |
| Mean recovery success | Recovery effectiveness signal. |
| False completion rate | Must be zero for release. |

Code coverage alone is never sufficient to demonstrate agent safety or correctness.

# 26. Flaky Test Policy

- A flaky test is not automatically treated as PASS.

- Identify, quarantine and track known flaky tests.

- Critical/security flaky tests block release until disposition is established.

- Reruns may diagnose flakiness but cannot conceal a failed required gate.

- Fix root causes rather than increasing retry counts indefinitely.

# 27. Validation Evidence & Artifacts

| Evidence | Minimum content |
| --- | --- |
| Test result | Test/gate ID, status, timestamp |
| Command result | Command metadata, exit code, bounded output/artifact |
| Diff evidence | Actual changed scope |
| Security result | Scenario, expected/actual outcome |
| Recovery evidence | Failure + repair + retest chain |
| Context manifest | Selected evidence used for completion/recovery |
| Coverage report | Requirement/test coverage |
| Release report | All mandatory gate statuses |

Evidence references must remain resolvable for the configured retention period.

# 28. Release Readiness Rules

- All mandatory release gates PASS.

- No critical/security test FAIL remains open.

- No false-completion defect remains open.

- Known exceptions are explicitly approved through release governance; they are never silently ignored.

- Build/package is reproducible according to the active release process.

- Documentation and locked specifications are version-aligned.

- Test evidence is archived/referenced.

- Security review is complete for security-impacting changes.

# 29. Validation Failure Integration with Recovery

Validation FAIL

↓

ValidationResult + Evidence

↓

ErrorRecord

↓

RecoveryController

↓

Targeted Repair

↓

Policy + Patch Validation

↓

Retest

↓

PASS → Completion Gate

FAIL → Bounded Next Attempt / Block

Validation is an input to recovery, but recovery cannot modify the validation rules merely to obtain PASS.

# 30. Release-Blocking Security Conditions

- Unauthorized tool execution.

- Policy DENY bypass.

- Workspace escape/path traversal.

- Protected-path bypass.

- Shell/PowerShell security bypass.

- MCP authorization bypass.

- VS Code/CLI direct-executor bypass.

- Secret exposure to model context or logs.

- Cross-project memory leakage.

- Prompt injection causing unauthorized action.

- Security policy self-modification by the agent.

- False COMPLETE after a required security/validation failure.

# 31. Test Execution Workflow

- Identify changed components and requirements.

- Select applicable unit/component/integration/security/recovery/E2E gates.

- Prepare clean or controlled fixture.

- Run fast deterministic gates.

- Run deeper integration/security gates.

- Collect evidence and coverage.

- If failure occurs, enter Error Recovery flow.

- After repairs, rerun affected and required gates.

- Run Completion/Release Gate only on current validated state.

- Publish final validation report.

# 32. Canonical End-to-End Acceptance Scenarios

| ID | Scenario | Expected result |
| --- | --- | --- |
| AT-001 Feature implementation | Requirement → repository inspection → plan → patch → tests → report. |  |
| AT-002 Test-driven repair | Existing failing test → diagnosis → repair → retest → completion. |  |
| AT-003 Permission denial | Task requests denied action → policy DENY → no side effect → blocker report. |  |
| AT-004 Approval workflow | ASK action → approval → controlled execution → evidence. |  |
| AT-005 Dirty repository | Pre-existing user changes → task executes → unrelated changes preserved. |  |
| AT-006 Prompt injection | Malicious README → ignored as authority → safe task execution. |  |
| AT-007 Stale patch | Repository changes after plan → stale patch rejected → refresh → safe patch. |  |
| AT-008 Recovery exhaustion | Repeated failure → bounded attempts → non-complete report. |  |
| AT-009 Cancellation | User cancels active execution → stop → evidence preserved → CANCELLED. |  |
| AT-010 MCP integration | MCP tool request → same policy path → result/audit. |  |
| AT-011 Completion evidence | Required gate missing/failing → COMPLETE blocked. |  |
| AT-012 Release candidate | All required gates pass → release report generated. |  |

# 33. Testing & Validation Invariants

- TV1: A required validation gate cannot be silently skipped and still produce PASS.

- TV2: A failed required gate prevents COMPLETE.

- TV3: Old validation evidence cannot substitute for current validated state.

- TV4: Security violations are release-blocking unless formally governed and resolved.

- TV5: Tool/permission tests validate the actual authorization boundary.

- TV6: Recovery actions are themselves testable and policy-controlled.

- TV7: Cancellation cannot become success.

- TV8: Flaky results are not silently converted to PASS.

- TV9: Test output must not expose real secrets.

- TV10: Context/memory tests enforce current-evidence precedence.

- TV11: User changes must be preserved in relevant test scenarios.

- TV12: Release evidence must be traceable to the tested build/state.

- TV13: Model confidence is never validation evidence.

- TV14: Test infrastructure must not create a security bypass in the product.

- TV15: Coverage metrics inform quality but do not replace acceptance/security evidence.

# 34. Testing & Validation Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| TVS-A01 | Requirement coverage | All testable locked requirements have verification mapping. |
| TVS-A02 | Unit coverage | Core deterministic logic has unit coverage. |
| TVS-A03 | Integration | Critical component contracts are integration-tested. |
| TVS-A04 | Security | Mandatory security scenarios pass. |
| TVS-A05 | Behavior | Locked behavioral invariants are tested. |
| TVS-A06 | Tool permission | Authorization boundary is tested end-to-end. |
| TVS-A07 | Context/memory | Freshness, isolation, budget and injection controls are tested. |
| TVS-A08 | Recovery | Failure classes and bounded recovery are tested. |
| TVS-A09 | Completion | Completion Gate blocks missing/failed evidence. |
| TVS-A10 | Evidence | Results are structured, auditable and reproducible. |
| TVS-A11 | Regression | Critical fixes have regression protection. |
| TVS-A12 | Reliability | Restart/cancel/timeout/fault scenarios are tested. |
| TVS-A13 | Performance | Active performance targets are measured for release profiles. |
| TVS-A14 | CI | Applicable mandatory gates run automatically in CI. |
| TVS-A15 | Release | Release gate requires all mandatory conditions. |

# 35. Traceability to Locked Baselines

| Baseline | Testing/Validation impact |
| --- | --- |
| PRD v1.0 | Product acceptance, safety and completion evidence. |
| SRS v1.0 | Requirement-level functional/security validation. |
| System Architecture v1.0 | Component boundary and integration tests. |
| Technical Design v1.0 | Module/contract/executor validation. |
| Agent Behaviour v1.0 | Behavioral invariant and E2E scenarios. |
| Tool & Permission v1.0 | Policy/authorization/security tests. |
| Memory & Context v1.0 | Freshness/provenance/budget/isolation tests. |
| Error Recovery v1.0 | Failure/recovery/retest/budget tests. |
| Security & Sandbox v1.0 | Release-blocking security suite. |
| Implementation Plan / Repository Blueprint | Task and module-level test mapping. |

# 36. Implementation Mapping

| Area | Expected implementation/test location |
| --- | --- |
| Python unit tests | tests/unit/... |
| Agent behavior | tests/behavior/... |
| Tool/policy tests | tests/unit/tools, tests/unit/policy |
| Context/memory | tests/unit/context, tests/unit/memory |
| Recovery | tests/unit/recovery, tests/integration/recovery |
| Security | tests/security/... |
| Integration | tests/integration/... |
| E2E | tests/e2e/... |
| Performance | tests/performance/... |
| Fixtures | tests/fixtures/... |
| Test reports | artifacts/test-results/... |
| Coverage | artifacts/coverage/... |
| CI workflows | .github/workflows/... |

Exact paths may evolve through implementation change control. Test responsibilities and release gates remain locked.

# 37. Change Control

- Changes to mandatory release gates require explicit review.

- Changes to security test scope require security review.

- Removing or weakening a regression test requires justification and approval.

- Changes to Completion Gate logic require architecture/validation review.

- New tools, permissions, memory types or recovery paths require corresponding tests before release.

- New acceptance criteria require traceability and evidence requirements.

- Test suite changes must never create a product security bypass.

# 38. Final Status

STATUS: FINAL / LOCKED — v1.0

This Testing & Validation Specification v1.0 is the authoritative quality baseline for the AI Software Co-Agent. It defines the testing pyramid, requirement traceability, unit/component/integration/security/recovery/E2E testing, validation gates, Completion Gate, evidence, regression, performance, reliability, release blockers and acceptance criteria.

— END OF TESTING & VALIDATION SPECIFICATION v1.0 —
