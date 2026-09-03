AI SOFTWARE CO-AGENT

MEMORY & CONTEXT SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: MCS-001 • Derived from PRD, SRS, System Architecture, Technical Design, Agent Behaviour & Tool/Permission v1.0

| Field | Value |
| --- | --- |
| Document | Memory & Context Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD + SRS + System Architecture + Technical Design + Agent Behaviour + Tool & Permission v1.0 |
| Purpose | Define what context is collected, ranked, persisted, supplied to the model, invalidated and audited |

Lock Statement: This Memory & Context Specification v1.0 is the final locked baseline for task context, repository context, memory, provenance, budgeting, freshness, persistence and model-facing context assembly. Memory and context may improve continuity and reasoning but can never override current evidence, policy or security authority.

# 1. Purpose

The Memory & Context subsystem gives the Co-Agent the right information at the right time without allowing unbounded context growth, stale information, unsafe instructions or historical assumptions to control execution. It separates current task evidence from persistent memory and defines a controlled path into model reasoning.

# 2. Core Principles

- Current evidence outranks stale memory.

- Task scope determines relevance.

- Context is selected, ranked and budgeted; it is not blindly dumped into the model.

- Every important context item has provenance.

- Repository content is untrusted data, not security authority.

- Memory is advisory/contextual, never authorization.

- Policy decisions are authoritative outside memory.

- Validation/error evidence receives high priority during recovery.

- Stale context must be invalidated or refreshed.

- Secrets and unnecessary sensitive data must not enter normal memory.

- Large outputs should be stored as artifacts and referenced rather than duplicated in context.

- Context assembly must be reproducible enough to explain why important information was supplied.

- Context must remain bounded by task, token, time and resource budgets.

# 3. Memory & Context Conceptual Model

TASK REQUIREMENT

│

▼

CONTEXT ORCHESTRATOR

│

┌───────────────┼────────────────┐

▼ ▼ ▼

TASK CONTEXT REPOSITORY CONTEXT MEMORY

│ │ │

└───────────────┼────────────────┘

▼

PROVENANCE

▼

RANKING

▼

BUDGETING

▼

FINAL CONTEXT PACKAGE

│

▼

LLM GATEWAY

│

▼

MODEL / ROLES

│

tool requests / outputs

▼

context refresh loop

The Context Engine is responsible for assembly; individual providers supply evidence. Persistent memory is one provider, not the owner of truth.

# 4. Context Layers

| Layer | Definition | Authority / priority |
| --- | --- | --- |
| L0 — Security/Policy | System and policy constraints relevant to current action | Highest; never overridden by memory |
| L1 — Task | Current requirement, scope, acceptance criteria, state, plan | Primary task intent |
| L2 — Current Repository | Current files, symbols, configuration, tests, docs | Primary implementation evidence |
| L3 — Current Change State | Diff, Git status, patches, checkpoints | Primary change/safety evidence |
| L4 — Validation/Error | Tests, build/lint output, failures, diagnostics | High priority for validation/recovery |
| L5 — Project Memory | Stable project conventions/decisions where still valid | Advisory |
| L6 — Task/Session Memory | Previous task/session facts and reasoning | Advisory; freshness-sensitive |
| L7 — Broader/Optional | Additional repository or external context | Lowest; only when relevant |

# 5. Context Providers

| Provider | Source | Primary responsibility |
| --- | --- | --- |
| TaskProvider | Task DB/runtime state | Requirement, scope, acceptance criteria, state, budgets |
| RepositoryProvider | Repository scanner/search/index/map | Current implementation evidence |
| SymbolProvider | Tree-sitter/index | Definitions, references, relationships |
| GitProvider | Git adapter | Status, diff, checkpoint/change evidence |
| ValidationProvider | Validation Runner | Tests/build/lint outcomes and evidence |
| FailureProvider | Recovery subsystem | Error records, diagnostics and prior attempts |
| ProjectMemoryProvider | Memory store | Stable project facts/conventions/decisions |
| TaskMemoryProvider | Memory store | Task-specific facts and decisions |
| SessionProvider | Runtime session state | Current conversational/task continuity |
| ArtifactProvider | Artifact store | Large outputs/reports/diffs referenced by ID |
| MCPContextProvider | MCP adapter where permitted | External context treated as untrusted tool data |

