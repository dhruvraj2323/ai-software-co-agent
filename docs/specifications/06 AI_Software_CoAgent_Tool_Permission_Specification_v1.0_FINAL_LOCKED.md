AI SOFTWARE CO-AGENT

TOOL & PERMISSION SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: TPS-001 • Derived from PRD, SRS, System Architecture, Technical Design & Agent Behaviour v1.0

| Field | Value |
| --- | --- |
| Document | Tool & Permission Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Source baselines | PRD + SRS + System Architecture + Technical Design + Agent Behaviour v1.0 |
| Purpose | Define tool contracts, capability metadata, permission evaluation, approval, execution routing and audit behavior |

Lock Statement: This Tool & Permission Specification v1.0 is the final locked authorization baseline. Every AI-requested tool action must conform to these contracts, policy decisions, scope rules and execution boundaries unless formally changed.

# 1. Purpose & Security Objective

The Tool & Permission layer is the authoritative control boundary between AI reasoning and executable side effects. The model may propose actions, but it does not receive direct filesystem, process, Git, network or external-tool authority. Actions become executable only after explicit tool validation and Policy Engine evaluation.

Primary rule: LLM intent is not authorization.

# 2. Core Principles

- Every executable capability is an explicit tool.

- Every tool has a typed input/output contract.

- Every tool request passes through one Tool Gateway.

- Every tool request is evaluated by one authoritative Policy Engine before execution.

- Policy decisions consider tool, arguments, scope, resource, risk and autonomy mode.

- ALLOW, ASK, DENY and RESTRICT are the only policy outcomes.

- ASK pauses the affected action until appropriate approval.

- DENY cannot be converted into execution by the model.

- RESTRICT narrows an action to an allowed scope/capability.

- Built-in and MCP tools use the same authorization path.

- Tool execution returns normalized structured results.

- Important requests, decisions, approvals and results are auditable.

- Security policy cannot be weakened by normal agent tools.

- Tool permission is capability-based and deny-by-default for unknown/high-risk actions.

# 3. Authorization Architecture

MODEL / AGENT ROLE

│

▼

Tool Intent

│

▼

ToolRequest construction

│

▼

Schema + Argument Validation

│

▼

TOOL GATEWAY

│

▼

POLICY / PERMISSION ENGINE

│

┌───┼───────────────┐

▼ ▼ ▼

ALLOW ASK DENY

│ │ │

│ ▼ └── Audit + Result

│ Approval

│ │

└────┴── approved ──┐

▼

AUTHORIZED EXECUTOR

│

▼

NORMALIZED RESULT

│

▼

Audit + State

No model-facing component may call an executor directly. No executor may be treated as an implicit policy engine.

# 4. Tool Contract Model

| Field | Required behavior |
| --- | --- |
| tool_id | Stable unique identifier. |
| name | Human-readable tool name. |
| description | Clear purpose and intended use. |
| version | Tool contract/version identifier. |
| input_schema | Typed/schema-validated arguments. |
| output_schema | Typed normalized result. |
| capability | Capability category. |
| risk_level | Baseline risk classification. |
| side_effects | Read/write/execute/destructive/external effects. |
| resource_scope | Workspace/file/process/network/resource scope. |
| approval_profile | Conditions that may require ASK. |
| executor | Authorized implementation boundary. |
| origin | Built-in or MCP/external source. |
| enabled | Whether capability is available under current configuration. |

# 5. Tool Capability Taxonomy

| Capability | Purpose | Effect | Baseline risk | Scope |
| --- | --- | --- | --- | --- |
| workspace.read | Read files/directories | Read | Low | Workspace-scoped |
| workspace.write | Create/update files | Write | Medium | Workspace-scoped |
| workspace.delete | Delete files | Destructive | High | Protected-path rules |
| search.text | Search repository text | Read | Low | Workspace-scoped |
| repository.map | Read repository structure/map | Read | Low | Workspace-scoped |
| repository.symbols | Read syntax/symbol data | Read | Low | Workspace-scoped |
| terminal.process | Run process/command | Execute | Medium/High | CWD + argument policy |
| terminal.powershell | Run PowerShell | Execute | High | Command-aware policy |
| testing.run | Run test command | Execute | Medium | Project/workspace scope |
| testing.lint | Run lint command | Execute | Medium | Project/workspace scope |
| testing.build | Run build command | Execute | Medium/High | Project/workspace scope |
| git.status | Read Git status | Read | Low | Repository-scoped |
| git.diff | Read Git diff | Read | Low | Repository-scoped |
| git.checkpoint | Create checkpoint | Write | Medium | Repository-scoped |
| git.rollback | Rollback task-owned changes | Destructive | High | Protected user changes |
| git.commit | Create commit | Write | High | Explicit approval/config |
| mcp.invoke | Invoke external MCP tool | External | Variable | Same central policy |

