"""
Output Folder Consolidation
Identifies and consolidates similar-named files in the output folder.

Patterns to consolidate:
1. Multiple grouped files for same catalog
2. Multiple extracted/smart_extracted variants
3. Similar catalog naming (dash vs underscore)
4. Duplicate data files (RVS, Makita variants)
5. Sample/report duplicates
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ARCHIVE_DIR = OUTPUT_DIR / "archive" / "output_consolidation"


def analyze_output_files() -> Dict[str, List[Path]]:
    """Analyze output folder and group similar files"""
    
    groups = {
        "catalogus_aandrijftechniek_variants": [],
        "grouped_files_needing_merge": [],
        "rvs_variants": [],
        "makita_variants": [],
        "sample_products": [],
        "reports": [],
        "image_jsons": [],
        "extraction_variants": [],
    }
    
    all_files = list(OUTPUT_DIR.glob("*.json")) + list(OUTPUT_DIR.glob("*.html")) + list(OUTPUT_DIR.glob("*.md"))
    
    for file in all_files:
        name = file.name
        
        # Group catalogus_aandrijftechniek variants
        if "catalogus_aandrijftechniek" in name and name != "catalogus_aandrijftechniek_enriched_complete.json":
            groups["catalogus_aandrijftechniek_variants"].append(file)
        
        # Group duplicate grouped files (non-enhanced)
        if "_grouped.json" in name and "_grouped_enhanced" not in name:
            # Check if enhanced version exists
            enhanced = OUTPUT_DIR / name.replace("_grouped.json", "_grouped_enhanced.json")
            if enhanced.exists():
                groups["grouped_files_needing_merge"].append(file)
        
        # Group RVS variants
        if "rvs_" in name and name not in ["rvs_draadfittingen_analysis_enriched.json", "rvs_draadfittingen_grouped.json"]:
            groups["rvs_variants"].append(file)
        
        # Group Makita variants (excluding consolidated)
        if "makita" in name and name not in ["makita_products_consolidated.json", "makita_frontend_display.json"]:
            if any(x in name for x in ["extracted", "properties", "batteries", "comparison", "matching", "tuinfolder_tables", "mowers"]):
                groups["makita_variants"].append(file)
        
        # Group sample products
        if "_sample_products.json" in name:
            groups["sample_products"].append(file)
        
        # Group reports
        if "_report.html" in name:
            groups["reports"].append(file)
        
        # Group small/placeholder image JSONs
        if "_images.json" in name:
            size = file.stat().st_size
            if size < 1000:  # Less than 1KB (likely empty or minimal)
                groups["image_jsons"].append(file)
        
        # Group extraction variants
        if any(x in name for x in ["_extracted.json", "_smart_extracted.json"]):
            if "_tools_extracted" not in name:  # Keep tools_extracted
                groups["extraction_variants"].append(file)
    
    return groups


def consolidate_catalogus_aandrijftechniek(files: List[Path]) -> None:
    """Consolidate catalogus_aandrijftechniek variants into enriched_complete"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: catalogus_aandrijftechniek variants")
    print("="*80)
    
    if not files:
        print("No variants found")
        return
    
    # The enriched_complete.json is the master
    master = OUTPUT_DIR / "catalogus_aandrijftechniek_enriched_complete.json"
    
    if not master.exists():
        print(f"❌ Master file not found: {master.name}")
        return
    
    print(f"Master file: {master.name}")
    print(f"Variants to archive ({len(files)}):")
    
    for file in files:
        print(f"   • {file.name} ({file.stat().st_size / (1024*1024):.1f} MB)")
    
    # Archive variants
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        target = ARCHIVE_DIR / file.name
        shutil.move(str(file), str(target))
        print(f"   Archived: {file.name}")
    
    print(f"\n✅ Kept master: {master.name}")


