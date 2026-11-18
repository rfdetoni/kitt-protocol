/** Cortex event plane: typed observations, never execution grants. */
export type CortexAutonomyTier = "GREEN" | "YELLOW" | "RED";
export type CortexPreflightDecision = "READ_ONLY" | "REQUIRE_APPROVAL" | "DENY";

export interface CortexEvent {
  id: string;
  topic: string;
  source: string;
  severity: number;
  untrusted: boolean;
  sensitivity: "public" | "personal" | "private" | "secret" | "ephemeral";
  payload: Record<string, unknown>;
  created: number;
  expires: number;
}
export interface CortexDelivery extends CortexEvent {
  attempt: number;
  lease_token: string;
}
export interface CortexPreflight {
  tier: CortexAutonomyTier;
  decision: CortexPreflightDecision;
  reason: string;
}
export interface CortexContextProjection {
  value: string;
  source: string;
  sensitivity: CortexEvent["sensitivity"];
  observed: number;
  expires: number;
  revision: number;
}
export interface CortexRouteAdvice {
  route: "local_only" | "existing_agent_router";
  advisory: Record<string, unknown> | null;
  status: "disabled" | "invalid_endpoint" | "invalid_timeout" | "unavailable" | "ok";
}
