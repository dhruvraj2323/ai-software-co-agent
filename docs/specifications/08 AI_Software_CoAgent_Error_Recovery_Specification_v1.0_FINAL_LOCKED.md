AI SOFTWARE CO-AGENT

ERROR RECOVERY SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: ERS-001 • Derived from PRD, SRS, System Architecture, Technical Design, Agent Behaviour, Tool/Permission & Memory/Context v1.0

| Field | Value |
| --- | --- |
| Document | Error Recovery Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD + SRS + System Architecture + Technical Design + Agent Behaviour + Tool & Permission + Memory & Context v1.0 |
| Purpose | Define deterministic, bounded and evidence-driven handling of tool, execution, validation, patch, Git, context, model and runtime failures |

Lock Statement: This Error Recovery Specification v1.0 is the final locked recovery baseline. Recovery must be bounded, policy-controlled, evidence-driven and validation-backed. Recovery may never weaken security controls or declare completion without required evidence.

# 1. Purpose & Recovery Mission

The recovery subsystem converts failures into controlled next actions. It must distinguish recoverable engineering failures from security, policy, scope and infrastructure conditions that require blocking or human intervention. The objective is not to retry blindly, but to diagnose from evidence, make the smallest justified repair, revalidate the action and stop safely when recovery is no longer justified.

Primary recovery principle: Failure is evidence, not permission to improvise.

# 2. Core Recovery Principles

- Never hide a failure.

- Normalize before diagnosing.

- Use actual failure evidence as the primary recovery input.

- Prefer targeted repairs over broad rewrites.

- Recovery must use the normal Tool Gateway and Policy Engine.

- Recovery must respect task scope and preserve unrelated user changes.

- Recovery must be bounded by attempts, time and scope.

- Re-read current repository state before repairing stale/changed files.

- Retest after every material repair.

- Do not weaken tests, security policy or sandbox restrictions to obtain success.

- Do not repeat identical failed actions without new evidence.

- Security/policy failures are not automatically repaired by changing policy.

- Completion remains the responsibility of the Completion Gate.

- Recovery exhaustion results in non-complete status and an evidence-backed report.

# 3. Recovery Lifecycle

FAILURE

↓

1. CAPTURE EVIDENCE

↓

2. NORMALIZE ERROR

↓

3. CLASSIFY

↓

4. CHECK RECOVERY ELIGIBILITY

↓

5. BUILD FAILURE CONTEXT

↓

6. DIAGNOSE

↓

7. CREATE REPAIR PLAN

↓

8. POLICY + SCOPE CHECK

↓

9. GENERATE VALIDATED PATCH/ACTION

↓

10. APPLY CONTROLLED REPAIR

↓

11. REFRESH CONTEXT

↓

12. RETEST

↓

┌───────────────┴────────────────┐

PASS FAIL

│ │

Continue/Completion Next bounded attempt

│

Budget / safety check

│

STOP / BLOCK / FAIL

# 4. Recovery States

| State | Meaning | Allowed next states |
| --- | --- | --- |
| FAILURE_CAPTURED | Failure evidence recorded | NORMALIZED, BLOCKED |
| NORMALIZED | Canonical error created | CLASSIFIED, BLOCKED |
| CLASSIFIED | Failure category identified | ELIGIBLE_CHECK, BLOCKED |
| RECOVERY_ELIGIBLE | Safe recovery path exists | CONTEXT_BUILD, BLOCKED |
| CONTEXT_BUILD | Relevant evidence assembled | DIAGNOSING, BLOCKED |
| DIAGNOSING | Root-cause hypothesis generated | REPAIR_PLANNED, BLOCKED |
| REPAIR_PLANNED | Repair strategy created | POLICY_CHECK, BLOCKED |
| POLICY_CHECK | Repair action authorized | APPLYING, BLOCKED |
| APPLYING | Repair action executing | RETESTING, BLOCKED, FAILED |
| RETESTING | Relevant validation running | RECOVERED, NEXT_ATTEMPT, FAILED |
| RECOVERED | Failure resolved and evidence passed | CONTINUE / COMPLETION_GATE |
| NEXT_ATTEMPT | Another bounded attempt allowed | CONTEXT_BUILD, FAILED, BLOCKED |
| BLOCKED | Recovery cannot safely proceed | Terminal until intervention |
| FAILED | Recovery exhausted/unrecoverable | Terminal non-complete |

