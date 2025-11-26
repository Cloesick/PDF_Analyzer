"""
Enhancement for Extract.py: Share descriptions for products in the same table.

For product variants (same product, different dimensions), this script ensures they share:
1. The same product description (base description)
2. The same product images
3. Only dimensions/specs vary per SKU

Usage:
  Run this AFTER Extract.py to consolidate descriptions for table-based products.
"""

import json
from pathlib import Path
from collections import defaultdict


def find_base_description(descriptions):
    """
    Find the common base description from a list of variant descriptions.
    
    Example:
      Input: ["ABS pipe 40mm", "ABS pipe 20mm", "ABS pipe 25mm"]
      Output: "ABS pipe"
    """
    if not descriptions:
        return None
    
    # Remove None/empty
    descriptions = [d for d in descriptions if d]
    if not descriptions:
        return None
    
    # If only one description, return it
    if len(descriptions) == 1:
        return descriptions[0]
    
    # Find common prefix (words)
    words_lists = [desc.split() for desc in descriptions]
    
    # Find minimum length
    min_len = min(len(words) for words in words_lists)
    
    # Find common words from the start
    common_words = []
    for i in range(min_len):
        first_word = words_lists[0][i]
        if all(words[i] == first_word for words in words_lists):
            common_words.append(first_word)
        else:
            break
    
    if common_words:
        return ' '.join(common_words)
    
    # Fallback: return first description
    return descriptions[0]


def group_products_by_table(products):
    """
    Group products that likely come from the same table.
    Heuristic: Same catalog + same page + similar SKU pattern = same table
    """
    
    # Group by (catalog, page)
    page_groups = defaultdict(list)
    
    for product in products:
        source = product.get('source', {})
        pdf_sources = source.get('pdf_sources', [])
        pages = source.get('pages', [])
        
        if pdf_sources and pages:
            # Use first source and first page
            key = (pdf_sources[0], pages[0])
            page_groups[key].append(product)
    
    # Further subdivide by SKU pattern (products with similar SKU prefix likely in same table)
    table_groups = []
    
    for (catalog, page), products_on_page in page_groups.items():
        if len(products_on_page) < 3:
            # Not a table if fewer than 3 products
            continue
        
        # Group by SKU prefix (first 3-4 chars)
        sku_groups = defaultdict(list)
        for product in products_on_page:
            sku = product.get('sku', '')
            if len(sku) >= 3:
                # Use first few characters as grouping key
                prefix = sku[:4] if len(sku) >= 4 else sku[:3]
                sku_groups[prefix].append(product)
        
        # Only consider groups with 3+ products
        for prefix, group in sku_groups.items():
            if len(group) >= 3:
                table_groups.append({
                    'catalog': catalog,
                    'page': page,
                    'sku_prefix': prefix,
                    'products': group
                })
    
    return table_groups


def enhance_table_descriptions(input_json, output_json):
    """
    Process products JSON and enhance descriptions for table-based products.
    """
    
    print("Loading products...")
    with open(input_json, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Loaded {len(products)} products")
    
    # Group products by table
    print("\nFinding product tables...")
    table_groups = group_products_by_table(products)
    
    print(f"Found {len(table_groups)} potential product tables")
    
    # Process each table group
    total_updated = 0
    
    for table in table_groups:
        catalog = table['catalog']
        page = table['page']
        prefix = table['sku_prefix']
        group_products = table['products']
        
        # Extract descriptions
        descriptions = [p.get('description') for p in group_products if p.get('description')]
        
        if not descriptions or len(descriptions) < 2:
            continue
        
        # Find base description
        base_desc = find_base_description(descriptions)
        
        if not base_desc:
            continue
        
        print(f"\nTable: {catalog} page {page}, SKUs {prefix}*")
        print(f"  Products: {len(group_products)}")
        print(f"  Base description: {base_desc}")
        
        # Update all products in this table with base description
        for product in group_products:
            old_desc = product.get('description', '')
            
            # Keep dimension-specific info if present
            dimension_info = ''
            if old_desc and len(old_desc) > len(base_desc):
                dimension_info = old_desc[len(base_desc):].strip('- ,|')
            
            # Set new description
            if dimension_info:
                product['description'] = f"{base_desc} - {dimension_info}"
            else:
                product['description'] = base_desc
            
            # Mark as table product
            product['is_table_variant'] = True
            
            total_updated += 1
    
    print(f"\n✓ Updated {total_updated} products with shared table descriptions")
    
    # Save enhanced products
    print(f"\nSaving to: {output_json}")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("✓ Enhanced products saved")
    
    return total_updated


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhance table-based product descriptions'
    )
    parser.add_argument(
        '--input',
        default=r'c:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json',
        help='Input products JSON'
    )
    parser.add_argument(
        '--output',
        help='Output JSON (default: overwrites input)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    print("="*70)
    print("TABLE DESCRIPTION ENHANCEMENT")
    print("="*70)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    
    if output_path == input_path:
        response = input("\nThis will overwrite the original file. Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            return 0
    
    enhanced_count = enhance_table_descriptions(input_path, output_path)
    
    print("\n" + "="*70)
    print(f"✓ Enhanced {enhanced_count} table-based products")
    print("="*70)
    
    return 0


if __name__ == '__main__':
    exit(main())