# 6. Tool Request Lifecycle

| ID | Stage | Required behavior |
| --- | --- | --- |
| TP-001 | Intent | Agent determines an external action is required. |
| TP-002 | Selection | Agent selects the narrowest appropriate registered tool. |
| TP-003 | Construction | Typed ToolRequest is constructed. |
| TP-004 | Validation | Tool and argument schemas are validated. |
| TP-005 | Scope | Workspace/resource scope is normalized and checked. |
| TP-006 | Policy | Policy Engine evaluates request. |
| TP-007 | Approval | ASK requests pause for human approval. |
| TP-008 | Execution | Authorized executor performs only approved operation. |
| TP-009 | Result | Executor returns normalized ToolResult. |
| TP-010 | Audit | Request, policy, approval and result are recorded as applicable. |
| TP-011 | Continuation | Orchestrator decides continue/recover/block/stop from result. |

# 7. ToolRequest Contract

ToolRequest {

request_id: UUID

task_id: UUID

correlation_id: UUID

tool_id: string

tool_version: string

arguments: object

requested_scope: Scope

autonomy_mode: AutonomyMode

source: Agent | Recovery | User

created_at: datetime

}

- Arguments must be schema-valid for the selected tool.

- requested_scope must be normalized before policy evaluation.

- Recovery requests use the same request contract.

- User-originated requests still pass policy when they cause agent-controlled side effects.

- Unknown tool IDs are rejected.

# 8. ToolResult Contract

ToolResult {

request_id: UUID

success: bool

status: SUCCESS | FAILED | DENIED | BLOCKED | CANCELLED

output: object | null

error: ErrorRecord | null

exit_code: int | null

duration_ms: int | null

evidence_ref: string | null

scope_effect: ScopeEffect

created_at: datetime

}

Tool results are evidence. The model may interpret them, but it cannot rewrite the underlying execution facts.

# 9. Policy Decision Model

| Decision | Meaning | Execution |
| --- | --- | --- |
| ALLOW | Action is authorized under current policy | Execute within evaluated scope. |
| ASK | Action may be permitted but requires human approval | Pause; execute only if approved. |
| DENY | Action is prohibited | Never execute. |
| RESTRICT | Action is allowed only under narrower controls | Transform/constrain to the policy-approved scope or require approval if the requested form cannot be safely constrained. |

A policy decision must include reason, rule identity, evaluated scope and relevant risk information.

# 10. Policy Evaluation Inputs

| Input | Examples |
| --- | --- |
| Tool identity | workspace.write, terminal.powershell, git.rollback |
| Arguments | Path, command, flags, target resource |
| Autonomy mode | CHAT, PLAN, ASSISTED IMPLEMENT, SUPERVISED AUTO, AUTONOMOUS, RESTRICTED |
| Workspace root | Authorized project root |
| Target resource | File, directory, process, repository, external endpoint |
| Path classification | Normal, protected, outside workspace |
| Risk | Read, write, execute, destructive, sensitive, external |
| Origin | Built-in, recovery, MCP |
| Task scope | Expected files/resources/actions |
| Current state | Git dirty state, task state, cancellation, budget |
| Policy configuration | Rules and approval profiles |

# 11. Policy Precedence

HARD SECURITY RULES

↓

PROTECTED RESOURCE RULES

↓

TOOL / ARGUMENT RISK RULES

↓

WORKSPACE / TASK SCOPE

↓

AUTONOMY MODE

↓

PROJECT / USER CONFIGURATION

↓

MODEL REQUEST

- Lower layers cannot override higher layers.

- Model-generated instructions are the lowest authorization input.

- Project files cannot modify hard security policy.

- Memory cannot modify hard security policy.

- MCP metadata cannot modify hard security policy.

- Changing autonomy mode does not disable hard security rules.

