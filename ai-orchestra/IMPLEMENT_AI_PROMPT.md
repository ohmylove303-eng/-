# 구현 AI 전용 프롬프트 템플릿

## 최적 AI 선택 기준

| 상황 | AI | 이유 |
|------|-----|------|
| 새 모듈 작성 (>100줄) | Claude Sonnet 4 | 코딩 벤치마크 1위, 에이전틱 |
| 기존 코드 수정 (<50줄) | Gemini 2.5 Flash | 빠르고 저렴 ($0.50/MTok) |
| 버그 수정 | Claude Sonnet 4 | 정밀 추론 |
| 반복 패턴 코드 | Gemini 2.5 Flash | 고속 생성 |
| 테스트 코드 생성 | GPT-5 mini | 저비용, 패턴 코드에 적합 |

---

## 프롬프트 템플릿

```markdown
# ROLE
너는 시니어 Python 개발자다. 설명 없이 코드만 출력하라.

# SPEC (설계 AI 출력물 붙여넣기)
{설계서_내용}

# EXISTING CODE (관련 부분만)
```python
{기존_함수_또는_클래스_스니펫}
```

# RULES
1. 주석은 핵심 로직에만 한국어로 1줄
2. 에러 처리 필수 (try/except)
3. 타입 힌트 필수
4. 출력: 완성된 코드 파일 1개만
5. import는 파일 상단에 모두 모음
6. 설명/마크다운 없이 코드 블록만 출력

# FILE TO CREATE
파일명: {파일_경로}
```

---

## 실전 예시 (이 프로젝트 기준)

```markdown
# ROLE
너는 시니어 Python 개발자다. 설명 없이 코드만 출력하라.

# SPEC
## 파일: scripts/telegram_alert.py
## 인터페이스:
def check_price_alerts(threshold_pct: float = 5.0) -> list[dict]:
    """급등/급락 종목 감지. data/smart_money_current.json 기반"""
    ...

def send_telegram(message: str, chat_id: str) -> bool:
    """Telegram Bot API로 메시지 전송"""
    ...

def main():
    """check → filter → send 파이프라인"""
    ...

## 데이터 흐름:
smart_money_current.json → 가격 비교 → 5% 이상 변동 필터 → Telegram 전송

## 의존성: requests (이미 설치됨), python-dotenv

# EXISTING CODE
```python
# scripts/update_all.py 패턴 참조
def run_script(name, desc, timeout):
    path = os.path.join(SCRIPTS_DIR, name)
    result = subprocess.run([sys.executable, path], timeout=timeout, capture_output=True, text=True)
```

# RULES
1. 주석은 핵심 로직에만 한국어로 1줄
2. 에러 처리 필수
3. 타입 힌트 필수
4. .env에서 TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID 읽기
5. 코드만 출력. 설명 없음.

# FILE TO CREATE
scripts/telegram_alert.py
```

---

## 구현 AI 사용 시 핵심 규칙

1. **설계서를 반드시 먼저 받아라** - 설계 없이 구현 요청 금지
2. **기존 코드는 관련 부분만** - 전체 파일 붙이지 마라 (토큰 낭비)
3. **1회 호출 1파일** - 여러 파일을 한번에 요청하면 품질 저하
4. **출력 형식 강제** - "코드만 출력하라" 반드시 명시
5. **검증은 별도** - 같은 호출에서 "맞는지 확인해줘" 추가하지 마라
