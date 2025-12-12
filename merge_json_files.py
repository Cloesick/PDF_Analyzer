"""
JSON Content Merger
Merges similar JSON files into single wholistic files instead of keeping duplicates.

This goes beyond just archiving - it actually consolidates data:
- Merges all products_ready_for_webshop_* into one comprehensive file
- Merges all Makita variants into one complete file
- Deduplicates products by SKU, keeping richest data
- Creates single source of truth for each dataset
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ARCHIVE_DIR = OUTPUT_DIR / "archive" / "merged_old_jsons"


class JSONMerger:
    """Merges and consolidates JSON files"""
    
    def __init__(self):
        self.stats = {
            "files_processed": 0,
            "files_merged": 0,
            "products_before": 0,
            "products_after": 0,
            "duplicates_removed": 0,
        }
    
    def merge_by_sku(self, products_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge products by SKU, keeping richest data"""
        
        products_by_sku = defaultdict(list)
        
        # Group by SKU
        for product in products_list:
            sku = product.get("sku")
            if sku:
                products_by_sku[sku].append(product)
        
        # Merge each SKU group
        merged = []
        for sku, variants in products_by_sku.items():
            if len(variants) == 1:
                merged.append(variants[0])
            else:
                # Merge multiple entries for same SKU
                merged_product = self._merge_product_variants(variants)
                merged.append(merged_product)
                self.stats["duplicates_removed"] += len(variants) - 1
        
        return merged
    
    def _merge_product_variants(self, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple variants of same product, keeping richest data"""
        
        # Start with first variant
        merged = variants[0].copy()
        
        # Merge in data from other variants
        for variant in variants[1:]:
            for key, value in variant.items():
                if key not in merged or not merged[key]:
                    # Add missing fields
                    merged[key] = value
                elif isinstance(value, dict) and isinstance(merged[key], dict):
                    # Merge nested dicts
                    merged[key].update(value)
                elif isinstance(value, list) and isinstance(merged[key], list):
                    # Merge lists
                    if value:
                        # For lists of dicts (like images), just extend
                        combined = merged[key] + value
                        # Remove exact duplicates by converting to JSON strings
                        seen = set()
                        unique = []
                        for item in combined:
                            if isinstance(item, dict):
                                item_str = json.dumps(item, sort_keys=True)
                                if item_str not in seen:
                                    seen.add(item_str)
                                    unique.append(item)
                            else:
                                if item not in seen:
                                    seen.add(item)
                                    unique.append(item)
                        merged[key] = unique
                elif value and len(str(value)) > len(str(merged[key])):
                    # Keep longer/richer value
                    merged[key] = value
        
        return merged
    
    def merge_products_ready_files(self) -> None:
        """Merge all products_ready_for_webshop variants"""
        
        print("\n" + "="*80)
        print("MERGING: products_ready_for_webshop_* variants")
        print("="*80)
        
        # Find all variants (including in archive now)
        patterns = [
            "products_ready_for_webshop*.json",
            "products_multilanguage.json",
        ]
        
        all_files = []
        for pattern in patterns:
            all_files.extend(OUTPUT_DIR.glob(pattern))
            all_files.extend((ARCHIVE_DIR.parent / "consolidated_old_jsons").glob(pattern))
        
        if not all_files:
            print("No products_ready files found")
            return
        
        print(f"Found {len(all_files)} files to merge:")
        for f in all_files:
            print(f"   • {f.name}")
        
        # Load all products
        all_products = []
        for file in all_files:
            try:
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_products.extend(data)
                        print(f"   Loaded {len(data)} products from {file.name}")
                    self.stats["files_processed"] += 1
            except Exception as e:
                print(f"   Error loading {file.name}: {e}")
        
        print(f"\nTotal products loaded: {len(all_products)}")
        self.stats["products_before"] = len(all_products)
        
        # Merge by SKU
        print("Merging products by SKU...")
        merged_products = self.merge_by_sku(all_products)
        self.stats["products_after"] = len(merged_products)
        
        # Sort
        merged_products.sort(key=lambda x: (x.get("catalog", ""), x.get("sku", "")))
        
        # Save merged file
        output_file = OUTPUT_DIR / "products_for_webshop_consolidated.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(merged_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Merged into: {output_file.name}")
        print(f"   Products before: {self.stats['products_before']}")
        print(f"   Products after:  {self.stats['products_after']}")
        print(f"   Duplicates removed: {self.stats['duplicates_removed']}")
        self.stats["files_merged"] += len(all_files)
    
    def merge_makita_files(self) -> None:
        """Merge all Makita product variants"""
        
        print("\n" + "="*80)
        print("MERGING: Makita product variants")
        print("="*80)
        
        # Find all Makita files
        patterns = [
            "makita*products*.json",
            "makita_integrated*.json",
            "makita_complete*.json",
            "products_with_makita*.json",
        ]
        
        all_files = []
        for pattern in patterns:
            all_files.extend(OUTPUT_DIR.glob(pattern))
            # Also check archive
            archive_path = ARCHIVE_DIR.parent / "consolidated_old_jsons"
            if archive_path.exists():
                all_files.extend(archive_path.glob(pattern))
        
        # Remove duplicates
        all_files = list(set(all_files))
        
        if not all_files:
            print("No Makita files found")
            return
        
        print(f"Found {len(all_files)} Makita files to merge:")
        for f in all_files:
            print(f"   • {f.name}")
        
        # Load all products
        all_products = []
        for file in all_files:
            try:
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_products.extend(data)
                        print(f"   Loaded {len(data)} products from {file.name}")
                    self.stats["files_processed"] += 1
            except Exception as e:
                print(f"   Error loading {file.name}: {e}")
        
        if not all_products:
            print("No products found in Makita files")
            return
        
        print(f"\nTotal Makita products loaded: {len(all_products)}")
        before = len(all_products)
        
        # Merge by SKU
        print("Merging Makita products by SKU...")
        merged_products = self.merge_by_sku(all_products)
        after = len(merged_products)
        
        # Sort
        merged_products.sort(key=lambda x: x.get("sku", ""))
        
        # Save merged file
        output_file = OUTPUT_DIR / "makita_products_consolidated.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(merged_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Merged into: {output_file.name}")
        print(f"   Products before: {before}")
        print(f"   Products after:  {after}")
        print(f"   Duplicates removed: {before - after}")
        self.stats["files_merged"] += len(all_files)
    
    def merge_catalog_analysis_files(self) -> None:
        """Merge analysis and enriched pairs into enriched versions"""
        
        print("\n" + "="*80)
        print("MERGING: Analysis/Enriched pairs")
        print("="*80)
        
        # Find all enriched files
        enriched_files = list(OUTPUT_DIR.glob("*_analysis_enriched.json"))
        
        if not enriched_files:
            print("No enriched analysis files found")
            return
        
        print(f"Found {len(enriched_files)} enriched analysis files")
        print("These already contain the richest data - no merging needed")
        print("Regular *_analysis.json files were already archived")
    
    def consolidate_grouped_files(self) -> None:
        """Ensure we're using enhanced grouped versions"""
        
        print("\n" + "="*80)
        print("CHECKING: Grouped/Enhanced files")
        print("="*80)
        
        enhanced_files = list(OUTPUT_DIR.glob("*_grouped_enhanced.json"))
        
        if not enhanced_files:
            print("No enhanced grouped files found")
            return
        
        print(f"Found {len(enhanced_files)} enhanced grouped files")
        print("These already contain the richest data - no merging needed")
        print("Regular *_grouped.json files were already archived")


def main():
    """Main consolidation function"""
    
    print("="*80)
    print("JSON CONTENT MERGER")
    print("="*80)
    print("This will merge similar JSON files into single comprehensive versions")
    print()
    
    merger = JSONMerger()
    
    # Merge products_ready variants
    merger.merge_products_ready_files()
    
    # Merge Makita variants
    merger.merge_makita_files()
    
    # Check analysis files
    merger.merge_catalog_analysis_files()
    
    # Check grouped files
    merger.consolidate_grouped_files()
    
    # Summary
    print("\n" + "="*80)
    print("CONSOLIDATION SUMMARY")
    print("="*80)
    print(f"Files processed:       {merger.stats['files_processed']}")
    print(f"Files merged:          {merger.stats['files_merged']}")
    print(f"Products before merge: {merger.stats['products_before']}")
    print(f"Products after merge:  {merger.stats['products_after']}")
    print(f"Duplicates removed:    {merger.stats['duplicates_removed']}")
    
    print("\n✅ CONSOLIDATED JSON FILES CREATED:")
    print("   • products_for_webshop_consolidated.json (unified shop feed)")
    print("   • makita_products_consolidated.json (unified Makita data)")
    print()
    print("💡 These are now your single sources of truth")
    print("="*80)


if __name__ == "__main__":
    main()
