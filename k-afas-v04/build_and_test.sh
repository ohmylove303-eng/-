#!/bin/bash
# K-AFAS v0.4.1 빌드+테스트 (Mac/Linux)
# 외장하드에서: chmod +x build_and_test.sh && ./build_and_test.sh

set -e
echo "============================================"
echo "  K-AFAS v0.4.1 빌드 + 테스트"
echo "============================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/frontend"

# Node.js 확인
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js 미설치. https://nodejs.org v20+ 설치 필요"
    exit 1
fi

echo "[1/4] npm install..."
npm install

echo "[2/4] TypeScript 타입 검사..."
npx tsc --noEmit
echo "  TYPECHECK: PASS"

echo "[3/4] Vite 빌드..."
npx vite build
echo "  BUILD: PASS"

echo "[4/4] 금지 키워드 검증..."
VIOLATIONS=$(grep -rn "fire_control\|weapon_release\|turret\|kill_chain\|firing_solution\|autonomous.fire" src/ --include="*.ts" --include="*.tsx" | grep -v "FORBIDDEN\|금지\|차단\|REJECT\|수행하지" | wc -l)
if [ "$VIOLATIONS" -gt 0 ]; then
    echo "  [FAIL] 금지 키워드 기능 사용 ${VIOLATIONS}건 감지!"
    exit 1
fi
echo "  FORBIDDEN GREP: PASS (0건)"

echo ""
echo "============================================"
echo "  모든 검증 통과!"
echo "  TYPECHECK: PASS"
echo "  BUILD: PASS"  
echo "  FORBIDDEN: PASS"
echo "============================================"
echo ""
echo "시현: demo/index.html 더블클릭"
echo "서버: cd frontend && npm run dev"
