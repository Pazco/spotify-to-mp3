@echo off
setlocal EnableDelayedExpansion
title spotify-to-mp3

echo.
echo ==================================================
echo   spotify-to-mp3
echo ==================================================
echo.
echo   Checking dependencies...
echo.

:: ── Check winget ─────────────────────────────────────────
winget --version >nul 2>&1
if errorlevel 1 (
    echo   [!] winget not found.
    echo   Please install it from the Microsoft Store
    echo   or update Windows to version 1809 or later.
    echo.
    pause
    exit /b 1
)

:: ── Python ───────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo   [+] Installing Python...
    winget install -e --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
    call :refresh_path
    python --version >nul 2>&1
    if errorlevel 1 (
        echo   [!] Python install failed.
        echo   Please install it manually from https://python.org
        pause
        exit /b 1
    )
    echo   [OK] Python installed
) else (
    echo   [OK] Python ready
)

:: ── ffmpeg ───────────────────────────────────────────────
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo   [+] Installing ffmpeg...
    winget install -e --id Gyan.FFmpeg --silent --accept-source-agreements --accept-package-agreements
    call :refresh_path
    ffmpeg -version >nul 2>&1
    if errorlevel 1 (
        echo   [!] ffmpeg install failed.
        echo   Please install it manually from https://ffmpeg.org
        pause
        exit /b 1
    )
    echo   [OK] ffmpeg installed
) else (
    echo   [OK] ffmpeg ready
)

:: ── nodejs ───────────────────────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo   [+] Installing Node.js...
    winget install -e --id OpenJS.NodeJS --silent --accept-source-agreements --accept-package-agreements
    call :refresh_path
    node --version >nul 2>&1
    if errorlevel 1 (
        echo   [!] Node.js install failed.
        echo   Please install it manually from https://nodejs.org
        pause
        exit /b 1
    )
    echo   [OK] Node.js installed
) else (
    echo   [OK] Node.js ready
)

:: ── yt-dlp ───────────────────────────────────────────────
yt-dlp --version >nul 2>&1
if errorlevel 1 (
    echo   [+] Installing yt-dlp...
    winget install -e --id yt-dlp.yt-dlp --silent --accept-source-agreements --accept-package-agreements >nul 2>&1
    call :refresh_path
    yt-dlp --version >nul 2>&1
    if errorlevel 1 (
        echo   [+] Trying pip install...
        python -m pip install yt-dlp --quiet
        call :refresh_path
    )
    yt-dlp --version >nul 2>&1
    if errorlevel 1 (
        echo   [!] yt-dlp install failed.
        echo   Please run: pip install yt-dlp
        pause
        exit /b 1
    )
    echo   [OK] yt-dlp installed
) else (
    echo   [OK] yt-dlp ready
)

:: ── windows-curses (needed for arrow key menu) ──────────
python -c "import curses" >nul 2>&1
if errorlevel 1 (
    echo   [+] Installing windows-curses...
    python -m pip install windows-curses --quiet
    echo   [OK] windows-curses installed
) else (
    echo   [OK] windows-curses ready
)

:: ── All good, run the bot ─────────────────────────────────
echo.
echo   [OK] All dependencies ready
echo.
echo ==================================================
echo.

set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%spotify-to-mp3-windows.py"

if errorlevel 1 (
    echo.
    echo   [!] The script exited with an error.
    pause
)
exit /b 0

:: ── Refresh PATH from registry ────────────────────────────
:refresh_path
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USR_PATH=%%b"
if defined USR_PATH (
    set "PATH=%SYS_PATH%;%USR_PATH%"
) else (
    set "PATH=%SYS_PATH%"
)
exit /b 0
