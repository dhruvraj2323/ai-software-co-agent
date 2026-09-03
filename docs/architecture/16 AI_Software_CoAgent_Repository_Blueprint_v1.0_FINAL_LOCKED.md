AI SOFTWARE CO-AGENT

REPOSITORY BLUEPRINT

Version 1.0 — FINAL / LOCKED

Document ID: RBP-001 • Canonical repository and module organization baseline

| Field | Value |
| --- | --- |
| Document | Repository Blueprint |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Define the canonical repository structure, module boundaries, ownership, dependency direction, test layout, documentation layout and implementation conventions. |
| Authority | Physical organization is governed here; component behavior remains governed by the corresponding locked specifications. |
| Change policy | Material boundary or root-structure changes require formal versioned change control. |

Lock Statement: Repository Blueprint v1.0 is the final locked physical organization baseline for implementation. New code must fit the logical boundaries below; convenience must not create alternate authority paths.

# 1. Purpose & Design Principles

- Make the repository understandable to both developers and the Co-Agent.

- Keep control, security and execution boundaries explicit in the filesystem.

- Prevent circular dependencies and hidden side-effect paths.

- Keep client integrations separate from runtime authority.

- Keep tests close to the contracts/boundaries they validate.

- Keep research/external-source material separate from production code.

- Make documentation and implementation traceable.

- Prefer small cohesive modules over a single giant agent module.

- Keep external integrations behind adapters.

- Keep generated/build artifacts out of source directories.

# 2. Canonical Repository Tree

ai-software-co-agent/

├── README.md

├── LICENSE

├── CHANGELOG.md

├── CONTRIBUTING.md

├── SECURITY.md

├── pyproject.toml

├── .gitignore

├── .env.example

├── .github/

│ └── workflows/

│ ├── ci.yml

│ ├── security.yml

│ └── release.yml

│

├── docs/

│ ├── architecture/

│ ├── specifications/

│ ├── project/

│ ├── research/

│ ├── decisions/

│ └── operations/

│

├── src/

│ └── coagent/

│ ├── core/

│ ├── runtime/

│ ├── agent/

│ ├── models/

│ ├── context/

│ ├── memory/

│ ├── repository/

│ ├── workspace/

│ ├── tools/

│ ├── security/

│ ├── execution/

│ ├── git/

│ ├── validation/

│ ├── recovery/

│ ├── audit/

│ ├── artifacts/

│ ├── protocol/

│ └── config/

│

├── cli/

│ └── coagent_cli/

│

├── vscode-extension/

│ ├── package.json

│ ├── src/

│ ├── media/

│ └── tests/

│

├── tests/

│ ├── unit/

│ ├── contract/

│ ├── integration/

│ ├── security/

│ ├── behavior/

│ ├── recovery/

│ ├── e2e/

│ ├── fixtures/

│ └── performance/

│

├── scripts/

│ ├── dev/

│ ├── ci/

│ └── release/

│

├── configs/

│ ├── schemas/

│ ├── development/

│ └── examples/

│

└── artifacts/

├── test-results/

├── research/

├── audit/

└── release/

# 3. Root Directory Ownership

| Path | Owner | Purpose | Rule |
| --- | --- | --- | --- |
| src/ | Engineering | Production runtime/library | No client-only UI code. |
| cli/ | CLI team/module | Headless client | Must use runtime protocol. |
| vscode-extension/ | VS Code integration | IDE client | No privileged executor. |
| tests/ | Quality | Automated verification | Tests cannot weaken production controls. |
| docs/ | Architecture/Governance | Specifications and project records | Locked docs are immutable baselines. |
| configs/ | Configuration | Schemas/examples/env-specific config | No secrets. |
| scripts/ | Engineering/Ops | Developer/CI/release helpers | No hidden production authority. |
| artifacts/ | Quality/Ops | Generated evidence | Never treated as source authority. |
| .github/ | Engineering/Ops | CI/CD workflows | Security-sensitive changes reviewed. |

# 4. Production Package Map

