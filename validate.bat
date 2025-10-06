@echo off
REM Directory Validation Helper Script
REM Usage: validate.bat "original_path" "extracted_path" [verbose]

if "%~1"=="" (
    echo Usage: validate.bat "original_path" "extracted_path" [verbose]
    echo Example: validate.bat "C:\MyProject" "extracted\MyProject_extracted_20251006_123456"
    echo Add "verbose" as third parameter for detailed output
    exit /b 1
)

if "%~2"=="" (
    echo Error: Please provide both original and extracted paths
    echo Usage: validate.bat "original_path" "extracted_path" [verbose]
    exit /b 1
)

set ORIGINAL_PATH=%~1
set EXTRACTED_PATH=%~2
set VERBOSE=%~3

echo.
echo ========================================
echo Directory Package Validation
echo ========================================
echo Original:  %ORIGINAL_PATH%
echo Extracted: %EXTRACTED_PATH%
echo.

if /i "%VERBOSE%"=="verbose" (
    python validator.py "%ORIGINAL_PATH%" "%EXTRACTED_PATH%" -v --save-report "validation_report.json"
) else (
    python validator.py "%ORIGINAL_PATH%" "%EXTRACTED_PATH%" --save-report "validation_report.json"
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ VALIDATION SUCCESSFUL
    echo Report saved to: validation_report.json
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ❌ VALIDATION FAILED
    echo Check validation_report.json for details
    echo ========================================
)

pause