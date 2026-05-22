# 안전게이트 + 하네스 불변조건

## 10개 안전게이트 (Safety Gates)

| # | 게이트 | PASS | HOLD | REJECT |
|---|--------|------|------|--------|
| 1 | Evidence | MULTI_SOURCE & SUFFICIENT | SINGLE_SOURCE / INSUFFICIENT | CONFLICTING |
| 2 | Freshness | GREEN | YELLOW / RED | BLACK |
| 3 | CoordinateQuality | HIGH | MEDIUM | LOW |
| 4 | CivilianRisk | LOW | MEDIUM / UNKNOWN | HIGH |
| 5 | FriendlyRisk | LOW | MEDIUM / UNKNOWN | HIGH |
| 6 | ROE | CLEAR | REVIEW_REQUIRED | HOLD |
| 7 | Deconfliction | CLEAR | UNKNOWN | CONFLICT |
| 8 | HumanApproval | review log 존재 | review 미존재 | review.decision=REJECT |
| 9 | Audit | 모든 단계 로그 | 일부 누락 | 핵심 누락/변조 |
| 10 | WeaponSeparation | 정책 Literal 일치 | — | 정책 변조 시도 |

> 집계 규칙: 하나라도 REJECT 면 전체 REJECT,
> REJECT 가 없고 HOLD 가 하나라도 있으면 전체 HOLD,
> 모두 PASS 면 전체 PASS.

## 6개 불변조건 (Invariants)

| # | 코드 | 검사 대상 | 위반 시 |
|---|------|-----------|---------|
| I1 | invariant_goal_lock | decision.weapon/firing/ballistic 필드 | REJECT |
| I2 | invariant_option_set | 검토자 선택지 집합 | 누락 시 REJECT |
| I3 | invariant_semantic_collision | 텍스트 18종 금지표현 | REJECT |
| I4 | invariant_evidence_ledger | candidate.source_type/observed_at_kst, evidence.packet_id | REJECT/HOLD |
| I5 | invariant_human_approval | review log 존재 + 결정 | HOLD/REJECT |
| I6 | invariant_weapon_separation | coord 정책 + decision 잠금 필드 | REJECT |

## 금지 표현(FORBIDDEN_PHRASES) 18종
```
자동사격, 사격제원, 탄도계산, 무기 직접연동,
포탑제어, 발사명령, 특정 표적 공격절차, 재밍 회피 구현,
automated coordinate generation, kill chain, strike planning,
autonomous fire, firing data, ballistic calculation,
direct weapon control, turret control, fire command, ...
```
이유, 분석관 요약, 결정 사유 등 어떤 텍스트에서도 발견되면 즉시 REJECT.

## 게이트와 불변조건 관계
```
[게이트 = 데이터 품질 검사]   →  L6 risk_gate.evaluate_risk_gates()
[불변조건 = 시스템 안전성 잠금] →  harness.evaluate_case()

게이트는 "이 후보를 인간에게 보여도 되는가"
불변조건은 "이 시스템이 자동사격 도구로 변질되었는가"
```

## 회귀 테스트
- `tests/test_safety_gates.py` 4건
- `tests/test_harness.py` 9건
- 모두 통과 시에만 코드 머지 허용 권장.
