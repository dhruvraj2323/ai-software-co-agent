AI SOFTWARE CO-AGENT

PRODUCT REQUIREMENTS DOCUMENT

Version 1.0 — FINAL / LOCKED

Product Requirements Baseline • Documentation ID: PRD-001

| Document | Product Requirements Document (PRD) |
| --- | --- |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Role | Authoritative product-requirements baseline for implementation |

Lock Statement: This document is the final locked PRD v1.0 baseline. Future implementation work must conform to this product scope unless a formal change-control decision explicitly changes the baseline.

# 1. Product Vision

Build a reliable AI-powered software development co-agent that works with VS Code and a local project workspace with a high degree of controlled autonomy. The product transforms a human software requirement into validated repository changes through an observable, policy-controlled engineering workflow.

Core product principle: The agent must never claim completion merely because code was generated. A task is complete only after its required validation gates pass and evidence is recorded.

## 1.1 Target Engineering Loop

Human Requirement → Agent Planning → Repository Understanding → File/Folder Creation → Code Generation → Controlled Terminal Execution → Testing → Error Diagnosis → Automatic Fix → Retesting → Validation → Final Report

# 2. Product Problem

Existing coding assistants can generate or modify code, but reliable software delivery requires more than generation. The Co-Agent is intended to connect requirement understanding, repository intelligence, controlled tool execution, validation, recovery, Git safety, memory, and reporting into one auditable workflow.

- Reduce the gap between natural-language requirements and working repository changes.

- Understand an existing codebase before proposing changes.

- Make execution deterministic, observable, permission-controlled, and reversible.

- Detect failures and support bounded diagnosis → repair → retest cycles.

- Prevent false completion through evidence-based completion gates.

- Keep the core runtime independent from VS Code so the same engine can support CLI/headless execution and future clients.

# 3. Product Goals

| ID | Goal | Requirement |
| --- | --- | --- |
| G1 | Requirement understanding | Accept natural-language software requirements and convert them into a structured task with acceptance criteria. |
| G2 | Repository understanding | Inspect workspace structure, documentation, files, symbols, relationships, Git state, and relevant project context. |
| G3 | Planning | Produce an implementation plan with expected files/changes, dependencies, risks, and validation requirements. |
| G4 | Controlled implementation | Create and modify files through validated, scoped changes rather than unrestricted model access. |
| G5 | Controlled execution | Run terminal/PowerShell and other tools only through the central tool/policy boundary. |
| G6 | Validation | Run configured lint/build/test checks and preserve machine-readable evidence. |
| G7 | Recovery | Diagnose failures and perform bounded targeted repair/retest cycles when permitted. |
| G8 | Safety | Protect secrets, user changes, workspace boundaries, and sensitive/destructive operations. |
| G9 | Traceability | Record plans, tool requests, approvals, changes, validation, recovery, Git state, and final results. |
| G10 | IDE integration | Provide a VS Code client without making VS Code the security or orchestration core. |

# 4. Users & Primary Use Cases

## 4.1 Primary User

Software developer / engineering user working on a local repository, using VS Code, CLI, or headless execution.

## 4.2 Core Use Cases

- Provide a requirement and ask the Co-Agent to inspect the repository and create an implementation plan.

- Ask the Co-Agent to implement an approved plan in an existing local project.

- Create new folders/files or modify existing files within the authorized workspace.

- Run project commands, tests, builds, and lint checks through controlled tools.

- Receive structured diagnosis when tests/builds fail.

- Allow bounded automatic repair and retesting when policy permits.

- Review proposed/applied diffs and Git state.

- Cancel or intervene in a running task.

- Receive a final report containing changes, validation evidence, retries, Git state, and outcome.

- Operate the same core capability from CLI/headless mode and later from VS Code.

# 5. Functional Requirements

## 5.1 Requirement & Task Management

- FR-001 The system shall accept a natural-language software requirement.

- FR-002 The system shall normalize the requirement into a structured task.

- FR-003 The task shall contain scope and acceptance criteria.

- FR-004 The system shall maintain task lifecycle state including cancellation, blocking, failure, validation, and completion.