# 6. Memory Types

| Memory type | Examples | Default lifetime | Authority |
| --- | --- | --- | --- |
| Task state | Task status, plan, acceptance criteria | Task lifetime | Operational state |
| Task memory | Decisions, assumptions, discovered constraints | Task/project policy | Advisory |
| Project memory | Architecture conventions, coding conventions | Long-lived | Advisory |
| Decision memory | Decision + rationale + source | Long-lived/versioned | Advisory |
| Failure memory | Failure category, diagnosis, successful repair | Long-lived with freshness | Advisory |
| Session memory | Recent interaction/task continuity | Session/task | Advisory |
| Repository index | Files, symbols, hashes, relationships | Until invalidated | Current evidence |
| Audit evidence | Tool/policy/validation events | Configured retention | Evidence; not reasoning authority |
| Artifacts | Logs, command output, reports | Configured retention | Evidence reference |

# 7. Memory Record Contract

MemoryRecord {

memory_id: UUID

type: MemoryType

project_id: UUID | null

task_id: UUID | null

key: string

value: object

summary: string | null

source: MemorySource

provenance: Provenance

confidence: float | null

created_at: datetime

updated_at: datetime

valid_from: datetime | null

valid_until: datetime | null

version: int

sensitivity: SensitivityClass

status: ACTIVE | STALE | INVALID | ARCHIVED

}

- Memory must be attributable to a source.

- Versioned memory prevents silent replacement of important decisions.

- Validity fields support freshness and expiry.

- Sensitivity classification controls whether memory may be model-facing.

- Invalid memory must not be selected as active context.

# 8. Context Item Contract

ContextItem {

context_id: UUID

source_type: ContextSource

source_id: string

content_or_ref: string | object

summary: string | null

relevance_score: float

freshness_score: float

authority_level: int

provenance: Provenance

sensitivity: SensitivityClass

token_estimate: int

created_at: datetime

expires_at: datetime | null

hash: string | null

}

ContextItem is the normalized unit used by ranking, budgeting, assembly and audit.

# 9. Provenance Model

| Provenance field | Purpose |
| --- | --- |
| source_type | Repository, task, memory, Git, validation, MCP, artifact, etc. |
| source_id | Stable identifier/path/reference. |
| source_version | File hash, memory version, task version or artifact version where available. |
| captured_at | When evidence was captured. |
| derived_from | Parent evidence if item is summarized/derived. |
| locator | File path/line/range, record ID or artifact reference where possible. |
| trust_class | Current evidence, historical memory, external/untrusted. |
| freshness | Fresh/stale/unknown or numerical freshness score. |

When context is summarized, provenance must remain traceable to the underlying evidence whenever practical.

# 10. Context Ranking

The MVP uses deterministic, explainable ranking rather than opaque retrieval behavior as the first implementation.

| Ranking signal | Typical weight/importance |
| --- | --- |
| Direct task relevance | Very high |
| Current repository evidence | Very high |
| Acceptance criterion relation | Very high |
| Validation/error relation | High during validation/recovery |
| Change/diff relation | High during implementation/review |
| Freshness | High |
| Authority layer | High |
| Project convention match | Medium |
| Memory relevance | Medium/low |
| Broader semantic similarity | Optional/future |

- Ranking is contextual to the current stage.

- Implementation favors current code and scope.

- Recovery favors actual error/validation evidence.

- Historical memory should not crowd out current repository evidence.

- Low-relevance items should be dropped before final assembly.

# 11. Context Budgeting

