@echo off
:: K-AFAS v0.4.1 빌드+테스트 (Windows)
:: 외장하드에서 실행: BUILD_AND_TEST.bat

echo ============================================
echo   K-AFAS v0.4.1 빌드 + 테스트
echo ============================================
echo.

:: Node.js 확인
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js가 설치되어 있지 않습니다.
    echo   https://nodejs.org 에서 v20+ 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

echo [1/4] npm install...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [FAIL] npm install 실패
    pause
    exit /b 1
)

echo [2/4] TypeScript 타입 검사...
call npx tsc --noEmit
if %errorlevel% neq 0 (
    echo [FAIL] typecheck 실패
    pause
    exit /b 1
)
echo   TYPECHECK: PASS

echo [3/4] Vite 빌드...
call npx vite build
if %errorlevel% neq 0 (
    echo [FAIL] build 실패
    pause
    exit /b 1
)
echo   BUILD: PASS

echo [4/4] 금지 키워드 검증...
findstr /s /i "fire_control weapon_release turret kill_chain firing_solution" src\*.ts src\*.tsx | findstr /v "FORBIDDEN 금지 차단 REJECT 수행하지" >nul 2>&1
if %errorlevel% equ 0 (
    echo [FAIL] 금지 키워드 기능 사용 감지!
    pause
    exit /b 1
)
echo   FORBIDDEN GREP: PASS (0건)

echo.
echo ============================================
echo   모든 검증 통과!
echo   TYPECHECK: PASS
echo   BUILD: PASS
echo   FORBIDDEN: PASS
echo ============================================
echo.
echo 시현: demo\index.html 더블클릭
echo 서버: npm run dev (http://localhost:3000)
pause