- FR-005 The system shall maintain execution budgets such as retry, time, and scope limits.

## 5.2 Repository Intelligence

- FR-006 The system shall inspect the configured workspace/repository before implementation.

- FR-007 The system shall provide file discovery and repository structure information.

- FR-008 The system shall support lexical code search.

- FR-009 The system shall support syntax/symbol-aware repository analysis where language support exists.

- FR-010 The system shall maintain a repository map containing relevant files, symbols, relationships, metadata, documentation, and change state.

- FR-011 The system shall support incremental invalidation/update of repository information.

## 5.3 Context

- FR-012 The system shall build task-relevant context from repository, task, Git, testing/error, and memory sources.

- FR-013 Context shall be ranked for relevance.

- FR-014 Context shall respect configured token/output budgets.

- FR-015 Context shall retain provenance.

- FR-016 Stale context shall be invalidated/rebuilt when relevant files change.

## 5.4 Planning & Code Changes

- FR-017 The system shall generate an implementation plan before execution when the task requires planning.

- FR-018 The plan shall identify expected files/changes and validation requirements.

- FR-019 Code changes shall preferably be represented as validated patches/diffs.

- FR-020 Patch application shall check file version/hash and detect conflicts.

- FR-021 The system shall support dry-run validation before mutation where applicable.

- FR-022 Actual changed files shall be compared against expected scope.

- FR-023 A reviewer step shall be available for scope/quality findings.

## 5.5 Tool System & Permissions

- FR-024 All AI-requested actions shall be represented as explicit tool requests.

- FR-025 Every tool request shall pass through the central Tool Gateway.

- FR-026 Every tool request shall be evaluated by the Policy/Permission Engine before execution.

- FR-027 Policy decisions shall support ALLOW, ASK, DENY, and RESTRICT outcomes.

- FR-028 Policy evaluation shall consider autonomy mode, tool, arguments, workspace/resource scope, and risk.

- FR-029 Built-in and MCP tools shall use the same policy path.

- FR-030 Tool execution shall return normalized structured results.

- FR-031 Important tool requests and policy decisions shall be auditable.

## 5.6 Terminal, Workspace & Sandbox

- FR-032 File/process/terminal side effects shall occur only through controlled executors.

- FR-033 The system shall support controlled PowerShell/process execution for the Windows-first MVP.

- FR-034 Workspace boundaries shall be explicitly enforced.

- FR-035 Protected paths and sensitive environment data shall be protected.

- FR-036 Process execution shall support practical timeout and output-size controls.

- FR-037 Destructive or sensitive operations shall be restricted or approval-controlled.

- FR-038 The execution layer shall expose a pluggable sandbox boundary.

## 5.7 Testing & Validation

- FR-039 The system shall discover or use configured project validation commands.

- FR-040 The system shall support lint, build, unit/integration/e2e validation as appropriate to the task.

- FR-041 Test/build/lint output, exit code, duration, stdout, and stderr shall be captured where applicable.

- FR-042 Validation results shall be stored as structured evidence.

- FR-043 The system shall implement a Completion Gate.

- FR-044 A task shall not be marked COMPLETE unless required validation gates pass.

## 5.8 Error Recovery

- FR-045 Validation failures shall be normalized into structured errors.

- FR-046 Failures shall be classified for recovery routing.

- FR-047 The system shall build relevant failure context for diagnosis.

- FR-048 The system shall support a repair-plan and repair-patch flow.

- FR-049 Repair attempts shall re-enter policy and patch validation before application.

- FR-050 Repair shall be bounded by configurable attempt/time/scope limits.

- FR-051 The system shall stop safely on unrecoverable or policy-blocked conditions.

- FR-052 Recovery attempts and outcomes shall be recorded.

## 5.9 Git & Change Safety

- FR-053 The system shall capture relevant Git baseline state.

- FR-054 The system shall provide status and diff information.

- FR-055 The system shall support task checkpoints and rollback.

- FR-056 Pre-existing unrelated user changes shall be detected and preserved.