# 5. Error Taxonomy

| Category | Meaning | Examples |
| --- | --- | --- |
| TASK | Lifecycle/task condition | Invalid state, cancellation, scope conflict |
| CTX | Context/repository intelligence | Stale index, retrieval failure, context budget |
| LLM | Model/provider | Timeout, provider error, malformed structured output |
| TOOL | Tool contract | Unknown tool, invalid schema, tool unavailable |
| POL | Policy/security decision | DENY, approval rejection, policy conflict |
| PATH | Workspace/resource scope | Outside root, protected path, traversal |
| EXEC | Process/execution | Non-zero exit, timeout, launch failure |
| PATCH | Change application | Stale hash, conflict, invalid patch, unexpected scope |
| TEST | Validation | Test/lint/build failure, timeout, invalid command |
| GIT | Version control | Dirty conflict, checkpoint failure, rollback failure |
| MCP | External tool integration | Server unavailable, malformed result, untrusted output |
| PERSIST | State/storage | Database/artifact write/read failure |
| SYSTEM | Runtime/infrastructure | Resource exhaustion, unexpected internal error |

# 6. ErrorRecord Contract

ErrorRecord {

error_id: UUID

task_id: UUID | null

correlation_id: UUID

category: ErrorCategory

code: string

source: string

message: string

severity: INFO | WARNING | ERROR | CRITICAL

recoverability: AUTO | ASSISTED | MANUAL | NONE

evidence_refs: [string]

affected_scope: Scope | null

retry_key: string | null

occurred_at: datetime

normalized_at: datetime

}

- Raw errors are retained as evidence where appropriate; normalized records provide stable classification.

- Messages must not intentionally expose secrets.

- retry_key supports repeated-failure detection.

- Severity does not by itself determine recoverability.

# 7. Failure Evidence Capture

| Failure source | Minimum evidence |
| --- | --- |
| Process | Program/args metadata, cwd, exit code, bounded stdout/stderr, duration |
| Test | Gate name, command, exit code, failure summary, artifact reference |
| Patch | Target files, base hashes, conflict details, expected/actual scope |
| Git | Repository, status, diff/checkpoint state |
| Policy | Tool, decision, rule, reason, scope |
| LLM | Provider/model metadata, timeout/error, structured-output failure details |
| Context | Provider, query, budget, freshness/index state |
| MCP | Server/tool identity, request correlation, normalized external error |
| Persistence | Store operation, record type, safe error details |
| Runtime | Component, operation, stack/reference, resource condition |

Evidence is captured before recovery begins. Recovery should never depend solely on a paraphrased conversational description of the failure.

# 8. Recovery Eligibility

| Condition | Default eligibility |
| --- | --- |
| Transient provider timeout | AUTO/ASSISTED within retry budget |
| Malformed model output | AUTO retry with correction/validation |
| Test/build failure | AUTO/ASSISTED if within task scope |
| Patch conflict/stale file | AUTO refresh/regenerate if safe |
| Tool execution failure | AUTO/ASSISTED depending on risk |
| Policy DENY | NONE for the denied action; do not bypass |
| Protected path violation | NONE unless user/policy explicitly changes authorization |
| Outside workspace | NONE unless scope is explicitly changed through normal authorization |
| Approval rejection | NONE for same action; may block task |
| Security detection | MANUAL/BLOCKED |
| Repeated identical failure | Stop when no new evidence/repair path exists |
| Resource exhaustion | MANUAL/BLOCKED after bounded retry |

Eligibility is evaluated before diagnosis/repair. A failure being technically fixable does not make it automatically authorized to fix.

# 9. Retry & Backoff Behaviour

