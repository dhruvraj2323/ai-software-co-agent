AI SOFTWARE CO-AGENT

RESEARCH SYNTHESIS

Version 1.0 — FINAL / LOCKED

Document ID: RS-001 • Research-to-Architecture Synthesis for the AI Software Co-Agent

| Field | Value |
| --- | --- |
| Document | Research Synthesis |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Purpose | Synthesize lessons from researched open-source agent/code-agent repositories into implementation decisions for our Co-Agent without copying their architecture blindly. |
| Research basis | Prior project deep-research set + current verification of public repository sources |
| Decision role | Advisory to locked product/architecture specifications; adopted decisions become implementation constraints only when explicitly mapped. |

Lock Statement: Research Synthesis v1.0 is the final locked synthesis of reusable patterns and lessons identified from the researched repositories. It does not replace the locked PRD/SRS/Architecture/Technical/Security documents. External repositories remain references, not authorities.

# 1. Research Objective

The research program examined mature open-source agent and coding-agent systems to identify patterns that can accelerate our implementation while avoiding known architectural traps. The goal is not to reproduce any one repository, but to extract reusable design ideas, compare them against our locked requirements, and decide what should be adopted, adapted, wrapped or rejected.

Research principle: Borrow patterns, not authority.

# 2. Research Sources & Evidence Boundary

| Repository / system | Research role | Verified public evidence |
| --- | --- | --- |
| Roo Code | IDE-native autonomous coding agent patterns | Official GitHub describes file read/write, terminal commands, browser actions, model/API integration and Custom Modes. citeturn0search3 |
| Agent-MCP | MCP-oriented multi-agent/task decomposition patterns | Public repository documentation describes a multi-agent framework using MCP and linear task steps; current public mirror points to the rinadelph source. citeturn0search19 |
| MetaGPT | Multi-agent software-engineering workflow patterns | Prior project research basis; this synthesis treats it as a workflow/orchestration reference, not an authority. |
| SWE-agent | Issue-to-code agent workflow and software-engineering evaluation patterns | Prior project research basis; use is limited to reusable workflow/evaluation ideas unless separately re-verified. |
| Aider | Terminal-first coding-agent and repository-editing patterns | Prior project research basis; use is limited to interaction/edit/test workflow patterns unless separately re-verified. |
| Continue | IDE/CLI/custom-agent/context configuration patterns | Official Continue docs/repo describe VS Code/JetBrains extensions, CLI, agent/chat/edit/autocomplete and configurable agents; its config can define models, rules, context providers and MCP tools. citeturn0search6turn0search12 |
| OpenHands | Sandboxed software-development agent/runtime patterns | Public documentation/repository material describes an AI software-development agent capable of code modification, command execution and web/API actions, with Docker-based runtime deployment. citeturn0search14 |
| AutoGen | Multi-agent runtime/message-passing patterns | Public AutoGen documentation describes agent applications, layered APIs, message/event-oriented runtime and extensions; current ecosystem status should be checked before direct dependency adoption. citeturn0search8turn0search11 |
| Cline | IDE-native coding-agent interaction patterns | Prior project research basis; use is limited to interaction/tool/approval ideas unless separately re-verified. |
| LangGraph | Graph/state-machine orchestration patterns | Prior project research basis; use is limited to orchestration/state concepts unless separately re-verified. |

Evidence boundary: where the earlier deep-research notes are not present in this document context, this synthesis does not invent repository-specific claims. Current web verification is used only to confirm high-level public positioning/features; detailed implementation conclusions remain architectural synthesis.

# 3. Cross-Repository Pattern Map

