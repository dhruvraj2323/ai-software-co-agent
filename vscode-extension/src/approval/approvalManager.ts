/**
 * Approval UI and decision routing (T098, VCI-001 §13).
 */

import { RuntimeClient } from "../client/runtimeClient";
import { RuntimeEvent } from "../protocol/types";

export interface PendingApproval {
  approvalId: string;
  taskId: string;
  toolId: string;
  reason: string;
  riskLevel: string;
  arguments: Record<string, any>;
  requestedAt: string;
}

export class ApprovalManager {
  private client: RuntimeClient;
  private pendingApprovals: Map<string, PendingApproval> = new Map();
  private onPendingApprovalListeners: Set<(approvals: PendingApproval[]) => void> = new Set();

  constructor(client: RuntimeClient) {
    this.client = client;
    this.registerEventListeners();
  }

  private registerEventListeners(): void {
    this.client.on("approval.requested", (event: RuntimeEvent) => {
      const p = event.payload;
      const approval: PendingApproval = {
        approvalId: p.approval_id || event.request_id || "unknown",
        taskId: p.task_id || event.task_id || "",
        toolId: p.tool_id || "unknown",
        reason: p.reason || "Policy authorization required",
        riskLevel: p.risk_level || "MEDIUM",
        arguments: p.arguments || {},
        requestedAt: event.created_at
      };
      this.pendingApprovals.set(approval.approvalId, approval);
      this.notifyListeners();
    });

    this.client.on("approval.expired", (event: RuntimeEvent) => {
      const approvalId = event.payload.approval_id;
      if (approvalId && this.pendingApprovals.has(approvalId)) {
        this.pendingApprovals.delete(approvalId);
        this.notifyListeners();
      }
    });
  }

  public getPendingApprovals(): PendingApproval[] {
    return Array.from(this.pendingApprovals.values());
  }

  public onPendingApprovalsChange(listener: (approvals: PendingApproval[]) => void): void {
    this.onPendingApprovalListeners.add(listener);
  }

  private notifyListeners(): void {
    const list = this.getPendingApprovals();
    for (const listener of this.onPendingApprovalListeners) {
      listener(list);
    }
  }

  /**
   * Submit an explicit user approval decision back to the runtime (T098).
   * Maps strictly to the exact approval request identifier.
   */
  public async submitDecision(approvalId: string, approved: boolean, reason?: string): Promise<RuntimeEvent> {
    const approval = this.pendingApprovals.get(approvalId);
    if (!approval) {
      throw new Error(`Approval '${approvalId}' is not pending or has expired.`);
    }

    const event = await this.client.respondApproval(
      approvalId,
      approved,
      reason,
      approval.taskId
    );

    this.pendingApprovals.delete(approvalId);
    this.notifyListeners();
    return event;
  }
}
