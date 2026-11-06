/**
 * Versioned protocol contracts matching coagent.protocol (VCI-001 §8, §9, §10).
 */

export const PROTOCOL_VERSION = "1.0";

export enum RequestType {
  SESSION_START = "session.start",
  TASK_CREATE = "task.create",
  TASK_RESUME = "task.resume",
  TASK_PAUSE = "task.pause",
  TASK_CANCEL = "task.cancel",
  TASK_STATUS = "task.status",
  PLAN_REQUEST = "plan.request",
  APPROVAL_RESPOND = "approval.respond",
  TOOL_STATUS = "tool.status",
  VALIDATION_STATUS = "validation.status",
  COMPLETION_STATUS = "completion.status",
  WORKSPACE_REFRESH = "workspace.refresh",
  DIFF_OPEN = "diff.open",
  ARTIFACT_OPEN = "artifact.open"
}

export enum EventType {
  TASK_CREATED = "task.created",
  TASK_STATE_CHANGED = "task.state_changed",
  PLAN_UPDATED = "plan.updated",
  CONTEXT_UPDATED = "context.updated",
  APPROVAL_REQUESTED = "approval.requested",
  APPROVAL_EXPIRED = "approval.expired",
  TOOL_STARTED = "tool.started",
  TOOL_PROGRESS = "tool.progress",
  TOOL_COMPLETED = "tool.completed",
  TOOL_FAILED = "tool.failed",
  VALIDATION_STARTED = "validation.started",
  VALIDATION_COMPLETED = "validation.completed",
  RECOVERY_STARTED = "recovery.started",
  RECOVERY_ATTEMPT = "recovery.attempt",
  RECOVERY_EXHAUSTED = "recovery.exhausted",
  SECURITY_BLOCKED = "security.blocked",
  TASK_CANCELLED = "task.cancelled",
  TASK_COMPLETED = "task.completed",
  TASK_FAILED = "task.failed"
}

export interface ClientRequest {
  protocol_version: string;
  request_id: string;
  session_id: string;
  task_id?: string | null;
  type: RequestType;
  payload: Record<string, any>;
  client_context: Record<string, any>;
  created_at: string;
}

export interface RuntimeEvent {
  protocol_version: string;
  event_id: string;
  request_id?: string | null;
  session_id: string;
  task_id?: string | null;
  type: EventType;
  payload: Record<string, any>;
  severity: "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  created_at: string;
}

export interface ProtocolError {
  code: string;
  message: string;
  request_id: string;
  details: Record<string, any>;
}

export interface ProtocolErrorEnvelope {
  protocol_version: string;
  request_id: string;
  error: ProtocolError;
  created_at: string;
}
