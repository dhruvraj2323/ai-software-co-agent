AI SOFTWARE CO-AGENT

VS CODE INTEGRATION SPECIFICATION

Version 1.0 — FINAL / LOCKED

Document ID: VCI-001 • Derived from the locked Product, SRS, Architecture, Technical Design, Agent Behaviour, Tool/Permission, Memory/Context, Error Recovery, Testing/Validation & Security/Sandbox baselines

| Field | Value |
| --- | --- |
| Document | VS Code Integration Specification |
| Version | v1.0 |
| Status | FINAL / LOCKED |
| Product | AI Software Co-Agent |
| Purpose | Define the VS Code extension/client integration, runtime communication, UI surfaces, workspace interaction, approvals, cancellation, progress, evidence and security boundaries |
| Security authority | Co-Agent runtime / Tool Gateway / Policy Engine, not the client UI |

Lock Statement: This VS Code Integration Specification v1.0 is the final locked client-integration baseline. VS Code is a controlled user interface and orchestration client; it is never an authorization boundary. All material side effects remain governed by the Co-Agent runtime, Tool Gateway, Policy Engine and Security/Sandbox layer.

# 1. Purpose & Integration Mission

The VS Code integration provides the primary developer-facing interface for interacting with the AI Software Co-Agent inside a repository. It must make planning, implementation, tool activity, approvals, validation, recovery and completion observable without duplicating or weakening runtime authority.

Primary integration principle: The extension displays and requests actions; the runtime authorizes and executes them.

# 2. Core Integration Principles

- VS Code UI is not a security boundary.

- All executable actions are authorized by the runtime Tool Gateway and Policy Engine.

- User intent from the UI must be represented as structured requests.

- Workspace identity and scope are explicit.

- Material file changes must be visible through standard editor/diff experiences.

- Approvals must identify the exact action, target and risk.

- Cancellation must propagate to the runtime.

- Progress must reflect actual runtime state, not optimistic UI state.

- Validation evidence and completion state come from the runtime.

- Runtime errors must be surfaced clearly without exposing secrets.

- Extension restarts must not silently resume privileged execution.

- Client/runtime protocol versions must be explicit and compatible.

- VS Code APIs are used for UI/workspace integration; direct privileged execution is prohibited.

# 3. Integration Architecture

┌──────────────────────────────────────────────┐

│ VS CODE │

│ │

│ Chat / Commands / Tree / Diff / Status │

│ Approval UI / Progress / Diagnostics │

└─────────────────────┬────────────────────────┘

│

Typed Client Protocol

│

▼

┌──────────────────────────────────────────────┐

│ CO-AGENT RUNTIME │

│ Session → Orchestrator → Context → Policy │

│ → Tools → Validation │

│ → Recovery → Completion │

└─────────────────────┬────────────────────────┘

│

Evidence / Events

│

▼

VS CODE UI

The client may request runtime operations and subscribe to runtime events, but must not call executors, filesystem mutation services, process execution services or privileged MCP endpoints directly.

# 4. Client Responsibilities

| Area | VS Code responsibility |
| --- | --- |
| Workspace | Detect/select workspace and provide workspace identity to runtime. |
| Conversation | Render chat/task interaction and submit user messages. |
| Commands | Translate UI actions into typed runtime requests. |
| Plan | Display plan/steps and current task stage. |
| Changes | Open files/diffs and show task-owned changes. |
| Approvals | Render approval request and submit explicit decision. |
| Progress | Render runtime task/tool/validation progress. |
| Diagnostics | Display structured errors/warnings. |
| Validation | Show gate status and evidence links. |
| Recovery | Show recovery state and user intervention needs. |
| Completion | Display runtime completion status/evidence. |
| Settings | Expose allowed client preferences without bypassing security policy. |

# 5. Runtime Responsibilities

| Area | Runtime responsibility |
| --- | --- |
| Authorization | Tool Gateway + Policy Engine. |
| Execution | Authorized executors/sandbox. |
| State | Task/session lifecycle and persistence. |
| Context | Context Engine and Memory. |
| Recovery | Recovery Controller. |
| Validation | Validation Runner + Completion Gate. |
| Security | Security/Sandbox enforcement. |
| Audit | Material action/event audit. |
| Protocol | Request validation, correlation and compatibility. |
| Evidence | Generate/store authoritative evidence references. |