- FR-057 Git commit behavior shall remain policy/approval-controlled.

- FR-058 The system shall never silently discard user changes.

## 5.10 Memory, Audit & Reporting

- FR-059 The system shall maintain task/project state.

- FR-060 The system shall support task, project, decision, failure, and session memory concepts.

- FR-061 Memory shall not override security policy.

- FR-062 The system shall maintain structured audit/activity events.

- FR-063 The system shall generate a final report containing changes and validation evidence.

- FR-064 The report shall identify result status, tests, retries/recovery, Git state, and relevant blockers/failures.

## 5.11 Clients & Extensibility

- FR-065 The core Agent Runtime shall operate independently of VS Code.

- FR-066 The system shall provide a CLI/headless path using the same runtime.

- FR-067 The VS Code client shall support task creation, plan display, approvals, diffs, progress, activity, cancellation, and final results.

- FR-068 The VS Code client shall not create a privileged parallel execution path.

- FR-069 The system shall support MCP through an adapter behind the Tool Gateway and Policy Engine.

- FR-070 The LLM integration shall use a provider abstraction so the runtime is not permanently coupled to one provider.

# 6. Non-Functional Requirements

| ID | Quality | Requirement |
| --- | --- | --- |
| NFR-001 Reliability | Deterministic state transitions, explicit failure states, bounded recovery, and evidence-based completion. |  |
| NFR-002 Security | Central policy boundary, workspace restrictions, protected secrets, controlled execution, and no unrestricted OS access by default. |  |
| NFR-003 Auditability | Important task, tool, policy, change, validation, recovery, Git, and completion events shall be observable. |  |
| NFR-004 Modularity | Core components shall have clear boundaries and independently testable interfaces. |  |
| NFR-005 Extensibility | LLM providers, tools, MCP, clients, and future multi-agent capabilities shall be replaceable/extensible. |  |
| NFR-006 Testability | Major capabilities shall have unit, integration, security, end-to-end, or evaluation tests as appropriate. |  |
| NFR-007 Performance | Repository indexing/context selection shall use incremental and budgeted approaches suitable for local projects. |  |
| NFR-008 User Control | Autonomy shall be configurable and policy-backed; high-risk actions shall not depend on prompt wording alone. |  |
| NFR-009 Recoverability | Changes shall be inspectable and reversible through diff/checkpoint mechanisms. |  |
| NFR-010 Portability | Core runtime shall not require VS Code and shall support CLI/headless operation. |  |

# 7. Safety, Security & Permission Requirements

- AI-to-OS access shall not be unrestricted; the model shall request capabilities through tools.

- Every tool, including MCP tools, shall pass through the same central policy boundary.

- Repository content shall be treated as untrusted data and shall not override security instructions.

- Secrets and credentials shall normally be unreadable to the agent unless an explicitly authorized mechanism exists.

- Destructive commands, production actions, live-system actions, live trading, and deployment shall receive special restrictions.

- The agent shall not be able to weaken or rewrite its own security policy through normal tools.

- Workspace boundaries shall be enforced below the prompt/rules layer.

- Important approvals and policy decisions shall be auditable.

- An emergency stop/cancellation capability shall be available for running execution.

- VS Code, model providers, memory, recovery, and MCP shall not create security bypass paths.

# 8. Autonomy Model

| Mode | Purpose | Default posture |
| --- | --- | --- |
| CHAT | Explain/discuss | No write/execute tools. |
| PLAN | Explore and plan | Read/search/Git-read capabilities; no mutation. |
| ASSISTED IMPLEMENT | Implement with user control | Safe reads automatic; writes/commands may ask. |
| SUPERVISED AUTO | Bounded task execution | Policy-approved low-risk actions automatic; risky actions ask. |
| AUTONOMOUS | Longer bounded execution | Still sandboxed and policy-bound; no unrestricted OS access. |
| RESTRICTED | Sensitive/production context | High-risk actions denied or approval-only. |

# 9. MVP Scope

The first milestone is a reliable local MVP, not a fully autonomous production agent.

## 9.1 In Scope

- Local workspace/repository.