| Pattern | Observed across research | Our decision |
| --- | --- | --- |
| IDE-native agent | Roo Code, Continue and other coding agents | ADOPT concept; implement behind our runtime boundary. |
| CLI/headless execution | Continue and terminal-oriented agents | ADOPT as a client mode; runtime remains authoritative. |
| Tool-driven coding | Roo Code/OpenHands/other agents | ADOPT through our Tool Gateway only. |
| Custom agent modes/config | Roo Code/Continue | ADAPT into our configuration/behavior layer. |
| Context providers | Continue and modern coding-agent systems | ADOPT with our Memory & Context contracts. |
| MCP tool integration | Agent-MCP/Continue/other agent systems | ADOPT capability; mandatory internal policy boundary. |
| Multi-agent decomposition | Agent-MCP/MetaGPT/AutoGen | ADAPT selectively; single-agent core remains default. |
| Sandboxed execution | OpenHands and comparable systems | ADOPT principle; align with our Security & Sandbox spec. |
| Structured state/workflows | AutoGen/MetaGPT/LangGraph-style systems | ADOPT state-machine principle. |
| Automated validation | SWE-agent/coding-agent workflows | ADOPT as mandatory completion evidence. |
| Iterative repair | SWE-agent/Aider/agentic coding workflows | ADOPT through bounded Error Recovery. |
| Human approval | IDE coding agents | ADOPT for high-risk operations. |
| Persistent task context | Modern coding agents | ADOPT with strict scope/freshness. |
| Open-ended autonomy | Several agent systems | REJECT as default behavior; use bounded autonomy. |
| Direct model-to-shell execution | Common in prototypes | REJECT; central policy/tool boundary required. |

# 4. Key Architectural Lessons

- Successful coding agents separate model reasoning from real-world side effects through tools/executors.

- Repository-aware context is essential; generic chat context is insufficient for reliable software work.

- Agent workflows need explicit state and progress rather than an unconstrained conversation loop.

- Validation must be part of the agent loop, not an afterthought.

- Recovery needs evidence and bounded attempts; blind retries create loops.

- IDE integration is a client experience, not the security authority.

- Configuration/custom modes are powerful, but must not override hard security rules.

- MCP expands capability and therefore expands the attack surface; it needs the same policy boundary as native tools.

- Multi-agent architectures are useful for specialized decomposition but introduce coordination, context and cost complexity.

- Sandboxing is an architectural capability, not merely a UI setting.

- Source-controlled configuration and checks can improve reproducibility and governance; Continue publicly documents configuration-driven agents and CI checks. citeturn0search12turn0search2

# 5. What We Should Adopt

| Decision | Why it fits our locked design | Target specification |
| --- | --- | --- |
| Tool-mediated execution | Provides clear side-effect boundary | Tool & Permission + Security |
| Explicit task state | Makes lifecycle observable/recoverable | Agent Behaviour |
| Repository-first context | Improves code-change correctness | Memory & Context |
| Context budgeting/ranking | Controls model input and freshness | Memory & Context |
| Validation after change | Prevents false completion | Testing & Validation |
| Bounded recovery | Prevents infinite repair loops | Error Recovery |
| Approval for high-risk actions | Preserves user control | Tool & Permission |
| Sandboxed process execution | Limits blast radius | Security & Sandbox |
| IDE client/runtime split | Prevents client-side bypass | VS Code Integration |
| Structured events/audit | Makes actions reconstructable | Observability/Audit |
| CLI/headless mode | Supports automation and CI | CLI Integration / Architecture |
| MCP adapter boundary | Extends tools safely | Tool & Permission + Security |

# 6. What We Should Adapt

| Pattern | Adaptation for our Co-Agent |
| --- | --- |
| Custom modes | Represent as governed behavior profiles, never policy overrides. |
| Multi-agent teams | Use only for tasks where specialization demonstrably improves outcome. |
| Graph/state orchestration | Use explicit state transitions while keeping the core system understandable. |
| Repository rules | Treat as untrusted project guidance; validate against higher-level policy. |
| Autonomous loops | Use bounded task/recovery loops with budgets. |
| External tool ecosystems | Wrap behind internal ToolDefinitions and PolicyDecision. |
| Configuration files | Version and validate; fail safely on invalid security-sensitive configuration. |
| Provider/model abstraction | Keep model gateway replaceable without changing tool/security contracts. |
| Agent memory | Store scoped, provenance-aware records rather than raw conversation indefinitely. |
| Browser/web actions | Treat as high-risk external capabilities with separate permissions. |

# 7. What We Should Reject

- Architecture in which model text directly executes arbitrary commands.

- Client-side security assumptions.

