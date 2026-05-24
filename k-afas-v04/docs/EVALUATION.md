# 평가 지표 (Evaluation Metrics)

## 허용 지표 — K-AFAS는 이것만 측정한다

| 지표 | 정의 | 출처 단계 |
|------|------|-----------|
| 후보탐지 정확도 (CDA) | 실제 후보를 후보로 잡는 비율 | L4 detection |
| 오탐률 (FPR) | 후보 아닌 것을 후보로 분류하는 비율 | L4 detection |
| 미탐률 (FNR) | 후보를 놓치는 비율 | L4 + L8 AAR |
| 좌표품질 정확도 | 등급과 실제 일치율 | L5 coord_support |
| 정보신선도 정확도 | 신선도 등급의 실제 유효성 | L3 cop |
| 보류·반려 적중률 | 위험 후보를 HOLD/REJECT 한 비율 | L6 risk_gate |
| 민간·아군위험 차단률 | 위험 후보를 자동 보류·반려한 비율 | L6 risk_gate |
| 인간검토 대기시간 | 후보 등록 → 인간검토대기 시간 | L7→L8 |
| 감사로그 완전성 | 입력·판단·결정·사유 모두 기록 비율 | L8 audit |
| 사후평가 반영률 | AAR 결과가 규칙·모델 개선으로 이어진 비율 | L8 AAR |

## 절대 측정 금지 — REJECT 항목

| 지표 | REJECT 사유 |
|------|-------------|
| Time to Fire (사격까지 소요시간) | 자동사격 KPI — 시스템 목적과 충돌 |
| 자동교전 성공률 | 인간승인 우회 KPI |
| 표적 무력화율 | 무기효과 KPI — 의사결정 지원 범위 밖 |

## 운용 KPI 권고치 (참고용)

| 지표 | 권고 임계 | 비고 |
|------|-----------|------|
| FPR | < 5% | 영상분석 단계에서 |
| 보류·반려 적중률 | > 95% | HIGH risk 후보 기준 |
| 감사로그 완전성 | 100% | 100% 미만은 운용중단 |
| 인간검토 대기시간 | < 60초 P95 | UI 응답성 |
| AAR 반영률 | > 50% | 학습 루프 건강성 |

## 측정 설계
1. 모든 지표는 **훈련·모의환경**에서 먼저 검증.
2. 비살상 데이터 = 훈련용 모의 데이터(Simulated Training Data) 또는
   과거 비식별 데이터(De-identified Historical Data).
3. 모델 자동 재학습 금지 (`model_update_allowed: false`).
4. AAR 통과 후에만 모델/규칙 개선 검토 (`review_required_before_training: true`).

## 보고 형식 (예시)
```json
{
  "report_kst": "2026-05-22T18:00:00+09:00",
  "window_hours": 24,
  "candidates_total": 412,
  "passed_to_review": 138,
  "held": 211,
  "rejected": 63,
  "audit_completeness": 1.00,
  "fpr": 0.038,
  "review_latency_p95_sec": 41
}
```