| Budget | Control |
| --- | --- |
| Token budget | Maximum model-facing context allocation. |
| Provider budget | Maximum items/bytes each provider can contribute. |
| Item size | Large items are summarized/truncated/referenced. |
| Artifact budget | Large raw logs remain external to prompt where possible. |
| Retrieval count | Limit number of search/index results. |
| History budget | Limit old session/task turns or memory records. |
| Latency budget | Stop/shorten retrieval when context collection exceeds configured time. |
| Duplicate budget | Deduplicate overlapping file/content evidence. |

Budgeting must be deterministic enough to explain why a context item was included or omitted.

# 12. Context Assembly Pipeline

1. Load task + stage

2. Determine required context classes

3. Query providers

4. Normalize ContextItems

5. Remove invalid/forbidden/sensitive items

6. Deduplicate

7. Score relevance/freshness/authority

8. Rank

9. Apply provider and global budgets

10. Build structured context sections

11. Attach provenance

12. Validate context package

13. Send through LLM Gateway

14. Record context manifest

A Context Manifest records the selected source IDs, scores/selection rationale where configured, token estimates, versions/hashes and assembly timestamp.

# 13. Stage-Specific Context Behaviour

| Stage | Highest-priority context |
| --- | --- |
| Understanding | Requirement, acceptance criteria, project metadata, relevant docs |
| Planning | Requirement + repository map + relevant code/tests/config + conventions |
| Implementation | Plan + exact target files + definitions/usages + current diff/Git state |
| Review | Plan + actual diff + impacted files + relevant tests |
| Validation | Changed files + validation configuration + current test/build/lint output |
| Recovery | Failure record + exact failing output + affected code + recent patch/diff + prior recovery attempts |
| Completion | Acceptance criteria + actual diff + required validation evidence + Git state |
| Reporting | Recorded task/change/validation/recovery/audit evidence |

# 14. Freshness & Invalidation

- File content is stale when the underlying file changes after capture.

- Repository index entries are invalidated using file metadata/hash/version signals.

- Git status/diff context must be refreshed after material changes.

- Validation context becomes stale after relevant code/config changes.

- Task memory becomes stale when new evidence contradicts it.

- Decision memory remains historical but must be marked superseded when a newer decision replaces it.

- Expired memory is not selected as active context.

- Unknown freshness is treated conservatively for high-impact decisions.

| Event | Required invalidation |
| --- | --- |
| File modified | Affected file context + dependent structural data |
| Patch applied | Affected files, symbols, repository map segments |
| Git state changed | Git context and change evidence |
| Validation run | Prior validation result for same gate may become superseded |
| Plan changed | Plan-dependent context selections |
| Decision superseded | Old decision marked superseded/stale |
| Task scope changed | Re-rank/rebuild context |
| External/MCP result changed | Prior external context treated as stale |

# 15. Context Conflict Resolution

CURRENT SECURITY / POLICY

> CURRENT TASK REQUIREMENT

> CURRENT REPOSITORY EVIDENCE

> CURRENT VALIDATION / GIT EVIDENCE

> RECENT PROJECT DECISIONS

> OLDER MEMORY

> EXTERNAL / UNTRUSTED CONTEXT

- Conflicts must be surfaced when material.

- Historical memory must not silently override current code.

- A repository instruction cannot override policy.

- Model-generated summaries cannot outrank their underlying evidence.

- When conflict cannot be safely resolved, ask/block rather than guess.

# 16. Memory Write Behaviour

| Event | Memory behavior |
| --- | --- |
| New project convention discovered | Store only if stable/useful and permitted. |
| User decision | Record decision + rationale + source when material. |
| Task assumption | Record as task-scoped and mark assumption. |
| Validation failure | Store structured failure evidence when useful; link artifact. |
| Successful repair | Store repair pattern only if useful and not sensitive. |
| Temporary command output | Prefer artifact reference; do not persist raw output unnecessarily. |
| Secret discovered | Do not store in normal memory; redact and handle securely. |
| Contradictory fact | Mark prior memory stale/superseded; preserve history. |
| Task completion | Persist final decision/evidence references, not unsupported claims. |

