@echo off
REM Setup script for AI-DevOps tools on Windows
REM This script installs kubectl-ai, kagent, and checks Gordon availability

echo ========================================
echo   AI-DevOps Tools Setup for Windows
echo ========================================
echo.

REM Check if running in Git Bash or CMD
if "%MSYSTEM%"=="" (
    echo Running in Windows CMD/PowerShell
    set SHELL_TYPE=cmd
) else (
    echo Running in Git Bash: %MSYSTEM%
    set SHELL_TYPE=gitbash
)

echo.
echo [INFO] Installing kubectl-ai for Windows...
echo.

REM Method 1: Direct download of kubectl-ai Windows binary
echo [INFO] Downloading kubectl-ai Windows binary...
curl -L -o kubectl-ai.exe https://github.com/kubernetes-sigs/kubectl-ai/releases/latest/download/kubectl-ai_windows_amd64.exe

if exist kubectl-ai.exe (
    echo [SUCCESS] Downloaded kubectl-ai.exe
    
    REM Move to a directory in PATH
    if exist "%USERPROFILE%\bin" (
        move kubectl-ai.exe "%USERPROFILE%\bin\"
        echo [SUCCESS] Installed to %USERPROFILE%\bin\kubectl-ai.exe
    ) else (
        mkdir "%USERPROFILE%\bin" 2>nul
        move kubectl-ai.exe "%USERPROFILE%\bin\"
        echo [SUCCESS] Installed to %USERPROFILE%\bin\kubectl-ai.exe
        echo [WARNING] Please add %USERPROFILE%\bin to your PATH environment variable
    )
) else (
    echo [ERROR] Failed to download kubectl-ai
    echo [INFO] Trying alternative method using kubectl krew...
    goto :install_krew
)

goto :install_kagent

:install_krew
REM Alternative: Install krew for kubectl plugin management
echo.
echo [INFO] Installing krew (kubectl plugin manager)...

cd %TEMP%
curl -L -o krew.zip https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-windows_amd64.zip
if exist krew.zip (
    powershell -Command "Expand-Archive -Path 'krew.zip' -DestinationPath '.' -Force"
    move krew-windows_amd64.exe %USERPROFILE%\bin\krew.exe 2>nul || move krew-windows_amd64.exe %USERPROFILE%\krew.exe
    echo [SUCCESS] Installed krew
    echo [INFO] You can now use: kubectl krew install ai
) else (
    echo [ERROR] Failed to download krew
)

:install_kagent
echo.
echo [INFO] Installing kagent for Windows...
echo.

cd %TEMP%
curl -L -o kagent.zip https://github.com/kagent-dev/kagent/releases/latest/download/kagent_windows_amd64.zip

if exist kagent.zip (
    powershell -Command "Expand-Archive -Path 'kagent.zip' -DestinationPath '.' -Force"
    move kagent.exe %USERPROFILE%\bin\kagent.exe 2>nul || move kagent.exe %USERPROFILE%\kagent.exe
    echo [SUCCESS] Installed kagent
) else (
    echo [ERROR] Failed to download kagent
    echo [INFO] Please install manually from: https://github.com/kagent-dev/kagent/releases
)

:check_gordon
echo.
echo [INFO] Checking Gordon (Docker AI) availability...
echo.

docker ai --help >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [SUCCESS] Gordon (Docker AI) is available!
    docker ai "What can you do?"
) else (
    echo [WARNING] Gordon (Docker AI) is not available
    echo.
    echo To enable Gordon:
    echo   1. Open Docker Desktop
echo   2. Go to Settings ^> Beta features
echo   3. Toggle "Docker AI" or "Gordon" ON
echo   4. Restart Docker Desktop
echo.
    echo Note: Gordon may not be available in all regions or Docker Desktop tiers.
echo If unavailable, use standard Docker CLI commands.
)

:finish
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Installed tools:
if exist "%USERPROFILE%\bin\kubectl-ai.exe" echo   [OK] kubectl-ai
if exist "%USERPROFILE%\bin\kagent.exe" echo   [OK] kagent
docker ai --help >nul 2>&1 && echo   [OK] Gordon (Docker AI)
echo.
echo IMPORTANT: Make sure %USERPROFILE%\bin is in your PATH
echo.
echo Next steps:
echo   1. Set your OpenAI API Key:
echo      set OPENAI_API_KEY=sk-your-key-here
echo.
echo   2. Deploy the chatbot:
echo      .\scripts\deploy-chatbot-minikube.sh
echo.
echo   3. Try AI-assisted commands:
echo      kubectl-ai "check pod status" -n todo-chatbot
echo      kagent "analyze cluster health"
echo.
pause