- One independent Agent Runtime.

- One initial LLM provider behind a provider abstraction.

- Repository scan, search, repository map, and task-relevant context selection.

- Read/create/edit files through validated patches.

- Controlled PowerShell/terminal execution.

- Configured lint/build/test execution.

- Failure classification and bounded fix → retest.

- Git status/diff/checkpoint/rollback.

- Task progress, minimal project/task memory, and activity/audit log.

- Completion Gate and final report.

- CLI/headless execution as the core validation path.

- Basic VS Code client after runtime stability.

## 9.2 Deferred / Post-MVP

- Fully autonomous production deployment.

- Unrestricted computer/OS control.

- Live trading or other high-impact actions.

- Full multi-agent swarm/orchestration.

- Complex model routing.

- Broad cloud/remote execution.

- Advanced background autonomy.

- Large-scale distributed orchestration.

- Advanced semantic/vector retrieval unless evaluation proves it necessary.

- Enterprise-scale multi-project controls and advanced analytics.

# 10. Product Boundaries & Explicit Non-Goals

- The product is not an unrestricted computer-control agent.

- The product is not allowed to bypass the policy engine because the model requests an action.

- The product shall not treat project documentation or repository instructions as higher authority than security policy.

- The product shall not declare success based solely on generated code.

- The product shall not silently overwrite unrelated user changes.

- The product shall not make VS Code the only execution/runtime environment.

- The product shall not make any single researched open-source repository a mandatory runtime dependency.

- The product shall not introduce multi-agent complexity before the single-runtime MVP is reliable.

# 11. Completion / Definition of Product Success

For the MVP, the product succeeds when it can reliably execute the following chain on a representative local software project:

- Read and understand the repository.

- Normalize a human requirement and produce a plan.

- Identify expected files and dependencies.

- Create or edit code using validated changes.

- Run controlled commands and project validation.

- Read and classify failures.

- Generate and apply a bounded repair when permitted.

- Retest after repair.

- Preserve Git/user-change safety.

- Pass the required Completion Gate with recorded evidence.

- Produce a final report.

Hard rule: If required validation evidence is missing or failed, the task remains non-complete.

# 12. High-Level Product Architecture Requirement

The product shall be structured around an independent Agent Runtime with clients and controlled execution boundaries.

- Clients: VS Code, CLI, and future headless/API clients.

- Agent Runtime: Task Manager, Orchestrator, logical Planner/Coder/Reviewer roles, Context Engine, LLM Gateway, Tool Gateway, Policy Engine, Execution/Sandbox, Testing/Validation, Recovery, Git, Memory/Project State, Audit, and Reporting.

- Repository Intelligence: scanner, repository map, symbols/references, search, indexing, and task-aware retrieval.

- All external actions: Tool Registry → Tool Gateway → Policy Engine → authorized Executor.

- Completion: Validation Evidence → Completion Gate → Final Report.

- MCP: external/untrusted tool source behind the same Tool Gateway and Policy Engine.

# 13. Product Constraints

- Initial target environment is Windows with PowerShell and VS Code.

- Core runtime must be independently executable without VS Code.

- Security-sensitive capabilities must have strong isolation boundaries.

- Provider-specific implementations must remain behind adapters.

- Local MVP should avoid unnecessary cloud/distributed infrastructure.

- Technology and repository choices must remain replaceable where practical.

- Every major capability must have a test strategy.

- Changes to locked requirements/architecture require formal change control.

# 14. Dependencies & Related Locked Baselines

This PRD is the product-level baseline and feeds the downstream requirements, architecture, technology, repository, implementation, and task documents.