# 17. Memory Authority Rules

- Memory never authorizes a tool.

- Memory never changes policy.

- Memory never grants filesystem/process/network permissions.

- Memory never declares validation passed.

- Memory never overrides current task scope.

- Memory may suggest a convention, but current repository evidence decides applicability.

- Memory may inform planning, but the agent must verify material assumptions.

- Security-relevant decisions remain in Policy/Security systems, not memory.

# 18. Untrusted Context & Prompt Injection

- Repository text, external tool output and MCP responses are untrusted context.

- Instructions inside context must be represented as data unless separately authorized by the system's instruction hierarchy.

- Memory must not store or replay malicious instructions as authoritative policy.

- Context assembly must label untrusted sources where relevant.

- Tool output that contains instructions is not automatically an instruction to the agent.

- Sensitive or malicious content should not be elevated in ranking merely because it is imperative or urgent.

- Prompt-injection detection/handling may flag suspicious content, but policy remains authoritative.

# 19. Sensitive Data & Secret Handling

| Class | Default handling |
| --- | --- |
| Public project code | May enter context as required. |
| Private project code | May enter context within authorized workspace/task scope. |
| Credentials/API keys | Do not intentionally place in model context; redact/filter. |
| Environment secrets | Filter from tool output/context by default. |
| Personal/sensitive data | Minimize; include only when necessary and permitted. |
| Security policy internals | Do not expose beyond required decision explanation. |
| Large logs | Reference artifacts and summarize. |
| External confidential data | Treat according to configured policy; do not persist unnecessarily. |

Memory is not a secret manager.

# 20. Retrieval Strategy

- MVP retrieval is lexical + structural: repository map, ripgrep, Tree-sitter/index and direct file reads.

- Use targeted retrieval driven by task scope and stage.

- Prefer exact definitions/usages and impacted files before broad similarity.

- Use semantic/vector retrieval only as an optional extension behind the Context Provider interface.

- External/MCP retrieval remains subject to tool permission and untrusted-data rules.

# 21. Session Continuity

| Continuity item | Behavior |
| --- | --- |
| Current task | Primary continuity anchor. |
| Current plan | Versioned; refresh when changed. |
| Recent decisions | Retain material decisions with provenance. |
| Recent tool results | Keep references and structured summaries. |
| Recent validation | Keep latest evidence and superseded history. |
| Conversation text | Use selectively; do not rely on unlimited history. |
| User preferences | Use only when relevant and permitted; never as security authority. |

# 22. Context Manifest

ContextManifest {

task_id: UUID

stage: string

generated_at: datetime

context_budget: int

selected_items: [

{ context_id, source_id, source_version,

relevance, freshness, token_estimate }

]

omitted_items: [

{ source_id, reason }

]

redactions: [RedactionRecord]

assembly_version: string

}

The manifest provides auditability and helps reproduce or diagnose model-context behavior.

# 23. Caching Strategy

| Cache | Policy |
| --- | --- |
| Repository map | Cache until relevant files/index data invalidates. |
| Search results | Short-lived/task-scoped; invalidate on relevant changes. |
| Parsed syntax | Hash/version keyed. |
| Symbols | Index/version keyed. |
| Context package | Stage/task scoped; rebuild after material changes. |
| Memory query | Cache only when underlying memory version is unchanged. |
| Validation evidence | Immutable evidence record; latest gate result supersedes previous for completion. |

# 24. Persistence Design

| Store | MVP mechanism | Purpose |
| --- | --- | --- |
| Memory records | SQLite | Structured memory. |
| Repository index | SQLite | Files/symbols/relationships. |
| Task state | SQLite | Task/lifecycle/context references. |
| Context manifests | SQLite + artifact metadata | Selected/omitted context trace. |
| Large artifacts | Filesystem artifact store | Logs, outputs, reports. |
| Audit | SQLite/structured JSON | Traceability. |