# 12. Scope & Resource Controls

- Normalize all filesystem paths before authorization.

- Require containment within the authorized workspace for workspace-scoped operations.

- Classify protected paths before execution.

- Do not allow path traversal to escape the workspace.

- Do not allow symlink/junction behavior to bypass containment checks where applicable.

- Limit terminal working directory to an authorized location.

- Limit Git operations to the intended repository.

- Limit process execution arguments according to tool-specific policy.

- External/MCP resources require explicit policy treatment.

| Scope result | Behavior |
| --- | --- |
| IN_SCOPE | Continue policy evaluation. |
| OUT_OF_SCOPE | DENY or ASK according to explicit policy; never silently broaden. |
| PROTECTED | DENY/ASK/RESTRICT according to hard policy. |
| AMBIGUOUS | ASK or BLOCK; do not guess. |
| STALE | Refresh state/context before proceeding where applicable. |

# 13. Autonomy Policy Profiles

| Mode | Default behavior | Permission posture |
| --- | --- | --- |
| CHAT | No side-effect tools. | Read/explain only. |
| PLAN | Repository inspection and planning. | No mutation/execute tools unless explicitly configured for safe inspection. |
| ASSISTED IMPLEMENT | Low-risk reads + controlled writes. | High-risk commands/changes ASK. |
| SUPERVISED AUTO | Low/medium-risk approved workflow. | Configured risky actions ASK. |
| AUTONOMOUS | Longer bounded workflow. | Hard restrictions and budgets remain active. |
| RESTRICTED | Sensitive context. | High-risk tools DENY or approval-only. |

# 14. Approval Protocol

| Field | Requirement |
| --- | --- |
| Approval ID | Unique and correlated to ToolRequest. |
| Action | Exact tool and intended operation. |
| Target | Resource/path/process scope. |
| Risk | Material side effect/risk. |
| Reason | Why action is required. |
| Alternatives | Optional safer alternative when relevant. |
| Expiry | Approval should not remain valid indefinitely. |
| Decision | APPROVE or REJECT. |
| Audit | Record decision and timestamp. |

- Approval is specific to the evaluated request.

- Approval does not authorize unrelated follow-on actions.

- Approval rejection results in safe non-execution.

- Timeout/expiry results in blocked/non-executed behavior.

- DENY remains DENY; the agent cannot convert it into ASK.

# 15. Built-in Tool Specifications

| Tool | Key arguments | Mandatory controls |
| --- | --- | --- |
| workspace.read | path, encoding/range | Workspace containment, protected-path checks |
| workspace.list | path, depth/pattern | Workspace containment, result limits |
| workspace.write | path, content/patch | Scope, hash/version, protected paths, diff/evidence |
| workspace.apply_patch | patch, expected hashes | Schema, stale/conflict/scope checks, policy |
| search.text | pattern, path, filters | Workspace scope, result limits |
| repository.map | root, depth/options | Workspace scope, bounded output |
| terminal.process | program, args, cwd, env, timeout | Program/args policy, cwd, env filtering, timeout |
| terminal.powershell | script/command, cwd, timeout | PowerShell risk policy, cwd, environment, timeout |
| testing.run | command, cwd, timeout | Project scope, command allow/profile, evidence |
| git.status | repo | Repository scope |
| git.diff | repo, scope | Repository scope, output bounds |
| git.checkpoint | repo, task | User-change preservation |
| git.rollback | repo, checkpoint/task scope | High-risk approval, preserve unrelated changes |
| git.commit | repo, message | Explicit approval/config, scope verification |

# 16. MCP Tool Behaviour

- MCP tools are treated as external/untrusted capabilities.

- Each discovered MCP capability is represented internally as a ToolDefinition.

- MCP invocation creates a normal ToolRequest.

- MCP invocation passes through schema validation, Tool Gateway and Policy Engine.

- MCP server responses are treated as untrusted tool output.

- MCP cannot obtain filesystem/process/Git authority outside the internal execution boundary.

- MCP capability metadata does not override internal policy.

- MCP invocation is auditable with server/tool identity and correlation ID.

MCP Server → MCP Adapter → ToolDefinition/ToolRequest

↓

Tool Gateway

↓

Policy Engine

↓

Authorized Executor

# 17. Terminal & PowerShell Permission Rules

