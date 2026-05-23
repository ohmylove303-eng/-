/**
 * LeftMapPanel — 지도 패널 (설계명세 호환)
 *
 * Props: layers:string[], activeLayers:string[] (기존 API 호환)
 * 내부: normalizeLayers() → LayerDefinition[] 변환
 * 정책: DISPLAY_ONLY, 클립보드/우클릭/드래그 차단
 * 금지: fire_control, weapon_release, turret, kill_chain 등
 */
import { useEffect, useRef, useCallback } from "react";
import { LeftMapPanelProps } from "../types/kafas";
import { normalizeLayers, attachDisplayOnlyGuards } from "../utils/displayOnlyGuards";

const GATE_COLOR = { PASS: "#22c55e", HOLD: "#eab308", REJECT: "#ef4444" } as const;

export default function LeftMapPanel({
  layers,
  activeLayers,
  targets,
  selectedTargetId,
  onSelectTarget,
  onToggleLayer,
}: LeftMapPanelProps) {
  const mapRef = useRef<HTMLDivElement>(null);

  // DISPLAY_ONLY 보안 이벤트 등록
  useEffect(() => {
    if (!mapRef.current) return;
    return attachDisplayOnlyGuards(mapRef.current);
  }, []);

  // 내부 레이어 정규화
  const normalizedLayers = normalizeLayers(layers, activeLayers);

  return (
    <section className="left-map-panel">
      {/* 헤더 */}
      <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", padding: "6px 12px", background: "#0f172a", borderBottom: "1px solid #334155", fontSize: "12px", fontWeight: 600, color: "#cbd5e1" }}>
        <span>지도/지형 패널 (3D)</span>
        <span style={{ fontSize: "10px", color: "#64748b" }}>DISPLAY_ONLY · CesiumJS</span>
      </div>

      {/* 레이어 토글 */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "3px", padding: "4px 8px", borderBottom: "1px solid #1e293b" }}>
        {normalizedLayers.map((layer) => (
          <span
            key={layer.id}
            onClick={() => onToggleLayer(layer.id)}
            style={{
              padding: "2px 7px", borderRadius: "12px", fontSize: "9px",
              cursor: "pointer", border: "1px solid #475569",
              background: layer.active ? "#3b82f6" : "transparent",
              borderColor: layer.active ? "#3b82f6" : "#475569",
              color: layer.active ? "#fff" : "#64748b",
              userSelect: "none",
            }}
          >
            {layer.label}
          </span>
        ))}
      </div>

      {/* 지도 영역 */}
      <div ref={mapRef} style={{ flex: 1, position: "relative", background: "#0a1628", overflow: "hidden", userSelect: "none" }}>
        {/* 그리드 배경 */}
        <svg style={{ position: "absolute", inset: 0, opacity: 0.12 }} width="100%" height="100%">
          <defs>
            <pattern id="mapgrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#334155" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#mapgrid)" />
        </svg>

        {/* 표적 마커 */}
        {targets.map((t) => (
          <div
            key={t.id}
            onClick={() => onSelectTarget(t.id)}
            style={{
              position: "absolute", left: `${t.x}%`, top: `${t.y}%`,
              width: "14px", height: "14px", borderRadius: "50%",
              border: "2px solid #fff", cursor: "pointer",
              background: GATE_COLOR[t.gate],
              transform: t.id === selectedTargetId ? "scale(1.4)" : "scale(1)",
              boxShadow: t.id === selectedTargetId ? "0 0 0 4px rgba(59,130,246,0.5)" : "none",
              transition: "transform 0.2s, box-shadow 0.2s", zIndex: 2,
            }}
          >
            <span style={{
              position: "absolute", top: "-16px", left: "50%", transform: "translateX(-50%)",
              fontSize: "8px", whiteSpace: "nowrap", color: "#fff",
              textShadow: "0 1px 2px #000", pointerEvents: "none",
            }}>
              {t.id}
            </span>
          </div>
        ))}
      </div>

      {/* 좌표 바 */}
      <div style={{ padding: "5px 12px", background: "#0f172a", borderTop: "1px solid #334155", display: "flex", alignItems: "center", gap: "10px", fontSize: "11px" }}>
        <span style={{ fontWeight: 700 }}>{selectedTargetId || "-"}</span>
        <span style={{ color: "#64748b" }}>DISPLAY_ONLY · 복사 차단</span>
      </div>
    </section>
  );
}
