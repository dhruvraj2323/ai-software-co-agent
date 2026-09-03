AI SOFTWARE CO-AGENT

TECHNOLOGY DECISIONS

Version 1.0 — FINAL / LOCKED

Document ID: TDM-001 • Technology selection and adoption baseline

| Field | Value |
| --- | --- |
| Document | Technology Decisions |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Lock technology-selection principles, default implementation choices, adapters, evaluation criteria and deferred selections without coupling architecture to vendors. |
| Authority | Technology choices must satisfy Master Architecture, Architecture Decision Matrix, Security/Sandbox and Testing/Validation. |
| Change policy | Material technology changes require compatibility, security, performance and migration review. |

Lock Statement: Technology Decisions v1.0 is the final locked technology-selection baseline. It intentionally locks architectural technology principles and implementation defaults while keeping provider-specific choices replaceable where evidence is still required.

# 1. Technology Mission

Technology is selected to serve the locked architecture, not to define it. The Co-Agent must remain replaceable at provider, client, storage, sandbox and external-integration boundaries. Core security and control-plane semantics must remain internally owned and testable.

Primary principle: Choose boring, typed, testable and replaceable technology for the core; use specialized frameworks only where measurable benefit justifies the dependency.

# 2. Technology Selection Criteria

- Security and isolation.

- Correctness and deterministic behavior where practical.

- Typed interfaces and schema validation.

- Testability and observability.

- Performance under representative repository workloads.

- Maintainability and ecosystem health.

- License compatibility.

- Operational simplicity.

- Portability across supported developer environments.

- Replaceability through adapters.

- Documentation quality.

- Failure behavior and recovery characteristics.

# 3. Technology Decision Status

| Status | Meaning |
| --- | --- |
| LOCKED | Required architectural technology principle/default. |
| DEFAULT | Preferred v1 implementation unless evidence shows a material issue. |
| CONDITIONAL | Allowed only after stated evaluation/constraints. |
| DEFERRED | Must be benchmarked/decided later; do not hard-code assumptions. |
| REJECTED | Not permitted for the v1 architecture. |

# 4. Master Technology Decision Matrix

