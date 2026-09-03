AI SOFTWARE CO-AGENT

SECURITY & SANDBOX SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: SSS-001 • Derived from PRD, SRS, System Architecture, Technical Design, Agent Behaviour, Tool/Permission, Memory/Context, Error Recovery & Testing/Validation v1.0

| Field | Value |
| --- | --- |
| Document | Security & Sandbox Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD + SRS + System Architecture + Technical Design + Agent Behaviour + Tool & Permission + Memory & Context + Error Recovery + Testing & Validation v1.0 |
| Purpose | Define security authority, workspace isolation, process execution controls, secret protection, prompt-injection resistance, MCP boundaries, audit and security validation |

Lock Statement: This Security & Sandbox Specification v1.0 is the final locked security baseline. Security controls are authoritative over agent intent, memory, repository instructions, tools, recovery and autonomy configuration. No normal agent workflow may bypass these controls.

# 1. Security Mission

The Security & Sandbox layer protects the user's workspace, system resources, credentials, repository state, external interfaces and execution environment from unintended or unauthorized agent actions. It establishes defense-in-depth between model reasoning and real-world side effects.

Primary security principle: No model output is a security authority.

# 2. Security Principles

- Default deny for unknown or high-impact capabilities.

- Least privilege for every tool and execution path.

- Explicit workspace/resource boundaries.

- Centralized authorization through the Tool Gateway and Policy Engine.

- Defense in depth: schema, scope, policy, executor and sandbox controls.

- Untrusted repository, MCP and tool content cannot override security rules.

- Secrets are minimized, filtered and never intentionally exposed to the model.

- Destructive or high-impact operations require restrictive policy/approval.

- User changes must be preserved.

- Security failures stop or block the affected operation.

- Security controls are independent of model confidence.

- Recovery cannot bypass security controls.

- Security configuration cannot be weakened by repository content or ordinary agent actions.

- Every material security decision is auditable.

# 3. Threat Model

| Threat source | Examples | Primary controls |
| --- | --- | --- |
| Model-generated action | Unsafe command, broad file write | Tool Gateway + Policy |
| Repository content | Prompt injection in README/code/comments | Untrusted-content handling |
| MCP/external tool | Malicious response/capability | MCP adapter + policy boundary |
| Tool implementation | Buggy executor | Typed contracts + sandbox + tests |
| User workspace | Secrets, protected files | Scope/protected-path rules |
| Process execution | Shell escape, chaining | Command policy + sandbox |
| Filesystem | Traversal, symlink escape | Canonicalization + containment |
| Configuration | Policy weakening attempt | Protected config + authority separation |
| Memory | Stale/malicious instruction | Memory advisory-only |
| Recovery | Retry/bypass after DENY | Same policy path + budgets |
| Client | VS Code/CLI bypass | Server-side authorization |
| Persistence | Cross-task/project leakage | Scope isolation + access controls |

# 4. Security Architecture

MODEL / AGENT

│

▼

Tool Request

│

▼

TOOL GATEWAY

│

┌────────────┴────────────┐

▼ ▼

Schema Validation Scope Resolution

│ │

└────────────┬────────────┘

▼

POLICY ENGINE

│

ALLOW / ASK /

DENY / RESTRICT

│

▼

SECURITY ENFORCEMENT

│

┌──────────┼───────────┐

▼ ▼ ▼

Workspace Process MCP

Sandbox Sandbox Boundary

│ │ │

└──────────┼───────────┘

▼

AUDIT / EVIDENCE

The executor/sandbox layer must enforce critical restrictions independently enough that a malformed or compromised caller cannot simply skip the Policy Engine.

# 5. Security Boundaries