| Failure type | Retry behavior |
| --- | --- |
| Transient LLM/network | Bounded retry with increasing delay where safe. |
| Tool unavailable | Small bounded retry; then block/fail. |
| Process timeout | Retry only if command is expected to be repeatable and budget permits. |
| Test failure | Do not blindly rerun identical failed test as recovery; diagnose first. |
| Patch stale | Refresh state and regenerate; not a blind retry. |
| Policy DENY | Zero retries intended to bypass decision. |
| Approval timeout/rejection | No automatic replay as approval. |
| Repeated same error | Stop or require new evidence. |

- Retries are separate from recovery attempts.

- Retry limits are configurable but bounded.

- Retrying must not expand scope.

- Backoff is a reliability measure, not a security control.

# 10. Failure Context Construction

| Priority | Recovery context |
| --- | --- |
| P1 | Exact failure output/evidence |
| P2 | Affected file/function/module/resource |
| P3 | Current diff and recent task changes |
| P4 | Current repository state and relevant tests/config |
| P5 | Acceptance criteria and plan |
| P6 | Prior recovery attempts and their outcomes |
| P7 | Relevant project memory/decisions |
| P8 | Broader repository context only if needed |

- Refresh stale repository context before repair.

- Include only relevant previous attempts to prevent repetitive fixes.

- Do not allow historical memory to override current failure evidence.

- Respect context budgets and sensitive-data filtering.

# 11. Diagnosis Behaviour

- Identify the immediate symptom from evidence.

- Separate symptom from likely root cause.

- Identify affected scope.

- Check whether the proposed cause is supported by repository/validation evidence.

- Generate one or more hypotheses when uncertainty remains.

- Prefer hypotheses that can be tested with low-risk inspection.

- Do not present speculation as fact.

- Do not repair security policy or protected controls as a diagnosis shortcut.

| Diagnosis confidence | Behavior |
| --- | --- |
| High | Proceed with targeted repair if policy allows. |
| Medium | Perform additional low-risk inspection or choose a conservative repair. |
| Low | Ask/block rather than making broad speculative changes. |
| Contradictory | Refresh context and resolve evidence conflict. |
| Security-related | Stop normal auto-repair and follow security handling. |

# 12. Repair Plan Behaviour

- Repair plan must reference the failure evidence.

- Identify exact intended files/resources.

- State expected effect.

- Define the validation gate that should demonstrate recovery.

- Prefer minimal scope.

- Include rollback/checkpoint strategy where appropriate.

- Do not change unrelated modules merely for convenience.

- Do not weaken validation or security controls.

# 13. Repair Execution

RepairPlan

↓

ToolRequest(s)

↓

Schema Validation

↓

Tool Gateway

↓

Policy Engine

↓

Patch/Execution Safety Checks

↓

Apply

↓

Diff + Scope Verification

↓

Context Refresh

↓

Retest

- Every repair side effect follows normal permission rules.

- Repair patches use current file versions/hashes.

- Actual diff is compared with intended repair scope.

- Unexpected scope causes block/review.

- Repair never directly writes to the OS outside the normal execution boundary.

# 14. Recovery Strategies by Failure Class

| Failure class | Recovery strategy |
| --- | --- |
| Malformed model output | Retry with schema correction; if repeated, change prompt/context strategy or fail. |
| Missing file | Refresh repository state; verify path; update plan if file truly absent. |
| Compile/type error | Inspect diagnostic → locate affected code → targeted patch → re-run relevant checks. |
| Test assertion failure | Inspect assertion/test fixture → diagnose behavior → targeted implementation/test fix only if justified → retest. |
| Lint/format failure | Apply minimal style/lint fix → rerun gate. |
| Build dependency failure | Inspect project configuration/dependency state → policy-approved correction → rebuild. |
| Patch conflict | Refresh file → regenerate patch from current base → revalidate scope. |
| Git dirty conflict | Preserve user changes → narrow scope or ask user. |
| Command timeout | Check command/process behavior → adjust only within policy/time budget or stop. |
| Tool unavailable | Retry boundedly → alternate safe registered tool if equivalent and authorized → otherwise block. |
| MCP failure | Normalize external failure → bounded retry → fallback if safe → block if unavailable. |
| Policy DENY | Do not recover by bypass; explain blocker. |
| Protected resource | Do not bypass; require explicit authorized change if appropriate. |
| Context/index stale | Invalidate/refresh affected data → continue. |
| Persistence failure | Retry safely if idempotent; otherwise block and preserve evidence. |