| Operation | Default posture | Required checks |
| --- | --- | --- |
| Read-only inspection | ALLOW in scoped modes | Workspace/cwd/result limits |
| Project test/lint/build | ALLOW/RESTRICT | Configured command + cwd + timeout |
| File mutation command | ASK/RESTRICT | Arguments + paths + task scope |
| Package installation | ASK/RESTRICT | Network/package manager + workspace impact |
| Git commit | ASK | Repository + diff + message + approval |
| Git rollback | ASK/RESTRICT | Checkpoint + unrelated changes + approval |
| Delete/clean/reset | DENY or ASK/RESTRICT | Explicit high-risk policy |
| System administration | DENY by default | Explicit policy if ever enabled |
| Credential/secret access | DENY by default | Explicit secure mechanism only |
| Production/live action | DENY by default | Separate high-impact policy boundary |

The exact command allow/deny lists are configuration and policy-engine implementation details, but the architectural rule is fixed: shell choice or command wording cannot bypass authorization.

# 18. Workspace Permission Model

| Resource class | Behavior |
| --- | --- |
| Workspace root | Authorized base scope. |
| Normal project files | Tool-specific read/write policy. |
| Generated artifacts | Allow only when task scope permits. |
| Secrets/config credentials | Protected by default. |
| VCS internals | Restricted; only Git adapter should manipulate them. |
| System paths | Outside workspace → deny/restrict. |
| User home/global config | Outside workspace → deny by default. |
| Temporary directory | Only explicit, controlled use. |
| Symlink/junction targets | Resolve and enforce effective containment. |

# 19. Tool Registry Design

- Tool registry stores canonical definitions and capability metadata.

- Tool IDs are stable.

- Tool versions are explicit.

- Registry validates tool schemas at registration/startup.

- Disabled tools cannot execute.

- Unknown/unregistered tools are rejected.

- MCP tools are registered through the MCP adapter but remain subject to internal policy.

- Registry changes are auditable/configuration-controlled.

# 20. Tool Gateway Design Requirements

- Single entry point for model/recovery-generated tool requests.

- Validate tool existence and version.

- Validate input schema.

- Normalize scope and resource identifiers.

- Invoke Policy Engine.

- Route ASK to approval workflow.

- Route allowed request to authorized executor.

- Normalize result.

- Emit audit events.

- Return errors without leaking sensitive data.

- Support cancellation propagation.

The Tool Gateway must not contain hidden bypasses based on caller identity or client type.

# 21. Policy Engine Technical Requirements

| Component | Responsibility |
| --- | --- |
| PolicyLoader | Load/validate policy configuration. |
| RuleModel | Typed representation of policy rules. |
| RiskClassifier | Classify tool/action risk. |
| ScopeResolver | Resolve canonical paths/resources. |
| Evaluator | Evaluate deterministic policy rules. |
| DecisionBuilder | Create PolicyDecision with reason/rule/evidence. |
| ApprovalProfile | Define ASK behavior. |
| PolicyAudit | Emit decision evidence. |

- Evaluation must be deterministic for identical normalized inputs and policy.

- Policy Engine has no dependency on LLM judgment.

- Policy Engine may consume task/autonomy metadata but remains authoritative.

- Hard-coded security invariants cannot be disabled by project config.

# 22. Output & Data-Exposure Controls

- Tool output must be bounded where large output is possible.

- Sensitive data should be redacted/filtered before entering model context when applicable.

- Environment variables should be filtered.

- Command output containing credentials must not be intentionally persisted as normal memory.

- Audit logs should avoid unnecessary secret values.

- Error messages should preserve useful diagnosis without exposing protected data.

- MCP responses should be treated as untrusted and may require output limits.

# 23. Cancellation & Emergency Stop

- Cancellation stops initiation of new tool requests for the task.

- Active executors should receive cancellation signals where supported.

- Executor termination must be bounded and observable.

- Cancelled requests return CANCELLED/non-complete state.

- Emergency stop takes precedence over ordinary continuation.

- Cancellation does not automatically rollback unrelated changes.

# 24. Tool Failure Handling