# 6. VS Code Integration Surfaces

| Surface | Purpose |
| --- | --- |
| Chat View / Webview | Primary conversational task interface. |
| Command Palette | Explicit task/agent commands. |
| Activity Bar / Sidebar | Task status, plans, changes, tools and validation. |
| Editor | Source inspection and task changes. |
| Diff Editor | Review actual task-owned modifications. |
| Problems Panel | Structured diagnostics where appropriate. |
| Notifications | Important approvals/errors/completion events. |
| Progress UI | Task/tool/validation progress. |
| Status Bar | Compact task/runtime state. |
| Quick Pick/Input | Scoped selections and approval inputs. |
| Output/Logs | Safe diagnostic details and evidence references. |

# 7. Workspace Binding

- At task start, the client identifies the active workspace/folder(s).

- Runtime resolves and validates canonical workspace scope.

- Multi-root workspaces must represent each authorized root explicitly.

- Client paths are untrusted input until runtime scope validation.

- Workspace changes during a task trigger a scope/context refresh.

- Closing or switching workspace must not silently broaden the active task.

- Opening a file outside task scope is allowed for user viewing only; agent modification requires runtime authorization.

| Event | Expected behavior |
| --- | --- |
| Workspace opened | Runtime session can bind to authorized root. |
| Workspace switched | Active task scope is revalidated. |
| Folder added/removed | Task context/scope refresh required. |
| File renamed/moved | Runtime refreshes affected context. |
| Workspace closed | Active privileged execution is stopped/blocked safely. |
| No workspace | Repository-dependent implementation task cannot proceed without a valid scope. |

# 8. Client ↔ Runtime Protocol

ClientRequest {

protocol_version: string

request_id: UUID

session_id: UUID

task_id: UUID | null

type: RequestType

payload: object

client_context: object

created_at: datetime

}

RuntimeEvent {

protocol_version: string

event_id: UUID

request_id: UUID | null

session_id: UUID

task_id: UUID | null

type: EventType

payload: object

severity: INFO | WARNING | ERROR | CRITICAL

created_at: datetime

}

- All requests/events use stable IDs and correlation.

- Unknown protocol versions are rejected or negotiated safely.

- Payloads are schema validated.

- Client context is advisory; runtime remains authoritative.

# 9. Protocol Request Types

| Request | Purpose | Side effect |
| --- | --- | --- |
| session.start | Start/attach client session | None/controlled state |
| task.create | Create task from user request | Task state |
| task.resume | Resume safe persisted task | Controlled; runtime policy |
| task.pause | Pause task | Lifecycle |
| task.cancel | Cancel task | Lifecycle/termination |
| task.status | Read task state | Read |
| plan.request | Request/update plan | Planning state |
| approval.respond | Approve/reject exact approval | Authorization input |
| tool.status | Read tool activity | Read |
| validation.status | Read gate results | Read |
| completion.status | Read completion state | Read |
| workspace.refresh | Refresh scope/context | Read/state |
| diff.open | Request diff/evidence reference | Read |
| artifact.open | Open safe artifact/evidence | Read |

# 10. Runtime Event Types

| Event | UI meaning |
| --- | --- |
| task.created | Task initialized. |
| task.state_changed | Task lifecycle changed. |
| plan.updated | Plan changed. |
| context.updated | Context refreshed/materially changed. |
| approval.requested | User decision required. |
| approval.expired | Approval no longer valid. |
| tool.started | Tool execution began. |
| tool.progress | Tool progress update. |
| tool.completed | Tool returned result. |
| tool.failed | Tool failed. |
| validation.started | Gate running. |
| validation.completed | Gate result available. |
| recovery.started | Recovery began. |
| recovery.attempt | Repair attempt underway. |
| recovery.exhausted | Recovery stopped. |
| security.blocked | Security/policy blocked operation. |
| task.cancelled | Task cancelled. |
| task.completed | Runtime reports completed task. |
| task.failed | Task ended non-complete. |

# 11. Task Lifecycle in VS Code

IDLE

↓

REQUESTED

↓

UNDERSTANDING

↓

PLANNING

↓

IMPLEMENTING

↓

VALIDATING

├── FAIL → RECOVERING → VALIDATING

│ ↓

└────────────────────── PASS

↓

COMPLETION

