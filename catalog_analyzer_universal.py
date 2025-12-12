"""
Universal Catalog Analyzer
Replaces 28+ catalog-specific analyze_* scripts with one configurable analyzer.

This script can analyze any catalog's extraction data and generate reports.
Replaces:
- analyze_aandrijftechniek.py
- analyze_abs_persluchtbuizen.py
- analyze_bronpompen.py
- analyze_centrifugaalpompen.py
- analyze_dompelpompen.py
- analyze_drukbuizen.py
- ... and 20+ more similar scripts

Usage:
    python catalog_analyzer_universal.py <catalog_name>
    python catalog_analyzer_universal.py abs-persluchtbuizen
    python catalog_analyzer_universal.py --all  # Analyze all catalogs
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict
import sys

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"


class CatalogAnalyzer:
    """Universal analyzer for any catalog"""
    
    def __init__(self, catalog_name: str):
        self.catalog_name = catalog_name
        self.analysis_file = OUTPUT_DIR / f"{catalog_name}_analysis.json"
        self.report = {
            "catalog": catalog_name,
            "total_products": 0,
            "products_with_images": 0,
            "products_with_specs": 0,
            "products_with_prices": 0,
            "unique_skus": 0,
            "pages_covered": [],
            "attribute_coverage": {},
            "brand_distribution": {},
            "issues": [],
            "recommendations": [],
        }
    
    def load_data(self) -> List[Dict[str, Any]]:
        """Load catalog data from JSON"""
        
        # Try multiple possible file locations
        possible_files = [
            self.analysis_file,
            OUTPUT_DIR / f"{self.catalog_name}_analysis_enriched.json",
            OUTPUT_DIR / f"{self.catalog_name}_smart_extracted.json",
            OUTPUT_DIR / f"{self.catalog_name}_grouped.json",
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                print(f"📂 Loading: {file_path.name}")
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Handle different data structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Might be grouped data
                    if "variants" in data:
                        return data.get("variants", [])
                    # Or a single product
                    return [data]
                
                return data
        
        print(f"❌ No data found for catalog: {self.catalog_name}")
        return []
    
    def analyze_products(self, products: List[Dict[str, Any]]) -> None:
        """Analyze product data and generate statistics"""
        
        if not products:
            self.report["issues"].append("No products found in catalog")
            return
        
        self.report["total_products"] = len(products)
        
        # Track various metrics
        skus = set()
        pages = set()
        brands = defaultdict(int)
        attribute_counts = defaultdict(int)
        
        for product in products:
            # SKU
            sku = product.get("sku")
            if sku:
                skus.add(sku)
            else:
                self.report["issues"].append(f"Product missing SKU: {product.get('id', 'unknown')}")
            
            # Images
            images = product.get("images") or product.get("media") or product.get("image_paths")
            if images and len(images) > 0:
                self.report["products_with_images"] += 1
            
            # Specs/Attributes
            specs = product.get("specs") or product.get("attributes")
            if specs:
                self.report["products_with_specs"] += 1
                
                # Count individual attributes
                if isinstance(specs, dict):
                    for key in specs.keys():
                        attribute_counts[key] += 1
                elif isinstance(specs, list):
                    for spec in specs:
                        if isinstance(spec, dict):
                            key = spec.get("key") or spec.get("label")
                            if key:
                                attribute_counts[key] += 1
            
            # Price
            price = product.get("price") or product.get("price_eur")
            if price:
                self.report["products_with_prices"] += 1
            
            # Pages
            page = product.get("page_in_pdf") or product.get("merged_pdf_page")
            if page:
                if isinstance(page, list):
                    pages.update(page)
                else:
                    pages.add(page)
            
            # Brand
            brand = product.get("brand")
            if brand:
                brands[brand] += 1
        
        self.report["unique_skus"] = len(skus)
        self.report["pages_covered"] = sorted(pages)
        self.report["brand_distribution"] = dict(brands)
        
        # Calculate attribute coverage percentages
        total = len(products)
        self.report["attribute_coverage"] = {
            attr: {
                "count": count,
                "percentage": round(count / total * 100, 1)
            }
            for attr, count in sorted(attribute_counts.items(), key=lambda x: x[1], reverse=True)
        }
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _generate_recommendations(self) -> None:
        """Generate recommendations based on analysis"""
        
        total = self.report["total_products"]
        if total == 0:
            return
        
        # Image coverage
        img_pct = (self.report["products_with_images"] / total) * 100
        if img_pct < 50:
            self.report["recommendations"].append(
                f"⚠️  Low image coverage ({img_pct:.1f}%) - Consider running image extraction"
            )
        elif img_pct < 80:
            self.report["recommendations"].append(
                f"📸 Moderate image coverage ({img_pct:.1f}%) - Some products need images"
            )
        
        # Specs coverage
        spec_pct = (self.report["products_with_specs"] / total) * 100
        if spec_pct < 50:
            self.report["recommendations"].append(
                f"⚠️  Low spec coverage ({spec_pct:.1f}%) - Consider enriching product data"
            )
        
        # Price coverage
        price_pct = (self.report["products_with_prices"] / total) * 100
        if price_pct < 10:
            self.report["recommendations"].append(
                f"💰 Very few products have prices ({price_pct:.1f}%) - Prices may need to be added manually"
            )
        
        # Missing SKUs
        if self.report["unique_skus"] < total:
            missing = total - self.report["unique_skus"]
            self.report["recommendations"].append(
                f"⚠️  {missing} products have missing or duplicate SKUs"
            )
    
    def print_report(self) -> None:
        """Print formatted analysis report"""
        
        print("\n" + "=" * 80)
        print(f"CATALOG ANALYSIS: {self.catalog_name}")
        print("=" * 80)
        
        print(f"\n📊 OVERVIEW")
        print(f"   Total products:         {self.report['total_products']}")
        print(f"   Unique SKUs:            {self.report['unique_skus']}")
        print(f"   Pages covered:          {len(self.report['pages_covered'])}")
        
        if self.report["brand_distribution"]:
            print(f"\n🏷️  BRANDS")
            for brand, count in sorted(self.report["brand_distribution"].items(), key=lambda x: x[1], reverse=True):
                print(f"   {brand}: {count} products")
        
        total = self.report["total_products"]
        if total > 0:
            print(f"\n📈 COVERAGE")
            img_pct = (self.report["products_with_images"] / total) * 100
            spec_pct = (self.report["products_with_specs"] / total) * 100
            price_pct = (self.report["products_with_prices"] / total) * 100
            
            print(f"   With images:            {self.report['products_with_images']} ({img_pct:.1f}%)")
            print(f"   With specifications:    {self.report['products_with_specs']} ({spec_pct:.1f}%)")
            print(f"   With prices:            {self.report['products_with_prices']} ({price_pct:.1f}%)")
        
        if self.report["attribute_coverage"]:
            print(f"\n🔍 TOP ATTRIBUTES (coverage)")
            top_attrs = list(self.report["attribute_coverage"].items())[:10]
            for attr, data in top_attrs:
                print(f"   {attr:25} {data['count']:4} products ({data['percentage']:5.1f}%)")
        
        if self.report["issues"]:
            print(f"\n⚠️  ISSUES ({len(self.report['issues'])})")
            for issue in self.report["issues"][:5]:
                print(f"   • {issue}")
            if len(self.report["issues"]) > 5:
                print(f"   ... and {len(self.report['issues']) - 5} more")
        
        if self.report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS")
            for rec in self.report["recommendations"]:
                print(f"   {rec}")
        
        print("\n" + "=" * 80)
    
    def save_report(self) -> None:
        """Save report to JSON"""
        report_file = OUTPUT_DIR / f"{self.catalog_name}_analysis_report.json"
        with report_file.open("w", encoding="utf-8") as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Report saved: {report_file.name}")
    
    def run(self) -> None:
        """Run complete analysis"""
        products = self.load_data()
        if products:
            self.analyze_products(products)
            self.print_report()
            self.save_report()
        else:
            print(f"❌ Could not analyze {self.catalog_name} - no data found")


def analyze_all_catalogs() -> None:
    """Analyze all available catalogs"""
    
    print("=" * 80)
    print("ANALYZING ALL CATALOGS")
    print("=" * 80)
    
    # Find all catalog files
    catalog_files = []
    for pattern in ["*_analysis.json", "*_smart_extracted.json", "*_grouped.json"]:
        catalog_files.extend(OUTPUT_DIR.glob(pattern))
    
    # Extract unique catalog names
    catalog_names = set()
    for file in catalog_files:
        name = file.stem
        # Remove suffixes
        for suffix in ["_analysis", "_analysis_enriched", "_smart_extracted", "_grouped", "_grouped_enhanced"]:
            name = name.replace(suffix, "")
        catalog_names.add(name)
    
    print(f"\nFound {len(catalog_names)} catalogs to analyze\n")
    
    # Analyze each
    for catalog_name in sorted(catalog_names):
        try:
            analyzer = CatalogAnalyzer(catalog_name)
            analyzer.run()
        except Exception as e:
            print(f"❌ Error analyzing {catalog_name}: {e}")
        
        print("\n")


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("   python catalog_analyzer_universal.py <catalog_name>")
        print("   python catalog_analyzer_universal.py abs-persluchtbuizen")
        print("   python catalog_analyzer_universal.py --all")
        print("\nAvailable catalogs:")
        
        # List available catalogs
        catalog_files = list(OUTPUT_DIR.glob("*_analysis.json"))
        for file in sorted(catalog_files):
            catalog = file.stem.replace("_analysis", "")
            print(f"   • {catalog}")
        
        return
    
    catalog_arg = sys.argv[1]
    
    if catalog_arg == "--all":
        analyze_all_catalogs()
    else:
        analyzer = CatalogAnalyzer(catalog_arg)
        analyzer.run()


if __name__ == "__main__":
    main()