| Package | Responsibility | Must not own |
| --- | --- | --- |
| core | Shared primitives, IDs, errors, common types | Business/tool authorization |
| runtime | Session/task lifecycle and orchestration coordination | Client UI |
| agent | Planning, behavior and task-loop logic | Direct OS execution |
| models | Model/provider abstraction | Tool authorization |
| context | Context assembly/ranking/budget | Security authorization |
| memory | Scoped memory persistence/retrieval | Permission decisions |
| repository | Repository map/search/symbol intelligence | Unscoped filesystem writes |
| workspace | Workspace scope/path operations | Policy ownership |
| tools | Tool definitions, registry, gateway and adapters | Direct bypass execution |
| security | Policy, scope, sandbox, secret/injection controls | Agent planning |
| execution | Authorized filesystem/process/patch execution | Client protocol |
| git | Controlled Git capabilities | Unreviewed destructive actions |
| validation | Checks, evidence and completion gates | Agent planning |
| recovery | Failure classification and bounded repair/retest | Policy override |
| audit | Structured events and audit records | Normal task authorization |
| artifacts | Bounded artifact storage/references | Unbounded model context |
| protocol | Typed client/runtime messages | Business logic |
| config | Schema validation and configuration loading | Secret storage |

# 5. Dependency Direction

core

↑

protocol / config / security primitives

↑

runtime ← agent ← context/memory/repository

↑

tools → security → execution/git/MCP

↑

validation → recovery → completion

↑

audit / artifacts

↑

cli / vscode-extension

Interpretation: arrows indicate dependency direction at the logical package level. Lower-level packages must not import higher-level clients. Cross-cutting services should depend on stable contracts rather than concrete clients.

# 6. Dependency Rules

- src/coagent/security must not depend on VS Code or CLI.

- src/coagent/execution must not depend on client UI.

- src/coagent/tools must route privileged operations through policy/security.

- src/coagent/agent must not invoke OS/process APIs directly.

- src/coagent/memory must not authorize tools.

- src/coagent/context must not mutate authorization state.

- src/coagent/repository may read through workspace-controlled interfaces.

- src/coagent/recovery must reuse normal Tool Gateway/Policy paths.

- vscode-extension and cli communicate through protocol/client APIs.

- Production modules should not import tests.

- Research documents never become runtime dependencies.

# 7. Core Package Details

| Package | Recommended files/modules |
| --- | --- |
| core | types.py, ids.py, errors.py, result.py, events.py |
| runtime | session.py, task.py, orchestrator.py, lifecycle.py |
| agent | planner.py, behavior.py, loop.py, policies.py |
| models | gateway.py, provider.py, messages.py, adapters/ |
| context | engine.py, providers.py, ranking.py, budget.py, manifest.py |
| memory | manager.py, store.py, records.py, provenance.py |
| repository | map.py, search.py, symbols.py, index.py |
| workspace | manager.py, scope.py, paths.py, changes.py |
| tools | definitions.py, registry.py, gateway.py, requests.py, results.py, mcp/ |
| security | policy.py, decisions.py, scope.py, sandbox.py, secrets.py, injection.py |
| execution | filesystem.py, process.py, patch.py, limits.py |
| git | adapter.py, status.py, diff.py, operations.py |
| validation | runner.py, checks.py, evidence.py, completion.py |
| recovery | classifier.py, controller.py, budgets.py, strategies.py |
| audit | events.py, recorder.py, filters.py |
| artifacts | store.py, refs.py, limits.py |
| protocol | messages.py, requests.py, events.py, versions.py |
| config | schema.py, loader.py, models.py, validation.py |

# 8. Control Plane Layout

src/coagent/runtime/

session.py

task.py

orchestrator.py

lifecycle.py

src/coagent/tools/

gateway.py

registry.py

definitions.py

src/coagent/security/

policy.py

decisions.py

scope.py

sandbox.py

src/coagent/validation/

runner.py

completion.py

src/coagent/recovery/

controller.py

Control-plane rule: There must be no second hidden implementation of task authority, policy authority or completion authority elsewhere in the repository.

# 9. Tool Architecture Layout

tools/

├── definitions.py # canonical capability contracts

├── registry.py # registered capabilities

├── gateway.py # mandatory routing boundary

├── requests.py # typed requests

├── results.py # typed results

├── native/

│ ├── filesystem.py

│ ├── process.py

│ ├── patch.py

│ └── git.py

└── mcp/

├── adapter.py

├── server.py

└── result_filter.py

Native and MCP tools are implementation providers. Both must enter the same authorization path.

# 10. Security Architecture Layout

security/

├── policy.py # policy evaluation

├── decisions.py # ALLOW/ASK/DENY/RESTRICT

├── scope.py # canonical resource scope

├── sandbox.py # execution isolation controls

├── secrets.py # secret filtering/protection

├── injection.py # untrusted-content controls

├── approval.py # approval lifecycle

└── limits.py # resource/time/concurrency limits

- Security modules are dependency-minimal.

- Security code must not import model-specific code.

- Security failures fail closed for affected privileged operations.