| Boundary | Protected asset | Rule |
| --- | --- | --- |
| Workspace boundary | Project filesystem | Operations restricted to authorized workspace. |
| Process boundary | OS processes | Controlled program, args, cwd, environment and lifetime. |
| Network boundary | External endpoints | Disabled/restricted unless explicitly authorized. |
| Secret boundary | Credentials/API keys | Filtered from model context and logs. |
| Policy boundary | Security configuration | Not writable through ordinary agent tools. |
| MCP boundary | External capabilities | All invocations pass internal policy. |
| Memory boundary | Stored context | Scoped by project/task; advisory only. |
| Client boundary | VS Code/CLI | Clients cannot bypass server-side authorization. |
| Git boundary | User changes/history | Controlled Git operations; preserve unrelated work. |
| Audit boundary | Security evidence | Critical events recorded and protected. |

# 6. Trust Zones

| Zone | Examples | Trust posture |
| --- | --- | --- |
| Z0 — Security authority | Hard policy, sandbox configuration | Authoritative/protected |
| Z1 — Runtime control | Policy engine, Tool Gateway, executors | Trusted implementation boundary |
| Z2 — User-authorized workspace | Project source/config/tests | Trusted as data, not as policy |
| Z3 — Agent-generated content | Plans, patches, commands | Untrusted until validated/authorized |
| Z4 — External/MCP | Remote tool output/data | Untrusted |
| Z5 — Model output | Reasoning/tool proposals | Untrusted and non-authoritative |

# 7. Workspace Sandbox

- Each task receives an explicit authorized workspace root/scope.

- Filesystem operations must canonicalize/normalize paths before authorization.

- Relative paths are resolved against the authorized root.

- Path traversal sequences must not escape the root.

- Absolute paths outside the root are denied/restricted.

- Symlinks, junctions and equivalent filesystem indirections must not bypass effective containment.

- Protected paths require stricter policy.

- Workspace scope must not silently expand because a file references another directory.

- Temporary directories are separate resources and require explicit policy.

| Path condition | Expected behavior |
| --- | --- |
| Normal file inside workspace | Tool-specific policy evaluation. |
| Nested directory | Allowed within scope if policy permits. |
| Parent traversal | DENY. |
| Absolute outside workspace | DENY/RESTRICT. |
| Symlink to outside | DENY/RESTRICT after target resolution. |
| Protected config/secret | DENY/ASK/RESTRICT according to policy. |
| System directory | DENY by default. |
| User home/global config | DENY by default. |
| Ambiguous/unresolvable path | BLOCK/ASK; never guess. |

# 8. Protected Resources

- Security/policy configuration.

- Credential stores and secret files.

- Operating-system/system directories.

- Global user configuration unrelated to the task.

- VCS internals unless accessed through the authorized Git adapter.

- Production/deployment resources when not explicitly in scope.

- Sandbox configuration and enforcement binaries.

- Audit/security evidence stores where modification would compromise traceability.

Protected resource classification is policy-driven; implementation must support both built-in and configurable protected-resource rules.

# 9. Process Execution Sandbox

| Control | Requirement |
| --- | --- |
| Program | Must be recognized/authorized by execution policy. |
| Arguments | Schema/risk/scope checked; no blind string execution. |
| CWD | Must be within authorized scope unless explicitly permitted. |
| Environment | Allowlist/filter; secrets excluded by default. |
| Timeout | Mandatory bounded timeout. |
| Output | Bounded capture; large output becomes artifact. |
| Process tree | Termination should include relevant child processes where supported. |
| Privileges | No privilege escalation by default. |
| Concurrency | Bounded by task/runtime budget. |
| Network | Restricted unless explicitly authorized. |
| Cleanup | Temporary resources/processes cleaned up after execution. |

# 10. Shell & PowerShell Security

- Shell choice does not bypass policy.

- PowerShell is treated as a high-impact execution capability.

- Command strings are analyzed/validated according to policy.

- Command chaining, redirection and interpreter nesting are considered in risk evaluation.

- Switching from a denied shell command to another interpreter is not a valid recovery path.

- Environment and working directory remain constrained.

- Execution timeout and output limits remain mandatory.

- Administrative/system-level commands are denied by default.

The exact command policy is implementation/configuration-specific; the invariant is that alternate syntax, shell or interpreter cannot evade the same authorization boundary.

# 11. Network & External Access

