# AI 오케스트라 - 즉시 시작 가이드

## 30초 요약

```
1. 새 기능 → DESIGN_AI_PROMPT.md로 설계 먼저
2. 설계 완료 → IMPLEMENT_AI_PROMPT.md로 구현
3. 컨텍스트 길어짐 → CONTEXT_COMPRESSOR.md로 압축
4. 30주제 도달 → SESSION_HANDOFF.md로 새 세션
5. 모든 요청 → HARNESS_CONFIG.md 형식 적용
```

---

## 어떤 AI를 쓸까? (즉시 결정 가이드)

```
질문: 무엇을 해야 하는가?

├─ "시스템 설계가 필요하다"
│   └─ Claude Sonnet 4 ($3/MTok)
│      프롬프트: DESIGN_AI_PROMPT.md 사용
│
├─ "복잡한 새 코드를 작성해야 한다" (>100줄)
│   └─ Claude Sonnet 4 ($3/MTok)
│      프롬프트: IMPLEMENT_AI_PROMPT.md 사용
│
├─ "간단한 수정/추가가 필요하다" (<50줄)
│   └─ Gemini 2.5 Flash ($0.50/MTok)
│      프롬프트: IMPLEMENT_AI_PROMPT.md (간소화)
│
├─ "대량 데이터 분석/요약이 필요하다"
│   └─ Gemini 2.5 Flash ($0.50/MTok) [1M 컨텍스트]
│      프롬프트: HARNESS_CONFIG.md 요약 하네스
│
├─ "문서/설명을 작성해야 한다"
│   └─ GPT-5 mini ($0.25/MTok)
│      프롬프트: 자유형 + 토큰 제한
│
└─ "빠른 프로토타입/실험"
    └─ Gemini 2.5 Flash ($0.50/MTok)
       프롬프트: 간단 지시 + "코드만 출력"
```

---

## 복사해서 바로 쓰는 프롬프트 3종

### 프롬프트 1: 빠른 기능 추가 (Gemini Flash용)
```
Python 개발자. 코드만 출력. 설명 금지.

기존 파일: scripts/update_all.py
패턴: scripts 리스트에 튜플 추가

작업: scripts 리스트에 ("new_script.py", "설명", 120) 추가
위치: "vcp_screener.py" 뒤에

수정된 부분만 출력. 전체 파일 아님.
```

### 프롬프트 2: 새 분석 스크립트 (Claude Sonnet용)
```
시니어 Python 개발자. 설명 없이 완전한 파일 1개 출력.

목적: {기능_설명}
입력: data/{입력파일}.json
출력: data/{출력파일}.json
패턴: scripts/insider_tracker.py와 동일 구조
의존성: yfinance, json, os, dotenv

필수 포함:
- main() 함수
- if __name__ == "__main__": main()
- try/except 전체 감싸기
- print(✅/❌) 상태 로그
- 타입 힌트
```

### 프롬프트 3: 세션 핸드오프 (아무 AI)
```
세션 종료. 핸드오프 문서 생성.

형식:
## 완료: [불릿 리스트]
## 미해결: [불릿 리스트]
## 결정사항: [번복 금지]
## 다음 작업: [1줄]
## 수정 파일: [경로 리스트]

500토큰 이내. 다음 AI가 이것만 보고 작업 가능해야 함.
```

---

## 월 비용 예상

| 사용량 | 설계(Claude) | 구현(Gemini) | 문서(GPT mini) | 총합 |
|--------|-------------|-------------|---------------|------|
| 가벼운 사용 (일 5건) | $0.03 | $0.013 | $0.003 | **$1.4/월** |
| 보통 사용 (일 15건) | $0.09 | $0.038 | $0.008 | **$4/월** |
| 헤비 사용 (일 30건) | $0.18 | $0.075 | $0.015 | **$8/월** |

---

## 참고 자료 (출처)

- AI 모델 비교: [intuitionlabs.ai](https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025)
- 토큰 효율 연구: [arxiv.org/html/2507.03254v1](https://arxiv.org/html/2507.03254v1) - 55-87% 토큰 절감
- 멀티에이전트 시스템: [arxiv.org/html/2510.26585v1](https://arxiv.org/html/2510.26585v1)
- 프롬프트 엔지니어링: [github.com/dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
- AI 오케스트레이션: [github.com/danielrosehill/AI-Orchestration-System-Prompts](https://github.com/danielrosehill/AI-Orchestration-System-Prompts)

Content was rephrased for compliance with licensing restrictions.
