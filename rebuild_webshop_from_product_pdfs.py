"""
Rebuild Webshop Feed from Product_pdfs JSON Files
==================================================
Generates webshop products from all JSON files in output/Product_pdfs/json/

This script:
1. Reads all catalog JSON files from Product_pdfs/json/
2. Transforms products into webshop format
3. Enriches with images, descriptions, and metadata
4. Exports to webshop's products_for_shop.json
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
SOURCE_JSON_DIR = PROJECT_ROOT / "output" / "Product_pdfs" / "json"
WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")
WEBSHOP_DATA_DIR = WEBSHOP_ROOT / "public" / "data"
OUTPUT_FILE = WEBSHOP_DATA_DIR / "products_for_shop.json"


def load_all_catalog_jsons() -> Dict[str, List[Dict]]:
    """Load all JSON files from Product_pdfs/json/"""
    
    print("📂 Loading catalog JSON files...")
    
    catalogs = {}
    json_files = sorted(SOURCE_JSON_DIR.glob("*.json"))
    
    for json_file in json_files:
        catalog_name = json_file.stem
        
        try:
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Handle different formats
                if isinstance(data, list):
                    products = data
                elif isinstance(data, dict) and "products" in data:
                    products = data["products"]
                else:
                    products = []
                
                catalogs[catalog_name] = products
                print(f"   ✓ {catalog_name}: {len(products)} products")
        
        except Exception as e:
            print(f"   ✗ {catalog_name}: Error - {e}")
    
    return catalogs


def transform_to_webshop_format(catalogs: Dict[str, List[Dict]]) -> List[Dict]:
    """Transform catalog products to webshop format"""
    
    print(f"\n🔄 Transforming products to webshop format...")
    
    webshop_products = []
    sku_seen = set()
    
    for catalog_name, products in catalogs.items():
        for product in products:
            sku = product.get("sku", "")
            
            if not sku or sku in sku_seen:
                continue
            
            sku_seen.add(sku)
            
            # Build webshop product
            webshop_product = {
                "id": sku,
                "sku": sku,
                "name": generate_product_name(product, catalog_name),
                "description": generate_description(product, catalog_name),
                "price": extract_price(product),
                "category": determine_category(catalog_name, product),
                "brand": determine_brand(catalog_name, product),
                "imageUrl": get_image_url(product, catalog_name),
                "inStock": True,
                "featured": False,
            }
            
            # Add optional fields
            if "maat" in product or "size" in product:
                webshop_product["size"] = product.get("maat") or product.get("size")
            
            # Add specs/attributes
            specs = extract_specs(product)
            if specs:
                webshop_product["specs"] = specs
            
            # Add media array
            media = build_media_array(product, catalog_name)
            if media:
                webshop_product["media"] = media
            
            # Add catalog source
            webshop_product["catalog"] = catalog_name
            webshop_product["pdf_source"] = f"{catalog_name}.pdf"
            
            if "page" in product:
                webshop_product["pages"] = [product["page"]]
            
            webshop_products.append(webshop_product)
    
    print(f"   ✓ Transformed {len(webshop_products)} unique products")
    
    return webshop_products


def generate_product_name(product: Dict, catalog: str) -> str:
    """Generate a readable product name"""
    
    # Try series_name first
    if "series_name" in product and product["series_name"]:
        name = product["series_name"]
    elif "name" in product:
        name = product["name"]
    elif "description" in product:
        name = product["description"][:100]
    else:
        # Generate from catalog and SKU
        catalog_readable = catalog.replace("-", " ").replace("_", " ").title()
        name = f"{catalog_readable} {product.get('sku', '')}"
    
    # Add size/type if available
    if "maat" in product:
        name = f"{name} - {product['maat']}"
    elif "type" in product and product.get("type"):
        type_str = str(product["type"]).replace("_", " ").title()
        if type_str.lower() not in name.lower():
            name = f"{name} - {type_str}"
    
    return name.strip()


def generate_description(product: Dict, catalog: str) -> str:
    """Generate product description"""
    
    # Use existing description if available
    if "description" in product and product["description"]:
        return product["description"]
    
    # Build description from available fields
    parts = []
    
    if "series_name" in product:
        parts.append(product["series_name"])
    
    if "application" in product:
        parts.append(f"Application: {product['application']}")
    
    if "material" in product:
        parts.append(f"Material: {product['material']}")
    
    if "maat" in product:
        parts.append(f"Size: {product['maat']}")
    
    # Add specs
    for key, value in product.items():
        if key.startswith("col_") and value:
            parts.append(str(value))
    
    if not parts:
        parts.append(f"Product from {catalog.replace('-', ' ').title()}")
    
    return " | ".join(parts)


def extract_price(product: Dict) -> float:
    """Extract price from product data"""
    
    # Look for price fields
    price_fields = ["price", "prijs", "cost", "kosten"]
    
    for field in price_fields:
        if field in product:
            try:
                price_str = str(product[field]).replace("€", "").replace(",", ".").strip()
                return float(price_str)
            except:
                continue
    
    # Default price if not found
    return 0.0


def determine_category(catalog: str, product: Dict) -> str:
    """Determine product category"""
    
    # Category mapping based on catalog
    category_map = {
        "slangkoppelingen": "Fittings & Couplings",
        "messing-draadfittingen": "Fittings & Couplings",
        "rvs-draadfittingen": "Fittings & Couplings",
        "zwarte-draad-en-lasfittingen": "Fittings & Couplings",
        "bronpompen": "Pumps",
        "dompelpompen": "Pumps",
        "centrifugaalpompen": "Pumps",
        "zuigerpompen": "Pumps",
        "digitale-versie-pompentoebehoren-compressed": "Pump Accessories",
        "pomp-specials": "Pumps",
        "airpress-catalogus-eng": "Air Compressors",
        "airpress-catalogus-nl-fr": "Air Compressors",
        "kranzle-catalogus-2021-nl-1": "Pressure Washers",
        "makita-catalogus-2022-nl": "Power Tools",
        "makita-tuinfolder-2022-nl": "Garden Tools",
        "catalogus-aandrijftechniek-150922": "Drive Technology",
        "rubber-slangen": "Hoses",
        "pu-afzuigslangen": "Hoses",
        "plat-oprolbare-slangen": "Hoses",
        "abs-persluchtbuizen": "Pipes",
        "verzinkte-buizen": "Pipes",
        "pe-buizen": "Pipes",
        "drukbuizen": "Pipes",
        "kunststof-afvoerleidingen": "Pipes",
        "slangklemmen": "Clamps",
    }
    
    # Get category from map
    category = category_map.get(catalog, "General")
    
    # Check product type for more specific category
    if "type" in product:
        prod_type = str(product["type"]).lower()
        if "pomp" in prod_type or "pump" in prod_type:
            category = "Pumps"
        elif "slang" in prod_type or "hose" in prod_type:
            category = "Hoses"
        elif "fitting" in prod_type or "koppeling" in prod_type:
            category = "Fittings & Couplings"
    
    return category


def determine_brand(catalog: str, product: Dict) -> str:
    """Determine product brand"""
    
    # Brand mapping
    if "makita" in catalog:
        return "Makita"
    elif "airpress" in catalog:
        return "Airpress"
    elif "kranzle" in catalog or "kränzle" in catalog:
        return "Kränzle"
    elif "brand" in product:
        return product["brand"]
    else:
        # Generic brand based on catalog
        return catalog.replace("-", " ").replace("_", " ").title()


def get_image_url(product: Dict, catalog: str) -> str:
    """Get image URL for product"""
    
    # Check for existing image fields
    if "image" in product and product["image"]:
        img = product["image"]
        # Clean path - remove 'images/' prefix if present
        if img.startswith("images/"):
            img = img[7:]  # Remove "images/" prefix
        return f"/product-images-by-pdf/{img}"
    
    if "series_image" in product and product["series_image"]:
        img = product["series_image"]
        # Clean path - remove 'images/' prefix if present
        if img.startswith("images/"):
            img = img[7:]  # Remove "images/" prefix
        return f"/product-images-by-pdf/{img}"
    
    # Generate from page if available
    if "page" in product:
        page = product["page"]
        return f"/product-images-by-pdf/{catalog}/{catalog}_page{page:03d}_img00.webp"
    
    # Fallback
    return "/images/placeholder.jpg"


def build_media_array(product: Dict, catalog: str) -> List[Dict]:
    """Build media array for product"""
    
    media = []
    
    # Main image
    main_url = get_image_url(product, catalog)
    media.append({
        "url": main_url,
        "type": "image",
        "role": "main",
        "format": "webp"
    })
    
    # Series image if different
    if "series_image" in product and product["series_image"]:
        series_url = get_image_url({"image": product["series_image"]}, catalog)
        if series_url != main_url:
            media.append({
                "url": series_url,
                "type": "image",
                "role": "gallery",
                "format": "webp"
            })
    
    return media


def extract_specs(product: Dict) -> List[Dict]:
    """Extract specifications from product"""
    
    specs = []
    
    # Common spec fields
    spec_fields = {
        "maat": "Size",
        "size": "Size",
        "material": "Material",
        "materiaal": "Material",
        "type": "Type",
        "application": "Application",
        "toepassing": "Application",
        "pressure": "Pressure",
        "druk": "Pressure",
        "diameter": "Diameter",
        "lengte": "Length",
        "length": "Length",
    }
    
    for field, label in spec_fields.items():
        if field in product and product[field]:
            specs.append({
                "label": label,
                "value": str(product[field])
            })
    
    # Add col_ fields
    for key, value in product.items():
        if key.startswith("col_") and value and key != "col_0":
            specs.append({
                "label": key.replace("col_", "Spec "),
                "value": str(value)
            })
    
    return specs


def save_webshop_feed(products: List[Dict]) -> None:
    """Save products to webshop feed"""
    
    print(f"\n💾 Saving webshop feed...")
    
    # Ensure directory exists
    WEBSHOP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Backup existing file
    if OUTPUT_FILE.exists():
        backup_file = OUTPUT_FILE.parent / f"{OUTPUT_FILE.stem}_backup.json"
        import shutil
        shutil.copy(OUTPUT_FILE, backup_file)
        print(f"   ✓ Backup created: {backup_file.name}")
    
    # Save new file
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ Saved to: {OUTPUT_FILE}")


def print_statistics(products: List[Dict]) -> None:
    """Print statistics about generated products"""
    
    print(f"\n{'='*80}")
    print("📊 WEBSHOP GENERATION STATISTICS")
    print("="*80)
    
    print(f"\n🔢 Total Products: {len(products)}")
    
    # By category
    categories = defaultdict(int)
    for p in products:
        categories[p.get("category", "Unknown")] += 1
    
    print(f"\n📁 By Category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat:30} {count:>5} products")
    
    # By brand
    brands = defaultdict(int)
    for p in products:
        brands[p.get("brand", "Unknown")] += 1
    
    print(f"\n🏷️  By Brand:")
    for brand, count in sorted(brands.items(), key=lambda x: -x[1])[:10]:
        print(f"   {brand:30} {count:>5} products")
    
    # With images
    with_images = sum(1 for p in products if p.get("imageUrl") and "placeholder" not in p["imageUrl"])
    print(f"\n📸 Products with images: {with_images} ({with_images/len(products)*100:.1f}%)")
    
    # With descriptions
    with_desc = sum(1 for p in products if p.get("description") and len(p["description"]) > 20)
    print(f"📝 Products with descriptions: {with_desc} ({with_desc/len(products)*100:.1f}%)")
    
    # With prices
    with_price = sum(1 for p in products if p.get("price", 0) > 0)
    print(f"💰 Products with prices: {with_price} ({with_price/len(products)*100:.1f}%)")
    
    print(f"\n{'='*80}")


def main():
    """Main entry point"""
    
    print("="*80)
    print("🏪 REBUILD WEBSHOP FROM PRODUCT_PDFS JSON")
    print("="*80)
    
    # Load all catalogs
    catalogs = load_all_catalog_jsons()
    
    if not catalogs:
        print("\n❌ No JSON files found!")
        return
    
    # Transform to webshop format
    products = transform_to_webshop_format(catalogs)
    
    if not products:
        print("\n❌ No products generated!")
        return
    
    # Save
    save_webshop_feed(products)
    
    # Statistics
    print_statistics(products)
    
    print(f"\n✅ WEBSHOP FEED REBUILT SUCCESSFULLY!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print("="*80)


if __name__ == "__main__":
    main()