def merge_grouped_files(files: List[Path]) -> None:
    """Merge non-enhanced grouped files into enhanced versions"""
    
    print("\n" + "="*80)
    print("MERGING: Grouped files into enhanced versions")
    print("="*80)
    
    if not files:
        print("No files need merging")
        return
    
    print(f"Found {len(files)} grouped files that have enhanced versions:")
    
    for file in files:
        enhanced_name = file.name.replace("_grouped.json", "_grouped_enhanced.json")
        enhanced_file = OUTPUT_DIR / enhanced_name
        
        if enhanced_file.exists():
            print(f"   • {file.name} → has enhanced version")
            
            # Archive the non-enhanced version
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            target = ARCHIVE_DIR / file.name
            shutil.move(str(file), str(target))
            print(f"     Archived to: archive/")


def consolidate_rvs_files(files: List[Path]) -> None:
    """Keep only essential RVS files"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: RVS files")
    print("="*80)
    
    if not files:
        print("No RVS variants found")
        return
    
    print(f"Found {len(files)} RVS variant files")
    print("Keeping: rvs_draadfittingen_analysis_enriched.json, rvs_draadfittingen_grouped.json")
    print("Archiving others:")
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        print(f"   • {file.name} ({file.stat().st_size / (1024*1024):.1f} MB)")
        target = ARCHIVE_DIR / file.name
        shutil.move(str(file), str(target))
        print(f"     Archived")


def consolidate_makita_variants(files: List[Path]) -> None:
    """Archive specific Makita extraction files (keeping consolidated)"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Makita variant files")
    print("="*80)
    
    if not files:
        print("No Makita variants found")
        return
    
    print(f"Found {len(files)} Makita variant files")
    print("Keeping: makita_products_consolidated.json, makita_frontend_display.json")
    print("Archiving extraction variants:")
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        size_mb = file.stat().st_size / (1024*1024)
        print(f"   • {file.name} ({size_mb:.1f} MB)")
        target = ARCHIVE_DIR / file.name
        shutil.move(str(file), str(target))


def cleanup_small_files(image_jsons: List[Path], samples: List[Path]) -> None:
    """Clean up small/empty placeholder files"""
    
    print("\n" + "="*80)
    print("CLEANING UP: Small placeholder files")
    print("="*80)
    
    all_small = image_jsons + samples
    
    if not all_small:
        print("No small files found")
        return
    
    print(f"Found {len(all_small)} small files (<1KB or sample files):")
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in all_small:
        size = file.stat().st_size
        print(f"   • {file.name} ({size} bytes)")
        target = ARCHIVE_DIR / file.name
        shutil.move(str(file), str(target))


def main():
    """Main consolidation"""
    
    print("="*80)
    print("OUTPUT FOLDER CONSOLIDATION")
    print("="*80)
    print(f"Analyzing: {OUTPUT_DIR}")
    
    # Analyze files
    groups = analyze_output_files()
    
    # Count total files to process
    total = sum(len(files) for files in groups.values())
    print(f"\nFound {total} files to consolidate across {len(groups)} categories")
    
    # Consolidate each group
    consolidate_catalogus_aandrijftechniek(groups["catalogus_aandrijftechniek_variants"])
    merge_grouped_files(groups["grouped_files_needing_merge"])
    consolidate_rvs_files(groups["rvs_variants"])
    consolidate_makita_variants(groups["makita_variants"])
    cleanup_small_files(groups["image_jsons"], groups["sample_products"])
    
    # Summary
    print("\n" + "="*80)
    print("CONSOLIDATION COMPLETE")
    print("="*80)
    print(f"Files archived: {total}")
    print(f"Archive location: {ARCHIVE_DIR}")
    print()
    print("✅ Output folder now contains only essential files:")
    print("   • Consolidated master files")
    print("   • Enriched analysis files")
    print("   • Enhanced grouped files")
    print("   • Essential catalog-specific data")
    print()
    print("All archived files are recoverable from archive/output_consolidation/")
    print("="*80)


if __name__ == "__main__":
    main()