| ID | Area | Decision | Status | Reason |
| --- | --- | --- | --- | --- |
| TD-001 | Primary runtime language | Python 3.12+ target; pin exact supported minor/patch in project tooling | DEFAULT | Fast iteration, strong ecosystem, suitable for orchestration/integration; final pin validated in P0. |
| TD-002 | Type system | Python type hints + strict static checking | LOCKED | Contracts must be explicit. |
| TD-003 | Data validation | Pydantic v2-style typed models for runtime/config boundaries | DEFAULT | Schema validation and serialization; benchmark/confirm before final dependency pin. |
| TD-004 | Package/build | pyproject.toml with modern standards-based build tooling | LOCKED | Single canonical Python project configuration. |
| TD-005 | Testing | pytest + coverage tooling | DEFAULT | Mature test ecosystem and fixture support. |
| TD-006 | Lint/format | Ruff or equivalent single-tool baseline | DEFAULT | Fast consistent quality checks; exact version pinned. |
| TD-007 | Static type checking | mypy or pyright; choose one canonical checker in P0 | CONDITIONAL | Avoid duplicate type systems. |
| TD-008 | Client protocol | Versioned typed JSON/JSONL or equivalent message protocol over local IPC/transport | LOCKED | Client/runtime independence. |
| TD-009 | Schema format | JSON Schema for externally inspectable configuration/protocol schemas where useful | DEFAULT | Interoperability. |
| TD-010 | VS Code | TypeScript + official VS Code Extension API | LOCKED | Primary client. |
| TD-011 | CLI | Python CLI using same runtime protocol | LOCKED | No second runtime. |
| TD-012 | Model gateway | Internal provider adapter interface | LOCKED | Provider replaceability. |
| TD-013 | LLM provider | Provider-specific SDK/API selected by benchmark and operational need | DEFERRED | No provider lock-in in v1 architecture. |
| TD-014 | Context storage | Internal ContextProvider/Store interfaces; concrete storage selected by workload | LOCKED | Architecture independent of storage vendor. |
| TD-015 | Vector search | Optional, benchmark-driven; not mandatory for v1 core | CONDITIONAL | Avoid premature vector dependency. |
| TD-016 | Primary persistence | SQLite/local transactional store acceptable for v1 where persistence is required | DEFAULT | Simple local deployment; scale path remains adapterized. |
| TD-017 | Database abstraction | Repository/store interfaces around persistence | LOCKED | Future storage replacement. |
| TD-018 | Sandbox | OS/container/process isolation behind internal Sandbox interface | LOCKED | Defense in depth. |
| TD-019 | Container | Docker/OCI-compatible runtime may be used for stronger isolation | CONDITIONAL | Deployment/security evaluation required. |
| TD-020 | MCP | Internal MCP adapter using MCP-compatible client implementation | LOCKED | External tools remain behind policy. |
| TD-021 | Git | Git CLI/library adapter behind internal Git interface | LOCKED | Provider/implementation replaceability. |
| TD-022 | IPC/process transport | Local process/IPC transport selected for v1 runtime-client deployment | DEFAULT | Simple local architecture. |
| TD-023 | Async execution | asyncio for concurrent I/O; bounded task concurrency | DEFAULT | Fits tool/model/IPC workloads. |
| TD-024 | Logging | Structured Python logging/events with redaction layer | LOCKED | Audit and secret safety. |
| TD-025 | Metrics | OpenTelemetry-compatible abstraction optional for v1; internal event model mandatory | CONDITIONAL | Avoid provider lock-in. |
| TD-026 | Secrets | Environment/OS secret store integration; never repository config | LOCKED | Credential safety. |
| TD-027 | Configuration | YAML/JSON/TOML accepted only through typed schema layer; canonical runtime representation typed | DEFAULT | Human-editable + validated. |
| TD-028 | Serialization | JSON for protocol/interchange unless binary is justified | DEFAULT | Debuggability/interoperability. |
| TD-029 | Caching | Explicit scoped caches with TTL/invalidation | LOCKED | No hidden stale authority. |
| TD-030 | Search/index | Ripgrep/filesystem/symbol adapters as appropriate; internal interface | DEFAULT | Repository intelligence. |
| TD-031 | Embeddings | Deferred until benchmark proves value | DEFERRED | Not required for deterministic baseline. |
| TD-032 | Browser automation | Separate optional capability adapter | CONDITIONAL | High-risk external side effect. |
| TD-033 | Web UI framework | Not part of v1 core | REJECTED | VS Code/CLI are primary clients. |
| TD-034 | Microservices | Not required for v1 local runtime | REJECTED | Avoid distributed complexity. |
| TD-035 | Kubernetes | Not required for v1 developer-local deployment | REJECTED | Operational overhead not justified. |
| TD-036 | Message broker | Not required for v1 local runtime | REJECTED | Direct typed runtime protocol is sufficient. |
| TD-037 | Agent framework | No framework owns the core control plane | LOCKED | Internal contracts remain authoritative. |
| TD-038 | Graph orchestration | Internal explicit state machine preferred; framework optional later | DEFAULT | Understandability/control. |
| TD-039 | Multi-agent framework | Deferred until bounded multi-agent benchmark | DEFERRED | Single-agent core first. |
| TD-040 | Dependency management | Pinned/constraint-managed production dependencies + automated update review | LOCKED | Reproducibility/security. |

# 5. Recommended v1 Technology Stack

| Layer | Recommended v1 | Status |
| --- | --- | --- |
| Runtime | Python 3.12+ | DEFAULT |
| Types/contracts | typing + Pydantic-style models | DEFAULT |
| Build/package | pyproject.toml | LOCKED |
| Tests | pytest | DEFAULT |
| Quality | Ruff + one static type checker | DEFAULT |
| Runtime protocol | Versioned JSON/JSONL typed messages | LOCKED |
| IDE client | TypeScript + VS Code API | LOCKED |
| CLI | Python | LOCKED |
| Async | asyncio | DEFAULT |
| Persistence | SQLite behind repository interfaces | DEFAULT |
| Config | Schema-validated YAML/JSON/TOML | DEFAULT |
| Search | Filesystem/ripgrep/symbol adapters | DEFAULT |
| Git | Internal adapter around Git implementation | LOCKED |
| MCP | Internal MCP adapter | LOCKED |
| Sandbox | Sandbox interface + platform/container implementation | LOCKED |
| Observability | Structured events/audit; telemetry adapter optional | LOCKED |
| Secrets | OS/environment secret mechanisms | LOCKED |

# 6. What Is Intentionally NOT Locked

- Specific LLM provider/model.

- Exact embedding model.

- Exact vector database.

- Exact remote database.

- Exact container runtime beyond supported sandbox contract.

- Exact telemetry backend.

- Exact MCP server set.

- Exact multi-agent framework.

- Cloud deployment platform.

- Paid SaaS dependency for core operation.

