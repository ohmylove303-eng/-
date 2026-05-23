/**
 * Freshness — 정보 신선도 분포 위젯
 * GREEN(5분이내) / YELLOW(15분) / RED(60분) / BLACK(만료)
 * 색맹 안전: Okabe-Ito 계열
 */
import { FreshnessDistribution } from "../types";

interface Props {
  distribution: FreshnessDistribution;
}

const COLORS = {
  green: "#009E73",
  yellow: "#F0E442",
  red: "#D55E00",
  black: "#64748b",
};

const LABELS = {
  green: "5분내",
  yellow: "15분내",
  red: "60분내",
  black: "만료",
};

export default function FreshnessWidget({ distribution }: Props) {
  const total = distribution.green + distribution.yellow + distribution.red + distribution.black;
  if (total === 0) return null;

  return (
    <div className="widget-card">
      <div className="widget-title">정보 신선도</div>

      {/* 도트 그리드 */}
      <div style={{ display: "flex", gap: "4px", marginBottom: "6px", flexWrap: "wrap" }}>
        {Array(distribution.green).fill(null).map((_, i) => (
          <span key={`g${i}`} style={{ width: "12px", height: "12px", borderRadius: "50%", background: COLORS.green }} />
        ))}
        {Array(distribution.yellow).fill(null).map((_, i) => (
          <span key={`y${i}`} style={{ width: "12px", height: "12px", borderRadius: "50%", background: COLORS.yellow }} />
        ))}
        {Array(distribution.red).fill(null).map((_, i) => (
          <span key={`r${i}`} style={{ width: "12px", height: "12px", borderRadius: "50%", background: COLORS.red }} />
        ))}
        {Array(distribution.black).fill(null).map((_, i) => (
          <span key={`b${i}`} style={{ width: "12px", height: "12px", borderRadius: "50%", background: COLORS.black }} />
        ))}
      </div>

      {/* 범례 */}
      <div style={{ display: "flex", gap: "8px", fontSize: "10px" }}>
        {(Object.keys(COLORS) as (keyof typeof COLORS)[]).map((key) => (
          <span key={key} style={{ display: "flex", alignItems: "center", gap: "3px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: COLORS[key] }} />
            <span style={{ color: "#94a3b8" }}>{LABELS[key]} ({distribution[key]})</span>
          </span>
        ))}
      </div>
    </div>
  );
}
