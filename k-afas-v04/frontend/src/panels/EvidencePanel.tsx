/**
 * EvidencePanel — 증거 검토 패널
 *
 * 선택된 표적후보의 증거 정보를 표시.
 * 인터랙션: play_video_clip, view_observer_report, view_sensor_event, compare_sources
 */
import { CaseResponse } from "../types";

interface Props {
  selectedCase: CaseResponse | null;
}

// Mock 증거 데이터
const MOCK_EVIDENCE: Record<string, Evidence[]> = {
  "TGT-001": [
    { id: "E1", type: "uav_video", source: "RQ-101 UAV", time: "14:32 KST", freshness: "GREEN", confidence: 0.85 },
    { id: "E2", type: "sigint", source: "전자전대대", time: "14:28 KST", freshness: "GREEN", confidence: 0.72 },
    { id: "E3", type: "humint", source: "GOP 관측소", time: "14:15 KST", freshness: "YELLOW", confidence: 0.60 },
  ],
  "TGT-002": [
    { id: "E4", type: "satellite", source: "정찰위성", time: "13:45 KST", freshness: "YELLOW", confidence: 0.68 },
  ],
  "TGT-003": [
    { id: "E5", type: "uav_video", source: "KUS-FS UAV", time: "12:10 KST", freshness: "RED", confidence: 0.45 },
  ],
  "TGT-004": [
    { id: "E6", type: "sigint", source: "합참 신호정보", time: "14:40 KST", freshness: "GREEN", confidence: 0.90 },
    { id: "E7", type: "uav_video", source: "소형 UAV", time: "14:38 KST", freshness: "GREEN", confidence: 0.82 },
  ],
  "TGT-005": [
    { id: "E8", type: "humint", source: "첩보원 보고", time: "11:30 KST", freshness: "RED", confidence: 0.40 },
  ],
};

interface Evidence {
  id: string;
  type: string;
  source: string;
  time: string;
  freshness: string;
  confidence: number;
}

const FRESHNESS_COLOR: Record<string, string> = {
  GREEN: "#22c55e",
  YELLOW: "#eab308",
  RED: "#ef4444",
  BLACK: "#64748b",
};

const TYPE_ICON: Record<string, string> = {
  uav_video: "📹",
  sigint: "📡",
  humint: "👤",
  satellite: "🛰️",
};

export default function EvidencePanel({ selectedCase }: Props) {
  const evidence = selectedCase ? (MOCK_EVIDENCE[selectedCase.candidate_id] || []) : [];

  return (
    <>
      <div className="panel-header">
        <span>증거 검토</span>
        <span style={{ fontSize: "10px", color: "#64748b" }}>
          {selectedCase?.candidate_id || "선택 없음"} · {evidence.length}건
        </span>
      </div>
      <div className="panel-body">
        {!selectedCase && (
          <div style={{ color: "#64748b", fontSize: "12px", textAlign: "center", paddingTop: "20px" }}>
            지도에서 표적후보를 선택하세요
          </div>
        )}

        {evidence.map((e) => (
          <div key={e.id} className="widget-card" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "18px" }}>{TYPE_ICON[e.type] || "📋"}</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: "12px", fontWeight: 600, color: "#f1f5f9" }}>
                {e.source}
              </div>
              <div style={{ fontSize: "10px", color: "#94a3b8", display: "flex", gap: "8px" }}>
                <span>{e.type}</span>
                <span>{e.time}</span>
                <span>신뢰도 {Math.round(e.confidence * 100)}%</span>
              </div>
            </div>
            <span
              style={{
                width: "8px", height: "8px", borderRadius: "50%",
                background: FRESHNESS_COLOR[e.freshness] || "#64748b",
              }}
              title={`신선도: ${e.freshness}`}
            />
          </div>
        ))}

        {selectedCase && evidence.length > 0 && (
          <div style={{ marginTop: "8px", display: "flex", gap: "4px" }}>
            <button className="btn btn-more" style={{ fontSize: "10px", padding: "4px 8px" }}>
              출처 비교
            </button>
          </div>
        )}
      </div>
    </>
  );
}