# 15. Bounded Recovery Loop

attempt = 0

while recovery_allowed:

capture_failure_evidence()

normalize_and_classify()

if not eligible: stop()

if repeated_without_new_evidence: stop()

build_failure_context()

diagnose()

create_repair_plan()

policy_check()

apply_repair()

refresh_context()

result = retest()

if result.passed: recovered()

attempt += 1

if budget_exhausted: stop()

This pseudocode is behavioral, not a requirement for a literal implementation. The key requirement is bounded, observable and policy-controlled recovery.

# 16. Recovery Budgets

| Budget | Purpose | Stop condition |
| --- | --- | --- |
| Recovery attempts | Prevent endless repair | Max attempts reached |
| Recovery time | Limit total recovery duration | Time budget exceeded |
| Repair scope | Prevent scope expansion | Expected scope exceeded |
| Tool calls | Prevent excessive retries | Tool budget exhausted |
| LLM calls | Control provider cost/latency | Model budget exhausted |
| Context budget | Keep diagnosis bounded | Context cannot be safely assembled |
| Process budget | Bound repair commands | Execution limit reached |

- Budgets apply across the task's recovery lifecycle according to configuration.

- Changing tools does not reset a budget unless the task policy explicitly defines a new bounded phase.

- Budget exhaustion is a non-complete condition.

# 17. Repeated Failure Detection

- Create a normalized retry_key from stable failure characteristics.

- Track prior attempts and repair outcomes.

- Detect identical or materially equivalent failures.

- Do not repeat the same repair without new evidence.

- Escalate to a different diagnosis only when new evidence exists.

- After repeated failure, stop or request human intervention.

| Pattern | Behavior |
| --- | --- |
| Same error + same repair + same result | Stop; report repeated failure. |
| Same error + new repository evidence | Permit bounded new diagnosis. |
| Different error after repair | Treat as new failure while preserving chain. |
| Flaky/intermittent error | Use configured evidence-based retry policy. |
| Security error repeated | Stop; never iterate around security controls. |

# 18. Rollback & Recovery Checkpoints

- Create checkpoints before high-impact task mutations when configured.

- Rollback only task-owned changes.

- Preserve unrelated user modifications.

- Use Git adapter/tool path for Git rollback.

- Verify resulting diff/status after rollback.

- Rollback is itself a high-risk action and follows policy/approval.

- Rollback failure becomes a new recovery/error record and may require manual intervention.

# 19. Retesting Behaviour

| Situation | Retest rule |
| --- | --- |
| Targeted code fix | Run directly relevant test/check first. |
| Build/config fix | Run build and relevant tests. |
| Dependency change | Run relevant build/tests and dependency validation. |
| Patch conflict repair | Re-run affected checks after applying fresh patch. |
| Lint-only repair | Re-run lint gate. |
| Multiple repairs | Run targeted check after each material repair, then required broader gates. |
| Final recovery success | Required completion gates still run before COMPLETE. |

- Passing a targeted check does not automatically mean task completion.

- Required validation gates remain mandatory.

- Old PASS results may be superseded by later code changes.

# 20. Security & Policy Recovery Rules

- Never modify policy configuration to make a denied action succeed.

- Never switch shells/interpreters to evade a denied command.

- Never use MCP as an alternate route around a denied capability.

- Never ask the model to reinterpret a DENY as approval.

- Never expose secrets as part of diagnosis for convenience.

- Security alerts may stop automatic recovery.

- Protected-path violations require explicit authorized scope change through normal control paths.

- Prompt injection is treated as untrusted input and is not a recoverable instruction.

# 21. Cancellation & Emergency Stop

- Cancellation immediately prevents initiation of new recovery actions.

- Active repair execution should receive cancellation signals.

- Persist failure/recovery evidence already produced.

- Do not start a new retry after cancellation.

- Task remains CANCELLED/non-complete.

