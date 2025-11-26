"""
Automated selective extraction - no prompts needed.
Extracts only catalogs with low coverage.
"""

import os
import shutil
from pathlib import Path

# Configuration
INPUT_FOLDER = Path(r"c:\Users\prova\Documents\Projects\PDF_Analyzer\input_pdfs")
TEMP_FOLDER = Path(r"c:\Users\prova\Documents\Projects\PDF_Analyzer\input_pdfs_temp")

# Catalogs to extract (0% or very low coverage)
LOW_COVERAGE_CATALOGS = [
    "offerteaanvraag-bronpomp.pdf",
    "plat-oprolbare-slangen.pdf",
    "pu-afzuigslangen.pdf",
    "rubber-slangen.pdf",
    "zuigerpompen (1).pdf",
    "zwarte-draad-en-lasfittingen (1).pdf",
    "abs-persluchtbuizen.pdf",
    "bronpompen.pdf",
    "pomp-specials.pdf",
    "rvs-draadfittingen.pdf",
]


def prepare_extraction():
    """Move non-targeted PDFs to temp folder."""
    
    print("="*75)
    print("AUTOMATED SELECTIVE EXTRACTION")
    print("="*75)
    
    # Create temp folder
    TEMP_FOLDER.mkdir(exist_ok=True)
    print(f"✓ Created temp folder: {TEMP_FOLDER}")
    
    # Get all PDFs
    all_pdfs = [f for f in INPUT_FOLDER.iterdir() if f.suffix.lower() == '.pdf']
    
    # Separate into extract vs move
    to_extract = [pdf for pdf in all_pdfs if pdf.name in LOW_COVERAGE_CATALOGS]
    to_move = [pdf for pdf in all_pdfs if pdf.name not in LOW_COVERAGE_CATALOGS]
    
    print(f"\nFound {len(all_pdfs)} total PDFs")
    print(f"  → Will extract: {len(to_extract)} PDFs")
    print(f"  → Will move to temp: {len(to_move)} PDFs")
    
    if to_extract:
        print("\nPDFs to extract:")
        for pdf in to_extract:
            print(f"  ✓ {pdf.name}")
    
    # Move files to temp
    moved_count = 0
    for pdf in to_move:
        dest = TEMP_FOLDER / pdf.name
        try:
            shutil.move(str(pdf), str(dest))
            moved_count += 1
        except Exception as e:
            print(f"  ✗ Error moving {pdf.name}: {e}")
    
    print(f"\n✓ Moved {moved_count} PDFs to temp folder")
    print(f"✓ {len(to_extract)} PDFs ready for extraction in: {INPUT_FOLDER}")
    
    return True


def restore_pdfs():
    """Move PDFs back from temp folder."""
    
    print("\n" + "="*75)
    print("RESTORING PDFs FROM TEMP")
    print("="*75)
    
    if not TEMP_FOLDER.exists():
        print("No temp folder found. Nothing to restore.")
        return
    
    pdfs = list(TEMP_FOLDER.glob("*.pdf"))
    
    if not pdfs:
        print("No PDFs found in temp folder.")
        return
    
    print(f"Found {len(pdfs)} PDFs in temp folder")
    
    moved_count = 0
    for pdf in pdfs:
        dest = INPUT_FOLDER / pdf.name
        try:
            shutil.move(str(pdf), str(dest))
            moved_count += 1
        except Exception as e:
            print(f"  ✗ Error moving {pdf.name}: {e}")
    
    print(f"✓ Moved {moved_count} PDFs back to input folder")
    
    # Remove temp folder if empty
    if not list(TEMP_FOLDER.iterdir()):
        TEMP_FOLDER.rmdir()
        print("✓ Removed empty temp folder")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_pdfs()
    else:
        prepare_extraction()
