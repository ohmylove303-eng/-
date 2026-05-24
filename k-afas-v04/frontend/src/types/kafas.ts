/**
 * K-AFAS v0.4.1 타입 정의 (설계명세 기준)
 * 금지: weapon_control, firing_data, ballistic_calculation
 */

export type Scenario = 'CLEAN' | 'DEGRADED' | 'CONTESTED';

export type StageKey =
  | 'SENSOR'
  | 'AI'
  | 'TRACK'
  | 'REVIEW_PACKAGE'
  | 'HITL'
  | 'LINK';

export interface ScenarioLatencyStat {
  scenario: Scenario;
  meanLatencySec: number;
  medianLatencySec: number;
  successRatePct: number;
}

export interface StageLatency {
  stage: StageKey;
  meanSec: number;
}

export interface ScenarioMetrics {
  currentScenario: Scenario;
  statsByScenario: ScenarioLatencyStat[];
  stagesForScenario: StageLatency[];
  ttsrSec: number;
}

export interface MetricsPanelProps {
  metrics: ScenarioMetrics;
  targetId: string | null;
}

/** 레이어 표시전용 정의 (프론트 내부 변환용) */
export interface LayerDefinition {
  id: string;
  label: string;
  active: boolean;
  displayOnly: true; // 타입레벨 잠금
}

/** 기존 API 호환 — layers: string[], activeLayers: string[] */
export interface LeftMapPanelProps {
  layers: string[];
  activeLayers: string[];
  targets: TargetMarker[];
  selectedTargetId: string | null;
  onSelectTarget: (id: string) => void;
  onToggleLayer: (layer: string) => void;
}

export interface TargetMarker {
  id: string;
  x: number; // % position
  y: number;
  gate: 'PASS' | 'HOLD' | 'REJECT';
  scenario: Scenario;
}
