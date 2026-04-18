@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

echo ==========================================
echo WhatsApp Catalog AI Docker Test Runner
echo ==========================================
echo.

where docker >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker tidak ditemukan di PATH.
    goto :fail
)

docker compose version >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker Compose tidak tersedia.
    goto :fail
)

if not exist ".env" (
    echo [ERROR] File .env tidak ditemukan.
    goto :fail
)

echo [1/4] Build dan start container...
docker compose up -d --build
if errorlevel 1 (
    echo [ERROR] Gagal menjalankan docker compose up.
    goto :show_logs
)

echo.
echo [2/4] Menunggu API siap di http://127.0.0.1:8000/ ...
set "MAX_RETRIES=30"
set "WAIT_SECONDS=2"
set "READY="

for /L %%i in (1,1,%MAX_RETRIES%) do (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

    if not errorlevel 1 (
        set "READY=1"
        echo [OK] API sudah siap.
        goto :run_tests
    )

    echo [WAIT] Percobaan %%i/%MAX_RETRIES% API belum siap, tunggu %WAIT_SECONDS% detik...
    timeout /t %WAIT_SECONDS% /nobreak >nul
)

if not defined READY (
    echo [ERROR] API tidak siap dalam waktu yang ditentukan.
    goto :show_logs
)

:run_tests
echo.
echo [3/4] Menjalankan pytest di dalam container...
docker compose exec -T wa-catalog-backend python -m pytest -v tests/
if errorlevel 1 (
    echo [ERROR] Pytest gagal.
    goto :show_logs
)

echo.
echo [4/4] Menjalankan smoke test webhook...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$payload = @{ sender = '6281234567890'; message = 'Halo min, ini test otomatis dari test.bat untuk katalog Warung Uji Docker di Jakarta dengan menu nasi goreng dan mie goreng, USP porsi besar.' } | ConvertTo-Json; " ^
    "try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/whatsapp-catalog' -Method Post -ContentType 'application/json' -Body $payload -TimeoutSec 10; " ^
    "if ($response.status -ne 'success') { Write-Error ('Smoke test gagal: ' + ($response | ConvertTo-Json -Compress)); exit 1 } " ^
    "Write-Host ('Smoke test response: ' + ($response | ConvertTo-Json -Compress)); exit 0 } catch { Write-Error $_; exit 1 }"
if errorlevel 1 (
    echo [ERROR] Smoke test webhook gagal.
    goto :show_logs
)

echo.
echo [SUCCESS] Semua test selesai dengan baik.
echo Service tetap berjalan di background.
goto :end

:show_logs
echo.
echo ===== Docker Logs =====
docker compose logs --tail=200
goto :fail

:fail
echo.
echo [FAILED] Test runner berhenti karena error.
exit /b 1

:end
echo.
pause
exit /b 0
