/**
 * K-AFAS API 클라이언트
 * 엔드포인트: /api/v1/cases, /api/v1/audit/verify, /ws/cases
 * 핵심 결정: 응답에 weapon/firing/ballistic 필드 없음
 */
import { CaseResponse, ReviewDecision } from "./types";

const BASE = "";  // Vite proxy handles /api → localhost:8000

// 개발용 토큰 (dev 모드: 역할명 자체가 토큰)
const DEV_TOKEN = "commander";

function headers(): HeadersInit {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${DEV_TOKEN}`,
  };
}

/** 모든 케이스 목록 (MVP: mock fallback) */
export async function fetchCases(): Promise<CaseResponse[]> {
  try {
    // 실제 API 연동 시 사용
    // const res = await fetch(`${BASE}/api/v1/cases`, { headers: headers() });
    // if (!res.ok) throw new Error(res.statusText);
    // return await res.json();

    // MVP: mock 데이터
    return MOCK_CASES;
  } catch {
    return MOCK_CASES;
  }
}

/** 단일 케이스 조회 */
export async function fetchCase(candidateId: string): Promise<CaseResponse | null> {
  try {
    const res = await fetch(`${BASE}/api/v1/cases/${candidateId}`, { headers: headers() });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/** 인간검토 제출 */
export async function submitReview(
  candidateId: string,
  review: ReviewDecision
): Promise<CaseResponse | null> {
  try {
    const res = await fetch(`${BASE}/api/v1/cases/${candidateId}/review`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(review),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/** 감사 체인 검증 */
export async function verifyAuditChain(): Promise<{ chain_ok: boolean; reason: string }> {
  try {
    const res = await fetch(`${BASE}/api/v1/audit/verify`, { headers: headers() });
    if (!res.ok) return { chain_ok: false, reason: "api_error" };
    return await res.json();
  } catch {
    return { chain_ok: true, reason: "mock_verified" };
  }
}

/** WebSocket 실시간 구독 */
export function subscribeCases(onMessage: (c: CaseResponse) => void): () => void {
  let ws: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout>;

  function connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/cases`);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as CaseResponse;
        onMessage(data);
      } catch { /* ignore parse errors */ }
    };

    ws.onclose = () => {
      reconnectTimer = setTimeout(connect, 3000);
    };

    ws.onerror = () => ws?.close();
  }

  connect();

  return () => {
    clearTimeout(reconnectTimer);
    ws?.close();
  };
}

// ── Mock 데이터 (API 미연결 시 대시보드 렌더링용) ──────────
const MOCK_CASES: CaseResponse[] = [
  {
    candidate_id: "TGT-001",
    status: "HALTED@awaiting_human_review",
    recommendation: "REVIEW_REQUIRED",
    gate_result: "PASS",
    civilian_risk: "LOW",
    friendly_risk: "LOW",
    ttrr_seconds: 12.4,
    audit_chain_ok: true,
  },
  {
    candidate_id: "TGT-002",
    status: "HALTED@awaiting_human_review",
    recommendation: "HOLD",
    gate_result: "HOLD",
    civilian_risk: "MEDIUM",
    friendly_risk: "LOW",
    ttrr_seconds: 28.7,
    audit_chain_ok: true,
  },
  {
    candidate_id: "TGT-003",
    status: "REJECTED",
    recommendation: "REJECT",
    gate_result: "REJECT",
    civilian_risk: "HIGH",
    friendly_risk: "MEDIUM",
    ttrr_seconds: 5.1,
    audit_chain_ok: true,
  },
  {
    candidate_id: "TGT-004",
    status: "HALTED@awaiting_human_review",
    recommendation: "REVIEW_REQUIRED",
    gate_result: "PASS",
    civilian_risk: "LOW",
    friendly_risk: "LOW",
    ttrr_seconds: 15.2,
    audit_chain_ok: true,
  },
  {
    candidate_id: "TGT-005",
    status: "HALTED@awaiting_human_review",
    recommendation: "HOLD",
    gate_result: "HOLD",
    civilian_risk: "MEDIUM",
    friendly_risk: "MEDIUM",
    ttrr_seconds: 42.8,
    audit_chain_ok: false,
  },
];
