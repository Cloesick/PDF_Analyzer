"""
JSON Consolidation Script
Identifies and consolidates duplicate JSON files to maintain a clean workspace.

Patterns addressed:
1. *_analysis.json + *_analysis_enriched.json → Keep enriched version only
2. *_grouped.json + *_grouped_enhanced.json → Keep enhanced version only
3. Multiple products_ready_for_webshop_*.json → Keep latest version
4. Multiple Makita product JSONs → Keep most complete version
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ARCHIVE_DIR = OUTPUT_DIR / "archive" / "consolidated_old_jsons"


def get_file_size(path: Path) -> int:
    """Get file size in bytes"""
    return path.stat().st_size if path.exists() else 0


def count_json_items(path: Path) -> int:
    """Count items in JSON file"""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return len(data)
            elif isinstance(data, dict):
                return len(data)
            return 0
    except:
        return 0


def find_duplicate_pairs() -> Dict[str, List[Tuple[Path, str]]]:
    """Find duplicate JSON file pairs"""
    
    duplicates = {
        "analysis_pairs": [],
        "grouped_pairs": [],
        "products_ready_variants": [],
        "makita_variants": [],
        "other_duplicates": [],
    }
    
    # Find all JSON files in output
    all_jsons = list(OUTPUT_DIR.glob("*.json"))
    
    # 1. Find analysis + enriched pairs
    for json_file in all_jsons:
        if json_file.name.endswith("_analysis.json"):
            base = json_file.name.replace("_analysis.json", "")
            enriched = OUTPUT_DIR / f"{base}_analysis_enriched.json"
            if enriched.exists():
                # Compare sizes - keep the larger one (usually enriched)
                size_normal = get_file_size(json_file)
                size_enriched = get_file_size(enriched)
                
                if size_enriched >= size_normal:
                    duplicates["analysis_pairs"].append((json_file, "DELETE - has enriched version"))
                else:
                    duplicates["analysis_pairs"].append((enriched, "DELETE - normal version is larger"))
    
    # 2. Find grouped + enhanced pairs
    for json_file in all_jsons:
        if json_file.name.endswith("_grouped.json"):
            enhanced = OUTPUT_DIR / json_file.name.replace("_grouped.json", "_grouped_enhanced.json")
            if enhanced.exists():
                # Keep enhanced version
                duplicates["grouped_pairs"].append((json_file, "DELETE - has enhanced version"))
    
    # 3. Find products_ready_for_webshop variants
    products_ready_files = [
        f for f in all_jsons 
        if "products_ready_for_webshop" in f.name or "products_multilanguage" in f.name
    ]
    
    if len(products_ready_files) > 1:
        # Sort by modification time, keep most recent
        products_ready_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        most_recent = products_ready_files[0]
        
        for old_file in products_ready_files[1:]:
            duplicates["products_ready_variants"].append(
                (old_file, f"DELETE - older than {most_recent.name}")
            )
    
    # 4. Find Makita product variants
    makita_files = [
        f for f in all_jsons
        if "makita" in f.name.lower() and any(x in f.name for x in [
            "complete_products", "products", "integrated", "ultra_aggressive"
        ])
    ]
    
    if len(makita_files) > 1:
        # Keep the one with most items
        sizes = [(f, count_json_items(f)) for f in makita_files]
        sizes.sort(key=lambda x: x[1], reverse=True)
        largest = sizes[0][0]
        
        for old_file, count in sizes[1:]:
            duplicates["makita_variants"].append(
                (old_file, f"DELETE - smaller than {largest.name} ({count} vs {sizes[0][1]} items)")
            )
    
    return duplicates


def archive_file(file_path: Path) -> None:
    """Move file to archive directory"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    target = ARCHIVE_DIR / file_path.name
    
    # If target exists, add timestamp
    if target.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ARCHIVE_DIR / f"{stem}_{timestamp}{suffix}"
    
    shutil.move(str(file_path), str(target))
    print(f"   Archived: {file_path.name} → archive/")


def consolidate_duplicates(duplicates: Dict[str, List[Tuple[Path, str]]], dry_run: bool = True) -> None:
    """Consolidate duplicate files"""
    
    total_files = sum(len(files) for files in duplicates.values())
    
    if total_files == 0:
        print("✅ No duplicates found!")
        return
    
    print(f"\n{'='*80}")
    print(f"FOUND {total_files} DUPLICATE FILES")
    print("=" * 80)
    
    for category, files in duplicates.items():
        if not files:
            continue
        
        print(f"\n📁 {category.replace('_', ' ').title()}: {len(files)} files")
        for file_path, reason in files:
            size_mb = get_file_size(file_path) / (1024 * 1024)
            print(f"   • {file_path.name} ({size_mb:.2f} MB)")
            print(f"     Reason: {reason}")
    
    if dry_run:
        print(f"\n{'='*80}")
        print("🔍 DRY RUN - No files were deleted")
        print("   Run with --execute to actually delete these files")
        print("=" * 80)
        return
    
    # Actually archive the files
    print(f"\n{'='*80}")
    print("ARCHIVING DUPLICATE FILES")
    print("=" * 80)
    
    archived_count = 0
    for category, files in duplicates.items():
        if not files:
            continue
        
        print(f"\n📦 Processing {category}...")
        for file_path, reason in files:
            try:
                archive_file(file_path)
                archived_count += 1
            except Exception as e:
                print(f"   ❌ Error archiving {file_path.name}: {e}")
    
    print(f"\n{'='*80}")
    print(f"✅ Archived {archived_count} duplicate files")
    print(f"   Location: {ARCHIVE_DIR}")
    print("=" * 80)


def main(execute: bool = False):
    """Main consolidation function"""
    
    print("=" * 80)
    print("JSON FILE CONSOLIDATION")
    print("=" * 80)
    print(f"Scanning: {OUTPUT_DIR}")
    
    # Find duplicates
    duplicates = find_duplicate_pairs()
    
    # Consolidate
    consolidate_duplicates(duplicates, dry_run=not execute)
    
    # Summary
    if not execute:
        print("\n💡 To execute the consolidation, run:")
        print("   python consolidate_json_files.py --execute")


if __name__ == "__main__":
    import sys
    execute = "--execute" in sys.argv or "-e" in sys.argv
    main(execute=execute)
