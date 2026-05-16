@echo off
REM Pull the latest COG framework into this vault.
REM Family members: just double-click this file.

cd /d "%~dp0"

echo Updating COG...
echo.

git pull

if errorlevel 1 (
    echo.
    echo *** Update failed. Your notes are safe. Ask Gusta to help. ***
) else (
    echo.
    echo COG updated successfully.
)

pause