# 25. Retention & Cleanup

- Retention must be configurable by memory/artifact type.

- Temporary session context may expire automatically.

- Stale memory should be marked before deletion when history is useful.

- Large artifacts may be pruned after configured retention while preserving necessary references.

- Audit retention must satisfy the project's audit requirements.

- Deletion must not remove evidence required to support an existing completion decision unless policy explicitly permits it.

- Secrets must be removed/redacted rather than retained for convenience.

# 26. Context Failure Behaviour

| Failure | Required response |
| --- | --- |
| Provider unavailable | Use other safe providers or report incomplete context. |
| Index stale | Refresh affected index/context. |
| Budget exceeded | Reduce/summarize/re-rank; do not silently exceed. |
| Memory conflict | Prefer current evidence; mark conflict. |
| Sensitive data detected | Redact/filter and record safe handling. |
| Malformed memory | Ignore invalid record; do not crash task unnecessarily. |
| Artifact unavailable | Report missing evidence and avoid unsupported claims. |
| Retrieval timeout | Use bounded fallback or stop safely. |
| External/MCP context untrusted | Treat as data; do not elevate authority. |

# 27. Recovery-Specific Context

- Failure context must prioritize the actual failing command/test output.

- Include exact affected file/function/module where known.

- Include current diff and relevant recent changes.

- Include prior recovery attempts to avoid repeating known failed approaches.

- Include applicable project conventions and acceptance criteria.

- Exclude irrelevant repository history to preserve budget.

- After repair, rebuild context from the current repository state before retest.

# 28. Completion Context

- Completion review must use current acceptance criteria.

- Completion must use actual current diff.

- Completion must use latest required validation evidence.

- Completion may use Git state and recovery evidence.

- Completion must not rely on old memory claiming that a test previously passed.

- Completion Gate is authoritative; context only supplies evidence to it.

# 29. Memory & Context Observability

| Event | Minimum evidence |
| --- | --- |
| context.requested | task, stage, provider set, budget |
| context.selected | context IDs/source IDs and scores/metadata |
| context.omitted | source/item + omission reason where practical |
| context.redacted | redaction class/reason, not secret value |
| memory.created | memory ID/type/source |
| memory.updated | version/change source |
| memory.invalidated | reason + superseding evidence |
| context.manifest | final package/version |
| context.failure | provider/error/bounded fallback |
| context.refresh | trigger + affected sources |

# 30. Mandatory Memory & Context Security Tests

- Secret/API-key filtering from model context.

- Environment-variable filtering.

- Repository prompt-injection fixtures.

- MCP malicious-output fixtures.

- Memory attempting to authorize a denied tool.

- Stale memory conflicting with current repository code.

- Context budget overflow attempts.

- Path/content provenance correctness.

- Untrusted instruction ranking manipulation.

- Context redaction correctness.

- Context manifest integrity.

- Cross-task memory leakage tests.

- Cross-project memory isolation tests.

- Protected policy/security content leakage tests.

# 31. Memory & Context Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| MCS-A01 | Layering | Context layers and authority are explicit. |
| MCS-A02 | Providers | Required context providers expose normalized contracts. |
| MCS-A03 | Memory model | Memory is typed, versioned and provenance-aware. |
| MCS-A04 | Ranking | Context ranking is task/stage relevant and explainable. |
| MCS-A05 | Budget | Global/provider/item budgets are enforced. |
| MCS-A06 | Freshness | Repository/validation/Git changes invalidate affected context. |
| MCS-A07 | Conflict | Current evidence outranks stale memory. |
| MCS-A08 | Security | Secrets are filtered and untrusted instructions cannot become authority. |
| MCS-A09 | Isolation | Task/project memory is properly scoped. |
| MCS-A10 | Audit | Context manifests and material memory changes are traceable. |
| MCS-A11 | Recovery | Failure context prioritizes actual evidence and refreshes after repair. |
| MCS-A12 | Completion | Completion uses current evidence, not historical claims. |
| MCS-A13 | Persistence | SQLite/artifact boundaries are explicit. |
| MCS-A14 | Testing | Security and correctness tests cover context/memory failure modes. |
| MCS-A15 | No authorization | Memory/context cannot modify tool permissions or policy. |

