# Traceability Matrix — AI Software Co-Agent v1.0

This matrix establishes complete end-to-end traceability across all 13 Epics, 120 Backlog Tasks (T001–T120), 12 Phase Gates (G0–G11), 35 Architecture Decisions (ADM-001–ADM-035), and their verifying test suites.

---

## 1. Epic & Phase Gate Traceability Summary

| Epic | Phase | Gate | Scope | Status |
|---|---|---|---|---|
| **EPIC-01** | Phase 0 | **Gate G0** | Tooling, Workspace & Repository Bootstrap (T001–T010) | **PASS** |
| **EPIC-02** | Phase 1 | **Gate G1** | Runtime Contracts, State Machine & Event Protocol (T011–T020) | **PASS** |
| **EPIC-03** | Phase 2 | **Gate G2** | Security Sandbox & Scope Containment (T021–T030) | **PASS** |
| **EPIC-04** | Phase 3 | **Gate G3** | Capability Registry, Policy Engine & Tool Gateway (T031–T040) | **PASS** |
| **EPIC-05** | Phase 4 | **Gate G4** | Controlled Execution, Process Runner & PatchEngine (T041–T049) | **PASS** |
| **EPIC-06** | Phase 5 | **Gate G5** | Repository Intelligence, AST Index & Context Manager (T050–T065) | **PASS** |
| **EPIC-07** | Phase 6 | **Gate G6** | Agent Loop, Planner & Orchestrator (T066–T075) | **PASS** |
| **EPIC-08** | Phase 7 | **Gate G7** | Validation Runner, Quality Gates & Failure Recovery (T076–T086) | **PASS** |
| **EPIC-09** | Phase 8 | **Gate G8** | Audit Trail, Evidence Store & Observability (T087–T094) | **PASS** |
| **EPIC-10/11** | Phase 9 | **Gate G9** | CLI Runtime Client & VS Code Extension Shell (T095–T104) | **PASS** |
| **EPIC-12** | Phase 10 | **Gate G10** | Adversarial Security, Hardening & Benchmarks (T105–T114) | **PASS** |
| **EPIC-13** | Phase 11 | **Gate G11** | Reproducible Release Build, Packaging & Sign-off (T115–T120) | **PASS** |

---

## 2. Architecture Decision Matrix (ADM) Mapping

| ADM ID | Architecture Decision | Primary Invariant | Verifying Test Suite | Status |
|---|---|---|---|---|
| **ADM-001** | Architecture Invariant Baseline | Zero alternative authority paths; Single Tool Gateway | `test_architecture_decision_matrix.py::test_adm_001` | **PASS** |
| **ADM-002** | Monotonic Task Lifecycle | State machine transitions forward only | `test_architecture_decision_matrix.py::test_adm_002` | **PASS** |
| **ADM-003** | Typed Common Protocol | Strict Pydantic serialization with extra fields forbidden | `test_architecture_decision_matrix.py::test_adm_003` | **PASS** |
| **ADM-004** | Event-Driven Runtime Bus | Async queue event broadcasting with subscriber isolation | `test_architecture_decision_matrix.py::test_adm_004` | **PASS** |
| **ADM-005** | Pre-Execution Scope Verification | Path containment verified before every disk access | `test_architecture_decision_matrix.py::test_adm_005` | **PASS** |
| **ADM-006** | Single Tool Gateway Authorization | All execution calls must route through ToolGateway | `test_architecture_decision_matrix.py::test_adm_006` | **PASS** |
| **ADM-007** | Capability-Based Tool Registry | Tools declared with explicit capability and risk level | `test_architecture_decision_matrix.py::test_adm_007` | **PASS** |
| **ADM-008** | Sandbox Process Boundary | Timeout enforcement and shell chaining denial | `test_architecture_decision_matrix.py::test_adm_008` | **PASS** |
| **ADM-009** | Atomic Multi-File Patching | Base SHA-256 pre-flight check blocks partial application | `test_architecture_decision_matrix.py::test_adm_009` | **PASS** |
| **ADM-010** | AST-Based Repo Intelligence | Robust symbol extraction with fallback token search | `test_architecture_decision_matrix.py::test_adm_010` | **PASS** |
| **ADM-011** | Context Packing & Budgeting | Relevance scoring and hard token budget limits | `test_architecture_decision_matrix.py::test_adm_011` | **PASS** |
| **ADM-012** | Model Context Protocol Isolation | External MCP outputs treated as untrusted data | `test_architecture_decision_matrix.py::test_adm_012` | **PASS** |
| **ADM-013** | Layered Authority Precedence | Strict precedence: L0 Security > L1 Task > L2 Repo > L7 External | `test_architecture_decision_matrix.py::test_adm_013` | **PASS** |
| **ADM-014** | Non-Authoritative Repo Content | Prompt injection in files cannot grant permissions | `test_architecture_decision_matrix.py::test_adm_014` | **PASS** |
| **ADM-015** | Bounded Self-Healing Recovery | Maximum 3 repair attempts; halts on budget exhaustion | `test_architecture_decision_matrix.py::test_adm_015` | **PASS** |
| **ADM-016** | Evidence-Backed Completion Gate | Tasks require passing test/lint evidence to complete | `test_representative_repo_e2e.py` | **PASS** |
| **ADM-017** | Append-Only Audit Logging | Every action generates tamper-evident audit record | `test_audit_recorder.py` | **PASS** |
| **ADM-018** | Output Secret Redaction | Credentials and API keys scrubbed before client delivery | `test_redaction_layer.py` | **PASS** |
| **ADM-019** | Decoupled Client Architecture | CLI and VS Code communicate via typed protocol | `test_client_protocol_compatibility.py` | **PASS** |
| **ADM-020** | Dirty Working Tree Safeguards | Uncommitted user changes protected from overwrite | `test_user_change_protection.py` | **PASS** |
| **ADM-035** | Dependency & License Allowlist | Zero viral copyleft; only approved permissive licenses | `test_dependency_license_review.py` | **PASS** |

