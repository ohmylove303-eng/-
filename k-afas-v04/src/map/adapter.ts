/**
 * K-AFAS v0.4.1 지도엔진 어댑터
 * CesiumJS (3D 지형 + 표고) + MapLibre GL (2D 벡터) 통합.
 *
 * 좌표: WGS84 (EPSG:4326), Web Mercator (EPSG:3857).
 * 모든 레이어: display_only=true 강제. false면 throw.
 *
 * REJECT: 사격제원 표시, 포탑 카메라, 무기 직접연동 레이어.
 */

// ── 타입 정의 ─────────────────────────────────────────
export interface LayerSpec {
  layer_id: string;
  name_ko: string;
  name_en: string;
  default_visible: boolean;
  display_only: boolean;
  source_hint: string;
  z_order: number;
}

export type MapMode = "3d" | "2d";

// 좌표 정책: 화면 표시만. 클립보드 복사 차단.
const COORD_POLICY = "DISPLAY_ONLY" as const;

// ── 금지 레이어 키워드 (추가 시도 차단) ───────────────────
const FORBIDDEN_KEYWORDS = [
  "fire_control", "weapon_release", "turret",
  "kill_chain", "strike_planner", "firing_solution",
  "사격제원", "사격지시", "발사명령",
];

// ── 표준 15 레이어 ────────────────────────────────────
export const STANDARD_LAYERS: LayerSpec[] = [
  { layer_id: "terrain", name_ko: "지형", name_en: "Terrain", default_visible: true, display_only: true, source_hint: "DTED/SRTM/DEM", z_order: 0 },
  { layer_id: "transport", name_ko: "교통망", name_en: "Transport", default_visible: true, display_only: true, source_hint: "OSM road/rail", z_order: 5 },
  { layer_id: "hydrology", name_ko: "수계", name_en: "Hydrology", default_visible: false, display_only: true, source_hint: "OSM water", z_order: 6 },
  { layer_id: "civilian_areas", name_ko: "민간거주·시설", name_en: "Civilian Areas", default_visible: true, display_only: true, source_hint: "OSM amenity", z_order: 10 },
  { layer_id: "restricted_zones", name_ko: "제한구역", name_en: "Restricted Zones", default_visible: true, display_only: true, source_hint: "ROE/공역", z_order: 15 },
  { layer_id: "friendly_forces", name_ko: "아군 위치", name_en: "Friendly Forces", default_visible: true, display_only: true, source_hint: "BFT", z_order: 20 },
  { layer_id: "deconfliction", name_ko: "임무 충돌영역", name_en: "Deconfliction", default_visible: true, display_only: true, source_hint: "인접부대 임무", z_order: 25 },
  { layer_id: "threat_layer", name_ko: "적 위험도", name_en: "Threat", default_visible: true, display_only: true, source_hint: "다중출처", z_order: 30 },
  { layer_id: "target_candidates", name_ko: "표적후보", name_en: "Target Candidates", default_visible: true, display_only: true, source_hint: "L4", z_order: 40 },
  { layer_id: "evidence_markers", name_ko: "증거 마커", name_en: "Evidence Markers", default_visible: false, display_only: true, source_hint: "출처별", z_order: 41 },
  { layer_id: "freshness_heatmap", name_ko: "정보신선도", name_en: "Freshness Heatmap", default_visible: true, display_only: true, source_hint: "L3", z_order: 45 },
  { layer_id: "coord_quality", name_ko: "좌표품질", name_en: "Coordinate Quality", default_visible: true, display_only: true, source_hint: "L5 CEP", z_order: 46 },
  { layer_id: "risk_gate_overlay", name_ko: "안전게이트 결과", name_en: "Safety Gate", default_visible: true, display_only: true, source_hint: "L6", z_order: 50 },
  { layer_id: "review_queue", name_ko: "검토 대기열", name_en: "Review Queue", default_visible: true, display_only: true, source_hint: "L7", z_order: 60 },
  { layer_id: "audit_trail", name_ko: "감사 추적", name_en: "Audit Trail", default_visible: false, display_only: true, source_hint: "L8 hashchain", z_order: 70 },
];

// ── display_only 검증 ─────────────────────────────────
function assertDisplayOnly(layer: LayerSpec): void {
  if (!layer.display_only) {
    throw new Error(`[REJECT] layer ${layer.layer_id} must be display_only=true`);
  }
}

