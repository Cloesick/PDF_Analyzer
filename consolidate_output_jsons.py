"""
Output JSON Consolidation
Consolidates similar-named JSON files in the output folder.

Patterns identified:
1. Multiple *_analysis_report.json files (30+) → Merge into one
2. Similar catalog data spread across multiple files
3. Redundant extraction/grouped files
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ARCHIVE_DIR = OUTPUT_DIR / "archive" / "json_name_consolidation"


def consolidate_analysis_reports():
    """Merge all *_analysis_report.json into one comprehensive report"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Analysis Report JSONs")
    print("="*80)
    
    report_files = list(OUTPUT_DIR.glob("*_analysis_report.json"))
    
    if not report_files:
        print("No analysis report files found")
        return 0
    
    print(f"Found {len(report_files)} analysis report files")
    
    # Merge all reports
    all_reports = {}
    
    for file in report_files:
        catalog_name = file.name.replace("_analysis_report.json", "")
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                all_reports[catalog_name] = data
                print(f"   Loaded: {file.name}")
        except Exception as e:
            print(f"   Error loading {file.name}: {e}")
    
    # Save consolidated report
    consolidated_file = OUTPUT_DIR / "all_catalogs_analysis_reports.json"
    with consolidated_file.open("w", encoding="utf-8") as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Consolidated into: {consolidated_file.name}")
    print(f"   Contains reports for {len(all_reports)} catalogs")
    
    # Archive individual report files
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\nArchiving individual report files:")
    for file in report_files:
        target = ARCHIVE_DIR / file.name
        shutil.move(str(file), str(target))
        if len(report_files) <= 10:
            print(f"   Archived: {file.name}")
    
    if len(report_files) > 10:
        print(f"   Archived all {len(report_files)} files")
    
    return len(report_files)


def consolidate_per_catalog_files():
    """For each catalog, consolidate related files into comprehensive catalog data"""
    
    print("\n" + "="*80)
    print("ANALYZING: Per-Catalog File Structure")
    print("="*80)
    
    # Get unique catalog names
    catalogs = set()
    
    for file in OUTPUT_DIR.glob("*.json"):
        name = file.stem
        # Remove common suffixes to get catalog name
        for suffix in ["_analysis_enriched", "_analysis_report", "_grouped", "_grouped_enhanced", 
                       "_smart_extracted", "_images", "_extracted", "_products_raw"]:
            if name.endswith(suffix):
                catalog = name.replace(suffix, "")
                catalogs.add(catalog)
                break
    
    print(f"Found {len(catalogs)} unique catalogs with multiple files\n")
    
    # Show structure for each catalog
    catalog_files = {}
    for catalog in sorted(catalogs):
        if catalog in ["products_for_webshop_consolidated", "makita_products_consolidated", 
                       "catalog_statistics", "catalogs_metadata", "makita_frontend_display"]:
            continue  # Skip consolidated files
        
        files = []
        patterns = [
            f"{catalog}_analysis_enriched.json",
            f"{catalog}_analysis_report.json",
            f"{catalog}_grouped.json",
            f"{catalog}_grouped_enhanced.json",
            f"{catalog}_smart_extracted.json",
            f"{catalog}_images.json",
            f"{catalog}_extracted.json",
            f"{catalog}_products_raw.json",
        ]
        
        for pattern in patterns:
            file_path = OUTPUT_DIR / pattern
            if file_path.exists():
                files.append(pattern)
        
        if len(files) > 1:
            catalog_files[catalog] = files
    
    if catalog_files:
        print("Catalogs with multiple related files:")
        for catalog, files in sorted(catalog_files.items())[:5]:  # Show first 5
            print(f"\n📁 {catalog}:")
            for f in files:
                size = (OUTPUT_DIR / f).stat().st_size / 1024
                print(f"   • {f} ({size:.1f} KB)")
        
        if len(catalog_files) > 5:
            print(f"\n... and {len(catalog_files) - 5} more catalogs")
    
    print(f"\n💡 These files are kept separate for different use cases:")
    print("   • *_analysis_enriched.json - Main enriched data")
    print("   • *_grouped_enhanced.json - Product groupings")
    print("   • *_smart_extracted.json - Raw extraction")
    print("   • *_images.json - Image references")
    print("\n✅ Current structure is optimal for flexibility")
    
    return 0


def consolidate_redundant_files():
    """Identify and archive truly redundant files"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Redundant Files")
    print("="*80)
    
    redundant = []
    
    # Check for _grouped.json when _grouped_enhanced.json exists
    for file in OUTPUT_DIR.glob("*_grouped.json"):
        enhanced = OUTPUT_DIR / file.name.replace("_grouped.json", "_grouped_enhanced.json")
        if enhanced.exists() and "_grouped_enhanced" not in file.name:
            redundant.append((file, f"Has enhanced version: {enhanced.name}"))
    
    # Check for raw/extracted versions when enriched exists
    for file in OUTPUT_DIR.glob("*_products_raw.json"):
        catalog = file.stem.replace("_products_raw", "")
        enriched = OUTPUT_DIR / f"{catalog}_analysis_enriched.json"
        if enriched.exists():
            redundant.append((file, f"Data in enriched version: {enriched.name}"))
    
    if not redundant:
        print("✅ No redundant files found")
        return 0
    
    print(f"Found {len(redundant)} redundant files:\n")
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    for file, reason in redundant:
        print(f"• {file.name}")
        print(f"  Reason: {reason}")
        target = ARCHIVE_DIR / file.name
        shutil.move(str(file), str(target))
        print(f"  Archived ✓\n")
    
    return len(redundant)


def main():
    """Run JSON consolidation"""
    
    print("="*80)
    print("OUTPUT JSON CONSOLIDATION")
    print("="*80)
    print(f"Analyzing: {OUTPUT_DIR}\n")
    
    counts = {}
    
    # Consolidate analysis reports
    counts["reports"] = consolidate_analysis_reports()
    
    # Analyze per-catalog structure
    consolidate_per_catalog_files()
    
    # Consolidate redundant files
    counts["redundant"] = consolidate_redundant_files()
    
    total = sum(counts.values())
    
    print("\n" + "="*80)
    print("CONSOLIDATION COMPLETE")
    print("="*80)
    print(f"Files consolidated: {total}")
    
    if counts["reports"] > 0:
        print(f"\n✅ Created: all_catalogs_analysis_reports.json")
        print(f"   Consolidated {counts['reports']} individual report files")
    
    if counts["redundant"] > 0:
        print(f"\n✅ Archived {counts['redundant']} redundant files")
    
    print(f"\nArchive location: {ARCHIVE_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
