/**
 * MapPanel — CesiumJS 3D 지형 + 15 레이어 토글
 *
 * 정책:
 * - 모든 레이어 display_only=true (타입레벨 강제)
 * - 좌표 클립보드 복사 차단
 * - 금지 레이어 키워드 추가 불가
 */
import { useEffect, useRef, useState, useCallback } from "react";
import { CaseResponse, LayerSpec } from "../types";

// 표준 15 레이어 (kafas/viz/layers.py 와 동기화)
const STANDARD_LAYERS: LayerSpec[] = [
  { layer_id: "terrain", name_ko: "지형", name_en: "Terrain", default_visible: true, display_only: true, source_hint: "DTED/SRTM/DEM", z_order: 0 },
  { layer_id: "transport", name_ko: "교통망", name_en: "Transport", default_visible: true, display_only: true, source_hint: "OSM road/rail", z_order: 5 },
  { layer_id: "hydrology", name_ko: "수계", name_en: "Hydrology", default_visible: false, display_only: true, source_hint: "OSM water", z_order: 6 },
  { layer_id: "civilian_areas", name_ko: "민간거주", name_en: "Civilian Areas", default_visible: true, display_only: true, source_hint: "OSM amenity", z_order: 10 },
  { layer_id: "restricted_zones", name_ko: "제한구역", name_en: "Restricted Zones", default_visible: true, display_only: true, source_hint: "ROE/공역", z_order: 15 },
  { layer_id: "friendly_forces", name_ko: "아군위치", name_en: "Friendly Forces", default_visible: true, display_only: true, source_hint: "BFT", z_order: 20 },
  { layer_id: "deconfliction", name_ko: "충돌영역", name_en: "Deconfliction", default_visible: true, display_only: true, source_hint: "인접부대", z_order: 25 },
  { layer_id: "threat_layer", name_ko: "적위험도", name_en: "Threat", default_visible: true, display_only: true, source_hint: "다중출처", z_order: 30 },
  { layer_id: "target_candidates", name_ko: "표적후보", name_en: "Target Candidates", default_visible: true, display_only: true, source_hint: "L4", z_order: 40 },
  { layer_id: "evidence_markers", name_ko: "증거마커", name_en: "Evidence Markers", default_visible: false, display_only: true, source_hint: "출처별", z_order: 41 },
  { layer_id: "freshness_heatmap", name_ko: "신선도", name_en: "Freshness Heatmap", default_visible: true, display_only: true, source_hint: "L3", z_order: 45 },
  { layer_id: "coord_quality", name_ko: "좌표품질", name_en: "Coord Quality", default_visible: true, display_only: true, source_hint: "L5 CEP", z_order: 46 },
  { layer_id: "risk_gate_overlay", name_ko: "게이트결과", name_en: "Safety Gate", default_visible: true, display_only: true, source_hint: "L6", z_order: 50 },
  { layer_id: "review_queue", name_ko: "검토대기열", name_en: "Review Queue", default_visible: true, display_only: true, source_hint: "L7", z_order: 60 },
  { layer_id: "audit_trail", name_ko: "감사추적", name_en: "Audit Trail", default_visible: false, display_only: true, source_hint: "L8", z_order: 70 },
];

// 좌표품질 색상 (Okabe-Ito 기반)
const QUALITY_COLOR = { HIGH: "#E53E3E", MEDIUM: "#D69E2E", LOW: "#A0AEC0" } as const;

// 게이트 결과 색상
const GATE_COLOR = { PASS: "#22c55e", HOLD: "#eab308", REJECT: "#ef4444" } as const;

interface Props {
  cases: CaseResponse[];
  selectedCase: CaseResponse | null;
  onSelect: (c: CaseResponse) => void;
}

