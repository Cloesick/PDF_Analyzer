@echo off
REM ============================================================================
REM Quick script to link product images to your products JSON
REM ============================================================================

echo.
echo ============================================================
echo   Product Image Linking Tool
echo ============================================================
echo.

REM Default paths
set JSON_PATH=output\products_for_shop.json
set IMAGE_PATH=product-images
set OUTPUT_PATH=output\products_with_images.json
set REPORT_PATH=output\missing_images_report.json

echo Configuration:
echo   JSON Input:     %JSON_PATH%
echo   Images Folder:  %IMAGE_PATH%
echo   JSON Output:    %OUTPUT_PATH%
echo   Report Output:  %REPORT_PATH%
echo.

REM Check if files exist
if not exist "%JSON_PATH%" (
    echo ERROR: JSON file not found at %JSON_PATH%
    echo Please check the path and try again.
    pause
    exit /b 1
)

if not exist "%IMAGE_PATH%" (
    echo ERROR: Images folder not found at %IMAGE_PATH%
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo Starting image linking process...
echo This may take a few minutes for large datasets.
echo.

REM Run the Python script
python link_images_to_products.py ^
    --json "%JSON_PATH%" ^
    --images "%IMAGE_PATH%" ^
    --output "%OUTPUT_PATH%" ^
    --report "%REPORT_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! Image linking completed.
    echo ============================================================
    echo.
    echo Output saved to: %OUTPUT_PATH%
    echo Report saved to: %REPORT_PATH%
    echo.
) else (
    echo.
    echo ============================================================
    echo   ERROR: Image linking failed.
    echo ============================================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
