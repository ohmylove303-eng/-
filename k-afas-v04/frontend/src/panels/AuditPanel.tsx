/**
 * AuditPanel — TTRR 메트릭 + 감사 해시체인 검증
 *
 * 표시 지표:
 * - TTRR (Time-to-Review-Ready): P50/P95/P99
 * - 게이트 분포: PASS/HOLD/REJECT
 * - 감사 체인 무결성 상태
 *
 * 금지 지표: Time-to-Fire, Kill Rate, 무기 효율
 */
import { useState, useCallback, useMemo } from "react";
import { CaseResponse } from "../types";
import { verifyAuditChain } from "../api";
import TtrrWidget from "../widgets/Ttrr";
import GateDistWidget from "../widgets/GateDist";
import FreshnessWidget from "../widgets/Freshness";

interface Props {
  cases: CaseResponse[];
}

export default function AuditPanel({ cases }: Props) {
  const [chainStatus, setChainStatus] = useState<{ ok: boolean; reason: string } | null>(null);
  const [verifying, setVerifying] = useState(false);

  // TTRR 계산
  const ttrrValues = useMemo(() => {
    const vals = cases
      .map((c) => c.ttrr_seconds)
      .filter((v): v is number => v !== null)
      .sort((a, b) => a - b);

    if (vals.length === 0) return { p50: 0, p95: 0, p99: 0, count: 0 };

    const percentile = (arr: number[], p: number) => {
      const idx = Math.ceil((p / 100) * arr.length) - 1;
      return arr[Math.max(0, idx)];
    };

    return {
      p50: percentile(vals, 50),
      p95: percentile(vals, 95),
      p99: percentile(vals, 99),
      count: vals.length,
    };
  }, [cases]);

  // 게이트 분포 계산
  const gateDist = useMemo(() => {
    const dist = { pass: 0, hold: 0, reject: 0 };
    for (const c of cases) {
      const g = c.gate_result.toUpperCase();
      if (g === "PASS") dist.pass++;
      else if (g === "HOLD") dist.hold++;
      else if (g === "REJECT") dist.reject++;
    }
    return dist;
  }, [cases]);

  // 체인 검증
  const handleVerify = useCallback(async () => {
    setVerifying(true);
    const result = await verifyAuditChain();
    setChainStatus({ ok: result.chain_ok, reason: result.reason });
    setVerifying(false);
  }, []);

  return (
    <>
      <div className="panel-header">
        <span>감사/메트릭</span>
        <button
          className="btn"
          style={{ padding: "2px 8px", fontSize: "10px", background: "#475569", color: "#fff" }}
          onClick={handleVerify}
          disabled={verifying}
        >
          {verifying ? "검증중..." : "체인 검증"}
        </button>
      </div>
      <div className="panel-body">
        {/* TTRR 위젯 */}
        <TtrrWidget metrics={ttrrValues} />

        {/* 게이트 분포 위젯 */}
        <GateDistWidget distribution={gateDist} />

        {/* 신선도 위젯 (mock) */}
        <FreshnessWidget distribution={{ green: 3, yellow: 1, red: 1, black: 0 }} />

        {/* 체인 검증 상태 */}
        {chainStatus && (
          <div className="widget-card">
            <div className="widget-title">SHA-256 해시체인</div>
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{
                width: "10px", height: "10px", borderRadius: "50%",
                background: chainStatus.ok ? "#22c55e" : "#ef4444",
              }} />
              <span style={{ fontSize: "12px", fontWeight: 600, color: chainStatus.ok ? "#22c55e" : "#ef4444" }}>
                {chainStatus.ok ? "무결성 확인" : "체인 손상 감지"}
              </span>
              <span style={{ fontSize: "10px", color: "#64748b" }}>{chainStatus.reason}</span>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
