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

├─ 95% → Kiro에서 직접 처리 (여기서 바로 작업)
│   ├─ 설계 + 구현 + 수정 + 리뷰 모두
│   └─ 하네스 적용으로 토큰 자동 최적화
│
├─ 4% → Kiro가 "초압축 프롬프트" 생성 → 별도 Claude AI에 복사
│   └─ Opus 급 작업: 시스템 재설계, 100+파일 리팩토링, 보안감사
│       조건: Kiro로 불충분 + 시스템 장애 위험 + 핵심 부분만
│
└─ 1% → Kiro가 "초압축 프롬프트" 생성 → 별도 ChatGPT에 복사
    └─ 수학/과학 논리증명이 필요한 설계 일부분
        조건: Opus로도 부족 + 수학집약 + 해당 부분만
```

### 프롬프트 요청 방법:
```
사용자: "이거 Claude에 물어볼 프롬프트 만들어줘"
사용자: "GPT에 넣을 프롬프트 줘"
→ Kiro가 토큰 극소화 초압축 프롬프트 즉시 생성
```

---

## 복사해서 바로 쓰는 프롬프트 3종

### 프롬프트 1: 별도 Claude AI에 복사용 (Opus 레벨 작업)
```
시스템: {프로젝트 1줄 설명}
스택: {기술스택 나열}
구조: {핵심 파일 5개 이내}

작업: {구체적 1문장}
범위: {영향받는 파일/모듈 명시}

출력 형식:
1. 판단 근거 (3줄 이내)
2. 해결안 (코드 또는 설계 - 해당 부분만)
3. 위험요소 (1~2개)

제약: 500토큰 이내. 설명 최소. 핵심만.
```

### 프롬프트 2: 별도 ChatGPT에 복사용 (수학/논리 증명)
```
수학적 판단 요청.

문제: {구체적 수학/논리 문제 1~2문장}
맥락: {왜 이게 필요한지 1문장}

출력: 결론 + 수식/증명 (200토큰 이내)
설명 금지. 결론과 근거만.
```

### 프롬프트 3: 세션 핸드오프 (Kiro에서 직접)
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

## 💡 Kiro가 프롬프트를 생성해주는 흐름

```
사용자: "이 부분 Claude에 물어보고 싶어"
       또는
사용자: "GPT에 넣을 프롬프트 줘"

→ Kiro 응답:
  1. [대상 AI] Claude AI / ChatGPT
  2. [프롬프트] (복사해서 바로 사용)
     - 컨텍스트 극압축 (L2~L3)
     - 출력 형식 강제 (하네스)
     - 토큰 상한 명시
  3. [기대 결과] 어떤 답이 올지 1줄
  4. [후속] 받은 답을 여기 붙이면 Kiro가 적용
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
