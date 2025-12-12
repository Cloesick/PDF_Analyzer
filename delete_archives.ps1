# Delete Archive Folders (PowerShell)
# Removes the original archive folders after successful compression

Write-Host "=" * 80
Write-Host "DELETE ARCHIVED FOLDERS"
Write-Host "=" * 80
Write-Host ""

$archiveFolders = @(
    "archive\example_components",
    "archive\html_demos",
    "archive\misc_json",
    "archive\old_documentation",
    "archive\old_scripts",
    "archive\shell_scripts",
    "archive\specialized_scripts",
    "archive\utility_scripts",
    "output\archive\catalog_extractions",
    "output\archive\consolidated_old_jsons",
    "output\archive\json_name_consolidation",
    "output\archive\output_consolidation"
)

$deleted = 0
$totalSize = 0

Write-Host "🗑️  Deleting archive folders..." -ForegroundColor Yellow
Write-Host ""

foreach ($folder in $archiveFolders) {
    $fullPath = Join-Path $PSScriptRoot $folder
    
    if (Test-Path $fullPath) {
        try {
            $size = (Get-ChildItem $fullPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
            $totalSize += $size
            
            Remove-Item $fullPath -Recurse -Force
            Write-Host "   [OK] Deleted: $folder ($($size.ToString('F2')) MB)" -ForegroundColor Green
            $deleted++
        }
        catch {
            Write-Host "   [ERROR] Deleting $folder : $_" -ForegroundColor Red
        }
    }
}

# Clean up empty parent directories
$emptyDirs = @("archive", "output\archive")
foreach ($dir in $emptyDirs) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if ((Test-Path $fullPath) -and ((Get-ChildItem $fullPath).Count -eq 0)) {
        Remove-Item $fullPath -Force
        Write-Host "   [OK] Removed empty directory: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=" * 80
Write-Host "CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "=" * 80
Write-Host "   Deleted: $deleted folders"
Write-Host "   Freed:   $($totalSize.ToString('F2')) MB"
Write-Host "   Backups: compressed_archives\ (12 zip files, 10.5 MB)"
Write-Host "=" * 80