- Emergency stop takes precedence over recovery success.

# 22. Human Intervention

| Trigger | Required user interaction |
| --- | --- |
| High-risk repair | ASK/approval according to policy. |
| Scope expansion | Explain proposed scope and request approval. |
| Security/policy blocker | Explain blocker; user may change authorized policy through normal administration, not agent bypass. |
| Low-confidence diagnosis | Ask targeted clarification/intervention. |
| Recovery exhausted | Present failure evidence and next recommended action. |
| Git conflict involving user changes | Ask user rather than overwrite. |
| Irreversible/destructive action | Explicit approval if policy permits; otherwise DENY. |

# 23. Recovery Reporting

| Report field | Content |
| --- | --- |
| Initial failure | Normalized category/code + evidence reference |
| Diagnosis | Root-cause hypothesis + confidence |
| Attempts | Count + attempt summaries |
| Repairs | Files/actions changed |
| Validation | Before/after relevant results |
| Final outcome | Recovered / blocked / failed / cancelled |
| Remaining issue | What still prevents completion |
| Git state | Diff/checkpoint/rollback evidence |
| Policy events | Relevant ASK/DENY/RESTRICT decisions |
| Recommendation | Action required if unresolved |

# 24. Recovery Audit Events

| Event | Minimum fields |
| --- | --- |
| recovery.started | task, error_id, correlation_id |
| recovery.classified | category, eligibility |
| recovery.context_built | sources/manifest reference |
| recovery.diagnosed | hypothesis, confidence |
| recovery.plan_created | scope, validation target |
| recovery.policy_decided | tool/action, decision, rule |
| recovery.applied | patch/action, diff/evidence |
| recovery.retested | gate/result/evidence |
| recovery.repeated | retry_key, attempt |
| recovery.exhausted | budget + reason |
| recovery.completed | outcome/evidence |

# 25. Recovery Chain Model

Task

└── Failure #1

├── Evidence

├── Diagnosis

├── Repair Attempt #1

│ └── Validation

├── Repair Attempt #2

│ └── Validation

└── Final Outcome

├── Recovered

├── Blocked

├── Failed

└── Cancelled

A recovery chain preserves causal history and prevents the final report from collapsing multiple failures into a misleading single success/failure statement.

# 26. Canonical Recovery Scenarios

| Scenario | Expected recovery |
| --- | --- |
| Compile failure | Capture compiler output → locate symbol/type → inspect current code → targeted patch → policy → compile/relevant tests → continue. |
| Test failure | Capture assertion → inspect test + implementation → diagnose → minimal repair → targeted test → required full gates. |
| Stale patch | Detect hash mismatch → refresh file → regenerate patch → recheck scope → apply → test. |
| Git dirty worktree | Record unrelated changes → narrow task scope → if unsafe, block/ask; never reset user work. |
| PowerShell timeout | Capture command/cwd/output → classify → determine safe repeatability → bounded retry or stop. |
| Policy DENY | Record DENY → no execution → explain blocker; no alternate route. |
| MCP unavailable | Normalize server failure → bounded retry → safe fallback if available → block if required capability unavailable. |
| Repeated same failure | Compare retry_key → detect repetition → stop and report rather than repeat. |
| Recovery introduces new failure | Record new error chain → diagnose new failure within same budgets → recover/stop. |
| Cancellation during repair | Stop new actions → terminate active repair where possible → persist evidence → CANCELLED. |

# 27. Recovery Invariants

- R1: Every recoverable failure has recorded evidence.

- R2: Every recovery attempt is bounded.

- R3: Recovery uses the normal Tool Gateway and Policy Engine.

- R4: Security DENY cannot be recovered by bypass.

- R5: Recovery does not silently expand task scope.

- R6: Current repository state is refreshed before repairing stale/conflicting changes.

- R7: Material repair is followed by retesting.

- R8: Repeated identical failure does not cause infinite retries.

- R9: Completion requires Completion Gate evidence after recovery.

- R10: Recovery never weakens security controls.

- R11: Unrelated user changes are preserved.

- R12: Cancellation prevents new recovery actions.

- R13: Recovery exhaustion produces non-complete status.

