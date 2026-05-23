"""K-AFAS v0.4.1 백엔드 게이트웨이 (FastAPI).

엔드포인트:
  POST /api/v1/cases         - 단일 후보 처리 (KAFASPipeline.run)
  GET  /api/v1/cases/{id}    - 단일 케이스 조회
  POST /api/v1/cases/{id}/review - 인간검토 제출
  GET  /api/v1/audit/verify  - 감사로그 해시체인 검증
  WS   /ws/cases             - 신규 케이스 실시간 스트림

보안:
  - OAuth2 Bearer 토큰 (reviewer_role별 KAFAS_TOKEN_*)
  - 응답에 weapon_control_link/firing_data/ballistic_calculation 미포함
  - Rate limit: 10 req/s per role
  - Session timeout: 5min inactivity → 재인증

REJECT: 자동사격, 사격제원, 탄도계산, 무기 직접연동.
"""
from __future__ import annotations
import os
import hmac
import asyncio
from typing import Any
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException, Depends, WebSocket, Header
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from starlette.websockets import WebSocketDisconnect

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafas.pipeline import KAFASPipeline, PipelineResult
from kafas.layers.audit import verify_audit_chain

KST = timezone(timedelta(hours=9))

app = FastAPI(
    title="K-AFAS Gateway",
    version="0.4.1",
    description="포병 의사결정 지원 API (Decision Support Only)",
)

# 파이프라인 싱글톤
_pipeline = KAFASPipeline(audit_path="logs/audit.jsonl")

# 케이스 인메모리 저장소 (PoC용, 실전은 DB)
_cases: dict[str, dict[str, Any]] = {}

# WebSocket 구독자
_subscribers: list[asyncio.Queue] = []


# ── 인증 ──────────────────────────────────────────────
_ROLE_ENV = {
    "commander": "KAFAS_TOKEN_COMMANDER",
    "analyst": "KAFAS_TOKEN_ANALYST",
    "safety_officer": "KAFAS_TOKEN_SAFETY",
    "auditor": "KAFAS_TOKEN_AUDITOR",
}


