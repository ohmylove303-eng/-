/**
 * TTRR (Time-to-Review-Ready) 위젯
 * KPI: P50 ≤30s, P95 ≤60s, P99 ≤120s (권고치)
 * 금지: Time-to-Fire 측정 절대 불가
 */
import { TtrrMetrics } from "../types";

interface Props {
  metrics: TtrrMetrics;
}

const THRESHOLDS = { p50: 30, p95: 60, p99: 120 };

function statusColor(value: number, threshold: number): string {
  if (value <= threshold * 0.7) return "#22c55e";
  if (value <= threshold) return "#eab308";
  return "#ef4444";
}

export default function TtrrWidget({ metrics }: Props) {
  return (
    <div className="widget-card">
      <div className="widget-title">TTRR (Time-to-Review-Ready)</div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div>
          <span className="widget-value" style={{ color: statusColor(metrics.p50, THRESHOLDS.p50) }}>
            {metrics.p50.toFixed(1)}
          </span>
          <span className="widget-unit">s (P50)</span>
        </div>
        <div style={{ textAlign: "right", fontSize: "11px" }}>
          <div>
            <span style={{ color: statusColor(metrics.p95, THRESHOLDS.p95) }}>
              P95: {metrics.p95.toFixed(1)}s
            </span>
          </div>
          <div>
            <span style={{ color: statusColor(metrics.p99, THRESHOLDS.p99) }}>
              P99: {metrics.p99.toFixed(1)}s
            </span>
          </div>
        </div>
      </div>
      <div style={{ fontSize: "10px", color: "#64748b", marginTop: "4px" }}>
        처리 {metrics.count}건 · 목표 P50≤30s P95≤60s
      </div>
    </div>
  );
}
