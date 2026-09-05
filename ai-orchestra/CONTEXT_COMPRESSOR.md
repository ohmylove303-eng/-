# 컨텍스트 압축 시스템

## 목적
제한된 컨텍스트 윈도우(128K~1M 토큰)를 최대 효율로 사용하기 위한 압축 기법

---

## 1. 압축 레벨 정의

| 레벨 | 압축률 | 용도 | 예시 |
|------|--------|------|------|
| L0 (원본) | 0% | 현재 작업 중인 코드 | 수정할 함수 전체 |
| L1 (요약) | 70% | 참조용 코드 | 시그니처 + docstring만 |
| L2 (메타) | 90% | 배경 지식 | "flask_app.py: 32개 API 엔드포인트, yfinance 사용" |
| L3 (태그) | 95% | 존재만 인지 | "scripts/: 18개 분석 스크립트" |

---

## 2. 프로젝트 압축 템플릿 (즉시 사용 가능)

### 이 프로젝트의 L2 압축본 (새 세션에 복사하여 사용):

```
## 시스템 컨텍스트 (L2 압축)

프로젝트: US Stock Market Dashboard
스택: Python 3.9 / Flask / yfinance / Gemini API + OpenAI
배포: Render (Procfile) + GitHub Actions (매일 UTC 22:00 자동 업데이트)

### 구조
- flask_app.py: 메인 서버, 11개 API 엔드포인트 (/api/us/*)
- engine/: 추천엔진(us_recommendation_engine), 데이터수집기, 종가분석기
- scripts/: 18개 분석 스크립트 (update_all.py로 순차실행)
  - 핵심: smart_money_screener_v2, macro_analyzer, ai_summary_generator
- data/: JSON 캐시 (smart_money_current, etf_flow_analysis 등)
- templates/index.html + static/js/dashboard.js: 프론트엔드

### 주요 API
GET /api/us/smart-money → 스마트머니 추천 종목 (10개)
GET /api/us/macro-analysis → 매크로 분석 + AI 예측
GET /api/us/etf-flows → ETF 자금 흐름
POST /api/refresh-data → 수동 데이터 갱신

### 데이터 흐름
yfinance → scripts/create_us_daily_prices.py → 분석 스크립트들 → data/*.json → Flask API → 프론트엔드

### 사용 중인 AI
- Gemini 2.0 Flash: 매크로 분석, AI 요약
- OpenAI (fallback): Gemini 실패 시 백업
- API키: .env (GOOGLE_API_KEY, OPENAI_API_KEY)
```

---

## 3. 코드 압축 방법

### L1 압축 (함수를 시그니처로):
```python
# 원본 (30줄) → L1 (3줄)
def get_us_smart_money() -> jsonify:
    """스마트머니 추천 종목 반환. smart_money_current.json 로드 → yfinance 현재가 → 수익률 계산"""
    # 구현: 50줄
```

### L2 압축 (파일을 1줄로):
```
flask_app.py: Flask 서버, 11 API endpoints, yfinance 실시간 가격, Gemini/OpenAI AI 분석
```

### L3 압축 (디렉토리를 1줄로):
```
scripts/: 18개 Python 분석 스크립트 (데이터수집, 스크리닝, AI분석, 리포트 생성)
```

---

## 4. 대화 압축 규칙

### 매 10개 주제마다 자동 압축:
```
## 대화 요약 (주제 1~10)
1. ✅ telegram_alert.py 생성 완료
2. ✅ update_all.py에 telegram 스크립트 추가
3. ✅ .env에 TELEGRAM_BOT_TOKEN 추가 안내
4. ❌ 테스트 실패 → timeout 이슈 → 해결: timeout=60→120
5. ✅ GitHub Actions에 telegram step 추가
...
핵심 결정: threshold 5%로 확정, 알림 주기 1시간
미해결: Telegram 채널 vs 개인 DM 선택 필요
```

---

## 5. 즉시 사용 프롬프트

### "컨텍스트 압축해줘" 요청 시 사용할 프롬프트:

```markdown
아래 대화/코드를 L2 수준으로 압축해줘.

규칙:
1. 결정사항은 유지
2. 미해결 이슈 명시
3. 코드는 시그니처만
4. 총 300토큰 이내
5. 다음 AI가 이것만 보고 이어서 작업 가능해야 함

출력 형식:
## 압축 컨텍스트
- 완료: [리스트]
- 미해결: [리스트]  
- 핵심 결정: [리스트]
- 다음 작업: [명확한 1줄]
```