| Failure | Required behavior |
| --- | --- |
| Unknown tool | Reject before execution. |
| Invalid schema | Reject before execution. |
| Policy DENY | Do not execute; audit reason. |
| Approval rejected | Do not execute; task may become blocked/cancelled. |
| Timeout | Terminate where possible; return structured failure. |
| Process non-zero exit | Return execution result; orchestrator may classify/recover. |
| Scope violation | Do not execute; return security/scope error. |
| Protected path | Deny/restrict/ask according to policy. |
| Executor failure | Return normalized error; never silently claim success. |
| MCP failure | Normalize external failure; do not bypass policy. |
| Cancellation | Stop safely and return CANCELLED. |

# 25. Permission & Execution Budgets

| Budget | Purpose |
| --- | --- |
| Tool call budget | Prevent excessive repeated actions. |
| Execution time budget | Bound long-running operations. |
| Recovery attempt budget | Bound automatic repair. |
| Scope budget | Prevent unplanned file/resource expansion. |
| Output budget | Prevent oversized command/tool output. |
| Approval lifetime | Prevent stale authorization. |
| Context budget | Prevent excessive tool output entering model context. |

Budget exhaustion is a controlled stop/block condition, not permission to bypass controls.

# 26. Audit & Traceability

| Event | Minimum audit data |
| --- | --- |
| tool.requested | request_id, task_id, tool_id, scope, correlation_id |
| policy.decided | request_id, decision, rule_id, reason |
| approval.requested | approval_id, request_id, target, risk |
| approval.decided | approval_id, decision, timestamp |
| tool.started | request_id, executor |
| tool.completed | request_id, status, duration, evidence_ref |
| tool.failed | request_id, error category/evidence |
| scope.blocked | request_id, attempted scope, reason |
| mcp.invoked | server/tool identity + request correlation |
| cancelled | task/request ID + cancellation source |

Audit records should be sufficient to reconstruct who/what requested an action, what policy decided, what executed and what result was produced.

# 27. Mandatory Security Test Areas

- Unknown-tool execution rejection.

- Invalid argument rejection.

- Path traversal rejection.

- Workspace boundary enforcement.

- Protected path enforcement.

- Symlink/junction containment checks.

- Shell/PowerShell command bypass attempts.

- Alternate-tool bypass attempts after DENY.

- Autonomy escalation attempts.

- Repository prompt-injection attempts.

- MCP policy bypass attempts.

- VS Code client bypass attempts.

- Secret/environment exposure checks.

- Approval replay/expiry checks.

- Recovery policy bypass attempts.

- Cancellation and executor termination behavior.

- False-completion after denied/failed tool actions.

# 28. Canonical Permission Scenarios

| Scenario | Expected path |
| --- | --- |
| Read project file | workspace.read inside root → policy ALLOW → execute. |
| Edit source file | workspace.apply_patch → schema/scope/hash → policy → execute if allowed/approved. |
| Run tests | testing.run configured project command → policy → execute → capture evidence. |
| Run arbitrary PowerShell | terminal.powershell → command risk evaluation → ASK/RESTRICT/DENY as configured. |
| Delete production-like file | workspace.delete → high-risk/protected evaluation → DENY or explicit ASK; never assume. |
| Git rollback | git.rollback → inspect checkpoint/user changes → high-risk approval → controlled rollback. |
| MCP database tool | MCP invoke → adapter → Tool Gateway → policy → authorized external execution only. |
| Policy denied terminal command | DENY → no execution; agent must not switch shells or rewrite command merely to evade. |
| Outside-workspace path | Scope resolver detects OUT_OF_SCOPE → no execution. |
| Approval rejected | No execution; task remains blocked/non-complete. |

# 29. Permission Invariants

- P1: No tool request without a registered tool.

- P2: No tool execution without schema validation.

- P3: No tool execution without Policy Engine decision.

- P4: DENY means no execution.

- P5: ASK means pause until appropriate approval.

- P6: RESTRICT cannot expand beyond policy-approved scope.

- P7: Model output cannot authorize itself.

- P8: MCP cannot bypass internal policy.

- P9: VS Code cannot bypass internal policy.

- P10: Recovery cannot bypass internal policy.

- P11: Unknown/ambiguous scope never defaults to unrestricted execution.

- P12: Hard security rules outrank configuration and model intent.

- P13: Tool results are evidence and cannot be rewritten by the agent.

- P14: Cancellation prevents further normal execution.

- P15: Permission budgets cannot be exceeded by changing tools or commands.

