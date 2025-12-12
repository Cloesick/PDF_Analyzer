"""
Webshop Data Quality Improvement
Improves consistency and completeness of the webshop feed data.

Improvements:
1. Generate missing descriptions (currently 58% → target 95%+)
2. Fix brand mapping (many showing "None")
3. Enrich with data from *_analysis_enriched.json files
4. Standardize category names
5. Extract more attributes
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import shutil

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")
SHOP_FEED = WEBSHOP_ROOT / "public" / "data" / "products_for_shop.json"


# Enhanced brand mappings
ENHANCED_BRAND_MAP = {
    # Catalogs with clear brands
    "makita-catalogus-2022-nl": "Makita",
    "makita-tuinfolder-2022-nl": "Makita",
    "airpress-catalogus-eng": "Airpress",
    "airpress-catalogus-nl-fr": "Airpress",
    "kranzle-catalogus-2021-nl-1": "Kränzle",
    
    # Dema product lines
    "aandrijftechniek": "Dema",
    "abs-persluchtbuizen": "Dema",
    "abs_persluchtbuizen": "Dema",
    "bronpompen": "Dema",
    "centrifugaalpompen": "Dema",
    "dompelpompen": "Dema",
    "drukbuizen": "Dema",
    "kunststof-afvoerleidingen": "Dema",
    "kunststof_afvoerleidingen": "Dema",
    "messing-draadfittingen": "Dema",
    "messing_draadfittingen": "Dema",
    "pe-buizen": "Dema",
    "pe_buizen": "Dema",
    "plat-oprolbare-slangen": "Dema",
    "plat_oprolbare": "Dema",
    "pomp-specials": "Dema",
    "pomp_specials": "Dema",
    "pompentoebehoren": "Dema",
    "pu-afzuigslangen": "Dema",
    "pu_afzuigslangen": "Dema",
    "rubber-slangen": "Dema",
    "rubber_slangen": "Dema",
    "rvs-draadfittingen": "Dema",
    "rvs_draadfittingen": "Dema",
    "slangklemmen": "Dema",
    "slangkoppelingen": "Dema",
    "verzinkte-buizen": "Dema",
    "verzinkte_buizen": "Dema",
    "zuigerpompen": "Dema",
    "zwarte-draad-en-lasfittingen": "Dema",
    "zwarte_draad_en_lasfittingen": "Dema",
    "catalogus-aandrijftechniek-150922": "Dema",
    "catalogus_aandrijftechniek": "Dema",
    "digitale-versie-pompentoebehoren-compressed": "Dema",
    "digitale_versie_pompentoebehoren_compressed": "Dema",
}

# Category standardization
CATEGORY_STANDARDS = {
    "catalogus abs persluchtbuizen": "Persluchtbuizen",
    "catalogus aandrijftechniek": "Aandrijftechniek",
    "catalogus bronpompen": "Bronpompen",
    "catalogus centrifugaalpompen": "Centrifugaalpompen",
    "catalogus dompelpompen": "Dompelpompen",
    "catalogus drukbuizen": "Drukbuizen",
    "catalogus kunststof afvoerleidingen": "Kunststof Afvoerleidingen",
    "catalogus messing draadfittingen": "Messing Draadfittingen",
    "catalogus pe buizen": "PE Buizen",
    "catalogus pomp specials": "Pomp Specials",
    "catalogus rvs draadfittingen": "RVS Draadfittingen",
    "catalogus slangklemmen": "Slangklemmen",
    "catalogus slangkoppelingen": "Slangkoppelingen",
    "catalogus verzinkte buizen": "Verzinkte Buizen",
    "makita": "Makita Gereedschap",
    "airpress": "Airpress Compressoren",
    "kranzle": "Kränzle Hogedrukreinigers",
}


def load_enriched_data() -> Dict[str, Dict]:
    """Load all enriched analysis files for reference"""
    
    print("\n📂 Loading enriched catalog data...")
    enriched = {}
    
    analysis_files = list(OUTPUT_DIR.glob("*_analysis_enriched.json"))
    
    for file in analysis_files:
        catalog = file.stem.replace("_analysis_enriched", "")
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                # Index by SKU for quick lookup
                # Handle both list and dict formats
                if isinstance(data, list):
                    enriched[catalog] = {item["sku"]: item for item in data if isinstance(item, dict) and "sku" in item}
                elif isinstance(data, dict):
                    # If it's already a dict, use it directly or extract products
                    if "products" in data:
                        enriched[catalog] = {item["sku"]: item for item in data["products"] if "sku" in item}
                    else:
                        enriched[catalog] = data
                print(f"   Loaded {len(enriched[catalog])} products from {catalog}")
        except Exception as e:
            print(f"   Error loading {file.name}: {e}")
    
    return enriched


def generate_better_description(product: Dict, enriched_data: Dict = None) -> str:
    """Generate comprehensive product description"""
    
    # Use existing if good enough
    existing = product.get("description") or ""
    existing = existing.strip() if isinstance(existing, str) else ""
    if existing and len(existing) > 80:
        return existing
    
    category = product.get("product_category", product.get("category", ""))
    sku = product.get("sku", "")
    name = product.get("name", sku)
    
    # Try to get more data from enriched source
    extra_data = {}
    if enriched_data:
        catalog = product.get("catalog", "")
        if catalog in enriched_data and sku in enriched_data[catalog]:
            extra_data = enriched_data[catalog][sku]
    
    parts = []
    
    # Start with product name if different from SKU
    if name and name.upper() != sku.upper():
        parts.append(f"{name}.")
    
    # Add category context
    if category:
        parts.append(f"Professioneel product uit de categorie {category}.")
    
    # Collect specifications
    specs = []
    
    # Try to get specs from multiple sources
    all_data = {**product, **extra_data}
    
    # Power
    power_kw = all_data.get("power_kw")
    power_hp = all_data.get("power_hp")
    if power_kw:
        specs.append(f"{power_kw} kW vermogen")
    elif power_hp:
        specs.append(f"{power_hp} HP vermogen")
    
    # Voltage
    voltage = all_data.get("voltage_v")
    if voltage:
        specs.append(f"{int(voltage)}V spanning")
    
    # Pressure
    pressure = all_data.get("pressure_max_bar") or all_data.get("pressure_bar")
    if pressure:
        specs.append(f"max. {pressure} bar druk")
    
    # Flow
    flow_m3 = all_data.get("flow_m3_hour")
    flow_lmin = all_data.get("flow_l_min")
    if flow_m3:
        specs.append(f"{flow_m3} m³/h debiet")
    elif flow_lmin:
        specs.append(f"{flow_lmin} L/min debiet")
    
    # Dimensions
    diameter = all_data.get("diameter_mm") or all_data.get("size_mm")
    length = all_data.get("length_mm")
    if diameter:
        specs.append(f"Ø {diameter}mm")
    if length:
        specs.append(f"{length}mm lengte")
    
    # Tank/Volume
    tank = all_data.get("tank_volume_l") or all_data.get("volume_l")
    if tank:
        specs.append(f"{int(tank)}L tank")
    
    # Weight
    weight = all_data.get("weight_kg")
    if weight:
        specs.append(f"{weight}kg")
    
    # Materials
    materials = all_data.get("materials")
    if materials:
        if isinstance(materials, list):
            specs.append(f"Materiaal: {', '.join(materials)}")
        else:
            specs.append(f"Materiaal: {materials}")
    
    if specs:
        parts.append("Specificaties: " + ", ".join(specs) + ".")
    
    # Add generic closing if still short
    if len(" ".join(parts)) < 50:
        parts.append("Geschikt voor professioneel gebruik.")
    
    return " ".join(parts)


def improve_product(product: Dict, enriched_data: Dict) -> Dict:
    """Improve a single product's data quality"""
    
    improved = product.copy()
    sku = product.get("sku", "")
    catalog = product.get("catalog", "")
    
    # 1. Fix brand if None or missing
    if not improved.get("brand") or improved.get("brand") == "None":
        brand = ENHANCED_BRAND_MAP.get(catalog)
        if brand:
            improved["brand"] = brand
    
    # 2. Standardize category
    category = product.get("product_category", product.get("category", ""))
    category_lower = category.lower()
    if category_lower in CATEGORY_STANDARDS:
        improved["product_category"] = CATEGORY_STANDARDS[category_lower]
        improved["category"] = CATEGORY_STANDARDS[category_lower]
    
    # 3. Generate description if missing or poor
    description = product.get("description") or ""
    description = description.strip() if isinstance(description, str) else ""
    if not description or len(description) < 50:
        improved["description"] = generate_better_description(product, enriched_data)
    
    # 4. Enrich attributes from enriched data
    if catalog in enriched_data and sku in enriched_data[catalog]:
        enriched_item = enriched_data[catalog][sku]
        
        # Add missing numeric attributes
        for attr in ["power_kw", "voltage_v", "pressure_max_bar", "flow_m3_hour", 
                     "diameter_mm", "length_mm", "weight_kg", "tank_volume_l"]:
            if attr in enriched_item and attr not in improved:
                improved[attr] = enriched_item[attr]
        
        # Add missing string attributes
        for attr in ["materials", "connection_types", "series", "product_type"]:
            if attr in enriched_item and attr not in improved:
                improved[attr] = enriched_item[attr]
    
    # 5. Ensure name is not just SKU
    name = improved.get("name", "")
    if not name or name.upper() == sku.upper():
        # Try to build better name
        product_type = improved.get("product_type", "")
        series = improved.get("series", "")
        if product_type and series:
            improved["name"] = f"{product_type} {series}"
        elif product_type:
            improved["name"] = product_type
        else:
            improved["name"] = sku
    
    return improved