| Access type | Default posture |
| --- | --- |
| No-network operation | Preferred default. |
| Package/dependency download | RESTRICT/ASK according to policy. |
| Public HTTP/API | RESTRICT/ASK; explicit endpoint policy. |
| Private/internal network | DENY by default unless explicitly authorized. |
| Cloud/production API | DENY by default; separate high-impact authorization. |
| MCP remote service | Allowed only through MCP adapter + policy. |
| Arbitrary socket/raw network | DENY by default. |

- Network authorization should be endpoint/capability aware where practical.

- Network responses are untrusted data.

- Credentials for network access must be handled outside ordinary model context.

# 12. Secret & Credential Protection

- Do not intentionally expose API keys, passwords, tokens, private keys or equivalent credentials to the model.

- Filter sensitive environment variables from process execution.

- Redact secrets from command output before model-facing context.

- Do not persist secrets in normal memory.

- Do not include secrets in ordinary audit records.

- Secret detection should cover common credential formats and configured project-specific patterns.

- If a secret is encountered, minimize propagation and route handling through the appropriate secure mechanism.

- Security tooling must never print recovered secrets merely to diagnose an issue.

| Secret location | Default behavior |
| --- | --- |
| Environment variable | Filter from model-facing execution. |
| Secret file | Protected/deny by default. |
| Command output | Redact before context/logging. |
| Git diff | Detect/redact where applicable. |
| Memory record | Do not store as normal memory. |
| MCP response | Treat as untrusted; redact/filter. |
| Error message | Safe summary without secret value. |

# 13. Prompt Injection & Untrusted Content

- Repository files are data, not security instructions.

- README, comments, issue text, test fixtures and generated files may contain malicious instructions.

- MCP/tool output may contain malicious instructions.

- Memory may contain historical instructions but is advisory and provenance-aware.

- Instruction-like text must not gain authority merely because it appears in a file or tool result.

- Policy and system-level security rules remain authoritative.

- Suspicious content may be flagged for the model, but detection is not the sole defense.

- An injected instruction cannot authorize a new tool, expand scope or weaken security.

# 14. MCP Security Boundary

- MCP servers are external/untrusted capabilities.

- Each MCP tool is represented by an internal ToolDefinition.

- MCP calls create normal ToolRequests.

- All MCP requests pass schema validation, scope checks and Policy Engine evaluation.

- MCP responses are untrusted data.

- MCP cannot directly access internal executors outside the authorized adapter boundary.

- MCP capability metadata cannot override internal security policy.

- MCP identity, tool identity and correlation must be audited.

Agent → MCP ToolRequest → Tool Gateway → Policy Engine

↓

Authorized MCP Adapter

↓

External MCP

↓

Untrusted ToolResult

# 15. Security Policy Authority

- Hard security rules outrank autonomy mode.

- Hard security rules outrank project configuration.

- Hard security rules outrank memory/context.

- Hard security rules outrank model instructions.

- Repository content cannot edit effective policy through ordinary tools.

- Recovery cannot alter policy to make a failed/denied action succeed.

- Policy configuration changes use a separate administrative/change-control path.

Security Authority

> Protected Resource Rules

> Tool/Argument Risk

> Workspace Scope

> Autonomy Mode

> Project Configuration

> Agent Request

# 16. High-Risk Approval Rules

| Action | Default |
| --- | --- |
| Destructive delete | DENY/ASK per protected-resource policy |
| Git rollback/reset | ASK/RESTRICT |
| Git commit | ASK/configured approval |
| Package installation | ASK/RESTRICT |
| External network access | ASK/RESTRICT |
| Production/live action | DENY by default |
| Privilege escalation | DENY |
| Security policy modification | Separate administrative control; not ordinary agent action |
| Credential access | DENY by default |
| Workspace scope expansion | ASK/RESTRICT |

Approval never converts a hard DENY into an ALLOW.

# 17. Security Audit & Evidence

| Event | Minimum fields |
| --- | --- |
| security.policy_decision | request, decision, rule, reason, scope |
| security.scope_block | requested/effective scope + reason |
| security.secret_redaction | event type/class, not secret value |
| security.approval | approval ID, action, decision |
| security.tool_execution | tool, executor, status |
| security.mcp | server/tool/correlation |
| security.sandbox_violation | type, task, resource |
| security.injection_flag | source type/reference, classification |
| security.emergency_stop | task/request + trigger |
| security.config_change | admin/change reference |