↓

DONE

Any stage → CANCELLED / BLOCKED / FAILED

The client mirrors runtime state; it does not independently transition a task to DONE.

# 12. Chat Interface Requirements

- Display the active task and workspace scope.

- Show concise stage/progress information.

- Distinguish plan, action, result, error and approval messages.

- Render structured tool/validation evidence when available.

- Allow explicit cancellation.

- Show when user approval is required.

- Do not present speculative model text as confirmed execution.

- Do not claim a tool ran unless a runtime event confirms it.

- Preserve enough task history for the active session while relying on runtime persistence for authoritative state.

# 13. Approval UI

| Element | Required display |
| --- | --- |
| Action | Exact requested operation. |
| Tool | Tool/capability identity. |
| Target | File/resource/process scope. |
| Risk | Relevant side-effect classification. |
| Reason | Why the agent needs the action. |
| Scope | Workspace/resource boundaries. |
| Decision | Approve / Reject. |
| Expiry | If approval has an expiration. |
| Evidence | Relevant diff/plan/context where useful. |

- Approve applies only to the correlated approval request.

- Reject must not be interpreted as permission to find a bypass.

- Expired approvals cannot be replayed.

- UI must not fabricate approval state locally.

# 14. File Editing & Diff Integration

- Agent-generated modifications are applied by the runtime's authorized workspace/patch tools.

- Extension refreshes the editor after confirmed runtime change events.

- Diff view must represent actual resulting file content.

- Expected/base hashes should be used by runtime patch logic to detect stale edits.

- User edits made concurrently must be preserved or surfaced as conflict.

- Extension must not silently overwrite user changes.

- Save/format actions triggered by the agent are still runtime-authorized side effects where applicable.

# 15. Diagnostics Integration

| Source | VS Code representation |
| --- | --- |
| Compiler/test output | Problems/Output + evidence reference |
| Lint | Problems/Diagnostics |
| Runtime error | Chat/notification + structured error |
| Policy DENY | Clear blocked-action message |
| Security block | Security-focused warning/block state |
| Recovery | Recovery status and attempt summary |
| Validation gate | Gate result with evidence |

Diagnostic UI should avoid exposing secrets or unsafe raw process output when filtering is required.

# 16. Terminal Integration

- Terminal UI may display authorized command activity, but execution authority remains in the runtime.

- Client must not directly execute agent-generated commands as a bypass.

- Commands displayed to the user should correspond to actual runtime requests.

- Sensitive environment values must not be rendered.

- Cancellation must propagate to runtime process control.

- Output may be truncated or artifact-referenced according to runtime limits.

# 17. Git Integration

| Feature | Behavior |
| --- | --- |
| Status | Show current repository state from runtime/Git adapter. |
| Diff | Open actual diff/evidence. |
| Checkpoint | Reflect runtime-created checkpoint when configured. |
| Rollback | Require runtime authorization/approval. |
| Commit | Require configured runtime authorization/approval. |
| User changes | Clearly distinguish/preserve unrelated changes. |
| Conflicts | Surface conflict; never silently reset user work. |

# 18. Validation & Completion UI

| State | UI behavior |
| --- | --- |
| NOT_RUN | Visible as not executed. |
| RUNNING | Show progress. |
| PASS | Show evidence/reference. |
| FAIL | Show failure and recovery path. |
| BLOCKED | Show blocker/reason. |
| TIMEOUT | Show timeout and recovery status. |
| CANCELLED | Show cancelled; never success. |
| COMPLETE | Only when runtime Completion Gate confirms. |

Critical rule: The extension cannot mark a task COMPLETE based on chat text, client assumptions or a stale cached result.

# 19. Recovery UI

- Show failure category and concise diagnosis.

- Show recovery attempt number within configured budget.

- Show current action/validation state.

- Show approval request if repair needs authorization.

- Show when recovery is blocked/exhausted.

- Provide evidence references for relevant failures.

- Do not encourage endless retries.

- Cancellation must immediately stop normal recovery continuation.

# 20. Cancellation & Emergency Stop

| Client action | Runtime behavior |
| --- | --- |
| Cancel task | Send correlated task.cancel. |
| Cancel tool | Request cancellation of active operation where supported. |
| Close workspace | Stop/block active privileged work safely. |
| Extension reload | Do not silently resume privileged execution. |
| Runtime disconnected | Client shows disconnected/block state; no fake success. |
| Emergency stop | Runtime takes priority; client reflects stopped state. |