- Security tests have dedicated repository ownership under tests/security/.

# 11. Validation & Recovery Layout

validation/

├── runner.py

├── checks.py

├── results.py

├── evidence.py

└── completion.py

recovery/

├── classifier.py

├── controller.py

├── budgets.py

├── strategies.py

└── state.py

- Completion is decided only in validation/completion.

- Recovery cannot directly mark completion.

- Recovery actions use Tool Gateway.

- Validation evidence is persisted/referenced through artifacts.

# 12. Tests Blueprint

| Test area | Location | Primary target |
| --- | --- | --- |
| Unit | tests/unit/ | Pure component behavior |
| Contract | tests/contract/ | Typed protocol/tool/schema contracts |
| Integration | tests/integration/ | Subsystem boundaries |
| Security | tests/security/ | Policy, sandbox, scope, secrets, injection |
| Behavior | tests/behavior/ | Agent lifecycle/invariants |
| Recovery | tests/recovery/ | Failure/recovery/retest |
| E2E | tests/e2e/ | Realistic software tasks |
| Fixtures | tests/fixtures/ | Controlled repositories/workspaces |
| Performance | tests/performance/ | Latency/resource/context benchmarks |
| VS Code | vscode-extension/tests/ | Client behavior/protocol/UI integration |

# 13. Canonical Test Naming

test_<component>_<scenario>_<expected>.py

Examples:

test_policy_denied_tool_is_blocked.py

test_workspace_traversal_is_rejected.py

test_completion_missing_evidence_is_rejected.py

test_recovery_budget_stops_repeated_failure.py

test_client_reconnect_does_not_replay_side_effect.py

# 14. Documentation Blueprint

docs/

├── architecture/

│ ├── MASTER_ARCHITECTURE_v1.0.md

│ └── ARCHITECTURE_DECISION_MATRIX_v1.0.md

├── specifications/

│ ├── PRD_v1.0.md

│ ├── SRS_v1.0.md

│ ├── TECHNICAL_DESIGN_v1.0.md

│ ├── AGENT_BEHAVIOUR_v1.0.md

│ ├── TOOL_PERMISSION_v1.0.md

│ ├── MEMORY_CONTEXT_v1.0.md

│ ├── ERROR_RECOVERY_v1.0.md

│ ├── TESTING_VALIDATION_v1.0.md

│ ├── SECURITY_SANDBOX_v1.0.md

│ └── VSCODE_INTEGRATION_v1.0.md

├── project/

│ └── PROJECT_PLAN_PROGRESS_v1.0.md

├── research/

│ └── RESEARCH_SYNTHESIS_v1.0.md

└── decisions/

└── ADR-*.md

# 15. Documentation Authority Rules

- Locked specifications are read-only baselines in normal implementation work.

- Implementation docs may link to specifications but cannot redefine them.

- Architecture Decision Records document new decisions or approved changes.

- Research notes remain separate from authoritative specifications.

- Generated reports are stored under artifacts, not docs/specifications.

- Version numbers must match the approved baseline.

# 16. Configuration Blueprint

configs/

├── schemas/

│ ├── agent.schema.json

│ ├── tools.schema.json

│ ├── policy.schema.json

│ └── project.schema.json

├── development/

│ └── example.yaml

└── examples/

└── minimal.yaml

- No credentials or API keys in configs/.

- Schema validation occurs before runtime activation.

- Hard security policy cannot be weakened through project config.

- Environment-specific secrets belong in approved secret/environment mechanisms.

# 17. CLI Blueprint

cli/coagent_cli/

├── __init__.py

├── main.py

├── commands/

│ ├── run.py

│ ├── task.py

│ ├── status.py

│ └── config.py

├── client.py

└── rendering.py

- CLI is a protocol client.

- CLI does not import execution internals for privileged actions.

- Headless mode uses the same runtime state and policy.

# 18. VS Code Blueprint

vscode-extension/

├── package.json

├── tsconfig.json

├── src/

│ ├── extension.ts

│ ├── client/

│ ├── protocol/

│ ├── chat/

│ ├── approval/

│ ├── diff/

│ ├── diagnostics/

│ ├── status/

│ └── state/

├── media/

└── tests/

- Extension communicates with runtime through protocol/client modules.

- UI state is not authoritative.

- Approval UI submits approval responses; runtime makes final policy decision.

# 19. Scripts Blueprint

scripts/

├── dev/

│ ├── bootstrap.py

│ └── run_local.py

├── ci/

│ ├── verify.py

│ ├── security_scan.py

│ └── test_all.py

└── release/

├── build.py

