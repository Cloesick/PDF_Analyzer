@echo off
REM ================================================================
REM Sync Products & Images to DemaWebshop
REM ================================================================

echo.
echo ================================================================
echo SYNCING PRODUCTS TO DEMAWEBSHOP
echo ================================================================
echo.

REM Define paths
set PDF_ANALYZER=C:\Users\prova\Documents\Projects\PDF_Analyzer
set WEBSHOP=C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop

echo Source: %PDF_ANALYZER%
echo Target: %WEBSHOP%
echo.

REM Check if paths exist
if not exist "%PDF_ANALYZER%\output\products_for_shop.json" (
    echo ERROR: products_for_shop.json not found!
    echo Run 'python link_images_to_products.py' first.
    pause
    exit /b 1
)

if not exist "%WEBSHOP%\public\data" (
    echo Creating webshop data folder...
    mkdir "%WEBSHOP%\public\data"
)

REM Copy products JSON
echo [1/2] Copying products_for_shop.json...
copy /Y "%PDF_ANALYZER%\output\products_for_shop.json" "%WEBSHOP%\public\data\products_for_shop.json" >nul

if %ERRORLEVEL% EQU 0 (
    echo       ✓ Products JSON copied
) else (
    echo       ✗ Failed to copy products JSON
    pause
    exit /b 1
)

REM Note about images
echo.
echo [2/2] Product images...
echo       Images are already at: %WEBSHOP%\public\product-images\
echo       (No copy needed - they're in the same location)

REM Show statistics
echo.
echo ================================================================
echo STATISTICS
echo ================================================================

REM Count products using PowerShell
for /f "delims=" %%i in ('powershell -Command "& {(Get-Content '%WEBSHOP%\public\data\products_for_shop.json' | ConvertFrom-Json).Count}"') do set TOTAL_PRODUCTS=%%i

REM Count products with images
for /f "delims=" %%i in ('powershell -Command "& {$p = Get-Content '%WEBSHOP%\public\data\products_for_shop.json' | ConvertFrom-Json; ($p | Where-Object {$_.media -and $_.media.Count -gt 0}).Count}"') do set WITH_IMAGES=%%i

echo Total products:      %TOTAL_PRODUCTS%
echo Products with images: %WITH_IMAGES%

REM Calculate coverage
for /f "delims=" %%i in ('powershell -Command "& {[math]::Round(%WITH_IMAGES% / %TOTAL_PRODUCTS% * 100, 1)}"') do set COVERAGE=%%i
echo Coverage:            %COVERAGE%%%

echo.
echo ================================================================
echo ✓ SYNC COMPLETE
echo ================================================================
echo.
echo Next steps:
echo   1. cd %WEBSHOP%
echo   2. npm run dev
echo   3. Visit http://localhost:3000/products
echo.

pause