// ── 금지 키워드 검증 ──────────────────────────────────
function assertNotForbidden(layer: LayerSpec): void {
  const blob = `${layer.layer_id} ${layer.name_ko} ${layer.name_en} ${layer.source_hint}`.toLowerCase();
  for (const kw of FORBIDDEN_KEYWORDS) {
    if (blob.includes(kw.toLowerCase())) {
      throw new Error(`[REJECT] forbidden keyword "${kw}" in layer ${layer.layer_id}`);
    }
  }
}

// ── Cesium 3D 렌더 (표적후보) ──────────────────────────
interface CandidatePoint {
  lat: number;
  lon: number;
  coord_quality: "HIGH" | "MEDIUM" | "LOW";
  cep_meters: number;
}

// 좌표품질별 시각 표현 규칙
const QUALITY_STYLE = {
  HIGH:   { color: "#E53E3E", size: 16 },   // 빨강 16px
  MEDIUM: { color: "#D69E2E", size: 12 },   // 노랑 12px
  LOW:    { color: "#A0AEC0", size: 8 },     // 회색 8px
} as const;

// 신선도별 히트맵 색상 (색맹 안전: Okabe-Ito 기반)
const FRESHNESS_COLOR = {
  GREEN:  "#009E73",  // 초록 (5분 이내)
  YELLOW: "#F0E442",  // 노랑 (15분 이내)
  RED:    "#D55E00",  // 주황-빨강 (60분 이내)
  BLACK:  "#000000",  // 검정 (만료)
} as const;

// ── 어댑터 클래스 ─────────────────────────────────────
export class MapAdapter {
  private mode: MapMode;
  private layers: Map<string, LayerSpec> = new Map();
  private visibleIds: Set<string> = new Set();

  constructor(mode: MapMode = "3d") {
    this.mode = mode;
    // 표준 레이어 등록
    for (const l of STANDARD_LAYERS) {
      assertDisplayOnly(l);
      assertNotForbidden(l);
      this.layers.set(l.layer_id, l);
      if (l.default_visible) this.visibleIds.add(l.layer_id);
    }
  }

  /** 레이어 토글 */
  toggle(layerId: string, on: boolean): void {
    if (!this.layers.has(layerId)) throw new Error(`unknown layer: ${layerId}`);
    if (on) this.visibleIds.add(layerId);
    else this.visibleIds.delete(layerId);
  }

  /** 사용자 정의 레이어 추가 (금지 키워드 + display_only 검증) */
  addCustomLayer(layer: LayerSpec): void {
    assertDisplayOnly(layer);
    assertNotForbidden(layer);
    this.layers.set(layer.layer_id, layer);
  }

  /** 현재 보이는 레이어 목록 (z_order 정렬) */
  getVisibleLayers(): LayerSpec[] {
    return Array.from(this.layers.values())
      .filter(l => this.visibleIds.has(l.layer_id))
      .sort((a, b) => a.z_order - b.z_order);
  }

  /** 표적후보 렌더 파라미터 생성 (Cesium PointPrimitive 용) */
  candidateStyle(point: CandidatePoint) {
    const style = QUALITY_STYLE[point.coord_quality];
    return {
      position: { lat: point.lat, lon: point.lon },
      pixelSize: style.size,
      color: style.color,
      cepRadius: point.cep_meters,
      policy: COORD_POLICY,  // 항상 DISPLAY_ONLY
    };
  }

  /** 신선도 히트맵 색상 반환 */
  freshnessColor(status: keyof typeof FRESHNESS_COLOR): string {
    return FRESHNESS_COLOR[status];
  }

  /** 제한구역 스타일 (폴리곤 외곽선 + 30% fill) */
  restrictedZoneStyle() {
    return {
      stroke: "#E53E3E",
      strokeWidth: 2,
      fillColor: "rgba(229, 62, 62, 0.3)",
      policy: COORD_POLICY,
    };
  }

  /** 좌표 클립보드 복사 차단 (이벤트 핸들러) */
  blockClipboardCopy(event: ClipboardEvent): void {
    event.preventDefault();
    console.warn("[K-AFAS] 좌표 클립보드 복사 차단됨 (DISPLAY_ONLY)");
  }

  /** 모드 전환 (3D ↔ 2D) */
  switchMode(newMode: MapMode): void {
    this.mode = newMode;
  }

  getMode(): MapMode {
    return this.mode;
  }
}