- Unbounded autonomous loops.

- Silent workspace scope expansion.

- Using repository instructions as security policy.

- Using memory as authorization.

- Using MCP as a bypass route.

- Blind retry of identical failures.

- Declaring success because the model says the task is complete.

- Overbuilding multi-agent coordination before the single-agent control plane is reliable.

- Copying external repository architecture wholesale.

- Adding dependencies without license, security and maintenance review.

# 8. Research-Derived Target Architecture

┌────────────────────┐

│ VS Code / CLI │

└─────────┬──────────┘

│

Client Protocol

│

▼

┌──────────────────────┐

│ Task / Orchestrator │

└──────────┬───────────┘

│

┌──────────────────┼──────────────────┐

▼ ▼ ▼

Context Planner State

│ │ │

└──────────────────┼──────────────────┘

▼

Tool Gateway

│

Policy Engine

│

┌──────────────────┼──────────────────┐

▼ ▼ ▼

Workspace Process MCP

Sandbox Sandbox Adapter

│ │ │

└──────────────────┼──────────────────┘

▼

Validation Runner

│

Recovery Controller

│

Completion Gate

│

Audit / Evidence

# 9. Research-to-Implementation Rules

- Every external pattern enters our system only through an internal contract.

- External code is not copied until license/security review is complete.

- Adopted patterns must map to a locked specification.

- Any pattern that conflicts with Security & Sandbox is rejected.

- Any pattern that creates a direct executor bypass is rejected.

- Patterns are tested against our own acceptance criteria.

- External repositories may inspire implementation but cannot define our completion criteria.

# 10. Recommended Internal Module Map

| Capability | Internal destination |
| --- | --- |
| Task orchestration | src/agent/orchestrator/ |
| Agent state | src/agent/state/ |
| Planning | src/agent/planning/ |
| Tool Gateway | src/tools/gateway/ |
| Policy | src/security/policy/ |
| Workspace | src/workspace/ |
| Process sandbox | src/execution/ |
| Repository intelligence | src/repository/ |
| Context | src/context/ |
| Memory | src/memory/ |
| Recovery | src/recovery/ |
| Validation | src/validation/ |
| Git | src/git/ |
| MCP | src/tools/mcp/ |
| Audit | src/audit/ |
| VS Code | vscode-extension/ |
| CLI | cli/ |

# 11. Research-Derived Testing Priorities

| Priority | Tests |
| --- | --- |
| P0 Critical | Policy bypass, workspace escape, secret leakage, false completion |
| P1 Critical | Tool schema/authorization, process sandbox, patch scope, recovery loops |
| P1 High | Prompt injection, MCP boundary, user-change preservation |
| P2 High | Repository context freshness, memory isolation, validation evidence |
| P2 High | Client/runtime protocol and reconnect safety |
| P3 Medium | Multi-agent coordination, advanced customization, performance |
| P4 Later | Experimental autonomy patterns and optional ecosystem integrations |

# 12. Research-Derived Implementation Priorities

Priority 1 — Control Plane

Contracts + State + Tool Gateway + Policy + Security

Priority 2 — Safe Execution Plane

Workspace + Process + Patch + Git + Validation

Priority 3 — Intelligence Plane

Repository Intelligence + Context + Memory + Planning

Priority 4 — Agent Loop

Orchestration + Behaviour + Recovery + Completion

Priority 5 — Client Plane

VS Code + CLI + Protocol + UX

Priority 6 — Scale/Optimization

Multi-agent + advanced MCP + performance + provider optimization

# 13. Multi-Agent Strategy Decision

Decision: ADAPT, not default. Multi-agent research demonstrates useful specialization and coordination patterns, but our v1 implementation should establish a reliable single-agent control plane first.

- Specialized agents may be introduced behind the same Task/Tool/Policy/Context contracts.

- Every sub-agent receives scoped context and capabilities.

- Sub-agents cannot bypass the parent task's policy.

- Cross-agent messages are untrusted data until interpreted by the orchestrator.

- Shared memory must remain scoped and provenance-aware.

- Coordination budgets prevent agent-to-agent loops.

# 14. MCP Strategy Decision