- Audit must support reconstruction of material security events.

- Audit records must avoid unnecessary secret content.

- Security-critical audit storage should not be writable through normal task tools.

# 18. Defense-in-Depth Enforcement

| Layer | Security responsibility |
| --- | --- |
| Input/schema | Reject malformed requests. |
| Scope resolver | Enforce canonical resource boundaries. |
| Policy Engine | Authorize capability/risk/scope. |
| Tool Gateway | Single routing boundary. |
| Executor | Enforce operation-specific restrictions. |
| Sandbox | Limit OS/resource effects. |
| Output filter | Prevent secret/untrusted leakage. |
| Audit | Record critical security events. |
| Validation | Detect unsafe/incorrect outcomes. |

A security property should not depend on a single model-generated instruction being followed correctly.

# 19. VS Code / CLI / Client Security

- Client UI is not a trusted authorization boundary by itself.

- Server/runtime must revalidate tool requests.

- Direct executor endpoints must not be exposed as unrestricted client APIs.

- Client-provided paths and commands are untrusted inputs.

- Client cancellation must propagate to the runtime.

- Authentication/session identity, where applicable, must be validated independently of model text.

# 20. Task & Project Isolation

- Task context must not automatically grant access to another project.

- Project memory is isolated by project identity/scope.

- Artifacts are associated with task/project scope.

- Workspace roots are task-authorized resources.

- Cross-task file access requires explicit scope.

- Cross-project MCP/external access requires separate policy.

- Persistent stores must prevent accidental cross-project retrieval.

# 21. Git & Change Safety

- Pre-existing user changes are protected.

- Agent changes should be distinguishable through task state/checkpoints where possible.

- Git operations follow Tool & Permission policy.

- Reset/clean/checkout-like destructive actions are restricted.

- Rollback must target task-owned changes.

- Security checks must inspect actual resulting diff, not only the intended patch.

# 22. Cancellation & Emergency Stop

- Emergency stop has highest runtime priority over normal task continuation.

- Cancellation prevents new privileged actions.

- Active processes should be terminated where supported.

- Pending approvals become invalid for the cancelled task.

- Recovery loops terminate.

- Security/audit evidence already generated is preserved.

- Cancellation does not trigger automatic rollback unless explicitly configured and safely authorized.

# 23. Resource & Abuse Controls

| Resource | Control |
| --- | --- |
| CPU/time | Execution timeouts and task budgets |
| Memory | Process/runtime resource limits where supported |
| Disk | Output/temp/artifact limits |
| Processes | Concurrency/process-count bounds |
| Files | Scope + file-count/size limits where applicable |
| Output | Bounded capture |
| Network | Endpoint/capability restrictions |
| LLM calls | Task/model budgets |
| Tool calls | Permission/execution budgets |
| Recovery | Attempt/time/scope budgets |

# 24. Security Configuration

- Security configuration has a protected schema.

- Invalid configuration fails closed for security-critical settings.

- Policy changes are versioned/audited.

- Normal repository write tools cannot silently alter effective security policy.

- Configuration precedence must preserve hard security invariants.

- Default configuration must be safe for first run.

- Sensitive configuration values are protected from model context.

# 25. Secure Startup & Shutdown

| Phase | Required behavior |
| --- | --- |
| Startup | Validate security configuration, tool registry and sandbox availability. |
| Workspace bind | Establish canonical authorized workspace scope. |
| Tool registration | Validate schemas/capabilities. |
| Policy load | Load and validate rules. |
| Runtime | Enforce policy and sandbox for every relevant operation. |
| Shutdown | Terminate/clean active task processes and preserve audit state. |
| Crash recovery | Resume only from safe persisted state; do not auto-run privileged actions without reauthorization. |

# 26. Security Failure Behaviour

