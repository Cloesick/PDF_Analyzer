"""
Link existing product images to the products JSON file.

This script scans the product-images folder and updates the products JSON
with actual image paths that match each product's SKU and source PDF.
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
import argparse


def normalize_pdf_name(pdf_name: str) -> str:
    """Normalize PDF names for matching (remove extension, lowercase)."""
    return Path(pdf_name).stem.lower()


def normalize_sku(sku: str) -> str:
    """Normalize SKU for matching."""
    return sku.strip().upper()


def extract_page_from_filename(filename: str) -> int | None:
    """Extract page number from filename pattern: ..._p{page}_img{idx}.ext"""
    match = re.search(r'_p(\d+)_img\d+', filename)
    if match:
        return int(match.group(1))
    return None


def extract_catalog_from_path(file_path: Path) -> str | None:
    """Extract catalog name from the parent directory structure."""
    # The parent directory is usually the PDF name
    parent = file_path.parent.name
    if parent and parent.lower().endswith('.pdf'):
        return parent[:-4]  # Remove .pdf extension
    return parent


def scan_image_folder(image_root: Path) -> Dict[tuple, List[Path]]:
    """
    Scan the image folder and create a mapping of (catalog, page) to image paths.
    
    Returns:
        Dict mapping (catalog_name, page_number) to list of image paths
    """
    print(f"Scanning image folder: {image_root}")
    
    catalog_page_to_images = defaultdict(list)
    image_extensions = {'.webp', '.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    
    total_images = 0
    matched_images = 0
    
    # Walk through all subdirectories
    for dirpath, _, filenames in os.walk(image_root):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            
            if file_path.suffix.lower() not in image_extensions:
                continue
                
            total_images += 1
            
            # Try to extract page number and catalog
            page_num = extract_page_from_filename(filename)
            catalog = extract_catalog_from_path(file_path)
            
            if page_num is not None and catalog:
                # Normalize catalog name for matching
                catalog_normalized = normalize_pdf_name(catalog)
                key = (catalog_normalized, page_num)
                catalog_page_to_images[key].append(file_path)
                matched_images += 1
    
    print(f"Found {total_images} total images")
    print(f"Matched {matched_images} images to catalog+page patterns")
    print(f"Unique (catalog, page) combinations: {len(catalog_page_to_images)}")
    
    return catalog_page_to_images


def get_relative_path(image_path: Path, json_path: Path) -> str:
    """Get relative path from JSON file to image file."""
    try:
        return os.path.relpath(image_path, json_path.parent)
    except ValueError:
        # If paths are on different drives, return absolute path
        return str(image_path)


def link_images_to_products(
    products: List[Dict],
    catalog_page_to_images: Dict[tuple, List[Path]],
    image_root: Path,
    json_path: Path,
    use_relative_paths: bool = True
) -> tuple[List[Dict], Dict]:
    """
    Update products with actual image paths based on catalog + page matching.
    
    Returns:
        Tuple of (updated_products, statistics, products_without_images)
    """
    stats = {
        'total_products': len(products),
        'products_with_images': 0,
        'products_without_images': 0,
        'total_images_linked': 0,
        'products_updated': 0,
    }
    
    products_without_images = []
    
    for idx, product in enumerate(products):
        # Progress indicator every 1000 products
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(products):,} products...", end='\r')
        sku = product.get('sku', '').strip()
        
        # Get source info from the product
        source = product.get('source', {})
        pdf_sources = source.get('pdf_sources', [])
        pages = source.get('pages', [])
        
        if not pdf_sources or not pages:
            stats['products_without_images'] += 1
            products_without_images.append({
                'sku': sku,
                'name': product.get('name', 'N/A'),
                'catalog': product.get('catalog', 'N/A'),
                'reason': 'no_source_info'
            })
            continue
        
        # Collect all matching images for this product across all source pages
        all_matching_images = []
        
        for pdf_source in pdf_sources:
            catalog_normalized = normalize_pdf_name(pdf_source)
            
            for page_num in pages:
                key = (catalog_normalized, page_num)
                images = catalog_page_to_images.get(key, [])
                all_matching_images.extend(images)
        
        if all_matching_images:
            stats['products_with_images'] += 1
            stats['total_images_linked'] += len(all_matching_images)
            stats['products_updated'] += 1
            
            # Update media section
            media_list = []
            for idx, img_path in enumerate(sorted(all_matching_images, key=lambda p: p.name)):
                if use_relative_paths:
                    path_str = get_relative_path(img_path, json_path)
                else:
                    path_str = str(img_path.absolute())
                
                # Normalize path separators for consistency
                path_str = path_str.replace('\\', '/')
                
                media_list.append({
                    'url': path_str,
                    'role': 'main' if idx == 0 else 'gallery',
                    'type': 'image',
                    'format': img_path.suffix[1:]  # Remove the dot
                })
            
            product['media'] = media_list
            
            # Add image_paths for backward compatibility
            product['image_paths'] = [m['url'] for m in media_list]
            
        else:
            stats['products_without_images'] += 1
            products_without_images.append({
                'sku': sku,
                'name': product.get('name', 'N/A'),
                'catalog': product.get('catalog', 'N/A'),
                'pdf_sources': pdf_sources,
                'pages': pages,
                'reason': 'no_matching_images'
            })
    
    # Clear progress line
    if len(products) > 0:
        print(f"  Processed {len(products):,} / {len(products):,} products... Done!")
    
    return products, stats, products_without_images


def main():
    parser = argparse.ArgumentParser(
        description='Link product images to products JSON'
    )
    parser.add_argument(
        '--json',
        default=r'c:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json',
        help='Path to products JSON file'
    )
    parser.add_argument(
        '--images',
        default=r'C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images',
        help='Path to product images folder'
    )
    parser.add_argument(
        '--output',
        help='Output JSON path (default: overwrite input)'
    )
    parser.add_argument(
        '--absolute-paths',
        action='store_true',
        help='Use absolute paths instead of relative paths'
    )
    parser.add_argument(
        '--report',
        help='Path to save missing images report (default: no report)'
    )
    
    args = parser.parse_args()
    
    json_path = Path(args.json)
    image_root = Path(args.images)
    output_path = Path(args.output) if args.output else json_path
    
    # Validate paths
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        return 1
    
    if not image_root.exists():
        print(f"Error: Image folder not found: {image_root}")
        return 1
    
    # Load products JSON
    print(f"Loading products from: {json_path}")
    print("This may take a moment for large files...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return 1
    
    if not isinstance(products, list):
        print("Error: JSON must contain a list of products")
        return 1
    
    print(f"Loaded {len(products)} products")
    
    # Scan images
    catalog_page_to_images = scan_image_folder(image_root)
    
    # Link images
    print("\nLinking images to products...")
    updated_products, stats, missing = link_images_to_products(
        products,
        catalog_page_to_images,
        image_root,
        json_path,
        use_relative_paths=not args.absolute_paths
    )
    
    # Print statistics
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Total products:              {stats['total_products']}")
    print(f"Products with images:        {stats['products_with_images']}")
    print(f"Products without images:     {stats['products_without_images']}")
    print(f"Total images linked:         {stats['total_images_linked']}")
    print(f"Products updated:            {stats['products_updated']}")
    print(f"Average images per product:  {stats['total_images_linked'] / max(stats['products_with_images'], 1):.2f}")
    print("="*60)
    
    # Save missing images report
    if args.report and missing:
        report_path = Path(args.report)
        print(f"\nSaving missing images report to: {report_path}")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(missing, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(missing)} products without images to report")
    
    # Save updated JSON
    print(f"\nSaving updated products to: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(updated_products, f, ensure_ascii=False, indent=2)
        print("Successfully saved updated products JSON")
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return 1
    
    print("\n✓ Image linking completed successfully!")
    
    return 0


if __name__ == '__main__':
    exit(main())
