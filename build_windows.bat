@echo off
setlocal
cd /d "%~dp0"
set "OUTPUT_DIR=dist\build-%RANDOM%"

python -m pip install -r requirements-build.txt
if errorlevel 1 exit /b %errorlevel%

python -m PyInstaller --clean --noconfirm --onefile --windowed --name DaysCounter --icon days_counter.ico --distpath "%OUTPUT_DIR%" --workpath build\app main.py
if errorlevel 1 exit /b %errorlevel%

powershell -NoProfile -ExecutionPolicy Bypass -Command "$exe = Join-Path (Get-Location) '%OUTPUT_DIR%\DaysCounter.exe'; $desktop = [Environment]::GetFolderPath('DesktopDirectory'); $shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Days Counter.lnk')); $shortcut.TargetPath = $exe; $shortcut.WorkingDirectory = Split-Path -Parent $exe; $shortcut.IconLocation = \"$exe,0\"; $shortcut.Description = 'Launch Days Counter'; $shortcut.Save()"
if errorlevel 1 exit /b %errorlevel%

echo.
echo Build complete: %~dp0%OUTPUT_DIR%\DaysCounter.exe
echo Desktop shortcut updated.