# 21. Connection & Reconnection

- Runtime connection has explicit CONNECTING/CONNECTED/DISCONNECTED/FAILED states.

- Client retries connection only within bounded policy.

- Reconnection must resynchronize authoritative task state.

- Pending approval state must be refreshed from runtime.

- Client must not replay side-effect requests blindly after reconnect.

- Idempotency/correlation IDs protect against duplicate requests.

- Privileged execution state remains runtime-owned during client disconnect.

# 22. Session Persistence

| State | Persistence |
| --- | --- |
| Conversation/task metadata | Runtime-managed. |
| Plan | Versioned runtime state. |
| Approval | Runtime authoritative; expiration retained. |
| Tool activity | Runtime/audit evidence. |
| Validation | Runtime evidence. |
| Recovery chain | Runtime persistence. |
| UI layout/preferences | VS Code/client state. |
| Security policy | Not client-owned. |

# 23. Client Security Boundary

- Do not store long-lived secrets in extension global state.

- Do not trust webview messages as authorization.

- Validate all webview-to-extension messages.

- Validate all extension-to-runtime requests.

- Do not expose privileged runtime endpoints to arbitrary webview content.

- Use least privilege for extension capabilities.

- Restrict URI/file access to intended workspace/resources.

- Treat content rendered from repository/MCP output as untrusted.

- Never execute arbitrary JavaScript/commands merely because repository content requests it.

# 24. Webview Security

| Control | Requirement |
| --- | --- |
| Message validation | Typed allowlisted message types. |
| Origin/content | Only trusted extension resources. |
| Script policy | Restrictive CSP where applicable. |
| HTML rendering | Escape/sanitize untrusted content. |
| Links | Controlled handling; no arbitrary privileged navigation. |
| Command messages | Must map to allowlisted client operations. |
| Secrets | Never inject into webview. |
| External content | Treat as untrusted. |

# 25. Client Configuration

| Setting class | Rule |
| --- | --- |
| Runtime endpoint | Configurable but validated/controlled. |
| Autonomy display | Reflect runtime; cannot locally elevate authority. |
| UI preferences | Client-owned. |
| Tool enablement | Runtime/policy-owned. |
| Security policy | Runtime/security-owned. |
| Workspace scope | Runtime validates. |
| Logging verbosity | May be client-configurable within safe bounds. |
| Telemetry | Must follow product privacy/configuration requirements. |

# 26. Error Handling

| Client condition | Required behavior |
| --- | --- |
| Malformed runtime response | Reject safely; show protocol error. |
| Unknown event | Ignore/store safely according to versioning strategy. |
| Runtime unavailable | Show disconnected; no privileged fallback. |
| Policy DENY | Show blocked action; no bypass. |
| Approval rejected | Show rejected; task may block. |
| Tool failed | Show failure + evidence/recovery state. |
| Validation failed | Show gate failure. |
| Security block | Show security blocker without sensitive internals. |
| Client exception | Fail safely; preserve runtime state. |

# 27. Accessibility & UX Requirements

- Approval controls must be keyboard accessible.

- Critical states must not rely on color alone.

- Progress/status should have textual labels.

- Error messages should be concise and actionable.

- Diff and diagnostics should use standard VS Code affordances where practical.

- Long-running tasks should remain cancellable.

- UI should distinguish user action, agent proposal, runtime execution and validation evidence.

# 28. Performance Requirements

| Area | Requirement |
| --- | --- |
| UI response | Client interactions should remain responsive. |
| Event stream | Events should be processed incrementally. |
| Large output | Use truncation/artifact references; do not render unbounded text. |
| Large diff | Use VS Code diff mechanisms and bounded metadata. |
| Reconnect | Resynchronize without replaying side effects. |
| Context | Client should not receive full internal context unless explicitly needed. |
| Memory | Avoid retaining unnecessary large task output in extension state. |

# 29. Observability

| Event | Required correlation |
| --- | --- |
| Client request | request_id/session_id/task_id |
| Runtime event | event_id/request_id/session_id/task_id |
| Approval | approval_id/request_id/task_id |
| Tool activity | tool request correlation |
| Validation | gate/task correlation |
| Recovery | error/recovery/task correlation |
| Client errors | session/request context where safe |

