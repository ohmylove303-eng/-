# 안전게이트 + 하네스 불변조건 (v0.4.1)

## 10개 안전게이트 (Safety Gates)

| # | 게이트 | 평가 위치 | PASS | HOLD | REJECT |
|---|--------|-----------|------|------|--------|
| 1 | Evidence | L6 | MULTI & SUFFICIENT | SINGLE / INSUFFICIENT | CONFLICTING |
| 2 | Freshness | L6 | GREEN | YELLOW / RED | BLACK |
| 3 | CoordinateQuality | L6 | HIGH | MEDIUM | LOW |
| 4 | CivilianRisk | L6 | LOW | MEDIUM / UNKNOWN | HIGH |
| 5 | FriendlyRisk | L6 | LOW | MEDIUM / UNKNOWN | HIGH |
| 6 | ROE | L6 | CLEAR | REVIEW_REQUIRED | HOLD |
| 7 | Deconfliction | L6 | CLEAR | UNKNOWN | CONFLICT |
| 8 | HumanApproval | L8 흐름 | review.decision != REJECT | review 미존재 | review.decision = REJECT |
| 9 | **Audit** (신규) | L9 | case 완전 + 체인 무결 | log 미연결 | 누락 / 변조 |
| 10 | WeaponSeparation | L6 + 하네스 | 정책 Literal 일치 | — | 정책 변조 |

> 집계 규칙: 하나라도 REJECT 면 전체 REJECT,
> REJECT 가 없고 HOLD 가 하나라도 있으면 전체 HOLD,
> 모두 PASS 면 전체 PASS.

## 6개 불변조건 (Invariants)

| # | 코드 | 검사 대상 | 위반 시 |
|---|------|-----------|---------|
| I1 | invariant_goal_lock | decision.weapon/firing/ballistic 필드 | REJECT |
| I2 | invariant_option_set | 검토자 선택지 집합 | 누락 시 REJECT |
| I3 | invariant_semantic_collision | 텍스트 27종 금지표현 (우회차단) | REJECT |
| I4 | invariant_evidence_ledger | candidate.source_type/observed_at_kst, evidence.packet_id | REJECT/HOLD |
| I5 | invariant_human_approval | review log + 결정 | HOLD/REJECT |
| I6 | invariant_weapon_separation | coord 정책 + decision 잠금 필드 | REJECT |

## 금지 표현 (FORBIDDEN_PHRASES) 27종 — 우회 차단 정규화

원문 텍스트를 **공백·구두점·대소문자 제거 후** 비교하므로
"fire command", "fire,command", "FIRE  COMMAND" 등 모두 동일 차단.

```
자동사격, 사격제원, 탄도계산, 사격지시, 발사지시, 무기직접연동, 포탑제어,
발사명령, 타격명령, 특정표적공격절차, 재밍회피구현, 사격승인,
automatedcoordinategeneration, killchain, strikeplanning, strikeauthorization,
autonomousfire, firingdata, firingsolution, ballisticcalculation,
directweaponcontrol, turretcontrol, firecommand, fireorder,
engageorder, weaponrelease, ...
```

## 게이트와 불변조건 관계
```
[게이트 = 데이터/감사 품질 검사]    →  L6 risk_gate, L9 audit_gate
[불변조건 = 시스템 안전성 잠금]      →  harness.evaluate_case()

게이트는 "이 후보를 인간에게 보여도 되는가 / 로그가 무결한가"
불변조건은 "이 시스템이 자동사격 도구로 변질되었는가"
```

## v0.4.1 신규 안전 보강

### A) 감사로그 SHA-256 해시 체인
- `kafas/layers/audit.py`
- `append_audit_log()` 가 prev_hash + payload → 새 hash 산출
- `verify_audit_chain()` 으로 사후 변조 탐지
- 회귀: `tests/test_audit_chain.py` 변조 시도 차단 확인

### B) Audit Gate (L9)
- `kafas/layers/audit_gate.py`
- case 키 5개(`candidate/evidence/coord/risk/decision`) 완전성 검사
- 로그 체인 무결성 검사
- 결과: PASS / HOLD / REJECT

### C) 검토자 토큰 인증
- 환경변수 `KAFAS_TOKEN_COMMANDER` 등으로 토큰 주입
- `hmac.compare_digest`로 비교 (timing-safe)
- 토큰 미설정 환경에서는 dev 모드 (검증 생략)

### D) 무기제어망 분리 선언
- `coord.coordinate_use_policy` 단일 Literal 강제
- `decision.weapon_control_link / firing_data / ballistic_calculation`
  Literal["NOT_ALLOWED"] 잠금
- 변조 시 I6 + WeaponSeparation 게이트가 동시 REJECT

### E) 사용자 정의 시각화 레이어 차단
- `kafas/viz/custom.py` 의 `add_custom()` 이
  금지 키워드(fire_control / weapon_release / 사격제원 …) 포함 시 ValueError
- `display_only=True` 강제

## 회귀 테스트 (50건 전체)
- test_schemas / test_harness / test_layers / test_pipeline
- test_safety_gates / test_audit_chain / test_audit_gate
- test_validators / test_metrics / test_viz / test_forbidden_strict