Decision: ADOPT with strict boundary.

- MCP is a capability transport/integration mechanism, not a security authority.

- Every MCP tool maps to an internal tool definition.

- All requests pass the same authorization path.

- MCP results remain untrusted.

- Server/tool identity is audited.

- MCP capability expansion requires security tests.

# 15. Configuration Strategy Decision

Decision: ADAPT. Continue's public documentation illustrates a configuration-driven agent model in which models, rules, context providers and MCP tools can be composed. citeturn0search12

- Our configuration layer should make behavior/profile composition easy.

- Security policy remains outside ordinary behavior configuration.

- Invalid security-sensitive configuration fails closed.

- Configuration versions are traceable.

- Project configuration is treated as input, not authority over hard policy.

# 16. IDE Strategy Decision

Decision: ADOPT IDE-native workflow, preserve runtime authority.Roo Code and Continue demonstrate the value of deep IDE integration; Roo Code publicly describes an editor-resident agent with file, terminal, browser and custom-mode capabilities, while Continue supports IDE and CLI agent workflows. citeturn0search3turn0search6

- VS Code is the primary client in our roadmap.

- CLI is a parallel client, not a separate core runtime.

- Both clients use the same runtime contracts.

- Neither client owns security authorization.

# 17. Sandbox Strategy Decision

Decision: ADOPT defense-in-depth sandboxing.OpenHands publicly documents a Docker-oriented runtime model for software-development agents, reinforcing the value of an explicit execution boundary. citeturn0search14

- Our sandbox design remains platform-aware and policy-controlled.

- Containerization may be one implementation option, not the only architecture.

- Workspace, process, network and secret boundaries remain independently testable.

# 18. Evaluation Strategy

- Evaluate task success and safety separately.

- Track false completion explicitly.

- Measure validation pass rate and recovery success.

- Measure security bypass attempts and zero successful bypasses.

- Benchmark repository/context handling on representative repositories.

- Compare single-agent vs specialized-agent workflows only after baseline reliability is established.

- Use reproducible fixtures and evidence rather than subjective model confidence.

# 19. Research Gaps & Follow-up

- Detailed file-level architecture findings from the original ten-repository deep-research notes should remain archived with the research artifacts.

- License status must be verified for any code actually imported.

- Dependency health and maintenance status must be rechecked immediately before implementation adoption.

- Security posture must be assessed for each external dependency/MCP server.

- Performance claims from external projects must not be assumed to apply to our runtime.

- Repository-specific implementation details may change over time; locked internal specifications take precedence.

# 20. Research-to-Decision Matrix

| Capability | Evidence pattern | Decision | Reason |
| --- | --- | --- | --- |
| IDE agent | Roo/Continue | ADOPT | High user value; aligns with VS Code baseline. |
| CLI/headless | Continue/terminal agents | ADOPT | Automation/CI value. |
| MCP | Agent-MCP/Continue | ADOPT | Extensibility; must be secured. |
| Multi-agent | MetaGPT/AutoGen/Agent-MCP | ADAPT | Useful specialization, higher complexity. |
| Sandbox | OpenHands | ADOPT | Strong safety boundary. |
| Validation loop | Coding-agent research | ADOPT | Required for correctness. |
| Recovery loop | Coding-agent research | ADOPT | Required for robustness. |
| Custom modes | Roo/Continue | ADAPT | Useful behavior profiles. |
| Config-driven agents | Continue | ADAPT | Reproducibility and customization. |
| Unbounded autonomy | Various agents | REJECT | Conflicts with bounded safety model. |
| Direct executor access | Prototype patterns | REJECT | Conflicts with Tool/Permission/Security. |

# 21. Locked Research Invariants

- RS1: External repositories are references, not authorities.

- RS2: No external pattern may bypass our locked security boundary.

- RS3: Every adopted capability maps to an internal contract.

- RS4: Research adoption requires license/security/maintenance review.

- RS5: Model reasoning remains separate from side-effect execution.

- RS6: Validation evidence is required regardless of research-derived architecture.

- RS7: Multi-agent coordination is optional and bounded.

- RS8: MCP is an integration mechanism, never an authorization authority.

