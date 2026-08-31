export const PROTOCOL_VERSION = 1 as const;
export type HudState = "listening" | "thinking" | "responding" | "executing" | "error";
export type HudEvent =
  | { type: "status"; state: HudState; message?: string | null }
  | { type: "text"; content: string; ttl_ms: number }
  | { type: "image"; src: string; alt?: string | null; ttl_ms: number }
  | { type: "hide" };
export interface Envelope<T = unknown> { version: 1; id: string; kind: string; payload: T; }
export type MemoryKind = "user_preference" | "project_rule" | "architecture_decision" | "technical_fact" | "working_pattern" | "failed_approach" | "open_issue" | "project_state" | "episodic" | "personal_fact" | "routine";
export type Sensitivity = "public" | "personal" | "private" | "secret" | "ephemeral";
export type MemoryScope = "global" | "workspace" | "conversation";
export interface MemoryDto { id:string; namespace:string; workspace_id:string; kind:MemoryKind; content:string; sensitivity:Sensitivity; scope:MemoryScope; importance:number; confidence:number; pinned:boolean; created_at:number; updated_at:number; }
