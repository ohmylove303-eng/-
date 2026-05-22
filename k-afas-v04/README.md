# K-AFAS v0.4

**한국형 지능형 포병 의사결정 지원체계**
(Korean Artillery AI Decision-support System — *Decision Support Only*)

> AI 오케스트라 + 환각ZERO 검증 + 안전설계 하네스를 적용한 공개형 참고 구현체.

## 절대 금지 (REJECT 항목)
- 자동사격(Autonomous Fire) / 사격제원(Firing Data) / 탄도계산(Ballistic Calculation)
- 무기 직접연동(Direct Weapon Control) / 포탑제어(Turret Control)
- 발사명령(Fire Command) / 특정 표적 공격절차 / 재밍 회피 구현

## 무엇을 하는가
1. 드론·관측·센서·위성 데이터를 표준화해 **표적후보(Target Candidate)** 로 변환
2. 위치 단서와 **좌표품질**, **정보신선도** 등급화
3. 10개 안전게이트 + 6개 불변조건 하네스 평가
4. **인간 검토자**(commander/analyst/safety_officer/auditor)에게 검토 패키지 전달
5. 모든 판단을 JSONL 감사로그로 적재, 사후평가(AAR)까지 추적

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
print(result.status())   # PASS | HOLD | REJECT | HALTED@...
```

## 디렉토리
```
kafas/
  schemas.py          # 7개 데이터 객체 (TypedDict)
  harness.py          # 6개 불변조건 검증
  pipeline.py         # 8계층 통합 + 인간승인 흐름
  layers/             # L1~L8 계층별 구현
ai-orchestra/         # AI 오케스트라 운영 매뉴얼
tests/                # 29개 테스트 (전부 통과)
docs/                 # ARCHITECTURE / SAFETY_GATES / EVALUATION
```

## 문서
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 8계층 구조
- [docs/SAFETY_GATES.md](docs/SAFETY_GATES.md) — 10게이트 + 6불변조건
- [docs/EVALUATION.md](docs/EVALUATION.md) — 평가지표
- [ai-orchestra/QUICK_START.md](ai-orchestra/QUICK_START.md) — 오케스트라 30초 가이드

## 면책
본 저장소는 공개 출처 기반 **참고 구현체**다. 실제 군 운용에는
DAPA·합참·기품원 공식 ROC, 보안검토, 야전시험이 별도로 필요하다.
