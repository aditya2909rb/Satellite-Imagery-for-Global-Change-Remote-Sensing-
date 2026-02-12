@echo off
REM Quick Git Push Script for Windows

echo ================================================================================
echo   PUSHING TO GITHUB
echo ================================================================================
echo.

echo Step 1: Checking git status...
git status
echo.

echo Step 2: Adding all files...
git add .
echo.

echo Step 3: Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update satellite fire detection system

git commit -m "%commit_msg%"
echo.

echo Step 4: Pushing to GitHub...
git push
echo.

if %ERRORLEVEL% EQU 0 (
    echo ================================================================================
    echo   ✅ SUCCESSFULLY PUSHED TO GITHUB!
    echo ================================================================================
) else (
    echo ================================================================================
    echo   ❌ PUSH FAILED - Check error messages above
    echo ================================================================================
    echo.
    echo If this is your first push, you may need to:
    echo   1. Create a repository on GitHub
    echo   2. Run: git remote add origin https://github.com/yourusername/your-repo.git
    echo   3. Run: git branch -M main
    echo   4. Run: git push -u origin main
)

echo.
pause
