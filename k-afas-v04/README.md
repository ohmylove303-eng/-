# K-AFAS v0.4.1

**한국형 지능형 포병 의사결정 지원체계**
(Korean Artillery AI Decision-support System — *Decision Support Only*)

> AI 오케스트라 + 환각ZERO 검증 + 안전설계 하네스를 적용한 공개형 참고 구현체.
> 50개 unittest 전부 PASS.

## 절대 금지 (REJECT 항목)
- 자동사격(Autonomous Fire) / 사격제원(Firing Data) / 탄도계산(Ballistic Calculation)
- 무기 직접연동 / 포탑제어 / 발사명령 / **사격지시**
- 특정 표적 공격절차 / 재밍 회피 구현

## 자동화 범위
**첩보(Raw) → 정보(Information) → 검토패키지 도달까지(TTRR)**.
사격지시 자체는 K-AFAS 외부, 별도 인가받은 무기체계에서 인간이 수행.
[`docs/INTENT_TRANSLATION.md`](docs/INTENT_TRANSLATION.md) 참조.

## 무엇을 하는가
1. 드론·관측·센서·위성 데이터 표준화 → **표적후보(Target Candidate)**
2. 위치 단서·**좌표품질**·**정보신선도** 등급화
3. **10개 안전게이트** + **6개 하네스 불변조건** 평가
4. **인간 검토자**(commander/analyst/safety_officer/auditor) 콘솔 4-패널
5. JSONL 감사로그 + **SHA-256 해시체인** + L9 Audit Gate

## 빠른 시작
```bash
python -m unittest discover -s tests
```

```python
from kafas.pipeline import KAFASPipeline

p = KAFASPipeline(audit_path="logs/audit.jsonl")
result = p.run(
    raw={"observed_at_kst": "2026-05-22T10:00:00+09:00",
         "confidence_score": 0.85},
    source_type="uav_video",
    cep_meters=20.0,
    evidence_count=3,
    source_diversity="MULTI_SOURCE",
    analyst_summary="2 trucks (provisional)",
    civilian_risk="LOW", friendly_risk="LOW",
    roe_status="CLEAR", deconfliction_status="CLEAR",
    human_decision=("commander", "APPROVE_FOR_NEXT_REVIEW", "ok"),
)
print(result.status())            # PASS | HOLD | REJECT | HALTED@...
print(result.audit_gate)          # L9 결과: completeness / chain_ok
```

## 디렉토리
```
kafas/
  schemas.py            # 7개 데이터 객체 (TypedDict, Literal 잠금)
  harness.py            # 6개 불변조건 + 27 금지표현(우회차단 정규화)
  validators.py         # 진입점 런타임 dict 검증
  metrics.py            # TTRR (Time-to-Review-Ready) KPI
  pipeline.py           # 8계층 통합 + run / run_batch
  layers/               # L1~L8 + L9(audit_gate)
  viz/                  # 시각화 레이어 시스템
    layers.py           # 표준 15 레이어
    custom.py           # 사용자 정의 + 금지키워드 차단
    console.py          # 4-패널 검토 콘솔 명세
ai-orchestra/           # AI 오케스트라 운영 매뉴얼 + ChatGPT 검증 프롬프트
tests/                  # 50개 (전부 PASS)
docs/
  ARCHITECTURE.md       # 8계층 구조
  SAFETY_GATES.md       # 10게이트 + 6불변조건 + 금지표현
  EVALUATION.md         # 평가지표 (Time-to-Fire 측정 금지)
  ECOSYSTEM.md          # 적용 가능한 실제 기술/제품/OSS 전체 나열
  INTENT_TRANSLATION.md # 사용자 표현 → 안전 표현 변환표
  VIZ_LAYERS.md         # 레이어 + 콘솔 명세
```

## v0.4.1에서 추가된 안전 보강
| 분류 | 내용 |
|---|---|
| Audit | SHA-256 해시체인 + verify_audit_chain |
| Audit Gate | L9 별도 게이트 (감사 완전성 + 체인 무결성) |
| Auth | reviewer_role 토큰 hmac 비교 (env: KAFAS_TOKEN_*) |
| Validation | TypedDict 한계 보완 (validators.py) |
| Forbidden | 띄어쓰기/구두점/대소문자 우회 차단 (정규화 비교) |
| Ingest | observed_at_kst 부재 시 즉시 raise (fallback 제거) |
| Batch | run_batch + MetricsAggregator |
| Viz | 표준 15 레이어 + 사용자 정의(금지키워드 차단) + 4-패널 콘솔 |

## 면책
본 저장소는 공개 출처 기반 **참고 구현체**다. 실제 군 운용에는
DAPA·합참·기품원 공식 ROC, 보안검토, 야전시험이 별도로 필요하다.