Client logs must be safe for local diagnostics and must not intentionally capture secrets or full sensitive model/tool payloads.

# 30. Offline / Disconnected Behaviour

- Read-only UI may remain available using cached non-authoritative state.

- Privileged operations require a live authoritative runtime.

- Client must not execute agent commands locally as an offline fallback.

- Cached completion state must be clearly labeled as cached until revalidated.

- Reconnect must refresh task state before allowing new privileged requests.

# 31. Extension Lifecycle

ACTIVATE

↓

CHECK COMPATIBILITY

↓

DISCOVER / CONNECT RUNTIME

↓

REGISTER UI + COMMANDS

↓

SUBSCRIBE TO EVENTS

↓

RUN SESSION

↓

DISCONNECT / RELOAD

↓

SAFE CLEANUP

- Activation must not automatically execute privileged task actions.

- Extension reload must not duplicate event subscriptions or side effects.

- Runtime session identity must be refreshed safely.

# 32. Integration Testing

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| VCI-IT-001 | Create task from chat | Runtime task created with correct workspace/session IDs. |
| VCI-IT-002 | Tool execution | Client sees runtime events; no direct executor call. |
| VCI-IT-003 | Approval | Approval UI reflects exact runtime request. |
| VCI-IT-004 | Reject approval | No tool side effect. |
| VCI-IT-005 | File edit | Actual diff appears after runtime confirms change. |
| VCI-IT-006 | Concurrent user edit | Conflict preserved/surfaced. |
| VCI-IT-007 | Validation failure | Gate failure displayed; task not complete. |
| VCI-IT-008 | Recovery | Recovery events displayed and bounded. |
| VCI-IT-009 | Cancellation | Runtime cancels; UI never shows success. |
| VCI-IT-010 | Reconnect | State resync without duplicate side effect. |
| VCI-IT-011 | MCP | MCP activity remains behind runtime policy. |
| VCI-IT-012 | Security block | Blocked state shown; no client bypass. |

# 33. Client Security Test Suite

- Webview message injection.

- Webview-to-extension command spoofing.

- Client direct-executor endpoint attempts.

- Path traversal through UI inputs.

- Workspace switching during privileged task.

- Approval replay/forgery.

- Duplicate request/replay after reconnect.

- Repository prompt-injection rendered in UI.

- MCP malicious content rendered as instructions.

- Secret leakage in notifications/output panels.

- Extension state containing credentials.

- Client attempt to elevate autonomy mode.

# 34. E2E Acceptance Scenarios

| ID | Scenario |
| --- | --- |
| AT-VS-001 | User opens workspace → starts task → sees plan → approves required action → reviews diff → validation passes → runtime reports COMPLETE. |
| AT-VS-002 | User rejects high-risk approval → no side effect → task is blocked/non-complete. |
| AT-VS-003 | User edits same file during agent work → runtime detects conflict → extension surfaces it without overwriting user edit. |
| AT-VS-004 | Validation fails → recovery starts → repair is shown → retest passes → completion evidence is shown. |
| AT-VS-005 | User cancels during tool execution → process stops where supported → task becomes CANCELLED. |
| AT-VS-006 | Runtime disconnects → client blocks privileged actions → reconnect resyncs authoritative state. |
| AT-VS-007 | Malicious README attempts instruction injection → content remains untrusted → no unauthorized action. |
| AT-VS-008 | Client sends forged privileged request → runtime rejects it. |

# 35. VS Code Integration Invariants

- VC1: VS Code is never an authorization boundary.

- VC2: No client request directly executes a privileged executor.

- VC3: Every material side effect is authorized by runtime policy.

- VC4: Client task state mirrors runtime authoritative state.

- VC5: Client cannot convert DENY into ALLOW.

- VC6: Client cannot replay expired approvals.

- VC7: Client disconnect cannot cause duplicate privileged actions.

- VC8: Client cancellation propagates to runtime.

- VC9: Client cannot declare COMPLETE independently.

- VC10: User changes are never silently overwritten.

- VC11: Repository/MCP content rendered in UI remains untrusted.

- VC12: Secrets are not intentionally stored/rendered by the extension.

- VC13: Workspace scope is runtime-validated.

- VC14: Extension reload does not resume privileged execution without safe runtime state.