| Failure | Required response |
| --- | --- |
| Policy engine unavailable | Fail closed for protected/high-impact actions. |
| Sandbox unavailable | Do not execute actions requiring sandbox guarantee. |
| Scope resolver failure | Block affected filesystem/resource operation. |
| Secret filter failure | Block model-facing output where secret exposure is possible. |
| Audit failure | Security-critical actions may be blocked according to policy. |
| MCP adapter failure | Block/fail external action; no direct fallback bypass. |
| Security config invalid | Fail closed for security-sensitive capability. |
| Injection detected | Treat content as untrusted; do not grant authority. |
| Unauthorized client request | Reject at runtime boundary. |
| Privilege escalation attempt | DENY and audit. |

# 27. Mandatory Security Test Suite

| ID | Scenario | Expected result |
| --- | --- | --- |
| ST-SBX-001 | Path traversal | Outside-workspace access is blocked. |
| ST-SBX-002 | Symlink escape | Effective target outside workspace is blocked. |
| ST-SBX-003 | Protected path | Protected resource cannot be modified through ordinary tool. |
| ST-EXE-001 | Shell chaining | Denied command cannot be bypassed with chaining. |
| ST-EXE-002 | Interpreter switch | Alternate shell cannot bypass policy. |
| ST-EXE-003 | Environment leak | Secrets are filtered from model context. |
| ST-NET-001 | Unauthorized network | External access is blocked/restricted. |
| ST-MCP-001 | MCP bypass | MCP cannot bypass internal policy. |
| ST-MEM-001 | Memory authorization | Memory cannot authorize denied tool. |
| ST-INJ-001 | Repository injection | Malicious instructions do not become authority. |
| ST-INJ-002 | MCP injection | Malicious tool output does not authorize actions. |
| ST-CLI-001 | Client bypass | Direct client request cannot skip policy. |
| ST-POL-001 | Policy tamper | Agent cannot weaken hard security rules. |
| ST-GIT-001 | User changes | Destructive Git operation cannot overwrite unrelated changes. |
| ST-CAN-001 | Emergency stop | No new privileged action after stop. |

# 28. Security Incident Handling

- Classify security failures separately from ordinary engineering failures.

- Stop affected privileged execution.

- Preserve relevant audit/evidence.

- Do not automatically repair around the security control.

- Surface the security condition clearly.

- Require authorized human/security intervention where appropriate.

- Record remediation/change-control outcome.

- Add a regression/security fixture for confirmed bypasses when practical.

# 29. Security & Sandbox Invariants

- SEC1: No model output is authorization.

- SEC2: No unknown capability executes.

- SEC3: Every executable action passes the central authorization path.

- SEC4: Hard security rules cannot be overridden by autonomy settings.

- SEC5: Repository content cannot override security policy.

- SEC6: Memory/context cannot authorize tools.

- SEC7: Recovery cannot bypass security controls.

- SEC8: MCP cannot bypass security controls.

- SEC9: Workspace containment is enforced after path normalization/resolution.

- SEC10: Protected resources are never silently broadened into scope.

- SEC11: Secrets are not intentionally exposed to normal model context.

- SEC12: Client interfaces cannot bypass server/runtime authorization.

- SEC13: Security-critical failures fail closed or block the affected operation.

- SEC14: Emergency stop prevents new privileged actions.

- SEC15: Material security decisions are auditable.

# 30. Security & Sandbox Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| SSS-A01 | Authorization | All executable actions use central policy authorization. |
| SSS-A02 | Workspace | Filesystem containment and protected paths are enforced. |
| SSS-A03 | Process | Program/args/cwd/env/time controls are enforced. |
| SSS-A04 | Network | External access is restricted by policy. |
| SSS-A05 | Secrets | Secret filtering/redaction prevents normal model exposure. |
| SSS-A06 | Injection | Repository/MCP/tool injection cannot gain authority. |
| SSS-A07 | MCP | MCP uses the same security boundary. |
| SSS-A08 | Client | VS Code/CLI cannot bypass server-side policy. |
| SSS-A09 | Recovery | Recovery cannot bypass DENY/security. |
| SSS-A10 | Isolation | Task/project resources are isolated. |
| SSS-A11 | Git | User changes are protected. |
| SSS-A12 | Stop | Cancellation/emergency stop prevents new privileged actions. |
| SSS-A13 | Audit | Critical security events are traceable. |
| SSS-A14 | Fail closed | Critical security-control failures block unsafe execution. |
| SSS-A15 | Testing | Mandatory security suite passes before release. |