| Document | Relationship | Role |
| --- | --- | --- |
| SRS v1.0 | Derived from PRD | Detailed software requirements and acceptance expectations. |
| System Architecture v1.0 | Derived from requirements | Logical component and boundary design. |
| Technical Design v1.0 | Derived from architecture | Implementation-level technical design. |
| Agent Behaviour Specification v1.0 | Derived from product behavior | Defines agent operating behavior. |
| Tool & Permission Specification v1.0 | Derived from safety requirements | Defines tool and authorization behavior. |
| Memory & Context Specification v1.0 | Derived from context/state needs | Defines memory/context behavior. |
| Error Recovery Specification v1.0 | Derived from validation/recovery needs | Defines failure and repair behavior. |
| Testing & Validation Plan v1.0 | Derived from completion principle | Defines validation strategy and evidence. |
| Security & Sandbox Specification v1.0 | Derived from safety constraints | Defines security and isolation. |
| VS Code Integration Specification v1.0 | Derived from client requirements | Defines IDE integration boundary. |
| Master Architecture v1.0 | Consumes PRD/SRS and decisions | System architecture baseline. |
| Repository Blueprint v1.0 | Consumes architecture | Physical codebase structure baseline. |
| Technology Decision v1.0 | Consumes architecture | Implementation technology baseline. |
| Implementation Plan v1.0 | Consumes technology/architecture | Controlled build sequence. |
| Task Backlog v1.0 | Consumes implementation plan | Actionable engineering work breakdown. |

# 15. Requirements Traceability Principle

Every major implementation task should be traceable back to a product requirement, and every completion decision should be traceable forward to validation evidence. New requirements discovered during implementation shall not be silently inserted into existing tasks; they must be recorded through formal change control.

Traceability chain:

PRD → SRS → Architecture → Technical Design → Specifications → Technology → Implementation Plan → Task Backlog → Code → Tests → Evidence → Report

# 16. Release / MVP Acceptance Criteria

| ID | Acceptance area | Evidence |
| --- | --- | --- |
| A1 | Repository understanding | Repository scan/search/map tests pass. |
| A2 | Planning | A structured plan with acceptance criteria is produced. |
| A3 | Code change | Validated patch/diff evidence shows intended changes. |
| A4 | Controlled execution | Authorized commands execute and results are captured. |
| A5 | Validation | Required validation commands produce structured evidence. |
| A6 | Failure diagnosis | Failures are normalized/classified and fed into recovery. |
| A7 | Repair/retest | Bounded repair loop can fix and retest representative failures. |
| A8 | Safety | Policy/sandbox/security tests pass. |
| A9 | Git safety | Checkpoint/diff/rollback behavior is verified. |
| A10 | Reporting | Final report contains changes and validation evidence. |
| A11 | Completion integrity | No incomplete task can be reported as COMPLETE. |
| A12 | Client independence | Core loop works without VS Code. |

# 17. Risks & Product-Level Mitigation Requirements

| Risk | Severity | Required direction |
| --- | --- | --- |
| Prompt injection in repositories | High | Repository content is untrusted; security policy remains authoritative. |
| Unintended file modification | High | Expected scope, patch validation, hashes/conflict checks, diff review. |
| Dangerous terminal commands | High | Argument-aware policy, workspace restrictions, sandbox/executor controls. |
| Infinite repair loop | High | Retry/time/scope budgets and explicit stop states. |
| False completion | High | Hard Completion Gate with evidence. |
| Dirty Git conflicts | High | Baseline capture, unrelated-change detection, protected user changes. |
| MCP policy bypass | High | Single Tool Gateway for all tool sources. |
| Context explosion | Medium | Repository map, relevance ranking, provenance and token budgets. |
| Overengineering | Medium | Single runtime with logical roles for MVP; defer multi-agent complexity. |
| Model/provider variability | Medium | Provider abstraction and capability registry. |

# 18. Change Control

- Locked PRD requirements shall not be changed silently during implementation.

- Any new product requirement, removed requirement, or material scope change shall receive a change identifier and impact assessment.

- Changes affecting architecture, security boundaries, completion gates, or MVP scope require review before implementation.

- Task-level discoveries that do not change product scope should be recorded in the engineering backlog rather than altering this PRD.

# 19. Final Status

STATUS: FINAL / LOCKED — v1.0

This PRD establishes the authoritative product scope for the AI Software Co-Agent. Implementation must follow the downstream locked specifications, architecture, technology decisions, implementation plan, and task backlog derived from this baseline.

— END OF PRD v1.0 —
