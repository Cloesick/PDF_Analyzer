"""
Analyze products JSON for data quality, completeness, and statistics.

This script provides insights into your product data without loading
the entire JSON into memory at once (streaming analysis).
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Iterator, Dict, Any
import argparse


def stream_products(json_path: Path) -> Iterator[Dict[str, Any]]:
    """Stream products from JSON file one at a time to avoid memory issues."""
    with open(json_path, 'r', encoding='utf-8') as f:
        # Skip opening bracket
        f.read(1)
        
        decoder = json.JSONDecoder()
        buffer = ''
        depth = 0
        in_string = False
        escape = False
        
        for line in f:
            for char in line:
                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                    elif char == '"':
                        in_string = True
                else:
                    if escape:
                        escape = False
                    elif char == '\\':
                        escape = True
                    elif char == '"':
                        in_string = False
                
                buffer += char
                
                # When we've closed a product object at depth 0
                if depth == 0 and char == '}' and buffer.strip().startswith('{'):
                    try:
                        product = decoder.decode(buffer.strip())
                        yield product
                        buffer = ''
                    except json.JSONDecodeError:
                        # Continue building buffer
                        pass


def analyze_products_streaming(json_path: Path) -> Dict[str, Any]:
    """Analyze products with streaming to handle large files."""
    
    stats = {
        'total_products': 0,
        'with_images': 0,
        'with_description': 0,
        'with_brand': 0,
        'with_price': 0,
        'catalogs': Counter(),
        'categories': Counter(),
        'brands': Counter(),
        'media_formats': Counter(),
        'avg_images_per_product': 0,
        'attribute_coverage': defaultdict(int),
        'missing_data': defaultdict(list),
    }
    
    total_images = 0
    sample_products = []
    
    print(f"Analyzing: {json_path}")
    print("Streaming products (this works for large files)...\n")
    
    for idx, product in enumerate(stream_products(json_path)):
        stats['total_products'] += 1
        
        # Track catalog distribution
        catalog = product.get('catalog')
        if catalog:
            stats['catalogs'][catalog] += 1
        
        # Track category distribution
        category = product.get('category')
        if category:
            stats['categories'][category] += 1
        
        # Track brand distribution
        brand = product.get('brand')
        if brand:
            stats['brands'][brand] += 1
            stats['with_brand'] += 1
        else:
            if len(stats['missing_data']['no_brand']) < 10:
                stats['missing_data']['no_brand'].append(product.get('sku', 'unknown'))
        
        # Track description
        if product.get('description'):
            stats['with_description'] += 1
        else:
            if len(stats['missing_data']['no_description']) < 10:
                stats['missing_data']['no_description'].append(product.get('sku', 'unknown'))
        
        # Track images
        media = product.get('media', [])
        if media and len(media) > 0:
            stats['with_images'] += 1
            total_images += len(media)
            
            # Track media formats
            for m in media:
                fmt = m.get('format', 'unknown')
                stats['media_formats'][fmt] += 1
        else:
            if len(stats['missing_data']['no_images']) < 10:
                stats['missing_data']['no_images'].append(product.get('sku', 'unknown'))
        
        # Track price
        price = product.get('price', {})
        if price.get('amount'):
            stats['with_price'] += 1
        
        # Track attribute coverage
        attributes = product.get('attributes', {})
        for key in attributes:
            if attributes[key] is not None:
                stats['attribute_coverage'][key] += 1
        
        # Collect samples
        if len(sample_products) < 5:
            sample_products.append({
                'sku': product.get('sku'),
                'name': product.get('name'),
                'catalog': catalog,
                'has_image': len(media) > 0,
                'has_description': bool(product.get('description')),
            })
        
        # Progress indicator
        if (idx + 1) % 1000 == 0:
            print(f"Processed {idx + 1} products...", end='\r')
    
    print(f"\nProcessed {stats['total_products']} products\n")
    
    # Calculate averages
    if stats['with_images'] > 0:
        stats['avg_images_per_product'] = total_images / stats['with_images']
    
    return stats, sample_products


def print_report(stats: Dict[str, Any], sample_products: list):
    """Print a formatted analysis report."""
    
    total = stats['total_products']
    
    print("="*70)
    print("PRODUCT DATA ANALYSIS REPORT")
    print("="*70)
    
    print(f"\n📊 OVERVIEW")
    print(f"   Total products:          {total:,}")
    print(f"   With images:             {stats['with_images']:,} ({stats['with_images']/total*100:.1f}%)")
    print(f"   With description:        {stats['with_description']:,} ({stats['with_description']/total*100:.1f}%)")
    print(f"   With brand:              {stats['with_brand']:,} ({stats['with_brand']/total*100:.1f}%)")
    print(f"   With price:              {stats['with_price']:,} ({stats['with_price']/total*100:.1f}%)")
    print(f"   Avg images/product:      {stats['avg_images_per_product']:.2f}")
    
    print(f"\n📁 CATALOGS ({len(stats['catalogs'])} unique)")
    for catalog, count in stats['catalogs'].most_common(10):
        print(f"   {catalog[:50]:<50} {count:>5} ({count/total*100:>5.1f}%)")
    
    if len(stats['catalogs']) > 10:
        print(f"   ... and {len(stats['catalogs']) - 10} more")
    
    print(f"\n🏷️  CATEGORIES ({len(stats['categories'])} unique)")
    for category, count in stats['categories'].most_common(10):
        print(f"   {category[:50]:<50} {count:>5} ({count/total*100:>5.1f}%)")
    
    if len(stats['categories']) > 10:
        print(f"   ... and {len(stats['categories']) - 10} more")
    
    if stats['brands']:
        print(f"\n🏢 BRANDS ({len(stats['brands'])} unique)")
        for brand, count in stats['brands'].most_common(10):
            print(f"   {brand[:50]:<50} {count:>5} ({count/total*100:>5.1f}%)")
        
        if len(stats['brands']) > 10:
            print(f"   ... and {len(stats['brands']) - 10} more")
    
    if stats['media_formats']:
        print(f"\n🖼️  IMAGE FORMATS")
        for fmt, count in stats['media_formats'].most_common():
            print(f"   {fmt:<20} {count:>8} images")
    
    if stats['attribute_coverage']:
        print(f"\n📋 ATTRIBUTE COVERAGE (top 10)")
        for attr, count in sorted(stats['attribute_coverage'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {attr[:50]:<50} {count:>5} ({count/total*100:>5.1f}%)")
    
    print(f"\n⚠️  MISSING DATA EXAMPLES")
    for issue, skus in stats['missing_data'].items():
        if skus:
            print(f"   {issue}:")
            for sku in skus[:5]:
                print(f"      - {sku}")
    
    print(f"\n📝 SAMPLE PRODUCTS")
    for p in sample_products[:5]:
        print(f"   SKU: {p['sku']}")
        print(f"      Name: {p['name']}")
        print(f"      Catalog: {p['catalog']}")
        print(f"      Has image: {'✓' if p['has_image'] else '✗'}")
        print(f"      Has description: {'✓' if p['has_description'] else '✗'}")
        print()
    
    print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze products JSON for quality and statistics'
    )
    parser.add_argument(
        'json_path',
        nargs='?',
        default=r'c:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json',
        help='Path to products JSON file'
    )
    parser.add_argument(
        '--export-stats',
        help='Export statistics to JSON file'
    )
    
    args = parser.parse_args()
    
    json_path = Path(args.json_path)
    
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        return 1
    
    try:
        stats, samples = analyze_products_streaming(json_path)
        print_report(stats, samples)
        
        if args.export_stats:
            export_path = Path(args.export_stats)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'statistics': {k: dict(v) if isinstance(v, (Counter, defaultdict)) else v 
                                   for k, v in stats.items()},
                    'sample_products': samples
                }, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Statistics exported to: {export_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error analyzing JSON: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