├── package.py

└── verify_release.py

- Scripts are convenience/automation layers, not alternate runtime authorities.

- Release scripts must validate artifacts before publication.

# 20. Naming & Coding Conventions

| Area | Convention |
| --- | --- |
| Python modules | snake_case |
| Classes | PascalCase |
| Functions | snake_case |
| Constants | UPPER_SNAKE_CASE |
| IDs | Stable prefixed identifiers where useful |
| Tests | Behavior-oriented descriptive names |
| Interfaces | Explicit protocol/abstract contracts |
| Adapters | Named by external system/capability |
| Security-sensitive methods | Explicitly documented and tested |
| Public APIs | Typed and versioned where externally consumed |

# 21. Import Boundary Rules

- Client packages may import protocol/client-facing types, not executors.

- Agent packages may import tools through interfaces, not concrete OS adapters.

- Security packages should expose narrow decisions/interfaces.

- Execution packages may consume approved policy decisions but must independently enforce hard limits.

- Audit may receive events from all layers but should not become an authorization dependency.

- Artifacts may be referenced by validation/audit but should not become a hidden state authority.

- Tests may use fixtures/helpers but must not monkeypatch away security boundaries in release suites.

# 22. Interface Boundary Rules

| Boundary | Interface |
| --- | --- |
| Client ↔ Runtime | Versioned Client Protocol |
| Agent ↔ Tools | ToolRequest / ToolResult |
| Tools ↔ Policy | PolicyRequest / PolicyDecision |
| Policy ↔ Approval | ApprovalRequest / ApprovalResult |
| Runtime ↔ Model | ModelGateway interface |
| Context ↔ Providers | ContextProvider interface |
| Memory ↔ Storage | MemoryStore interface |
| Repository ↔ Workspace | Scoped repository access interface |
| Execution ↔ Sandbox | ExecutionPolicy / Sandbox interface |
| Validation ↔ Completion | ValidationEvidence / CompletionDecision |
| Recovery ↔ Validation | RecoveryPlan / RetestResult |
| Runtime ↔ Audit | EventEnvelope |
| Runtime ↔ Artifacts | ArtifactRef |

# 23. Generated & Ignored Files

- Build output belongs outside source packages.

- Python caches, virtual environments, node_modules and editor metadata are ignored.

- Runtime logs are not committed by default.

- Secrets and local configuration are never committed.

- Generated test/evidence artifacts are stored under artifacts/ or CI storage.

- Large binaries require explicit repository policy.

# 24. Repository Security Rules

- SECURITY.md is maintained at repository root.

- Security-sensitive modules require dedicated tests.

- Dependency scanning runs in CI.

- Secrets scanning runs in CI.

- Production dependencies are reviewed before introduction.

- CI must not expose secrets in logs.

- Pull requests changing policy/sandbox/execution require security review.

- Release artifacts are verified before publication.

# 25. Development Workflow

ISSUE / WORK ITEM

↓

SPEC REFERENCE

↓

IMPLEMENT IN OWNED MODULE

↓

UNIT / CONTRACT TEST

↓

INTEGRATION TEST

↓

SECURITY TEST IF APPLICABLE

↓

REVIEW / DIFF

↓

PHASE GATE

↓

MERGE

# 26. Repository-to-Spec Traceability