# 31. Traceability to Locked Baselines

| Baseline | Security/Sandbox impact |
| --- | --- |
| PRD v1.0 | User control, safety, trusted execution and responsible autonomy. |
| SRS v1.0 | Security, sandbox, permissions, secrets and isolation requirements. |
| System Architecture v1.0 | Central policy, gateway, executor and sandbox boundaries. |
| Technical Design v1.0 | Workspace/process/MCP/security component implementation boundaries. |
| Agent Behaviour v1.0 | No bypass, safe tool use, cancellation and evidence behavior. |
| Tool & Permission v1.0 | ALLOW/ASK/DENY/RESTRICT authorization model. |
| Memory & Context v1.0 | Untrusted context, secret handling and memory authority. |
| Error Recovery v1.0 | Security failures are blocked; recovery follows normal policy. |
| Testing & Validation v1.0 | Release-blocking security tests and acceptance gates. |
| Repository Blueprint v1.0 | Physical placement of security/sandbox modules and tests. |

# 32. Implementation Mapping

| Area | Expected implementation modules |
| --- | --- |
| Security models | src/security/models.py |
| Security policy | src/security/policy.py / src/policy/... |
| Path/scope | src/security/scope.py |
| Sandbox | src/security/sandbox.py / src/execution/sandbox.py |
| Process controls | src/security/process.py |
| Secret filtering | src/security/secrets.py |
| Injection handling | src/security/injection.py |
| MCP security | src/security/mcp.py / src/tools/mcp/... |
| Audit | src/security/audit.py / src/audit/... |
| Security config | config/security/... |
| Security tests | tests/security/... |
| Sandbox fixtures | tests/fixtures/security/... |

Exact filenames may evolve through implementation change control. Security boundaries, authority rules and invariants are locked.

# 33. Threat-to-Control Matrix

| Threat | Control | Validation |
| --- | --- | --- |
| Prompt injection | Untrusted-content handling + policy authority | ST-INJ |
| Path traversal | Canonicalization + containment | ST-SBX |
| Symlink escape | Effective target resolution | ST-SBX |
| Command bypass | Central policy + executor controls | ST-EXE |
| Secret leakage | Filtering/redaction | ST-EXE/ST-MEM |
| MCP malicious output | MCP boundary + untrusted data | ST-MCP/ST-INJ |
| Policy tampering | Protected configuration + fail-closed | ST-POL |
| Client bypass | Server-side authorization | ST-CLI |
| Recovery bypass | Same policy path | RT/ST |
| User-change loss | Git/change controls | ST-GIT |
| Cross-project leakage | Isolation/scoped persistence | ST-MEM |
| Resource abuse | Budgets/timeouts/limits | PT/ST |

# 34. Change Control

- Any change to hard security invariants requires explicit security/architecture review.

- New tools with filesystem/process/network/destructive effects require threat analysis and security tests.

- Sandbox implementation changes require regression testing.

- Changes to secret handling require security review.

- Changes to MCP capabilities require boundary and injection testing.

- Changes to protected-path rules require policy/security review.

- Security test removal/weakening requires formal justification and approval.

- No implementation shortcut may create a direct executor path around the Tool Gateway.

# 35. Final Status

STATUS: FINAL / LOCKED — v1.0

This Security & Sandbox Specification v1.0 is the authoritative security baseline for the AI Software Co-Agent. It defines trust zones, workspace/process/network isolation, secret protection, prompt-injection resistance, MCP/client boundaries, policy authority, approvals, audit, fail-closed behavior, emergency stop, security testing and release-blocking invariants.

— END OF SECURITY & SANDBOX SPECIFICATION v1.0 —
