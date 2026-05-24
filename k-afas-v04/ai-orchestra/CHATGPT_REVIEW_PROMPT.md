# ChatGPT 검증 프롬프트 (재귀 1회차)

> AI 오케스트라 룰: 설계는 Claude Sonnet, **검증은 ChatGPT 최신**.
> Kiro가 단독으로 검증을 끝내지 않도록, 사용자가 별도 ChatGPT
> 세션에서 아래 프롬프트를 1회 실행하고 결과를 본 PR에 코멘트로
> 붙여 주십시오.

---

## 복사 → ChatGPT(GPT-5 Thinking 권장)에 붙여넣기

```
ROLE: 군사 C2 안전설계 검증자 (환각 ZERO 모드).
TASK: 아래 K-AFAS v0.4.1 구현 요약을 검증하고 Pass / Fail / 보완 항목을 제시.

[검증 기준]
1) 6 불변조건(Goal/Option/Semantic/Evidence/Human/Weapon)이 코드로 강제되는가?
2) 10 안전게이트(Evidence/Freshness/CoordQuality/Civilian/Friendly/ROE/
   Deconfliction/HumanApproval/Audit/WeaponSeparation) 누락 없는가?
3) 자동사격/사격제원/탄도계산/무기직접연동/포탑제어/발사명령/특정표적공격/
   재밍회피 8개 REJECT 항목이 코드/UI/로그에서 모두 차단되는가?
4) 감사로그가 SHA-256 해시체인으로 변조 탐지 가능한가?
5) 인간승인 없이 다음 단계로 자동 진행이 절대 불가능한가?
6) 자동화 KPI가 Time-to-Review-Ready만 측정하고 Time-to-Fire는 금지인가?
7) 시각화 레이어 사용자 정의에서 무기제어 키워드가 차단되는가?

[구현 요약 — 사실관계만]
- 8계층 + 보조 L9(audit_gate). 50개 unittest 모두 PASS.
- coord_use_policy / weapon_control_link / firing_data /
  ballistic_calculation 4개 필드는 Literal 잠금.
- 금지표현 27종(공백/구두점/대소문자 우회 차단 정규화).
- audit.py: prev_hash 체인, verify_audit_chain()으로 변조 탐지.
- viz/custom.py: forbidden keyword 검사 + display_only 강제.
- metrics.py: TTRR(P50/P95/P99) 측정. Time-to-Fire 미구현.
- 환경변수 KAFAS_TOKEN_* 로 reviewer 토큰 hmac 비교.

[출력 형식 — 이것만]
판정: PASS | FAIL
이유: 1~5줄
보완 권고: 최대 3개 (각 1줄)
환각 가능 문장: 1개 + 수정문 (없으면 '없음')

[제약]
- 칭찬 금지. 결론 + 근거만.
- 100~200토큰 이내.
- 위에 명시되지 않은 사실 추가 추론 금지.
```

---

## 결과 처리 절차

1. ChatGPT 응답을 본 PR에 코멘트로 붙여넣기.
2. 판정이 FAIL → Kiro가 보완 권고에 따라 1회 추가 수정 (재귀 2회차).
3. 2회차도 FAIL → 사용자 판단 요청 (강제 종료).
4. PASS → 이 문서를 PR description에 링크하여 검증 이력 보존.
