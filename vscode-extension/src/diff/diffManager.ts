/**
 * Diff and change presentation manager (T099, VCI-001 §14).
 */

import { RuntimeClient } from "../client/runtimeClient";
import { RuntimeEvent } from "../protocol/types";

export interface FileChange {
  filePath: string;
  operation: "CREATE" | "MODIFY" | "DELETE";
  diffHunk?: string;
}

export class DiffManager {
  private client: RuntimeClient;

  constructor(client: RuntimeClient) {
    this.client = client;
  }

  public async fetchTaskDiff(taskId?: string): Promise<string> {
    const event: RuntimeEvent = await this.client.getDiff(taskId);
    return event.payload.diff || "";
  }

  public parseChanges(diffText: string): FileChange[] {
    const changes: FileChange[] = [];
    if (!diffText.trim()) {
      return changes;
    }

    const lines = diffText.split("\n");
    let currentFile = "";
    let currentHunks: string[] = [];

    for (const line of lines) {
      if (line.startsWith("--- a/") || line.startsWith("+++ b/")) {
        const path = line.substring(6).trim();
        if (path && path !== currentFile) {
          if (currentFile) {
            changes.push({
              filePath: currentFile,
              operation: "MODIFY",
              diffHunk: currentHunks.join("\n")
            });
            currentHunks = [];
          }
          currentFile = path;
        }
      } else {
        currentHunks.push(line);
      }
    }

    if (currentFile) {
      changes.push({
        filePath: currentFile,
        operation: "MODIFY",
        diffHunk: currentHunks.join("\n")
      });
    }

    return changes;
  }
}
