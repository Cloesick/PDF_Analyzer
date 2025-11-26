"""
Copy existing product images from DemaWebshop to PDF_Analyzer folder.

This preserves already-extracted images so you don't have to re-run Extract.py
for catalogs that already have images.
"""

import os
import shutil
from pathlib import Path

# Source: where Extract.py currently saves images
SOURCE_FOLDER = r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\product-images"

# Destination: where link_images_to_products.py looks for images
DEST_FOLDER = r"C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images"


def copy_images(source: Path, dest: Path, dry_run: bool = True):
    """Copy images from source to destination."""
    
    if not source.exists():
        print(f"ERROR: Source folder not found: {source}")
        return
    
    print(f"Source: {source}")
    print(f"Destination: {dest}")
    print()
    
    # Get all subdirectories (catalog folders)
    catalog_folders = [d for d in source.iterdir() if d.is_dir()]
    
    print(f"Found {len(catalog_folders)} catalog folders to copy")
    print()
    
    total_files = 0
    copied_files = 0
    skipped_files = 0
    
    for catalog_folder in catalog_folders:
        catalog_name = catalog_folder.name
        dest_catalog_folder = dest / catalog_name
        
        # Count images in this catalog
        images = list(catalog_folder.glob("**/*"))
        image_files = [f for f in images if f.is_file() and f.suffix.lower() in {'.webp', '.png', '.jpg', '.jpeg', '.gif'}]
        
        if not image_files:
            continue
        
        total_files += len(image_files)
        
        print(f"Catalog: {catalog_name}")
        print(f"  Images: {len(image_files)}")
        
        if dry_run:
            print(f"  [DRY RUN] Would copy to: {dest_catalog_folder}")
        else:
            # Create destination folder
            dest_catalog_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy all images
            for img_file in image_files:
                dest_file = dest_catalog_folder / img_file.name
                
                if dest_file.exists():
                    skipped_files += 1
                else:
                    try:
                        shutil.copy2(img_file, dest_file)
                        copied_files += 1
                    except Exception as e:
                        print(f"  ERROR copying {img_file.name}: {e}")
            
            print(f"  ✓ Copied {copied_files} images (skipped {skipped_files} existing)")
        
        print()
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total images found: {total_files}")
    
    if dry_run:
        print("\n[DRY RUN MODE - No files were copied]")
        print("\nTo actually copy the files, run:")
        print("  python copy_existing_images.py --copy")
    else:
        print(f"Copied: {copied_files}")
        print(f"Skipped (already exist): {skipped_files}")
        print("\n✓ Image copy completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Copy existing product images")
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Actually copy files (default is dry-run preview)"
    )
    
    args = parser.parse_args()
    
    copy_images(
        Path(SOURCE_FOLDER),
        Path(DEST_FOLDER),
        dry_run=not args.copy
    )
