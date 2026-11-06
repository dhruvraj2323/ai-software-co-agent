/**
 * VS Code extension shell entrypoint (T096, VCI-001 §31).
 */

import { RuntimeClient } from "./client/runtimeClient";
import { ConnectionManager } from "./client/connectionManager";
import { ChatViewProvider } from "./chat/chatViewProvider";
import { ApprovalManager } from "./approval/approvalManager";
import { DiffManager } from "./diff/diffManager";
import { CoAgentStatusBar } from "./status/statusBarItem";
import { DiagnosticsManager } from "./diagnostics/diagnosticsManager";

export interface ExtensionContextLike {
  subscriptions: { dispose(): any }[];
}

export class ExtensionShell {
  public client: RuntimeClient;
  public connectionManager: ConnectionManager;
  public chatProvider: ChatViewProvider;
  public approvalManager: ApprovalManager;
  public diffManager: DiffManager;
  public statusBar: CoAgentStatusBar;
  public diagnostics: DiagnosticsManager;

  constructor(client: RuntimeClient) {
    this.client = client;
    this.connectionManager = new ConnectionManager(client);
    this.chatProvider = new ChatViewProvider(client);
    this.approvalManager = new ApprovalManager(client);
    this.diffManager = new DiffManager(client);
    this.statusBar = new CoAgentStatusBar(client);
    this.diagnostics = new DiagnosticsManager(client);
  }

  public async activate(): Promise<void> {
    await this.connectionManager.connect();
  }

  public async deactivate(): Promise<void> {
    // Graceful teardown
  }
}

export function activate(context: any): ExtensionShell {
  const sessionId = "session-" + Date.now();
  const client = new RuntimeClient(sessionId);
  const shell = new ExtensionShell(client);
  shell.activate().catch(console.error);
  return shell;
}

export function deactivate(): void {
  // Teardown
}