These choices are deliberately deferred so that implementation evidence—not popularity—determines adoption.

# 7. Technology Boundary Architecture

INTERNAL CONTRACTS

│

┌───────────────────┼───────────────────┐

▼ ▼ ▼

Model Adapter Storage Adapter Sandbox Adapter

│ │ │

Provider SDK/API SQLite/other DB OS/container

┌───────────────────┼───────────────────┐

▼ ▼ ▼

Git Adapter MCP Adapter Telemetry Adapter

│ │ │

Git impl MCP server(s) OTel/backend

Boundary rule: External technology must not leak its assumptions into the control-plane contracts.

# 8. Technology Selection Workflow

NEED

↓

ARCHITECTURE CONSTRAINTS

↓

SHORTLIST

↓

SECURITY + LICENSE REVIEW

↓

FUNCTIONAL FIT TEST

↓

PERFORMANCE / RELIABILITY BENCHMARK

↓

OPERABILITY REVIEW

↓

ADOPT / ADAPT / DEFER / REJECT

↓

PIN VERSION

↓

RECORD DECISION

# 9. Dependency Governance

- Every production dependency has a purpose.

- Direct dependencies are preferred over unnecessary transitive reliance.

- Versions are pinned or constrained reproducibly.

- Security advisories are monitored.

- License information is recorded.

- Unused dependencies are removed.

- High-risk dependencies require explicit review.

- Framework upgrades must pass the affected test suites.

- External code copied into the repository requires separate license/security review.

# 10. LLM/Model Technology Strategy

- Model access is isolated behind ModelGateway.

- Provider-specific SDKs stay inside adapters.

- Model output is treated as untrusted proposal data.

- Tool authorization never depends on provider-specific features.

- Prompt/context construction remains internal.

- Model selection is benchmarked using representative coding tasks.

- Track quality, latency, context capacity, cost and failure modes.

- Use fallback only when fallback behavior is explicitly safe and authorized.

# 11. Model Evaluation Matrix

| Metric | Required evaluation |
| --- | --- |
| Task success | Correct implementation on representative tasks |
| Validation pass | Tests/lint/type checks after change |
| False completion | Must remain near zero; release-critical |
| Tool correctness | Appropriate tool selection/arguments |
| Recovery | Ability to diagnose and repair bounded failures |
| Context efficiency | Useful result within context budget |
| Latency | End-to-end task/tool/model timing |
| Cost | Token/API/runtime cost per task |
| Security | Injection/bypass resistance |
| Stability | Repeated-run consistency |

# 12. Storage & Memory Technology Strategy

- Use interfaces for memory and persistence.

- SQLite is the v1 default for local durable state where needed.

- Do not make vector search a prerequisite for core operation.

- Memory records require scope/provenance/freshness metadata.

- Large artifacts remain outside ordinary memory payloads.

- Storage failures must not create authorization failures that default to ALLOW.

- Migration paths are required before changing durable schemas.

# 13. Search & Repository Intelligence Strategy

| Need | Technology direction |
| --- | --- |
| Filename/content search | Fast local search adapter, e.g. ripgrep/filesystem |
| Symbol search | Language-aware/index adapter |
| Repository map | Internal repository index abstraction |
| Diff | Git/native diff adapter |
| Large repo handling | Incremental indexing + bounded context |
| Semantic retrieval | Optional embedding/vector adapter after benchmark |

The architecture must function for ordinary repository navigation without requiring semantic/vector infrastructure.

# 14. Sandbox Technology Strategy

- Define internal Sandbox interface first.

- Implement platform-appropriate process/resource controls.

- Use container isolation where deployment/security evaluation supports it.

- Apply workspace, network, environment, timeout and resource restrictions independently.

- Do not treat a container as the sole security control.

- Sandbox failure blocks operations that require the missing guarantee.

# 15. Protocol Technology Strategy

Client → Runtime

Request {version, request_id, session_id, task_id, type, payload}

Runtime → Client

Event {version, event_id, request_id, session_id, task_id, type, payload}

Rules:

- schema validation

- correlation IDs

- version compatibility

- bounded payloads

- explicit error envelopes

- no privileged semantics hidden in UI-only messages

# 16. Configuration Technology Strategy

- Canonical configuration becomes typed internal objects after validation.

- User/project configuration is lower authority than hard security policy.

- Environment-specific values remain separate from source-controlled defaults.

- Secrets are never stored in repository configuration.

- Invalid configuration fails safely before privileged operations begin.

- Configuration migrations are versioned.

# 17. Observability Technology Strategy