- VC15: Security controls remain authoritative regardless of client UI/configuration.

# 36. Acceptance Criteria

| ID | Area | Acceptance condition |
| --- | --- | --- |
| VCI-A01 | Workspace | Workspace scope is explicitly bound and runtime-validated. |
| VCI-A02 | Protocol | Typed versioned client/runtime protocol works. |
| VCI-A03 | Task lifecycle | Client accurately mirrors runtime lifecycle. |
| VCI-A04 | Tool execution | No direct client executor path exists. |
| VCI-A05 | Approval | Approval UI is exact, correlated and non-replayable. |
| VCI-A06 | Editing | Actual runtime changes are reflected and user changes preserved. |
| VCI-A07 | Validation | Gate results/evidence are authoritative from runtime. |
| VCI-A08 | Recovery | Recovery states and intervention are visible. |
| VCI-A09 | Cancellation | Cancellation is propagated and cannot become success. |
| VCI-A10 | Reconnect | State resynchronizes without duplicate side effects. |
| VCI-A11 | Security | Webview/client bypass tests pass. |
| VCI-A12 | Secrets | No intentional secret exposure through client. |
| VCI-A13 | Performance | Client remains responsive under normal workload. |
| VCI-A14 | Accessibility | Critical controls/states are accessible. |
| VCI-A15 | Completion | Only runtime Completion Gate can report COMPLETE. |

# 37. Traceability to Locked Baselines

| Baseline | VS Code impact |
| --- | --- |
| PRD v1.0 | Developer UX, user control, transparency and completion behavior. |
| SRS v1.0 | Client/runtime integration, commands, UI and lifecycle requirements. |
| System Architecture v1.0 | Runtime authority and client boundary. |
| Technical Design v1.0 | Protocol, modules, event flow and integration interfaces. |
| Agent Behaviour v1.0 | Plan/tool/approval/progress/cancel/recovery behavior. |
| Tool & Permission v1.0 | Client cannot bypass central authorization. |
| Memory & Context v1.0 | Client receives controlled summaries/evidence, not unrestricted internal context. |
| Error Recovery v1.0 | Recovery states/events and cancellation. |
| Testing & Validation v1.0 | Integration/security/E2E gates. |
| Security & Sandbox v1.0 | Client security boundary, webview and no-bypass rules. |

# 38. Implementation Mapping

| Area | Expected implementation location |
| --- | --- |
| VS Code extension | vscode-extension/ |
| Extension activation | vscode-extension/src/extension.ts |
| Runtime client | vscode-extension/src/client/ |
| Protocol models | vscode-extension/src/protocol/ |
| Chat UI | vscode-extension/src/chat/ |
| Sidebar/tree | vscode-extension/src/views/ |
| Commands | vscode-extension/src/commands/ |
| Approvals | vscode-extension/src/approval/ |
| Diff/change view | vscode-extension/src/changes/ |
| Diagnostics | vscode-extension/src/diagnostics/ |
| Progress/status | vscode-extension/src/status/ |
| Webviews | vscode-extension/src/webview/ |
| Security boundary | vscode-extension/src/security/ |
| Extension tests | vscode-extension/test/ |
| E2E tests | tests/e2e/vscode/ or equivalent |

Exact filenames may evolve during implementation. The client/runtime boundary, authorization model, lifecycle and security invariants are locked.

# 39. Change Control

- Changes to client/runtime protocol require versioning and compatibility tests.

- Changes that add client-side execution authority require architecture/security review and are prohibited under this v1.0 boundary.

- New UI actions with side effects require runtime ToolRequest mappings and permission tests.

- Webview changes require security regression tests.

- Approval UI changes require approval/replay/security tests.

- Changes to completion display must preserve runtime Completion Gate authority.

- New VS Code integrations must preserve workspace scope and user-change protection.

# 40. Final Status

STATUS: FINAL / LOCKED — v1.0

This VS Code Integration Specification v1.0 is the authoritative client-integration baseline for the AI Software Co-Agent. It defines the extension/runtime boundary, workspace binding, protocol, task lifecycle, UI surfaces, approvals, editing/diff behavior, validation/recovery presentation, cancellation, reconnection, webview security, testing and client invariants.

— END OF VS CODE INTEGRATION SPECIFICATION v1.0 —