| Specification | Primary repository locations |
| --- | --- |
| PRD / SRS | docs/specifications/ + tests/acceptance where used |
| System Architecture | docs/architecture/ + src/coagent/ |
| Technical Design | docs/architecture/ + src/coagent/* |
| Agent Behaviour | src/coagent/agent/ + tests/behavior/ |
| Tool & Permission | src/coagent/tools/ + src/coagent/security/ + tests/security/ |
| Memory & Context | src/coagent/context/ + src/coagent/memory/ |
| Error Recovery | src/coagent/recovery/ + tests/recovery/ |
| Testing & Validation | src/coagent/validation/ + tests/ |
| Security & Sandbox | src/coagent/security/ + src/coagent/execution/ + tests/security/ |
| VS Code Integration | vscode-extension/ + src/coagent/protocol/ |
| Project Plan | docs/project/ + progress artifacts |
| Research Synthesis | docs/research/ + research artifacts |
| Architecture Decision Matrix | docs/architecture/ + ADRs |
| Master Architecture | docs/architecture/ + all mapped production packages |

# 27. Implementation Sequence by Repository Area

| Order | Area | Reason |
| --- | --- | --- |
| 1 | core + config + protocol primitives | Stable contracts first |
| 2 | security + workspace | Establish safety boundary |
| 3 | tools + policy + approval | Establish capability control |
| 4 | execution + git + patch | Controlled side effects |
| 5 | repository + context + memory | Software understanding |
| 6 | agent + runtime | Orchestrated intelligence |
| 7 | validation + recovery + completion | Correctness and resilience |
| 8 | audit + artifacts | Evidence/traceability |
| 9 | CLI + VS Code | Client surfaces |
| 10 | E2E/performance/security hardening | Release readiness |

# 28. Repository Invariants

- RB1: There is one production source tree for the runtime.

- RB2: Client code is physically separated from runtime execution code.

- RB3: Security and policy code has no client dependency.

- RB4: Agent code cannot directly invoke OS/process APIs.

- RB5: Privileged tools route through Tool Gateway and Policy.

- RB6: MCP lives behind the tools boundary.

- RB7: Completion logic has one authoritative home.

- RB8: Recovery has one authoritative controller.

- RB9: Tests have explicit security/recovery/E2E areas.

- RB10: Research material cannot become runtime authority.

- RB11: Generated artifacts cannot become source-of-truth configuration.

- RB12: External integrations use adapters.

- RB13: Configuration contains no secrets.

- RB14: Repository structure must remain traceable to the Master Architecture.

- RB15: Material root/module boundary changes require versioned change control.

# 29. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| RB-A01 | Root tree | Canonical repository structure is defined. |
| RB-A02 | Ownership | Root directories have explicit ownership/rules. |
| RB-A03 | Modules | Production package responsibilities are explicit. |
| RB-A04 | Dependencies | Dependency direction and forbidden dependencies are defined. |
| RB-A05 | Security | Security modules and tests are isolated/traceable. |
| RB-A06 | Tools | Tool Gateway and policy boundaries are represented. |
| RB-A07 | Execution | Execution modules are separated from clients/agent logic. |
| RB-A08 | Context | Context/memory are separate from authorization. |
| RB-A09 | Validation | Validation/completion/recovery structure is explicit. |
| RB-A10 | Clients | VS Code and CLI are protocol clients. |
| RB-A11 | Testing | Test categories and naming are defined. |
| RB-A12 | Docs | Specification/research/project documentation is organized. |
| RB-A13 | Traceability | Repository areas map to locked specifications. |
| RB-A14 | Invariants | Repository invariants are explicit. |
| RB-A15 | Change control | Material structural changes require versioned control. |

# 30. Traceability to Locked Baselines

| Baseline | Repository Blueprint role |
| --- | --- |
| 01 PRD v1.0 | Provides product scope context for implementation organization. |
| 02 SRS v1.0 | Maps requirements to modules/tests. |
| 03 System Architecture v1.0 | Defines logical boundaries reflected physically here. |
| 04 Technical Design v1.0 | Drives package/interface decomposition. |
| 05 Agent Behaviour v1.0 | Maps behavior to agent/runtime/tests. |
| 06 Tool & Permission v1.0 | Maps tool/policy/security packages. |
| 07 Memory & Context v1.0 | Maps context/memory packages and tests. |
| 08 Error Recovery v1.0 | Maps recovery package and recovery tests. |
| 09 Testing & Validation v1.0 | Maps validation and test hierarchy. |
| 10 Security & Sandbox v1.0 | Maps security/execution boundaries. |
| 11 VS Code Integration v1.0 | Maps extension/protocol/client separation. |
| 12 Project Plan & Progress v1.0 | Defines repository implementation sequence. |
| 13 Research Synthesis v1.0 | Defines external integration/adaptation discipline. |
| 14 Architecture Decision Matrix v1.0 | Constrains structural decisions. |
| 15 Master Architecture v1.0 | Provides the master component map this blueprint implements. |

# 31. Final Change Control

- Adding a root directory requires architecture/repository review.

- Moving a security boundary requires security + architecture review.

- Creating a second Tool Gateway or Policy Engine is prohibited.

- Creating a second Completion Gate is prohibited.

- Moving client code into runtime execution packages requires architecture review.

- Changing dependency direction requires impact analysis.

- Future structural changes create Repository Blueprint v1.1+; v1.0 remains immutable.

# 32. Final Status

STATUS: FINAL / LOCKED — v1.0

Repository Blueprint v1.0 is the canonical physical organization baseline for implementing the AI Software Co-Agent. It translates the Master Architecture into repository boundaries, production packages, test structure, documentation structure, client separation, security boundaries, dependency rules, traceability and structural invariants.

— END OF REPOSITORY BLUEPRINT v1.0 —