| Capability | v1 requirement |
| --- | --- |
| Structured events | MANDATORY |
| Correlation IDs | MANDATORY |
| Audit trail | MANDATORY for material actions |
| Redaction | MANDATORY |
| Metrics backend | OPTIONAL |
| Distributed tracing backend | OPTIONAL |
| Local diagnostics | MANDATORY |
| Evidence artifacts | MANDATORY for validation/release |

# 18. Technology Alternatives Matrix

| Area | Preferred | Alternative | Decision |
| --- | --- | --- | --- |
| Runtime | Python | TypeScript/Go | Python default; alternatives only with architecture evidence. |
| Protocol | JSON/JSONL | gRPC/MessagePack | JSON/JSONL default; binary later if measured need. |
| Persistence | SQLite | PostgreSQL | SQLite v1 local; PostgreSQL later if scale requires. |
| Sandbox | Internal interface + platform/container | Container-only | Defense-in-depth; no container-only dependency. |
| Search | Filesystem/ripgrep adapters | Dedicated search service | Local first; service only if benchmark requires. |
| Vector | None initially | Qdrant/pgvector/etc. | Deferred. |
| Orchestration | Internal state machine | LangGraph/etc. | Internal default; framework optional. |
| Multi-agent | Internal bounded abstraction | AutoGen/MetaGPT/etc. | Deferred. |
| Telemetry | Internal events | OpenTelemetry backend | Internal events mandatory; backend optional. |
| Client | VS Code + CLI | Web UI | Web UI rejected for v1 core. |

# 19. Technology Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Provider lock-in | High | ModelGateway adapter + benchmark-based selection |
| Framework lock-in | High | Internal contracts/state machine |
| Dependency vulnerability | Critical | Scanning, pinning, update review |
| License incompatibility | High | License review before adoption |
| Sandbox weakness | Critical | Defense-in-depth + dedicated tests |
| Storage migration pain | Medium | Repository interfaces + schema versioning |
| Context technology overbuild | Medium | Start deterministic; benchmark vector needs |
| Performance regression | Medium | Representative benchmarks in P10 |
| Protocol drift | High | Versioned schemas + contract tests |
| Client/runtime coupling | High | Protocol boundary + dependency rules |

# 20. Technology Decision Gates

| Gate | Required before |
| --- | --- |
| T0 | Adding any production dependency |
| T1 | Selecting model/provider |
| T2 | Selecting persistence implementation beyond default |
| T3 | Enabling semantic/vector retrieval |
| T4 | Enabling remote/network capability |
| T5 | Introducing a framework into core control plane |
| T6 | Introducing multi-agent framework |
| T7 | Changing sandbox implementation |
| T8 | Changing client/runtime protocol |
| T9 | Release dependency update with security/behavior impact |

# 21. Technology Test Requirements

- Dependency imports/build must be reproducible.

- Security-sensitive dependencies have vulnerability checks.

- Protocol implementations pass contract tests.

- Adapters pass conformance tests against internal interfaces.

- Sandbox implementations pass escape/resource tests.

- Storage adapters pass persistence/migration tests.

- Model adapters pass gateway contract tests.

- MCP adapter passes policy-boundary tests.

- Client builds pass protocol compatibility tests.

- Performance-sensitive technology choices pass benchmark gates.

# 22. Technology-to-Repository Mapping

| Technology area | Repository location |
| --- | --- |
| Python/runtime | pyproject.toml + src/coagent/ |
| Type/schema | src/coagent/core/ + protocol/ + config/ |
| Model SDKs | src/coagent/models/adapters/ |
| Persistence | src/coagent/memory/store/ or repository store adapters |
| Sandbox | src/coagent/security/sandbox/ + execution/ |
| MCP | src/coagent/tools/mcp/ |
| Git | src/coagent/git/ |
| Search | src/coagent/repository/ |
| Protocol | src/coagent/protocol/ |
| CLI | cli/coagent_cli/ |
| VS Code | vscode-extension/ |
| Tests | tests/ |
| Dependency reviews | docs/research/dependency-reviews/ |
| Technology ADRs | docs/decisions/ |

# 23. Locked Technology Invariants

- TDI1: Core architecture is not vendor-owned.

- TDI2: External providers are behind replaceable adapters.

- TDI3: Security controls are internally owned and independently testable.

- TDI4: No framework may become the authorization authority.

- TDI5: No model provider may define tool permissions.

- TDI6: Core operation must not require vector search.

- TDI7: Client technology cannot bypass runtime boundaries.

