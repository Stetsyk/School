@echo off
REM Right-click -> Run as administrator, while logged in as the student user

REM 1. VS Code settings (old settings saved as settings.json.bak)
set "S=%APPDATA%\Code\User\settings.json"
if not exist "%APPDATA%\Code\User" mkdir "%APPDATA%\Code\User"
if exist "%S%" copy /y "%S%" "%S%.bak" >nul
(
echo {
echo   "chat.disableAIFeatures": true,
echo   "telemetry.telemetryLevel": "off",
echo   "update.mode": "none",
echo   "extensions.autoUpdate": false,
echo   "editor.minimap.enabled": false,
echo   "git.enabled": false,
echo   "workbench.startupEditor": "none"
echo }
) > "%S%"

REM 2. Remove heavy extensions (Python is in Thonny now)
for %%E in (ms-python.python ms-python.vscode-pylance GitHub.copilot GitHub.copilot-chat) do call code --uninstall-extension %%E

REM 3. Chrome: Memory Saver on, no running in background after closing
reg add "HKLM\SOFTWARE\Policies\Google\Chrome" /v HighEfficiencyModeEnabled /t REG_DWORD /d 1 /f
reg add "HKLM\SOFTWARE\Policies\Google\Chrome" /v BackgroundModeEnabled /t REG_DWORD /d 0 /f

echo Done. Restart VS Code and Chrome.
pause
