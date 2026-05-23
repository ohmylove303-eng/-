/**
 * K-AFAS 프론트엔드 공용 타입 정의
 * 핵심 결정: 무기 관련 필드 절대 포함 금지
 */

export interface LayerSpec {
  layer_id: string;
  name_ko: string;
  name_en: string;
  default_visible: boolean;
  display_only: true; // 항상 true (타입레벨 잠금)
  source_hint: string;
  z_order: number;
}

export type MapMode = "3d" | "2d";

export type CoordQuality = "HIGH" | "MEDIUM" | "LOW";
export type FreshnessStatus = "GREEN" | "YELLOW" | "RED" | "BLACK";
export type GateResult = "PASS" | "HOLD" | "REJECT";

export interface CaseResponse {
  candidate_id: string;
  status: string;
  recommendation: string;
  gate_result: string;
  civilian_risk: string;
  friendly_risk: string;
  ttrr_seconds: number | null;
  audit_chain_ok: boolean | null;
}

export interface ReviewDecision {
  reviewer_role: string;
  decision: "request_more_evidence" | "hold" | "reject" | "approve_for_next_review";
  decision_reason: string;
}

/** TTRR 메트릭 (초 단위) */
export interface TtrrMetrics {
  p50: number;
  p95: number;
  p99: number;
  count: number;
}

/** 게이트 분포 */
export interface GateDistribution {
  pass: number;
  hold: number;
  reject: number;
}

/** 신선도 분포 */
export interface FreshnessDistribution {
  green: number;
  yellow: number;
  red: number;
  black: number;
}
