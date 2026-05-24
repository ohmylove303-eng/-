/**
 * DecisionPanel — 의사결정 지원 패널 (4버튼 동시 표시)
 *
 * 허용 인터랙션:
 *   1. 추가증거요청 (request_more_evidence)
 *   2. 보류 (hold)
 *   3. 거부 (reject)
 *   4. 다음 검토단계 승인 (approve_for_next_review)
 *
 * 절대 금지: fire, release_weapon, auto_engage, send_fire_command
 */
import { useState, useCallback } from "react";
import { CaseResponse, ReviewDecision } from "../types";
import { submitReview } from "../api";

interface Props {
  selectedCase: CaseResponse | null;
}

export default function DecisionPanel({ selectedCase }: Props) {
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);

  const handleDecision = useCallback(
    async (decision: ReviewDecision["decision"]) => {
      if (!selectedCase) return;
      if (!reason.trim()) {
        alert("결정 사유를 입력하세요.");
        return;
      }
      setSubmitting(true);
      const review: ReviewDecision = {
        reviewer_role: "commander",
        decision,
        decision_reason: reason,
      };
      await submitReview(selectedCase.candidate_id, review);
      setLastAction(`${decision} → ${selectedCase.candidate_id}`);
      setReason("");
      setSubmitting(false);
    },
    [selectedCase, reason]
  );

  const isDisabled = !selectedCase || submitting;
  const isRejected = selectedCase?.status === "REJECTED";

  return (
    <>
      <div className="panel-header">
        <span>의사결정 지원</span>
        <span style={{ fontSize: "10px", color: "#64748b" }}>
          {selectedCase?.candidate_id || "—"} · {selectedCase?.status || ""}
        </span>
      </div>
      <div className="panel-body">
        {!selectedCase ? (
          <div style={{ color: "#64748b", fontSize: "12px", textAlign: "center", paddingTop: "12px" }}>
            표적후보를 선택 후 검토하세요
          </div>
        ) : (
          <>
            {/* 케이스 요약 */}
            <div className="widget-card">
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px" }}>
                <span>게이트: <b style={{ color: selectedCase.gate_result === "PASS" ? "#22c55e" : selectedCase.gate_result === "HOLD" ? "#eab308" : "#ef4444" }}>{selectedCase.gate_result}</b></span>
                <span>추천: <b>{selectedCase.recommendation}</b></span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", marginTop: "4px" }}>
                <span>민간위험: {selectedCase.civilian_risk}</span>
                <span>아군위험: {selectedCase.friendly_risk}</span>
              </div>
            </div>

            {/* 사유 입력 */}
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="결정 사유를 입력하세요 (필수)..."
              disabled={isDisabled}
              style={{
                width: "100%", height: "40px", resize: "none",
                background: "#0f172a", border: "1px solid #334155",
                borderRadius: "4px", padding: "6px 8px",
                color: "#e2e8f0", fontSize: "11px", marginBottom: "8px",
              }}
            />

            {/* 4버튼 동시 표시 */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
              <button
                className="btn btn-more"
                disabled={isDisabled}
                onClick={() => handleDecision("request_more_evidence")}
              >
                추가증거요청
              </button>
              <button
                className="btn btn-hold"
                disabled={isDisabled}
                onClick={() => handleDecision("hold")}
              >
                보류
              </button>
              <button
                className="btn btn-reject"
                disabled={isDisabled || isRejected}
                onClick={() => handleDecision("reject")}
              >
                거부
              </button>
              <button
                className="btn btn-approve"
                disabled={isDisabled || isRejected}
                onClick={() => handleDecision("approve_for_next_review")}
              >
                다음검토 승인
              </button>
            </div>

            {/* 마지막 액션 피드백 */}
            {lastAction && (
              <div style={{ marginTop: "8px", fontSize: "10px", color: "#94a3b8" }}>
                최근: {lastAction}
              </div>
            )}

            {/* 안전 고지 */}
            <div style={{
              marginTop: "8px", fontSize: "9px", color: "#475569",
              borderTop: "1px solid #1e293b", paddingTop: "6px",
            }}>
              ⚠ 본 시스템은 의사결정 <b>지원</b>만 제공합니다. 최종 결정은 인가된 인간 지휘관의 권한입니다.
            </div>
          </>
        )}
      </div>
    </>
  );
}
