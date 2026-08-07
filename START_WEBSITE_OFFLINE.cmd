@echo off
TITLE Local Jekyll Website Server (Offline Preview)
echo ====================================================================
echo   Starting Local Development Server with Live-Reload...
echo ====================================================================
echo.

:: Ensure Ruby system PATH is included
set "PATH=%PATH%;C:\Ruby33-x64\bin"

:: Automatically launch your default web browser after waiting for server startup
:: (Jekyll's own build can take several seconds, so we wait longer than before)
start "" /b cmd /c "timeout /t 10 /nobreak >nul && explorer.exe http://127.0.0.1:4000/"

echo Your web browser will open to http://127.0.0.1:4000/ automatically!
echo Any changes you save to HTML, CSS, or JS files will refresh instantly.
echo.
echo [To STOP the server, press CTRL+C and close this window]
echo.

bundle exec jekyll serve --livereload
pause
