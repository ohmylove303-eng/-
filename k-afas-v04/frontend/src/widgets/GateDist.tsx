/**
 * GateDist — 안전게이트 결과 분포 위젯
 * 수평 스택 바 (PASS/HOLD/REJECT 비율)
 */
import { GateDistribution } from "../types";

interface Props {
  distribution: GateDistribution;
}

export default function GateDistWidget({ distribution }: Props) {
  const total = distribution.pass + distribution.hold + distribution.reject;
  if (total === 0) return null;

  const pct = {
    pass: Math.round((distribution.pass / total) * 100),
    hold: Math.round((distribution.hold / total) * 100),
    reject: Math.round((distribution.reject / total) * 100),
  };

  return (
    <div className="widget-card">
      <div className="widget-title">안전게이트 분포</div>

      {/* 스택 바 */}
      <div style={{
        display: "flex", height: "16px", borderRadius: "4px",
        overflow: "hidden", marginBottom: "4px",
      }}>
        {pct.pass > 0 && (
          <div style={{ width: `${pct.pass}%`, background: "#22c55e", transition: "width 0.3s" }} />
        )}
        {pct.hold > 0 && (
          <div style={{ width: `${pct.hold}%`, background: "#eab308", transition: "width 0.3s" }} />
        )}
        {pct.reject > 0 && (
          <div style={{ width: `${pct.reject}%`, background: "#ef4444", transition: "width 0.3s" }} />
        )}
      </div>

      {/* 레이블 */}
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px" }}>
        <span style={{ color: "#22c55e" }}>PASS {distribution.pass} ({pct.pass}%)</span>
        <span style={{ color: "#eab308" }}>HOLD {distribution.hold} ({pct.hold}%)</span>
        <span style={{ color: "#ef4444" }}>REJECT {distribution.reject} ({pct.reject}%)</span>
      </div>
    </div>
  );
}
