/**
 * Status bar indicator reflecting runtime state (T100, VCI-001 §6, §28).
 */

import { RuntimeClient } from "../client/runtimeClient";
import { RuntimeEvent } from "../protocol/types";

export class CoAgentStatusBar {
  private client: RuntimeClient;
  private currentText: string = "Co-Agent: Ready";
  private currentTooltip: string = "AI Software Co-Agent Idle";

  constructor(client: RuntimeClient) {
    this.client = client;
    this.registerEventListeners();
  }

  private registerEventListeners(): void {
    this.client.on("task.created", (event: RuntimeEvent) => {
      this.updateState("INITIALIZED", event.task_id || "Active Task");
    });

    this.client.on("task.state_changed", (event: RuntimeEvent) => {
      this.updateState(event.payload.state || "WORKING", event.task_id || "");
    });

    this.client.on("validation.started", () => {
      this.updateState("VALIDATING", "Running quality gates...");
    });

    this.client.on("task.completed", () => {
      this.updateState("COMPLETE", "All gates passed cleanly");
    });

    this.client.on("task.failed", (event: RuntimeEvent) => {
      this.updateState("FAILED", event.payload.reason || "Task failed");
    });

    this.client.on("task.cancelled", () => {
      this.updateState("CANCELLED", "Task cancelled by user");
    });
  }

  public updateState(state: string, details?: string): void {
    this.currentText = `Co-Agent: ${state}`;
    this.currentTooltip = details || `Task state: ${state}`;
  }

  public getText(): string {
    return this.currentText;
  }

  public getTooltip(): string {
    return this.currentTooltip;
  }
}