- TDI8: Protocols are typed/versioned and contract-tested.

- TDI9: Production dependencies require reproducible version management.

- TDI10: Secrets never belong in source-controlled configuration.

- TDI11: Sandbox is defense-in-depth, not a single technology dependency.

- TDI12: Observability uses a stable internal event model.

- TDI13: Technology adoption requires security/license review where applicable.

- TDI14: Deferred technologies cannot be treated as hidden prerequisites.

- TDI15: Material technology changes require formal change control.

# 24. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| TD-A01 | Stack | v1 defaults and status are explicitly defined. |
| TD-A02 | Replaceability | Provider/storage/sandbox integrations use adapters. |
| TD-A03 | Runtime | Runtime technology does not bypass architecture. |
| TD-A04 | Protocol | Typed/versioned protocol technology is defined. |
| TD-A05 | Security | Security technology is independent and testable. |
| TD-A06 | Dependencies | Dependency governance is explicit. |
| TD-A07 | LLM | Model provider is not hard-wired into core. |
| TD-A08 | Storage | Persistence is interface-driven and migration-aware. |
| TD-A09 | Sandbox | Sandbox technology is defense-in-depth. |
| TD-A10 | MCP | MCP remains behind internal adapter/policy. |
| TD-A11 | Clients | VS Code/CLI remain protocol clients. |
| TD-A12 | Testing | Technology choices have test requirements. |
| TD-A13 | Risks | Major technology risks have mitigations. |
| TD-A14 | Deferred | Deferred choices are explicitly bounded. |
| TD-A15 | Governance | Technology changes require formal review. |

# 25. Traceability to Locked Baselines

| Baseline | Technology Decisions role |
| --- | --- |
| 01 PRD v1.0 | Supports product capability and deployment goals. |
| 02 SRS v1.0 | Maps non-functional and technical requirements. |
| 03 System Architecture v1.0 | Preserves architectural boundaries. |
| 04 Technical Design v1.0 | Defines implementation technology interfaces. |
| 05 Agent Behaviour v1.0 | Supports controlled agent lifecycle. |
| 06 Tool & Permission v1.0 | Keeps authorization independent of vendors. |
| 07 Memory & Context v1.0 | Provides replaceable storage/context technologies. |
| 08 Error Recovery v1.0 | Supports bounded async/process/recovery mechanisms. |
| 09 Testing & Validation v1.0 | Defines technology conformance and quality gates. |
| 10 Security & Sandbox v1.0 | Controls sandbox, secrets, dependencies and fail-closed behavior. |
| 11 VS Code Integration v1.0 | Locks TypeScript/VS Code client boundary. |
| 12 Project Plan & Progress v1.0 | Maps technology choices to implementation phases. |
| 13 Research Synthesis v1.0 | Provides external pattern/dependency adoption discipline. |
| 14 Architecture Decision Matrix v1.0 | Constrains technology choices to architecture decisions. |
| 15 Master Architecture v1.0 | Provides the architectural target technology must serve. |
| 16 Repository Blueprint v1.0 | Maps technology into canonical repository locations. |

# 26. Implementation Sequence

T0 Tooling/bootstrap + Python/Node versions

T1 Type/schema/config foundations

T2 Protocol + runtime contracts

T3 Security/scope/sandbox interfaces

T4 Tool Gateway + policy

T5 Execution + Git + MCP adapters

T6 Context/memory/repository adapters

T7 Agent/model gateway

T8 Validation/recovery/audit

T9 CLI + VS Code

T10 E2E/performance/security benchmarks

T11 Finalize deferred technology decisions from evidence

# 27. Final Change Control

- Changing a LOCKED technology principle requires Architecture Decision Matrix review.

- Changing a DEFAULT technology requires compatibility/regression review.

- Selecting a DEFERRED technology requires documented evidence and an ADR.

- Adding a production dependency requires dependency/license/security review.

- Changing model/provider must not alter tool/security contracts.

- Changing protocol technology requires migration and compatibility analysis.

- Changing sandbox technology requires security and escape testing.

- Future approved changes create Technology Decisions v1.1+; v1.0 remains immutable.

# 28. Final Status

STATUS: FINAL / LOCKED — v1.0

Technology Decisions v1.0 is the final locked technology-selection baseline for the AI Software Co-Agent. It establishes the v1 implementation defaults, technology boundaries, dependency governance, model/storage/sandbox strategy, deferred technology decisions, evaluation gates, technology invariants and repository mapping while preserving the architecture's vendor independence.

— END OF TECHNOLOGY DECISIONS v1.0 —
