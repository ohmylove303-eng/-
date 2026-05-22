# K-AFAS v0.4 아키텍처

## 8계층 구조 (Human-in-the-loop Decision Flow)

```
[L1] 자료수집     ingest.py         UAV/관측/센서/위성/기상·지형
   ↓
[L2] 증거정규화   normalize.py      KST 시간 / WGS84 / 신뢰도 밴드
   ↓
[L3] 공통작전상황도 cop.py          신선도(GREEN/YELLOW/RED/BLACK)
   ↓
[L4] AI 후보탐지  detection.py      → "candidate" 만 생성 (확정 금지)
   ↓
[L5] 좌표화 지원  coord_support.py  품질(HIGH/MEDIUM/LOW) + 정책 잠금
   ↓
[L6] 위험게이트   risk_gate.py      10개 게이트 통합 평가
   ↓
[L7] 의사결정 지원 decision.py      REVIEW/RECHECK/HOLD/REJECT
   ↓
[L8] 인간승인·감사 audit.py         HumanReviewLog + JSONL 감사로그
```

## 핵심 설계 원칙

### 1) 좌표 사용 정책 단일 Literal 강제
```python
"coordinate_use_policy":
    "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY"
```
타입 레벨에서 다른 값을 지정할 수 없으므로 코드 변경 자체가 차단된다.

### 2) 의사결정 NOT_ALLOWED 잠금
`DecisionSupport` 객체의 `weapon_control_link`,
`firing_data`, `ballistic_calculation` 필드는
`Literal["NOT_ALLOWED"]` 로 고정.

### 3) 인간승인 없으면 진행 차단
`KAFASPipeline.run()` 호출 시 `human_decision=None` 이면
`HALTED@awaiting_human_review` 로 종결되며 감사로그 적재.

### 4) 위험게이트 REJECT 우선
민간위험·아군위험·신선도·좌표품질 어느 하나라도 REJECT 면
인간검토 단계로 가지 않고 즉시 halt.

### 5) 감사재생(Audit Replay) 강제
모든 케이스가 JSONL 한 줄로 보존 →
`audit_replay_required: true` 가 AAR에 명시.

## 파이프라인 단일 진입점
```python
KAFASPipeline.run(...)        # 8계층 + 1차/2차 하네스 검증
KAFASPipeline.submit_aar(...) # 사후평가 별도 트리거
```

## 데이터 흐름 다이어그램
```
raw → ingest_record → normalize → cop_entry
                                      ↓
                              detect_candidate
                                      ↓
                            build_coord_support
                                      ↓
                          evaluate_risk_gates ──→ harness 1차
                                      ↓                ↓ (REJECT면 halt)
                              build_decision
                                      ↓
                            make_review_log ───→ harness 2차
                                      ↓                ↓
                              append_audit_log ←──────┘
                                      ↓
                              submit_aar (선택)
```