- RS9: Client integrations never become security boundaries.

- RS10: Repository instructions remain untrusted project data.

- RS11: Memory remains advisory and scoped.

- RS12: Recovery remains bounded.

- RS13: External performance claims do not become internal guarantees without measurement.

- RS14: Research findings cannot silently modify locked specifications.

- RS15: Every major adopted research pattern has a recorded implementation decision.

# 22. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| RS-A01 | Source set | Research sources and evidence boundary are identified. |
| RS-A02 | Pattern extraction | Reusable patterns are separated from project-specific architecture. |
| RS-A03 | Adoption | Adopt/adapt/reject decisions are explicit. |
| RS-A04 | Security | No research pattern weakens locked security. |
| RS-A05 | Architecture | Research maps to internal components/contracts. |
| RS-A06 | MCP | MCP adoption preserves internal policy boundary. |
| RS-A07 | Multi-agent | Multi-agent use is bounded and optional. |
| RS-A08 | IDE | IDE/client integration preserves runtime authority. |
| RS-A09 | Validation | Research-derived implementation is subject to our validation gates. |
| RS-A10 | Licensing | External code adoption requires license review. |
| RS-A11 | Maintenance | External dependency health is reviewed before adoption. |
| RS-A12 | Evidence | Research claims are traceable to source evidence where available. |
| RS-A13 | Gaps | Unverified repository-specific details are not invented. |
| RS-A14 | Invariants | Locked research invariants are explicit. |
| RS-A15 | Change control | Research cannot silently change locked specifications. |

# 23. Traceability to Locked Baselines

| Baseline | Research synthesis impact |
| --- | --- |
| 01 PRD v1.0 | Research supports product capability priorities. |
| 02 SRS v1.0 | Patterns are evaluated against functional/non-functional requirements. |
| 03 System Architecture v1.0 | Research patterns map into controlled internal boundaries. |
| 04 Technical Design v1.0 | Implementation ideas are adapted into internal contracts. |
| 05 Agent Behaviour v1.0 | Agent loops, modes and multi-agent ideas remain bounded. |
| 06 Tool & Permission v1.0 | All external capabilities use the internal tool/policy path. |
| 07 Memory & Context v1.0 | Context/provider patterns are adopted with provenance/freshness. |
| 08 Error Recovery v1.0 | Repair loops are bounded and evidence-driven. |
| 09 Testing & Validation v1.0 | External ideas do not replace internal acceptance tests. |
| 10 Security & Sandbox v1.0 | Sandbox/injection/MCP lessons are subordinated to locked security. |
| 11 VS Code Integration v1.0 | IDE patterns inform client UX without becoming authorization. |
| 12 Project Plan & Progress v1.0 | Research adoption is a controlled implementation activity. |

# 24. Implementation Mapping

| Research output | Repository artifact |
| --- | --- |
| Pattern decision | docs/research/decisions/ |
| Source register | docs/research/sources/ |
| Adoption notes | docs/research/adoptions/ |
| External code review | docs/research/dependency-reviews/ |
| License review | docs/research/licenses/ |
| Security review | docs/research/security/ |
| Benchmark results | artifacts/research/benchmarks/ |
| Research tests | tests/research/ |
| Synthesis document | docs/research/RESEARCH_SYNTHESIS_v1.0.md |

# 25. Change Control

- New research does not automatically change architecture.

- New external repositories require source/maintenance/license/security review.

- Adopting a new architecture pattern requires impact analysis against locked documents.

- Replacing an adopted dependency requires regression/compatibility testing.

- Security-related research findings require immediate review if they expose a weakness in our design.

- Any baseline-changing conclusion is promoted through formal specification versioning.

- v1.0 remains the historical locked research synthesis; future research creates v1.1+.

# 26. Final Status

STATUS: FINAL / LOCKED — v1.0

Research Synthesis v1.0 is the authoritative record of how the researched agent/code-agent ecosystem informs our implementation. It deliberately separates external inspiration from our internal architecture and preserves the locked security, behavior, validation and project-governance boundaries.

— END OF RESEARCH SYNTHESIS v1.0 —
