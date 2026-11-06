/**
 * Webview View Provider for primary conversational task interaction (T097, VCI-001 §12).
 */

import { RuntimeClient } from "../client/runtimeClient";
import { RuntimeEvent } from "../protocol/types";

export interface ChatMessage {
  sender: "user" | "coagent" | "system";
  text: string;
  timestamp: string;
}

export class ChatViewProvider {
  public static readonly viewType = "coagent.chatView";
  private client: RuntimeClient;
  private messages: ChatMessage[] = [];
  private onMessageUpdateListeners: Set<() => void> = new Set();

  constructor(client: RuntimeClient) {
    this.client = client;
    this.registerEventListeners();
  }

  private registerEventListeners(): void {
    this.client.on("task.created", (event: RuntimeEvent) => {
      this.addMessage("coagent", `Task created: ${event.payload.goal || event.task_id}`);
    });

    this.client.on("plan.updated", (event: RuntimeEvent) => {
      const steps = (event.payload.plan || []).map((s: any) => `[${s.step}] ${s.description}`).join("\n");
      this.addMessage("coagent", `Generated Plan:\n${steps}`);
    });

    this.client.on("task.state_changed", (event: RuntimeEvent) => {
      this.addMessage("system", `Status: ${event.payload.state}`);
    });

    this.client.on("task.cancelled", (event: RuntimeEvent) => {
      this.addMessage("system", `Task cancelled: ${event.payload.reason}`);
    });
  }

  public getMessages(): ChatMessage[] {
    return [...this.messages];
  }

  public addMessage(sender: "user" | "coagent" | "system", text: string): void {
    this.messages.push({
      sender,
      text,
      timestamp: new Date().toISOString()
    });
    for (const listener of this.onMessageUpdateListeners) {
      listener();
    }
  }

  public onMessageUpdate(listener: () => void): void {
    this.onMessageUpdateListeners.add(listener);
  }

  public async handleUserSubmit(userGoal: string): Promise<void> {
    const trimmed = userGoal.trim();
    if (!trimmed) {
      return;
    }
    this.addMessage("user", trimmed);
    try {
      await this.client.createTask(trimmed);
      await this.client.requestPlan();
    } catch (err: any) {
      this.addMessage("system", `Error: ${err.message || String(err)}`);
    }
  }

  public getHtmlForWebview(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Co-Agent Chat</title>
  <style>
    body { font-family: sans-serif; padding: 10px; }
    .chat-box { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 5px; }
    .msg { margin-bottom: 8px; }
    .user { color: #0066cc; }
    .coagent { color: #009933; }
    .system { color: #666; font-style: italic; }
  </style>
</head>
<body>
  <h3>AI Software Co-Agent</h3>
  <div id="messages" class="chat-box"></div>
  <input type="text" id="userInput" placeholder="Describe engineering task..." style="width: 80%;" />
  <button id="sendBtn">Send</button>
</body>
</html>`;
  }
}
