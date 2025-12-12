"""
Generate Grouped Catalog JSON Files from Product_pdfs
======================================================
Creates individual catalog JSON files with grouped product structure
for each catalog page.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
SOURCE_JSON_DIR = PROJECT_ROOT / "output" / "Product_pdfs" / "json"
WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")
WEBSHOP_DATA_DIR = WEBSHOP_ROOT / "public" / "data"


def load_catalog_json(catalog_name: str) -> List[Dict]:
    """Load a catalog JSON file"""
    
    json_file = SOURCE_JSON_DIR / f"{catalog_name}.json"
    
    if not json_file.exists():
        return []
    
    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "products" in data:
        return data["products"]
    else:
        return []


def group_products_by_series(products: List[Dict], catalog_name: str) -> List[Dict]:
    """Group products by series/family"""
    
    # Group by series_id or series_name
    grouped = defaultdict(list)
    
    for product in products:
        # Determine group key
        if "series_id" in product and product["series_id"]:
            group_key = product["series_id"]
        elif "series_name" in product and product["series_name"]:
            group_key = product["series_name"].lower().replace(" ", "-")
        elif "type" in product and product["type"]:
            group_key = product["type"]
        else:
            # Use SKU prefix as fallback
            sku = product.get("sku", "")
            if len(sku) >= 3:
                group_key = sku[:3]
            else:
                group_key = sku
        
        grouped[group_key].append(product)
    
    # Convert to group structure
    product_groups = []
    
    for group_id, variants in grouped.items():
        if not variants:
            continue
        
        # Get group info from first variant
        first = variants[0]
        
        # Determine group name
        group_name = (
            first.get("series_name") or
            first.get("type", "").replace("_", " ").title() or
            group_id.replace("-", " ").replace("_", " ").title()
        )
        
        # Get image based on page number (using actual extracted image names)
        # The extracted images are named: [catalog]_page[XXX]_img00.webp
        first_page = first.get("page", 1)
        group_image = f"product-images-by-pdf/{catalog_name}/{catalog_name}_page{first_page:03d}_img00.webp"
        
        # Build variant list
        variant_list = []
        for idx, variant in enumerate(variants):
            # Try to get SKU from multiple sources
            sku = variant.get("sku")
            
            # If SKU is null/empty, try enriched data
            if not sku or sku == "null" or str(sku).lower() == "none":
                if "_enriched" in variant:
                    enriched = variant.get("_enriched", {})
                    # Try different enrichment sources
                    if "airpress" in enriched and enriched["airpress"].get("sku"):
                        sku = enriched["airpress"]["sku"]
                    elif "makita" in enriched and enriched["makita"].get("sku"):
                        sku = enriched["makita"]["sku"]
            
            # Final fallback - ensure we NEVER have null/None
            if not sku or sku == "null" or str(sku).lower() == "none":
                # Generate unique SKU from group and index
                sku = f"{group_id}_variant_{idx}"
            
            # Convert to string and ensure it's valid
            sku = str(sku).strip()
            if not sku or sku == "None":
                sku = f"{group_id}_variant_{idx}"
            
            # Build label - just use SKU for dropdown simplicity
            # All details will be shown in property badges instead
            label = str(sku)
            
            variant_data = {
                "sku": str(sku),
                "label": label,
                "page_in_pdf": variant.get("page", 1),
                "properties": {},
                "attributes": {}
            }
            
            # Add ALL relevant properties from variant
            # Skip internal/meta fields
            skip_fields = {
                "sku", "series_id", "series_name", "page", "image", "series_image", 
                "_enriched", "_meta", "confidence", "matched_image"
            }
            
            for key, value in variant.items():
                # Skip if in skip list or value is empty
                if key in skip_fields or not value or value == "":
                    continue
                
                # Add to properties
                variant_data["properties"][key] = value
            
            # Ensure these common fields are included if available
            priority_fields = ["maat", "size", "material", "materiaal", "type", "application", 
                             "pressure", "druk", "diameter", "length", "lengte", "weight", 
                             "gewicht", "capacity", "volume", "power", "voltage"]
            
            for field in priority_fields:
                if field in variant and variant[field] and field not in variant_data["properties"]:
                    variant_data["properties"][field] = variant[field]
            
            variant_list.append(variant_data)
        
        # Build media array for the component
        media = []
        if group_image:
            media.append({
                "url": group_image,
                "type": "image",
                "role": "main"
            })
        
        # Create group
        product_group = {
            "group_id": f"{catalog_name}_{group_id}",
            "name": group_name,
            "family": first.get("application") or first.get("type") or "",
            "catalog": catalog_name,
            "brand": determine_brand(catalog_name),
            "category": determine_category(catalog_name),
            "variant_count": len(variant_list),
            "variants": variant_list,
            "images": [group_image] if group_image else [],
            "media": media,
            "pdf_source": f"{catalog_name}.pdf",
            "pages": sorted(set(v.get("page", 1) for v in variants if "page" in v))
        }
        
        product_groups.append(product_group)
    
    return product_groups


def determine_brand(catalog_name: str) -> str:
    """Determine brand from catalog name"""
    if "makita" in catalog_name:
        return "Makita"
    elif "airpress" in catalog_name:
        return "Airpress"
    elif "kranzle" in catalog_name:
        return "Kränzle"
    else:
        return catalog_name.replace("-", " ").replace("_", " ").title()


def determine_category(catalog_name: str) -> str:
    """Determine category from catalog name"""
    category_map = {
        "slangkoppelingen": "Fittings & Couplings",
        "slangklemmen": "Clamps",
        "messing-draadfittingen": "Fittings & Couplings",
        "rvs-draadfittingen": "Fittings & Couplings",
        "zwarte-draad-en-lasfittingen": "Fittings & Couplings",
        "bronpompen": "Pumps",
        "dompelpompen": "Pumps",
        "centrifugaalpompen": "Pumps",
        "zuigerpompen": "Pumps",
        "pomp-specials": "Pumps",
        "digitale-versie-pompentoebehoren-compressed": "Pump Accessories",
        "rubber-slangen": "Hoses",
        "pu-afzuigslangen": "Hoses",
        "plat-oprolbare-slangen": "Hoses",
        "verzinkte-buizen": "Pipes",
        "pe-buizen": "Pipes",
        "drukbuizen": "Pipes",
        "kunststof-afvoerleidingen": "Pipes",
        "abs-persluchtbuizen": "Pipes",
        "airpress-catalogus-eng": "Air Compressors",
        "airpress-catalogus-nl-fr": "Air Compressors",
        "kranzle-catalogus-2021-nl-1": "Pressure Washers",
        "makita-catalogus-2022-nl": "Power Tools",
        "makita-tuinfolder-2022-nl": "Garden Tools",
        "catalogus-aandrijftechniek-150922": "Drive Technology",
    }
    return category_map.get(catalog_name, "General")


def save_grouped_catalog(catalog_name: str, product_groups: List[Dict]) -> None:
    """Save grouped catalog JSON"""
    
    output_file = WEBSHOP_DATA_DIR / f"{catalog_name}_grouped.json"
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(product_groups, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ {catalog_name}: {len(product_groups)} groups, {sum(g['variant_count'] for g in product_groups)} variants")


def generate_all_grouped_json() -> None:
    """Generate all grouped JSON files"""
    
    print("📦 Generating grouped catalog JSON files...")
    
    json_files = sorted(SOURCE_JSON_DIR.glob("*.json"))
    
    # Ensure output directory exists
    WEBSHOP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    catalogs_processed = 0
    total_groups = 0
    total_variants = 0
    
    for json_file in json_files:
        catalog_name = json_file.stem
        
        # Skip empty files
        if json_file.stat().st_size < 10:
            continue
        
        # Load products
        products = load_catalog_json(catalog_name)
        
        if not products:
            print(f"   ⚠️  {catalog_name}: No products found")
            continue
        
        # Group products
        product_groups = group_products_by_series(products, catalog_name)
        
        if not product_groups:
            print(f"   ⚠️  {catalog_name}: No groups created")
            continue
        
        # Save
        save_grouped_catalog(catalog_name, product_groups)
        
        catalogs_processed += 1
        total_groups += len(product_groups)
        total_variants += sum(g['variant_count'] for g in product_groups)
    
    print(f"\n✅ Generated {catalogs_processed} grouped catalog files")
    print(f"   Total groups: {total_groups}")
    print(f"   Total variants: {total_variants}")


def generate_combined_grouped_json() -> None:
    """Generate combined products_all_grouped.json for /products page"""
    
    print(f"\n📦 Generating combined grouped JSON...")
    
    all_groups = []
    json_files = sorted(SOURCE_JSON_DIR.glob("*.json"))
    
    for json_file in json_files:
        catalog_name = json_file.stem
        
        if json_file.stat().st_size < 10:
            continue
        
        products = load_catalog_json(catalog_name)
        
        if not products:
            continue
        
        product_groups = group_products_by_series(products, catalog_name)
        all_groups.extend(product_groups)
    
    # Save combined file
    output_file = WEBSHOP_DATA_DIR / "products_all_grouped.json"
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(all_groups, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Saved products_all_grouped.json")
    print(f"   Total groups: {len(all_groups)}")
    print(f"   Total variants: {sum(g['variant_count'] for g in all_groups)}")


def main():
    """Main entry point"""
    
    print("="*80)
    print("🏗️  GENERATE GROUPED CATALOG JSON FILES")
    print("="*80)
    
    # Check source directory
    if not SOURCE_JSON_DIR.exists():
        print(f"\n❌ Source directory not found: {SOURCE_JSON_DIR}")
        return
    
    # Generate individual catalog files
    generate_all_grouped_json()
    
    # Generate combined file
    generate_combined_grouped_json()
    
    print(f"\n{'='*80}")
    print("✅ ALL GROUPED JSON FILES GENERATED")
    print("="*80)
    print(f"\n📁 Output: {WEBSHOP_DATA_DIR}")
    print(f"\n💡 Catalog pages will now load data from:")
    print(f"   /data/[catalog-name]_grouped.json")
    print(f"\n🌐 Test pages:")
    print(f"   /catalog/slangkoppelingen-grouped")
    print(f"   /catalog/bronpompen-grouped")
    print(f"   /products (uses products_all_grouped.json)")
    print("="*80)


if __name__ == "__main__":
    main()
