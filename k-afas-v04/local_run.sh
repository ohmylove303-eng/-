#!/bin/bash
# K-AFAS v0.4.1 로컬 시현 (Mac/Linux)
# 외장형 하드에서: chmod +x local_run.sh && ./local_run.sh

echo "============================================"
echo "  K-AFAS v0.4.1 검토 콘솔 시현"
echo "============================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="$SCRIPT_DIR/demo"

if command -v python3 &>/dev/null; then
    echo "[INFO] Python HTTP 서버 시작 (http://localhost:8080)"
    echo "[INFO] 종료: Ctrl+C"
    echo ""
    
    # 브라우저 자동 열기
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8080" &
    else
        xdg-open "http://localhost:8080" 2>/dev/null &
    fi
    
    python3 -m http.server 8080 --directory "$DEMO_DIR"
else
    echo "[INFO] Python 미설치 — 파일 직접 열기"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$DEMO_DIR/index.html"
    else
        xdg-open "$DEMO_DIR/index.html"
    fi
fi
