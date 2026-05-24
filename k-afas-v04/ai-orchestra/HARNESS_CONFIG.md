# 하네스(Harness) 기법 설정

## 하네스란?
AI 출력을 **구조화된 형식으로 강제**하여:
- 환각(hallucination) 방지
- 토큰 낭비 제거
- 일관된 품질 보장

---

## 1. 입력 하네스 (AI에게 보낼 때)

### 규칙: 모든 요청은 이 구조를 따른다
```
[ROLE] 1줄
[CONTEXT] 최대 200토큰 (L2 압축)
[TASK] 1~2문장
[FORMAT] 출력 형식 명시
[CONSTRAINTS] 금지사항 리스트
```

### 나쁜 예 (하네스 없음):
```
"우리 프로젝트에서 이런저런 기능을 추가하고 싶은데,
현재 코드가 이렇게 되어있고, 여기서 저기를 고치면...
어떻게 하면 좋을까? 자세히 알려줘."
```
→ 결과: 장황한 설명 + 부정확한 코드 + 3000토큰 낭비

### 좋은 예 (하네스 적용):
```
[ROLE] Python 개발자. 코드만 출력.
[CONTEXT] Flask 앱. /api/us/smart-money 엔드포인트 존재.
[TASK] 캐시 TTL 추가 (5분)
[FORMAT] 수정할 함수 코드블록 1개만
[CONSTRAINTS] 설명 금지. import 변경 시 명시.
```
→ 결과: 정확한 코드 20줄 + 800토큰

---

## 2. 출력 하네스 (AI 응답 형식 강제)

### 설계 AI 출력 하네스:
```json
{
  "files": [{"path": "str", "purpose": "str"}],
  "interfaces": [{"name": "str", "params": "str", "returns": "str"}],
  "data_flow": "str",
  "dependencies": ["str"],
  "risks": ["str"]
}
```

### 구현 AI 출력 하네스:
```
---FILE: {path}---
{code}
---END---
```

### 검증 AI 출력 하네스:
```json
{
  "pass": true/false,
  "issues": [{"line": N, "severity": "high/med/low", "fix": "str"}],
  "token_cost": N
}
```

---

## 3. 에러 방지 하네스

### 환각 방지:
```
[CONSTRAINTS]
- 확실하지 않으면 "UNKNOWN"이라고 출력하라
- 추측하지 마라. 주어진 정보만 사용하라
- 존재하지 않는 라이브러리를 만들어내지 마라
```

### 반복 방지:
```
[CONSTRAINTS]
- 이전에 말한 내용 반복 금지
- "앞서 말씀드렸듯이" 금지
- 새 정보만 출력
```

### 토큰 제한:
```
[CONSTRAINTS]
- 최대 N토큰 이내 응답
- 불필요한 서론/결론 없이 본문만
- 리스트는 최대 5개 항목
```

---

## 4. 프로젝트별 하네스 프리셋

### 이 프로젝트(US Stock Dashboard) 전용:

```markdown
## 기본 하네스 (모든 요청에 붙이기)
- 언어: Python 3.9+
- 프레임워크: Flask
- 데이터: JSON 파일 기반 캐시 (data/ 폴더)
- AI: google.generativeai (Gemini), openai (fallback)
- 패턴: 각 스크립트는 독립 실행 가능 (scripts/)
- 스타일: 한국어 주석, 영어 코드, snake_case
- 에러: 항상 try/except, print(f"❌ ...")
- 로그: print(f"✅ ...") / print(f"⚠️ ...")
```

---

## 5. 실전 적용 치트시트

| 작업 | 하네스 키워드 |
|------|--------------|
| 새 기능 설계 | "시그니처만. 구현 금지. 500토큰 이내." |
| 코드 작성 | "코드만. 설명 금지. 완성된 파일 1개." |
| 버그 수정 | "JSON으로: {line, fix, reason}" |
| 코드 리뷰 | "이슈만 리스트. 칭찬 금지. severity 포함." |
| 요약 | "300토큰 이내. 불릿 5개 이하." |
| 비교 | "표 형식. 5개 기준 이하. 결론 1줄." |
