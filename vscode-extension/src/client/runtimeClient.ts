/**
 * Typed client for communicating with the Co-Agent runtime over protocol (T096, VCI-001 §3).
 */

import {
  PROTOCOL_VERSION,
  ClientRequest,
  RuntimeEvent,
  ProtocolErrorEnvelope,
  RequestType,
  EventType
} from "../protocol/types";

export type EventCallback = (event: RuntimeEvent) => void;

export class RuntimeClient {
  private sessionId: string;
  private currentTaskId: string | null = null;
  private listeners: Map<string, Set<EventCallback>> = new Map();
  private sendHandler?: (req: ClientRequest) => Promise<RuntimeEvent | ProtocolErrorEnvelope>;

  constructor(sessionId: string, sendHandler?: (req: ClientRequest) => Promise<RuntimeEvent | ProtocolErrorEnvelope>) {
    this.sessionId = sessionId;
    this.sendHandler = sendHandler;
  }

  public getSessionId(): string {
    return this.sessionId;
  }

  public getCurrentTaskId(): string | null {
    return this.currentTaskId;
  }

  public setCurrentTaskId(taskId: string | null): void {
    this.currentTaskId = taskId;
  }

  public on(eventType: string, callback: EventCallback): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);
  }

  public off(eventType: string, callback: EventCallback): void {
    const set = this.listeners.get(eventType);
    if (set) {
      set.delete(callback);
    }
  }

  public emit(event: RuntimeEvent): void {
    const set = this.listeners.get(event.type);
    if (set) {
      for (const cb of set) {
        cb(event);
      }
    }
    // Also emit to wildcards
    const wildcards = this.listeners.get("*");
    if (wildcards) {
      for (const cb of wildcards) {
        cb(event);
      }
    }
  }

  public createRequest(type: RequestType, payload: Record<string, any> = {}, taskId?: string | null): ClientRequest {
    return {
      protocol_version: PROTOCOL_VERSION,
      request_id: this.generateUUID(),
      session_id: this.sessionId,
      task_id: taskId !== undefined ? taskId : this.currentTaskId,
      type,
      payload,
      client_context: { client: "vscode-extension", version: "0.1.0" },
      created_at: new Date().toISOString()
    };
  }

  public async send(request: ClientRequest): Promise<RuntimeEvent> {
    if (!this.sendHandler) {
      throw new Error("No transport handler configured for runtime client.");
    }
    const response = await this.sendHandler(request);
    if ("error" in response) {
      throw new Error(`Runtime protocol error [${response.error.code}]: ${response.error.message}`);
    }
    this.emit(response);
    return response;
  }

  public async startSession(): Promise<RuntimeEvent> {
    const req = this.createRequest(RequestType.SESSION_START);
    return this.send(req);
  }

  public async createTask(goal: string, files: string[] = []): Promise<RuntimeEvent> {
    const taskId = this.generateUUID();
    const req = this.createRequest(RequestType.TASK_CREATE, { goal, files }, taskId);
    const event = await this.send(req);
    this.currentTaskId = taskId;
    return event;
  }

  public async getStatus(taskId?: string): Promise<RuntimeEvent> {
    const target = taskId || this.currentTaskId;
    if (!target) {
      throw new Error("No task specified for status check.");
    }
    const req = this.createRequest(RequestType.TASK_STATUS, {}, target);
    return this.send(req);
  }

  public async requestPlan(taskId?: string): Promise<RuntimeEvent> {
    const target = taskId || this.currentTaskId;
    if (!target) {
      throw new Error("No task specified for plan request.");
    }
    const req = this.createRequest(RequestType.PLAN_REQUEST, {}, target);
    return this.send(req);
  }

  public async respondApproval(approvalId: string, approved: boolean, reason?: string, taskId?: string): Promise<RuntimeEvent> {
    const target = taskId || this.currentTaskId;
    if (!target) {
      throw new Error("No task specified for approval response.");
    }
    const req = this.createRequest(
      RequestType.APPROVAL_RESPOND,
      { approval_id: approvalId, approved, reason: reason || "" },
      target
    );
    return this.send(req);
  }

  public async cancelTask(reason?: string, taskId?: string): Promise<RuntimeEvent> {
    const target = taskId || this.currentTaskId;
    if (!target) {
      throw new Error("No task specified for cancellation.");
    }
    const req = this.createRequest(
      RequestType.TASK_CANCEL,
      { reason: reason || "Cancelled by user via VS Code" },
      target
    );
    return this.send(req);
  }

  public async getDiff(taskId?: string): Promise<RuntimeEvent> {
    const target = taskId || this.currentTaskId;
    if (!target) {
      throw new Error("No task specified for diff request.");
    }
    const req = this.createRequest(RequestType.DIFF_OPEN, {}, target);
    return this.send(req);
  }

  private generateUUID(): string {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}