export default function MapPanel({ cases, selectedCase, onSelect }: Props) {
  const cesiumRef = useRef<HTMLDivElement>(null);
  const [visibleLayers, setVisibleLayers] = useState<Set<string>>(
    () => new Set(STANDARD_LAYERS.filter((l) => l.default_visible).map((l) => l.layer_id))
  );
  const [mapMode, setMapMode] = useState<"3d" | "2d">("3d");
  const [cesiumLoaded, setCesiumLoaded] = useState(false);

  // CesiumJS 초기화
  useEffect(() => {
    if (!cesiumRef.current) return;

    let viewer: any = null;

    async function initCesium() {
      try {
        const Cesium = await import("cesium");
        // Ion 토큰 (데모용 — 실제 운용 시 환경변수)
        Cesium.Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_TOKEN || "";

        viewer = new Cesium.Viewer(cesiumRef.current!, {
          terrain: Cesium.Terrain.fromWorldTerrain(),
          baseLayerPicker: false,
          geocoder: false,
          homeButton: false,
          sceneModePicker: false,
          navigationHelpButton: false,
          animation: false,
          timeline: false,
          fullscreenButton: false,
          selectionIndicator: true,
          infoBox: false,
        });

        // 한반도 중심 (약 대전 부근)
        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(127.5, 36.5, 500000),
          duration: 0,
        });

        // 표적후보 마커 표시 (mock 위치)
        const mockPositions = [
          { lon: 127.1, lat: 37.5, id: "TGT-001", gate: "PASS" },
          { lon: 126.9, lat: 37.4, id: "TGT-002", gate: "HOLD" },
          { lon: 127.3, lat: 36.8, id: "TGT-003", gate: "REJECT" },
          { lon: 128.1, lat: 35.9, id: "TGT-004", gate: "PASS" },
          { lon: 127.8, lat: 36.2, id: "TGT-005", gate: "HOLD" },
        ];

        for (const pos of mockPositions) {
          const color = GATE_COLOR[pos.gate as keyof typeof GATE_COLOR] || "#fff";
          viewer.entities.add({
            position: Cesium.Cartesian3.fromDegrees(pos.lon, pos.lat),
            point: {
              pixelSize: 12,
              color: Cesium.Color.fromCssColorString(color),
              outlineColor: Cesium.Color.WHITE,
              outlineWidth: 2,
            },
            label: {
              text: pos.id,
              font: "11px sans-serif",
              fillColor: Cesium.Color.WHITE,
              style: Cesium.LabelStyle.FILL_AND_OUTLINE,
              outlineWidth: 2,
              verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
              pixelOffset: new Cesium.Cartesian2(0, -14),
            },
          });
        }

        setCesiumLoaded(true);

        // 클립보드 복사 차단
        cesiumRef.current?.addEventListener("copy", (e) => {
          e.preventDefault();
          console.warn("[K-AFAS] 좌표 클립보드 복사 차단 (DISPLAY_ONLY)");
        });
      } catch (err) {
        console.warn("[MapPanel] CesiumJS 초기화 실패 (토큰 또는 CDN 문제):", err);
        setCesiumLoaded(false);
      }
    }

    initCesium();

    return () => {
      if (viewer && !viewer.isDestroyed()) viewer.destroy();
    };
  }, []);

  // 레이어 토글
  const toggleLayer = useCallback((layerId: string) => {
    setVisibleLayers((prev) => {
      const next = new Set(prev);
      if (next.has(layerId)) next.delete(layerId);
      else next.add(layerId);
      return next;
    });
  }, []);

  return (
    <>
      <div className="panel-header">
        <span>지도/지형 패널 ({mapMode.toUpperCase()})</span>
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          <button
            className="btn"
            style={{ padding: "2px 8px", fontSize: "10px", background: "#475569", color: "#fff" }}
            onClick={() => setMapMode(mapMode === "3d" ? "2d" : "3d")}
          >
            {mapMode === "3d" ? "2D 전환" : "3D 전환"}
          </button>
          <span style={{ fontSize: "10px", color: "#64748b" }}>
            {cesiumLoaded ? "Cesium OK" : "로딩중..."}
          </span>
        </div>
      </div>

      {/* 레이어 토글 바 */}
      <div className="layer-toggle">
        {STANDARD_LAYERS.map((layer) => (
          <span
            key={layer.layer_id}
            className={`layer-chip ${visibleLayers.has(layer.layer_id) ? "active" : "inactive"}`}
            onClick={() => toggleLayer(layer.layer_id)}
            title={`${layer.name_en} — ${layer.source_hint}`}
          >
            {layer.name_ko}
          </span>
        ))}
      </div>

      {/* Cesium 뷰포트 */}
      <div
        ref={cesiumRef}
        style={{ flex: 1, position: "relative", background: "#0a0f1a" }}
      >
        {!cesiumLoaded && (
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            alignItems: "center", justifyContent: "center",
            color: "#64748b", fontSize: "14px", flexDirection: "column", gap: "8px",
          }}>
            <div style={{ fontSize: "32px" }}>🌍</div>
            <div>CesiumJS 3D 지형 로딩중...</div>
            <div style={{ fontSize: "11px" }}>VITE_CESIUM_TOKEN 설정 필요</div>
          </div>
        )}
      </div>

      {/* 선택된 표적 정보 바 */}
      {selectedCase && (
        <div style={{
          padding: "6px 12px", background: "#0f172a",
          borderTop: "1px solid #334155", display: "flex",
          alignItems: "center", gap: "12px", fontSize: "11px",
        }}>
          <span style={{ fontWeight: 700, color: "#f1f5f9" }}>{selectedCase.candidate_id}</span>
          <span style={{
            color: GATE_COLOR[selectedCase.gate_result as keyof typeof GATE_COLOR] || "#fff",
            fontWeight: 600,
          }}>
            {selectedCase.gate_result}
          </span>
          <span>민간위험: {selectedCase.civilian_risk}</span>
          <span>아군위험: {selectedCase.friendly_risk}</span>
          <span style={{ color: "#64748b" }}>DISPLAY_ONLY</span>
        </div>
      )}

      {/* 표적 목록 (선택용) */}
      <div style={{
        display: "flex", gap: "4px", padding: "4px 8px",
        overflowX: "auto", background: "#0f172a",
        borderTop: "1px solid #1e293b",
      }}>
        {cases.map((c) => (
          <button
            key={c.candidate_id}
            onClick={() => onSelect(c)}
            style={{
              padding: "2px 8px", borderRadius: "4px", border: "none",
              fontSize: "10px", cursor: "pointer", whiteSpace: "nowrap",
              background: c.candidate_id === selectedCase?.candidate_id ? "#3b82f6" : "#334155",
              color: c.candidate_id === selectedCase?.candidate_id ? "#fff" : "#94a3b8",
            }}
          >
            {c.candidate_id}
          </button>
        ))}
      </div>
    </>
  );
}