# 30. Tool & Permission Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| TPS-A01 | Explicit tools | All executable capabilities are represented as registered tools. |
| TPS-A02 | Single gateway | All AI/recovery tool calls enter through one Tool Gateway. |
| TPS-A03 | Policy enforcement | Every tool call receives a policy decision before execution. |
| TPS-A04 | Decision model | ALLOW/ASK/DENY/RESTRICT semantics are implemented and tested. |
| TPS-A05 | Scope | Workspace/resource scope is normalized and enforced. |
| TPS-A06 | Argument safety | Tool arguments are schema-validated and risk-evaluated. |
| TPS-A07 | Approval | ASK actions pause and require explicit approval. |
| TPS-A08 | MCP | MCP uses the same Tool Gateway/Policy Engine. |
| TPS-A09 | Execution | Executors perform only authorized operations. |
| TPS-A10 | Audit | Requests, decisions, approvals and results are traceable. |
| TPS-A11 | Cancellation | Running tool execution supports safe cancellation. |
| TPS-A12 | Security tests | Mandatory bypass/security tests pass. |
| TPS-A13 | No self-bypass | Agent cannot modify policy to authorize denied actions. |
| TPS-A14 | Evidence | Tool results and policy decisions are structured and usable by validation/reporting. |
| TPS-A15 | Determinism | Policy evaluation is deterministic for identical normalized inputs. |

# 31. Traceability to Locked Baselines

| Baseline | Tool/permission impact |
| --- | --- |
| PRD v1.0 | Controlled autonomy, safety, completion and user-control principles. |
| SRS v1.0 | Detailed tool, policy, terminal, security, lifecycle and audit requirements. |
| System Architecture v1.0 | Tool Gateway → Policy → Executor boundary. |
| Technical Design v1.0 | Concrete tool contracts, executors, policy components and interfaces. |
| Agent Behaviour v1.0 | Tool-use, approval, terminal, cancellation and behavioural invariants. |
| Memory & Context Specification v1.0 | Context authority and sensitive-output handling. |
| Error Recovery Specification v1.0 | Recovery must re-enter normal policy. |
| Security & Sandbox Specification v1.0 | Hard security and isolation rules. |
| Testing & Validation v1.0 | Permission/security test evidence. |
| Repository Blueprint v1.0 | Physical placement of tools/policy/execution modules. |

# 32. Implementation Mapping

| Area | Expected implementation modules |
| --- | --- |
| Tool contracts | src/tools/models.py / contracts.py |
| Tool registry | src/tools/registry.py |
| Tool Gateway | src/tools/gateway.py |
| Built-in tools | src/tools/builtin/... |
| MCP adapter | src/tools/mcp/... |
| Policy models | src/policy/models.py |
| Policy evaluator | src/policy/engine.py |
| Policy loader | src/policy/config.py |
| Scope resolver | src/policy/scope.py |
| Workspace executor | src/execution/workspace.py |
| Process executor | src/execution/process.py |
| PowerShell executor | src/execution/powershell.py |
| Sandbox interface | src/execution/sandbox.py |
| Approval | src/agent/approval.py or equivalent runtime service |
| Audit | src/audit/... |
| Tests | tests/unit/tools, tests/unit/policy, tests/integration, tests/security |

Exact filenames may evolve during implementation only through repository/technical change control; the architectural responsibilities and single authorization path are locked.

# 33. Change Control

- Adding a new high-impact capability requires a tool definition, risk classification, policy rules, executor boundary and security tests.

- Changing a tool contract requires schema/version updates and regression tests.

- Adding a new execution route requires architecture/security review.

- Changing policy precedence requires explicit security review.

- Changing DENY/ASK semantics requires behavioral and security regression testing.

- MCP capability expansion cannot create a bypass path.

- New permission requirements discovered during implementation must be traced to SRS/architecture or approved change control.

# 34. Final Status

STATUS: FINAL / LOCKED — v1.0

This Tool & Permission Specification v1.0 is the authoritative authorization baseline for the AI Software Co-Agent. It defines the explicit tool model, single Tool Gateway, deterministic Policy Engine, ALLOW/ASK/DENY/RESTRICT semantics, scope controls, approvals, execution boundaries, MCP integration, audit behavior and security invariants.

— END OF TOOL & PERMISSION SPECIFICATION v1.0 —
