@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ==========================================
echo Reset Database Docker
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

echo [1/4] Menghentikan container...
docker compose down
if errorlevel 1 (
    echo [ERROR] Gagal menjalankan docker compose down.
    goto :fail
)

echo.
echo [2/4] Menghapus database lama...
if exist "data\catalog_db.sqlite" (
    del /f /q "data\catalog_db.sqlite"
    if errorlevel 1 (
        echo [ERROR] Gagal menghapus data\catalog_db.sqlite
        goto :fail
    )
    echo [OK] Database lama berhasil dihapus.
) else (
    echo [INFO] Database lama tidak ditemukan, lanjut membuat database baru.
)

echo.
echo [3/4] Build dan start container baru...
docker compose up -d --build
if errorlevel 1 (
    echo [ERROR] Gagal menjalankan docker compose up.
    goto :show_logs
)

echo.
echo [4/4] Menampilkan log terbaru seed dan startup...
docker compose logs --tail=80

echo.
echo [SUCCESS] Database berhasil di-reset dan di-load ulang dari seed.py
goto :end

:show_logs
echo.
echo ===== Docker Logs =====
docker compose logs --tail=200
goto :fail

:fail
echo.
echo [FAILED] Reset database tidak selesai.
exit /b 1

:end
echo.
pause
exit /b 0
