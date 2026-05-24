@echo off
:: K-AFAS v0.4.1 로컬 시현 (Windows)
:: 외장형 하드에서 이 파일을 더블클릭하면 됩니다.

echo ============================================
echo   K-AFAS v0.4.1 검토 콘솔 시현
echo ============================================
echo.

:: Python이 있으면 HTTP 서버로, 없으면 직접 열기
where python >nul 2>&1
if %errorlevel%==0 (
    echo [INFO] Python HTTP 서버 시작 (http://localhost:8080)
    echo [INFO] 브라우저가 자동으로 열립니다.
    echo [INFO] 종료하려면 이 창을 닫으세요.
    echo.
    start http://localhost:8080
    python -m http.server 8080 --directory demo
) else (
    echo [INFO] Python 미설치 — 파일 직접 열기
    start demo\index.html
)