def main():
    """Improve webshop feed data quality"""
    
    print("="*80)
    print("WEBSHOP DATA QUALITY IMPROVEMENT")
    print("="*80)
    
    # Load enriched catalog data
    enriched_data = load_enriched_data()
    
    # Load current shop feed
    print(f"\n📂 Loading shop feed: {SHOP_FEED.name}")
    with SHOP_FEED.open("r", encoding="utf-8") as f:
        products = json.load(f)
    
    print(f"   Loaded {len(products)} products")
    
    # Analyze current quality
    print("\n📊 Current Data Quality:")
    with_desc = sum(1 for p in products if p.get("description") and len(p["description"]) > 50)
    with_brand = sum(1 for p in products if p.get("brand") and p["brand"] != "None")
    with_images = sum(1 for p in products if p.get("media") and p["media"])
    
    print(f"   With good descriptions: {with_desc} ({with_desc/len(products)*100:.1f}%)")
    print(f"   With valid brand:       {with_brand} ({with_brand/len(products)*100:.1f}%)")
    print(f"   With images:            {with_images} ({with_images/len(products)*100:.1f}%)")
    
    # Backup current file
    backup_file = SHOP_FEED.parent / f"{SHOP_FEED.stem}_backup.json"
    shutil.copy(SHOP_FEED, backup_file)
    print(f"\n💾 Backup created: {backup_file.name}")
    
    # Improve all products
    print(f"\n🔧 Improving product data...")
    improved_products = []
    
    for i, product in enumerate(products):
        if i % 1000 == 0 and i > 0:
            print(f"   Processed {i}/{len(products)} products...")
        
        improved = improve_product(product, enriched_data)
        improved_products.append(improved)
    
    # Analyze improved quality
    print("\n📊 Improved Data Quality:")
    with_desc_new = sum(1 for p in improved_products if p.get("description") and len(p["description"]) > 50)
    with_brand_new = sum(1 for p in improved_products if p.get("brand") and p["brand"] != "None")
    
    print(f"   With good descriptions: {with_desc_new} ({with_desc_new/len(improved_products)*100:.1f}%)")
    print(f"   With valid brand:       {with_brand_new} ({with_brand_new/len(improved_products)*100:.1f}%)")
    
    # Show improvements
    print("\n📈 Improvements:")
    print(f"   Descriptions: +{with_desc_new - with_desc} ({(with_desc_new - with_desc)/len(products)*100:.1f}% increase)")
    print(f"   Brands:       +{with_brand_new - with_brand} ({(with_brand_new - with_brand)/len(products)*100:.1f}% increase)")
    
    # Save improved feed
    print(f"\n💾 Saving improved feed...")
    with SHOP_FEED.open("w", encoding="utf-8") as f:
        json.dump(improved_products, f, ensure_ascii=False, indent=2)
    
    print(f"   Saved to: {SHOP_FEED}")
    
    print("\n" + "="*80)
    print("✅ DATA QUALITY IMPROVEMENT COMPLETE")
    print("="*80)
    print(f"\n📋 Summary:")
    print(f"   Products processed:  {len(improved_products)}")
    print(f"   Description coverage: {with_desc_new/len(improved_products)*100:.1f}%")
    print(f"   Brand coverage:       {with_brand_new/len(improved_products)*100:.1f}%")
    print(f"   Backup saved:        {backup_file.name}")
    print("="*80)


if __name__ == "__main__":
    main()
