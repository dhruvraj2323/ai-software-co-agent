/**
 * Connection management and safe state synchronization on reconnect (T101, VCI-001 §21).
 */

import { RuntimeClient } from "./runtimeClient";
import { RuntimeEvent } from "../protocol/types";

export enum ConnectionState {
  DISCONNECTED = "DISCONNECTED",
  CONNECTING = "CONNECTING",
  CONNECTED = "CONNECTED"
}

export class ConnectionManager {
  private client: RuntimeClient;
  private state: ConnectionState = ConnectionState.DISCONNECTED;
  private onStateChangeListeners: Set<(state: ConnectionState) => void> = new Set();

  constructor(client: RuntimeClient) {
    this.client = client;
  }

  public getState(): ConnectionState {
    return this.state;
  }

  public onStateChange(listener: (state: ConnectionState) => void): void {
    this.onStateChangeListeners.add(listener);
  }

  private setState(newState: ConnectionState): void {
    if (this.state !== newState) {
      this.state = newState;
      for (const listener of this.onStateChangeListeners) {
        listener(this.state);
      }
    }
  }

  public async connect(): Promise<boolean> {
    this.setState(ConnectionState.CONNECTING);
    try {
      await this.client.startSession();
      this.setState(ConnectionState.CONNECTED);
      return true;
    } catch {
      this.setState(ConnectionState.DISCONNECTED);
      return false;
    }
  }

  /**
   * Idempotent reconnect: resumes existing session and resynchronizes active task state
   * without duplicating execution side-effects (T101).
   */
  public async reconnect(): Promise<{ reconnected: boolean; taskEvent?: RuntimeEvent }> {
    this.setState(ConnectionState.CONNECTING);
    try {
      // 1. Re-establish session
      await this.client.startSession();

      // 2. Synchronize active task state if one existed
      const currentTask = this.client.getCurrentTaskId();
      let taskEvent: RuntimeEvent | undefined;
      if (currentTask) {
        taskEvent = await this.client.getStatus(currentTask);
      }

      this.setState(ConnectionState.CONNECTED);
      return { reconnected: true, taskEvent };
    } catch {
      this.setState(ConnectionState.DISCONNECTED);
      return { reconnected: false };
    }
  }
}