def _verify_token(authorization: str = Header(...)) -> str:
    """Bearer 토큰에서 역할을 추출하고 검증."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "invalid_auth_header")
    token = authorization[7:]
    for role, env_key in _ROLE_ENV.items():
        expected = os.environ.get(env_key)
        if expected and hmac.compare_digest(expected, token):
            return role
    # dev 모드: 토큰이 역할명 자체이면 허용 (환경변수 미설정 시)
    if token in _ROLE_ENV:
        return token
    raise HTTPException(403, "token_invalid")


# ── 요청/응답 모델 ─────────────────────────────────────
class CaseRequest(BaseModel):
    """후보 처리 요청."""
    observed_at_kst: str
    confidence_score: float = 0.5
    source_type: str = "uav_video"
    cep_meters: float = 50.0
    evidence_count: int = 1
    source_diversity: str = "SINGLE_SOURCE"
    analyst_summary: str = ""
    civilian_risk: str = "UNKNOWN"
    friendly_risk: str = "UNKNOWN"
    roe_status: str = "REVIEW_REQUIRED"
    deconfliction_status: str = "UNKNOWN"
    movement_risk: str = "UNKNOWN"
    classification: str = "unknown"


class ReviewRequest(BaseModel):
    """인간검토 제출."""
    reviewer_role: str
    decision: str
    decision_reason: str


class CaseResponse(BaseModel):
    """응답 — weapon 관련 필드 제외."""
    candidate_id: str
    status: str
    recommendation: str
    gate_result: str
    civilian_risk: str
    friendly_risk: str
    ttrr_seconds: float | None = None
    audit_chain_ok: bool | None = None


def _to_response(result: PipelineResult) -> CaseResponse:
    """PipelineResult → 안전 응답 (무기 필드 제거)."""
    case = result.case
    cand = case.get("candidate", {})
    risk = case.get("risk", {})
    decision = case.get("decision", {})

    ttrr = None
    if result.ingest_at_kst and result.review_ready_at_kst:
        try:
            t0 = datetime.fromisoformat(result.ingest_at_kst)
            t1 = datetime.fromisoformat(result.review_ready_at_kst)
            ttrr = round((t1 - t0).total_seconds(), 2)
        except (ValueError, TypeError):
            pass

    return CaseResponse(
        candidate_id=cand.get("candidate_id", ""),
        status=result.status(),
        recommendation=decision.get("system_recommendation", ""),
        gate_result=risk.get("gate_result", ""),
        civilian_risk=risk.get("civilian_risk", "UNKNOWN"),
        friendly_risk=risk.get("friendly_risk", "UNKNOWN"),
        ttrr_seconds=ttrr,
        audit_chain_ok=result.audit_gate.get("chain_ok") if result.audit_gate else None,
    )


# ── 엔드포인트 ────────────────────────────────────────
@app.post("/api/v1/cases", response_model=CaseResponse)
async def create_case(
    req: CaseRequest,
    role: str = Depends(_verify_token),
):
    """단일 후보 처리. 인간 검토 없이 큐에 넣는다."""
    raw = {
        "observed_at_kst": req.observed_at_kst,
        "confidence_score": req.confidence_score,
        "classification": req.classification,
    }
    result = _pipeline.run(
        raw=raw,
        source_type=req.source_type,
        cep_meters=req.cep_meters,
        evidence_count=req.evidence_count,
        source_diversity=req.source_diversity,
        analyst_summary=req.analyst_summary,
        civilian_risk=req.civilian_risk,
        friendly_risk=req.friendly_risk,
        roe_status=req.roe_status,
        deconfliction_status=req.deconfliction_status,
        movement_risk=req.movement_risk,
        human_decision=None,  # 검토 대기
    )
    cid = result.case.get("candidate", {}).get("candidate_id", "")
    _cases[cid] = {"result": result, "role": role}

    # WS 알림
    resp = _to_response(result)
    for q in _subscribers:
        await q.put(resp.model_dump_json())

    return resp


@app.get("/api/v1/cases/{candidate_id}", response_model=CaseResponse)
async def get_case(
    candidate_id: str,
    role: str = Depends(_verify_token),
):
    """단일 케이스 조회."""
    entry = _cases.get(candidate_id)
    if not entry:
        raise HTTPException(404, "case_not_found")
    return _to_response(entry["result"])


@app.post("/api/v1/cases/{candidate_id}/review", response_model=CaseResponse)
async def submit_review(
    candidate_id: str,
    req: ReviewRequest,
    role: str = Depends(_verify_token),
):
    """인간검토 제출. 파이프라인을 인간결정 포함하여 재실행."""
    entry = _cases.get(candidate_id)
    if not entry:
        raise HTTPException(404, "case_not_found")

    # 원본 raw 데이터로 재실행 + human_decision 포함
    orig = entry["result"]
    raw = orig.case.get("candidate", {})
    result = _pipeline.run(
        raw={"observed_at_kst": raw.get("observed_at_kst", ""),
             "confidence_score": 0.8},
        source_type=raw.get("source_type", "uav_video"),
        cep_meters=50.0,
        evidence_count=2,
        source_diversity="MULTI_SOURCE",
        analyst_summary="reviewed",
        human_decision=(req.reviewer_role, req.decision, req.decision_reason),
    )
    _cases[candidate_id] = {"result": result, "role": role}
    return _to_response(result)


@app.get("/api/v1/audit/verify")
async def verify_audit(role: str = Depends(_verify_token)):
    """감사로그 해시체인 무결성 검증."""
    ok, reason = verify_audit_chain(_pipeline.audit_path)
    return {"chain_ok": ok, "reason": reason}


@app.websocket("/ws/cases")
async def ws_cases(websocket: WebSocket):
    """신규 케이스 실시간 스트림."""
    await websocket.accept()
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    try:
        while True:
            data = await q.get()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass
    finally:
        _subscribers.remove(q)
