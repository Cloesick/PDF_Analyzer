"""
Extract images only from catalogs that have 0% or low coverage.

This avoids re-processing everything and focuses on missing catalogs.
"""

import os
import shutil
import json
from pathlib import Path
from collections import Counter

# Configuration
INPUT_FOLDER = r"c:\Users\prova\Documents\Projects\PDF_Analyzer\input_pdfs"
TEMP_FOLDER = r"c:\Users\prova\Documents\Projects\PDF_Analyzer\input_pdfs_temp"
PRODUCTS_JSON = r"c:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json"
MISSING_JSON = r"c:\Users\prova\Documents\Projects\PDF_Analyzer\output\missing_images.json"

# Catalogs with 0% or very low coverage (customize this list)
LOW_COVERAGE_CATALOGS = [
    "offerteaanvraag-bronpomp.pdf",
    "plat-oprolbare-slangen.pdf",
    "pu-afzuigslangen.pdf",
    "rubber-slangen.pdf",
    "zuigerpompen (1).pdf",
    "zwarte-draad-en-lasfittingen (1).pdf",
    "abs-persluchtbuizen.pdf",  # 0.8% coverage
    "bronpompen.pdf",  # 5.3% coverage
    "pomp-specials.pdf",  # 22% coverage
    "rvs-draadfittingen.pdf",  # 23.5% coverage
]


def analyze_coverage():
    """Analyze which catalogs have low coverage."""
    print("Analyzing coverage by catalog...\n")
    
    # Load data
    with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
        all_products = json.load(f)
    
    with open(MISSING_JSON, 'r', encoding='utf-8') as f:
        missing_products = json.load(f)
    
    # Count by catalog
    total_by_catalog = Counter()
    missing_by_catalog = Counter()
    
    for p in all_products:
        catalog = p.get('catalog', 'unknown')
        total_by_catalog[catalog] += 1
    
    for p in missing_products:
        catalog = p.get('catalog', 'unknown')
        missing_by_catalog[catalog] += 1
    
    # Calculate coverage
    results = []
    for catalog in sorted(total_by_catalog.keys()):
        total = total_by_catalog[catalog]
        missing = missing_by_catalog.get(catalog, 0)
        coverage = (1 - missing/total) * 100 if total > 0 else 100
        
        results.append({
            'catalog': catalog,
            'total': total,
            'missing': missing,
            'coverage': coverage
        })
    
    # Sort by coverage (lowest first)
    results.sort(key=lambda x: x['coverage'])
    
    print(f"{'Catalog':<45} {'Missing':>8} {'Total':>8} {'Coverage':>10}")
    print("-" * 75)
    
    for r in results:
        print(f"{r['catalog']:<45} {r['missing']:>8} {r['total']:>8} {r['coverage']:>9.1f}%")
    
    return results


def prepare_for_selective_extraction():
    """Move non-targeted PDFs to temp folder."""
    
    print("\n" + "="*75)
    print("SELECTIVE EXTRACTION PREPARATION")
    print("="*75)
    
    input_path = Path(INPUT_FOLDER)
    temp_path = Path(TEMP_FOLDER)
    
    # Create temp folder
    temp_path.mkdir(exist_ok=True)
    
    # Get all PDFs
    all_pdfs = [f for f in input_path.iterdir() if f.suffix.lower() == '.pdf']
    
    # Identify which to keep and which to move
    to_extract = []
    to_move = []
    
    for pdf in all_pdfs:
        if pdf.name in LOW_COVERAGE_CATALOGS:
            to_extract.append(pdf)
        else:
            to_move.append(pdf)
    
    print(f"\nFound {len(all_pdfs)} total PDFs")
    print(f"Will extract: {len(to_extract)} PDFs")
    print(f"Will move to temp: {len(to_move)} PDFs")
    
    if to_extract:
        print("\nPDFs to extract:")
        for pdf in to_extract:
            print(f"  ✓ {pdf.name}")
    
    print("\nThis will:")
    print(f"1. Move {len(to_move)} PDFs to: {temp_path}")
    print(f"2. Leave {len(to_extract)} PDFs in: {input_path}")
    print("3. You can then run: python Extract.py")
    print(f"4. Afterwards, move PDFs back from temp folder")
    
    response = input("\nProceed with moving files? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Cancelled.")
        return False
    
    # Move files
    moved_count = 0
    for pdf in to_move:
        dest = temp_path / pdf.name
        try:
            shutil.move(str(pdf), str(dest))
            moved_count += 1
        except Exception as e:
            print(f"Error moving {pdf.name}: {e}")
    
    print(f"\n✓ Moved {moved_count} PDFs to temp folder")
    print(f"✓ Ready to run: python Extract.py")
    
    return True


def restore_pdfs():
    """Move PDFs back from temp folder."""
    
    print("\n" + "="*75)
    print("RESTORE PDFs FROM TEMP")
    print("="*75)
    
    input_path = Path(INPUT_FOLDER)
    temp_path = Path(TEMP_FOLDER)
    
    if not temp_path.exists():
        print("Temp folder doesn't exist. Nothing to restore.")
        return
    
    pdfs = list(temp_path.glob("*.pdf"))
    
    if not pdfs:
        print("No PDFs found in temp folder.")
        return
    
    print(f"\nFound {len(pdfs)} PDFs in temp folder")
    
    response = input(f"Move them back to {input_path}? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Cancelled.")
        return
    
    moved_count = 0
    for pdf in pdfs:
        dest = input_path / pdf.name
        try:
            shutil.move(str(pdf), str(dest))
            moved_count += 1
        except Exception as e:
            print(f"Error moving {pdf.name}: {e}")
    
    print(f"\n✓ Moved {moved_count} PDFs back to input folder")
    
    # Remove temp folder if empty
    if not list(temp_path.iterdir()):
        temp_path.rmdir()
        print("✓ Removed empty temp folder")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_pdfs()
    elif len(sys.argv) > 1 and sys.argv[1] == "analyze":
        analyze_coverage()
    else:
        print("="*75)
        print("EXTRACT MISSING CATALOGS - HELPER TOOL")
        print("="*75)
        
        # Show coverage analysis
        analyze_coverage()
        
        print("\n" + "="*75)
        print("NEXT STEPS")
        print("="*75)
        print("\n1. Run this script to prepare for selective extraction:")
        print("     python extract_missing_catalogs.py")
        print("\n2. Then run extraction on just the missing catalogs:")
        print("     python Extract.py")
        print("\n3. Then restore all PDFs:")
        print("     python extract_missing_catalogs.py restore")
        print("\n4. Finally, link images:")
        print("     python link_images_to_products.py")
        
        print("\nOR run just the analysis:")
        print("     python extract_missing_catalogs.py analyze")
        
        response = input("\n\nPrepare for selective extraction now? (yes/no): ").strip().lower()
        
        if response == 'yes':
            prepare_for_selective_extraction()