# 32. Traceability to Locked Baselines

| Baseline | Memory/Context impact |
| --- | --- |
| PRD v1.0 | Reliable context, continuity, safety and evidence-backed completion. |
| SRS v1.0 | Context, memory, audit, security and lifecycle requirements. |
| System Architecture v1.0 | Context Engine + Memory + Repository/Validation/Git provider boundaries. |
| Technical Design v1.0 | Provider contracts, SQLite persistence, ranking/budgeting and Context Manifest. |
| Agent Behaviour v1.0 | Current evidence over memory, repository-first behavior, injection resistance and communication. |
| Tool & Permission v1.0 | Tool output as evidence; memory/context cannot authorize actions. |
| Error Recovery v1.0 | Failure context and bounded recovery loop. |
| Testing & Validation v1.0 | Validation evidence as current context. |
| Security & Sandbox v1.0 | Secret, injection, isolation and policy authority. |
| Repository Blueprint v1.0 | Physical memory/context/index module placement. |

# 33. Implementation Mapping

| Area | Expected implementation modules |
| --- | --- |
| Context models | src/context/models.py / contracts.py |
| Context providers | src/context/providers/... |
| Ranking | src/context/ranker.py |
| Budgeting | src/context/budget.py |
| Assembly | src/context/assembler.py |
| Provenance | src/context/provenance.py |
| Freshness | src/context/freshness.py |
| Manifest | src/context/manifest.py |
| Memory models | src/memory/models.py |
| Memory repository | src/memory/repository.py |
| Memory service | src/memory/service.py |
| Memory lifecycle | src/memory/lifecycle.py |
| Repository index | src/repository/index/... |
| Artifacts | src/reporting/artifacts.py or equivalent |
| Audit | src/audit/... |
| Tests | tests/unit/context, tests/unit/memory, tests/security, tests/integration |

Exact filenames may evolve through implementation change control. The data contracts, authority rules and context pipeline are locked.

# 34. Memory & Context Invariants

- M1: Current security/policy authority cannot be overridden by memory.

- M2: Current task requirements outrank historical assumptions.

- M3: Current repository evidence outranks stale memory.

- M4: Validation evidence must be current for completion decisions.

- M5: Every important model-facing context item has provenance.

- M6: Context cannot exceed configured budgets.

- M7: Invalid/stale memory is not silently treated as current truth.

- M8: Secrets are not intentionally persisted in normal memory.

- M9: Task/project memory is isolated by scope.

- M10: External/MCP content is untrusted context.

- M11: Context assembly is observable through a manifest.

- M12: Memory cannot authorize tools or modify policy.

- M13: Repair context is refreshed after repository changes.

- M14: Historical success cannot substitute for current validation.

- M15: Missing context evidence leads to clarification, fallback or non-complete behavior rather than invention.

# 35. Change Control

- Changes to context authority hierarchy require architecture/security review.

- Changes to memory retention or sensitivity handling require security/privacy review.

- Changes to budget semantics require performance/evaluation review.

- Changes to provenance requirements require auditability review.

- Changes that allow memory to influence permissions are prohibited without an explicit security architecture revision.

- New retrieval technologies must preserve the Context Provider contract and authority rules.

- New memory types require defined lifetime, sensitivity, provenance and authority.

# 36. Final Status

STATUS: FINAL / LOCKED — v1.0

This Memory & Context Specification v1.0 is the authoritative baseline for how the AI Software Co-Agent collects, ranks, budgets, persists, invalidates and supplies information to its reasoning system. It explicitly separates current evidence from advisory memory and prevents context from becoming an authorization mechanism.

— END OF MEMORY & CONTEXT SPECIFICATION v1.0 —
