/**
 * Diagnostics and error presentation without secret leakage (T100, VCI-001 §15).
 */

import { RuntimeClient } from "../client/runtimeClient";
import { RuntimeEvent } from "../protocol/types";

export interface DiagnosticItem {
  message: string;
  severity: "error" | "warning" | "info";
  gateId?: string;
  source: string;
}

export class DiagnosticsManager {
  private client: RuntimeClient;
  private diagnostics: DiagnosticItem[] = [];
  private onDiagnosticsChangeListeners: Set<() => void> = new Set();

  constructor(client: RuntimeClient) {
    this.client = client;
    this.registerEventListeners();
  }

  private registerEventListeners(): void {
    this.client.on("validation.completed", (event: RuntimeEvent) => {
      const p = event.payload;
      if (p.status !== "PASS") {
        this.addDiagnostic({
          message: p.stderr_summary || `Validation gate '${p.gate_id}' failed with exit code ${p.exit_code}`,
          severity: "error",
          gateId: p.gate_id,
          source: "coagent.validation"
        });
      }
    });

    this.client.on("security.blocked", (event: RuntimeEvent) => {
      this.addDiagnostic({
        message: event.payload.reason || "Operation blocked by security policy",
        severity: "error",
        source: "coagent.security"
      });
    });
  }

  public getDiagnostics(): DiagnosticItem[] {
    return [...this.diagnostics];
  }

  public addDiagnostic(item: DiagnosticItem): void {
    this.diagnostics.push(item);
    for (const listener of this.onDiagnosticsChangeListeners) {
      listener();
    }
  }

  public clearDiagnostics(): void {
    this.diagnostics = [];
    for (const listener of this.onDiagnosticsChangeListeners) {
      listener();
    }
  }

  public onDiagnosticsChange(listener: () => void): void {
    this.onDiagnosticsChangeListeners.add(listener);
  }
}