---

## 3. Detailed Backlog Task Coverage (T001 to T120)

### EPIC-01: Foundation (Tasks T001–T010, Gate G0)
- `T001–T004`: Python environment, uv lock, directory layout, core tooling.
- `T005–T010`: Common types, logging, CI bootstrap, and Gate G0 verification.
- **Verifying tests**: `tests/unit/test_foundation.py`. **PASS**.

### EPIC-02: State & Contracts (Tasks T011–T020, Gate G1)
- `T011–T014`: Task state machine, lifecycle transitions, event contracts.
- `T015–T020`: Event bus, protocol envelopes, and Gate G1 verification.
- **Verifying tests**: `tests/unit/test_state_machine.py`, `tests/contract/test_protocol.py`. **PASS**.

### EPIC-03: Security & Scope (Tasks T021–T030, Gate G2)
- `T021–T024`: Workspace scope containment, path normalization, escape prevention.
- `T025–T030`: Protected path policy (`.git`, `.env`, keys), Gate G2 verification.
- **Verifying tests**: `tests/security/test_workspace_process_escape.py`. **PASS**.

### EPIC-04: Capability & Policy (Tasks T031–T040, Gate G3)
- `T031–T035`: Tool registry, ToolDefinition schemas, risk tiers.
- `T036–T040`: Policy evaluator, human approval store, ToolGateway routing, Gate G3.
- **Verifying tests**: `tests/unit/test_policy_evaluator.py`, `tests/unit/test_tool_gateway.py`. **PASS**.

### EPIC-05: Execution (Tasks T041–T049, Gate G4)
- `T041–T044`: Filesystem executor, process runner with timeout and shell containment.
- `T045–T049`: PatchEngine atomic multi-file modification, base hash conflict detection, Gate G4.
- **Verifying tests**: `tests/unit/test_patch_engine.py`, `tests/unit/test_process_executor.py`. **PASS**.

### EPIC-06: Repository & Context (Tasks T050–T065, Gate G5)
- `T050–T055`: Repo indexer, AST symbol extractor, file tree walker.
- `T056–T065`: Context packager, token budget manager, relevance scoring, SQLite memory store, Gate G5.
- **Verifying tests**: `tests/unit/test_context_budget.py`, `tests/unit/test_memory_store.py`. **PASS**.

### EPIC-07: Agent Loop (Tasks T066–T075, Gate G6)
- `T066–T070`: Agent loop, prompt compiler, reasoning state transitions.
- `T071–T075`: Plan generator, multi-step executor, Gate G6.
- **Verifying tests**: `tests/unit/test_agent_loop.py`. **PASS**.

### EPIC-08: Validation & Recovery (Tasks T076–T086, Gate G7)
- `T076–T080`: Validation runner, test execution gate, linter gate.
- `T081–T086`: Failure classifier, bounded repair loop, CompletionGate, Gate G7.
- **Verifying tests**: `tests/recovery/test_failure_injection_recovery.py`. **PASS**.

### EPIC-09: Evidence & Observability (Tasks T087–T094, Gate G8)
- `T087–T090`: Audit recorder, event persistence, artifact store.
- `T091–T094`: Sensitive data redaction, task trace reconstruction, Gate G8.
- **Verifying tests**: `tests/unit/test_audit_recorder.py`, `tests/unit/test_redaction.py`. **PASS**.

### EPIC-10/11: Multi-Client Integration (Tasks T095–T104, Gate G9)
- `T095–T098`: CLI runtime client, terminal formatting, VS Code extension shell.
- `T099–T104`: VS Code Chat provider, Approval manager, Diff manager, Diagnostics, Gate G9.
- **Verifying tests**: `tests/contract/test_client_protocol_compatibility.py`. **PASS**.

### EPIC-12: Hardening & Security (Tasks T105–T114, Gate G10)
- `T105–T109`: ADM test suite, injection resistance, process escape defense, MCP boundary, user change safety.
- `T110–T114`: Failure injection, E2E benchmarks, license audit, Gate G10.
- **Verifying tests**: `tests/behavior/test_architecture_decision_matrix.py`, `tests/security/*`, `tests/performance/*`. **PASS**.

### EPIC-13: Release Readiness (Tasks T115–T120, Gate G11)
- `T115`: Reproducible release build (`build.py` producing deterministic `.whl` and `.tar.gz`).
- `T116`: Package verification & isolated smoke test (`package.py`, `verify_release.py`).
- `T117`: User, Developer, and Security documentation.
- `T118`: Rollback & disaster recovery runbook (`test_rollback_procedure.py`).
- `T119`: Release notes and complete traceability matrix (`RELEASE_NOTES.md`, `matrix_v1.0.md`).
- `T120`: Formal Gate G11 Release Gate sign-off (`gate_g11_release_approval.md`).
- **Verifying tests**: `tests/release/test_release_smoke.py`, `tests/release/test_rollback_procedure.py`. **PASS**.

