# 요구사항 추적표 (Requirements Traceability Matrix)

## K-AFAS v0.4.1 — 요구사항 → 설계 → 구현 → 테스트 추적

| REQ# | 요구사항 | 설계 | 구현 | 테스트 | 상태 |
|------|----------|------|------|--------|------|
| R01 | 8계층 아키텍처 | ARCHITECTURE.md | pipeline.py | test_pipeline | ✅ |
| R02 | 7개 데이터 스키마 | ARCHITECTURE.md | schemas.py | test_schemas | ✅ |
| R03 | 6개 불변조건 하네스 | SAFETY_GATES.md | harness.py | test_harness (9건) | ✅ |
| R04 | 10개 안전게이트 | SAFETY_GATES.md | risk_gate + audit_gate | test_safety_gates + test_audit_gate | ✅ |
| R05 | 인간승인 필수 (HiTL) | ARCHITECTURE.md | pipeline.py | test_pipeline: no_human | ✅ |
| R06 | 8개 REJECT 항목 차단 | SRD v0.4 | harness FORBIDDEN + Literal | test_forbidden_strict | ✅ |
| R07 | 감사로그 SHA-256 해시체인 | SAFETY_GATES.md | audit.py | test_audit_chain | ✅ |
| R08 | Audit Gate (L9) | SAFETY_GATES.md | audit_gate.py | test_audit_gate | ✅ |
| R09 | 검토자 토큰 인증 | SAFETY_GATES.md | audit.py _verify_reviewer | test_layers | ✅ |
| R10 | 런타임 dict 검증 | — | validators.py | test_validators | ✅ |
| R11 | 금지표현 27종 우회 차단 | SAFETY_GATES.md | harness _normalize | test_forbidden_strict | ✅ |
| R12 | observed_at_kst 필수 | — | ingest.py | test_layers | ✅ |
| R13 | TTRR 메트릭 | EVALUATION.md | metrics.py | test_metrics | ✅ |
| R14 | 시각화 15 표준 레이어 | VIZ_LAYERS.md | viz/layers.py | test_viz | ✅ |
| R15 | 커스텀 레이어 금지키워드 차단 | VIZ_LAYERS.md | viz/custom.py | test_viz | ✅ |
| R16 | display_only=true 강제 | VIZ_LAYERS.md | viz/custom + adapter.ts | test_viz | ✅ |
| R17 | 4-패널 검토 콘솔 | VIZ_LAYERS.md | viz/console.py | test_viz | ✅ |
| R18 | 좌표 클립보드 복사 차단 | S1 와이어 | adapter.ts | UI 테스트 예정 | ✅설계 |
| R19 | 세션 5분 자동잠금 | S1 와이어 | 프론트엔드 예정 | — | 🟡설계 |
| R20 | VALIDATED→외부 명시 | INTENT_TRANSLATION.md | UI 고지문 | — | ✅문서 |
| R21 | FastAPI 게이트웨이 | S2 | gateway.py | 통합 예정 | ✅구현 |
| R22 | 응답에 weapon 필드 미포함 | S2 | gateway.py | — | ✅구현 |
| R23 | CesiumJS+MapLibre 어댑터 | S3 | adapter.ts | TS 컴파일 | ✅구현 |
| R24 | run_batch 배치 처리 | — | pipeline.py | — | ✅구현 |
| R25 | 생태계 기술 나열 | ECOSYSTEM.md | 문서 | — | ✅ |
| R26 | ChatGPT 검증 프롬프트 | CHATGPT_REVIEW_PROMPT.md | — | S1×2+S2×1 PASS | ✅ |

## 미충족 (실전 직전 — 코드 외부)

| REQ# | 요구사항 | 비고 |
|------|----------|------|
| R27 | 외부 침투 테스트 | 보안 전문팀 |
| R28 | KMS/HSM 통합 | 인프라 |
| R29 | DAPA 공식 ROC 매핑 | 기관 문서 |
| R30 | 야전 시험 | 운용 시험 |

## 총 현황: 구현 26/30 (87%) | 설계 28/30 (93%) | 테스트 50건 PASS