- R14: Model confidence cannot substitute for validation evidence.

- R15: Historical memory cannot override current failure evidence.

# 28. Error Recovery Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| ERS-A01 | Capture | Failures are normalized with evidence and correlation IDs. |
| ERS-A02 | Classification | Supported failure categories and recoverability are deterministic. |
| ERS-A03 | Eligibility | Non-recoverable/security failures are not blindly retried. |
| ERS-A04 | Diagnosis | Recovery uses actual failure evidence and current repository context. |
| ERS-A05 | Repair | Repairs are minimal, scoped and policy-controlled. |
| ERS-A06 | Retest | Material repairs trigger relevant validation. |
| ERS-A07 | Budgets | Attempt/time/scope/tool/model budgets are enforced. |
| ERS-A08 | Repeat detection | Identical failure loops are detected and stopped. |
| ERS-A09 | Git safety | Rollback preserves unrelated user changes. |
| ERS-A10 | Security | Recovery cannot bypass policy, sandbox or protected paths. |
| ERS-A11 | Cancellation | Recovery responds safely to cancellation/emergency stop. |
| ERS-A12 | Audit | Recovery chain is reconstructable from events/evidence. |
| ERS-A13 | Reporting | Unresolved failures and next actions are accurately reported. |
| ERS-A14 | Completion | Recovery success alone never creates COMPLETE without required gates. |
| ERS-A15 | Testing | Recovery failure modes have automated security/integration coverage. |

# 29. Traceability to Locked Baselines

| Baseline | Recovery impact |
| --- | --- |
| PRD v1.0 | Reliability, safety, evidence-backed completion and controlled autonomy. |
| SRS v1.0 | Error handling, recovery, validation, budgets and security requirements. |
| System Architecture v1.0 | Recovery component and validation/completion boundaries. |
| Technical Design v1.0 | Error taxonomy, RecoveryController, Validation Runner, Policy/Tool path and Git design. |
| Agent Behaviour v1.0 | Bounded repair, current evidence, no false completion and safe stopping. |
| Tool & Permission v1.0 | All recovery actions follow Tool Gateway/Policy Engine. |
| Memory & Context v1.0 | Failure context, freshness and current-evidence precedence. |
| Testing & Validation v1.0 | Retest and evidence requirements. |
| Security & Sandbox v1.0 | Security blockers and no-bypass rules. |
| Repository Blueprint v1.0 | Physical recovery module/test placement. |

# 30. Implementation Mapping

| Area | Expected implementation modules |
| --- | --- |
| Error models | src/recovery/models.py |
| Normalizer | src/recovery/normalizer.py |
| Classifier | src/recovery/classifier.py |
| Eligibility | src/recovery/eligibility.py |
| Failure context | src/recovery/context.py |
| Diagnosis | src/recovery/diagnosis.py |
| Repair planning | src/recovery/repair_plan.py |
| Recovery controller | src/recovery/controller.py |
| Retry/budget | src/recovery/budget.py |
| Repeat detection | src/recovery/repetition.py |
| Recovery audit | src/recovery/audit.py |
| Tests | tests/unit/recovery, tests/integration/recovery, tests/security/recovery |

Exact filenames may evolve through implementation change control. The recovery lifecycle, authority rules, budgets and invariants are locked.

# 31. Change Control

- Changes to recovery eligibility require reliability/security review.

- Changes to retry/budget semantics require performance/evaluation review.

- Changes that allow recovery to alter security policy require architecture/security approval.

- Changes to Completion Gate interaction require validation review.

- New failure categories require normalized codes, recovery behavior and tests.

- New recovery strategies must define evidence, scope, authorization and stop conditions.

# 32. Final Status

STATUS: FINAL / LOCKED — v1.0

This Error Recovery Specification v1.0 is the authoritative recovery baseline for the AI Software Co-Agent. It defines failure evidence capture, normalization, classification, bounded diagnosis and repair, policy enforcement, retesting, repeated-failure detection, rollback, cancellation, reporting and recovery invariants.

— END OF ERROR RECOVERY SPECIFICATION v1.0 —
