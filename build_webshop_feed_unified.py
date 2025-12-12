"""
Unified Webshop Feed Builder
Consolidates all shop feed building functionality into one configurable script:
- Builds from raw extraction data
- Links images and enriches products
- Supports product groups and variants
- Generates complete webshop-ready JSON

This replaces:
- build_shop_feed.py
- build_shop_feed_with_groups.py
- build_complete_webshop_feed.py
- build_enriched_webshop_feed.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")

# Configuration
class Config:
    # Input files
    # Use the comprehensive version from archive (has complete enriched data)
    RAW_EXTRACTION = OUTPUT_DIR / "archive" / "consolidated_old_jsons" / "products_ready_for_webshop_v2_comprehensive.json"
    GROUPED_PRODUCTS = OUTPUT_DIR / "abs_persluchtbuizen_grouped.json"
    
    # Output
    SHOP_FEED = WEBSHOP_ROOT / "public" / "data" / "products_for_shop.json"
    
    # Options
    INCLUDE_GROUPS = True
    GENERATE_DESCRIPTIONS = True
    FIX_IMAGE_URLS = True
    
    # Base media URL (for legacy support)
    BASE_MEDIA_URL = "https://example.com/media/"


# Catalog mappings
CATALOG_CATEGORIES = {
    "abs-persluchtbuizen": "Persluchtbuizen",
    "airpress-catalogus-eng": "Compressoren & Accessoires",
    "airpress-catalogus-nl-fr": "Compressoren & Accessoires",
    "bronpompen": "Bronpompen",
    "catalogus-aandrijftechniek": "Aandrijftechniek",
    "centrifugaalpompen": "Centrifugaalpompen",
    "dompelpompen": "Dompelpompen",
    "drukbuizen": "Drukbuizen",
    "gardena-assortiment": "Tuinartikelen",
    "hogedrukreiniger": "Hogedrukreinigers",
    "industrile-slangen": "Industriële Slangen",
    "kranzle-catalogus": "Hogedrukreinigers Kränzle",
    "kunststof-afvoerleidingen": "Kunststof Afvoerleidingen",
    "makita-catalogus-2022-nl": "Elektrisch Gereedschap Makita",
    "makita-tuinfolder-2022-nl": "Tuingereedschap Makita",
    "messing-draadfittingen": "Messing Fittingen",
    "pe-buizen": "PE Buizen & Hulpstukken",
    "plat-oprolbare-slangen": "Plat Oprolbare Slangen",
    "pomp-specials": "Pomp Specials",
    "pu-afzuigslangen": "PU Afzuigslangen",
    "rvs-draadfittingen": "RVS Fittingen",
    "slangklemmen": "Slangklemmen",
    "slangkoppelingen": "Slangkoppelingen",
    "verzinkte-buizen": "Verzinkte Buizen",
    "zwarte-draad-en-lasfittingen": "Zwarte Draad- & Lasfittingen",
}

CATALOG_BRANDS = {
    "airpress-catalogus-eng": "Airpress",
    "airpress-catalogus-nl-fr": "Airpress",
    "kranzle-catalogus": "Kränzle",
    "makita-catalogus-2022-nl": "Makita",
    "makita-tuinfolder-2022-nl": "Makita",
    "gardena-assortiment": "Gardena",
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_float(val: Any) -> Optional[float]:
    """Safely convert any value to float"""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            cleaned = val.replace(",", ".").split()[0]
            return float(cleaned)
        except (ValueError, IndexError):
            return None
    return None


def safe_list(val: Any) -> Optional[List]:
    """Ensure value is a list"""
    if val is None:
        return None
    if isinstance(val, list):
        return val if val else None
    return [val]


def fix_image_url(url: str, catalog: str = "") -> str:
    """Convert image URL to webshop-compatible path"""
    if not url:
        return url
    
    # Already correct format
    if url.startswith("/product-images/"):
        return url
    
    # Handle ../product-images/ format
    if url.startswith("../product-images/"):
        return url.replace("../product-images/", "/product-images/")
    
    # Handle example.com legacy format
    if "example.com/media/" in url:
        filename = url.split("example.com/media/")[-1]
        if catalog:
            return f"/product-images/{catalog}.pdf/{filename}"
        return f"/product-images/{filename}"
    
    # Handle relative paths
    if url.startswith("product-images/"):
        return f"/{url}"
    
    return url


def clean_description(desc: Any) -> Optional[str]:
    """Clean and format description"""
    if not desc or desc == "null":
        return None
    text = str(desc).strip()
    if len(text) < 5:
        return None
    return " ".join(text.split())


# ============================================================================
# ATTRIBUTE EXTRACTION
# ============================================================================

def extract_attributes(raw_data: Dict) -> Dict[str, Any]:
    """Extract all relevant attributes from raw data"""
    attrs = {}
    
    # Power attributes
    for key in ["power_kw", "power_kw_derived", "power_hp"]:
        val = safe_float(raw_data.get(key))
        if val is not None:
            attr_key = key.replace("_derived", "")
            if attr_key not in attrs:
                attrs[attr_key] = val
    
    # Voltage
    for key in ["voltage_v", "voltage_derived"]:
        val = safe_float(raw_data.get(key))
        if val is not None and "voltage_v" not in attrs:
            attrs["voltage_v"] = val
    
    # Pressure
    for key in ["pressure_max_bar", "pressure_min_bar", "pressure_bar"]:
        val = safe_float(raw_data.get(key))
        if val is not None:
            attrs[key] = val
    
    # Flow
    for key in ["flow_m3_hour", "flow_m3_hour_derived", "flow_l_min", "debiet_m3_h"]:
        val = safe_float(raw_data.get(key))
        if val is not None:
            attr_key = key.replace("_derived", "")
            if attr_key not in attrs:
                attrs[attr_key] = val
    
    # Dimensions
    for key in ["diameter_mm", "length_mm", "width_mm", "height_mm", 
                "dimensions_mm", "size_mm", "bore_mm", "wall_thickness_mm"]:
        val = safe_float(raw_data.get(key))
        if val is not None:
            attrs[key] = val
    
    # Other numeric attributes
    for key in ["weight_kg", "tank_volume_l", "volume_l", "noise_db_a", 
                "rpm", "cable_length_m", "head_m", "particle_size_mm",
                "frequency_hz", "dew_point_c", "temperature_c"]:
        val = safe_float(raw_data.get(key))
        if val is not None:
            attrs[key] = val
    
    # String/list attributes
    for key in ["materials", "connection_types", "series", "product_type"]:
        val = raw_data.get(key)
        if val:
            attrs[key] = val
    
    # Size inch (can be string or number)
    size_inch = raw_data.get("size_inch") or raw_data.get("connection_inch")
    if size_inch:
        attrs["size_inch"] = size_inch
    
    # Boolean attributes
    float_switch = raw_data.get("float_switch") or raw_data.get("float_switch_raw")
    if float_switch:
        if isinstance(float_switch, bool):
            attrs["float_switch"] = float_switch
        elif isinstance(float_switch, str):
            attrs["float_switch"] = float_switch.lower().startswith("ja")
    
    return attrs


# ============================================================================
# NAME & DESCRIPTION GENERATION
# ============================================================================

def derive_product_name(raw_data: Dict, category: str, sku: str) -> str:
    """Generate descriptive product name from available data"""
    
    # Try explicit name fields first
    for key in ["product_name", "name", "type", "product_type"]:
        candidate = raw_data.get(key)
        if candidate and isinstance(candidate, str) and len(candidate) > 3:
            if candidate.upper() != sku.upper():
                return candidate.strip()
    
    # Extract key specs
    power_kw = safe_float(raw_data.get("power_kw") or raw_data.get("power_kw_derived"))
    voltage_v = safe_float(raw_data.get("voltage_v") or raw_data.get("voltage_derived"))
    tank_l = safe_float(raw_data.get("tank_volume_l") or raw_data.get("volume_l"))
    diameter = safe_float(raw_data.get("diameter_mm") or raw_data.get("size_mm"))
    
    parts = []
    
    # Category-specific naming
    cat_lower = category.lower()
    
    if "compressor" in cat_lower or "airpress" in cat_lower:
        parts.append("Compressor")
        parts.append(sku)
        if power_kw and tank_l:
            parts.append(f"{power_kw}kW {int(tank_l)}L")
        elif power_kw:
            parts.append(f"{power_kw}kW")
        return " ".join(parts)
    
    if "pomp" in cat_lower or "pump" in cat_lower:
        parts.append("Pomp")
        parts.append(sku)
        if power_kw:
            parts.append(f"{power_kw}kW")
        return " ".join(parts)
    
    if "makita" in cat_lower:
        parts.append("Makita")
        parts.append(sku)
        if voltage_v:
            parts.append(f"{int(voltage_v)}V")
        return " ".join(parts)
    
    if any(x in cat_lower for x in ["buis", "slang", "pipe", "hose", "leiding"]):
        if diameter:
            return f"{category} {sku} - {diameter}mm"
        return f"{category} {sku}"
    
    if any(x in cat_lower for x in ["fitting", "koppeling"]):
        return f"Koppeling {sku}"
    
    # Default: Category + SKU
    return f"{category} {sku}"


def generate_description(raw_data: Dict, category: str) -> Optional[str]:
    """Generate descriptive text from product data"""
    
    # Use existing description if good enough
    existing = clean_description(raw_data.get("description"))
    if existing and len(existing) > 50:
        return existing
    
    parts = [f"Professioneel product uit de categorie {category}."]
    specs = []
    
    # Collect key specs
    power_kw = safe_float(raw_data.get("power_kw") or raw_data.get("power_kw_derived"))
    power_hp = safe_float(raw_data.get("power_hp"))
    voltage = safe_float(raw_data.get("voltage_v") or raw_data.get("voltage_derived"))
    pressure = safe_float(raw_data.get("pressure_max_bar"))
    flow_m3 = safe_float(raw_data.get("flow_m3_hour") or raw_data.get("flow_m3_hour_derived"))
    flow_lmin = safe_float(raw_data.get("flow_l_min"))
    tank = safe_float(raw_data.get("tank_volume_l") or raw_data.get("volume_l"))
    weight = safe_float(raw_data.get("weight_kg"))
    
    if power_kw:
        specs.append(f"{power_kw} kW vermogen")
    elif power_hp:
        specs.append(f"{power_hp} HP vermogen")
    
    if voltage:
        specs.append(f"{int(voltage)}V spanning")
    
    if pressure:
        specs.append(f"max. {pressure} bar druk")
    
    if flow_m3:
        specs.append(f"{flow_m3} m³/h debiet")
    elif flow_lmin:
        specs.append(f"{flow_lmin} L/min debiet")
    
    if tank:
        specs.append(f"{int(tank)}L tank")
    
    if weight:
        specs.append(f"{weight}kg gewicht")
    
    if specs:
        parts.append("Specificaties: " + ", ".join(specs) + ".")
    
    # Add materials
    materials = raw_data.get("materials")
    if materials:
        mat_list = materials if isinstance(materials, list) else [materials]
        parts.append(f"Materiaal: {', '.join(str(m) for m in mat_list)}.")
    
    return " ".join(parts) if len(parts) > 1 else None


# ============================================================================
# PRODUCT TRANSFORMATION
# ============================================================================

def transform_individual_product(raw_data: Dict) -> Dict[str, Any]:
    """Transform raw extraction data into webshop product"""
    
    sku = raw_data.get("sku")
    if not sku:
        return None
    
    # Handle both catalog_name (raw) and catalog (enriched) fields
    catalog = raw_data.get("catalog") or raw_data.get("catalog_name", "")
    catalog = catalog.replace(".pdf", "")
    category = CATALOG_CATEGORIES.get(catalog, raw_data.get("category") or catalog.replace("-", " ").title())
    brand = raw_data.get("brand") or CATALOG_BRANDS.get(catalog)
    
    # Generate name and description (or use existing if already enriched)
    name = raw_data.get("name") or derive_product_name(raw_data, category, sku)
    description = raw_data.get("description") or (generate_description(raw_data, category) if Config.GENERATE_DESCRIPTIONS else None)
    
    # Extract attributes
    attributes = extract_attributes(raw_data)
    
    # Process images
    media = []
    image_paths = []
    
    # Check if already has processed media (comprehensive format)
    if "media" in raw_data and isinstance(raw_data["media"], list) and raw_data["media"]:
        media = raw_data["media"]
        image_paths = raw_data.get("image_paths", [])
    else:
        # Process raw images format
        images = raw_data.get("images", [])
        for idx, img in enumerate(images):
            img_path = img.get("image_path") if isinstance(img, dict) else img
            if not img_path:
                continue
            
            url = fix_image_url(img_path, catalog) if Config.FIX_IMAGE_URLS else img_path
            media.append({
                "url": url,
                "role": "main" if idx == 0 else "gallery",
                "type": "image",
                "format": "webp"
            })
            image_paths.append(url)
    
    # Get PDF source info (handle both formats)
    pdf_source = raw_data.get("pdf_source") or (raw_data.get("source", {}).get("pdf_sources", [None])[0] if raw_data.get("source") else None)
    pages = raw_data.get("source_pages") or raw_data.get("merged_pdf_page", [])
    if not pages and raw_data.get("source"):
        pages = raw_data.get("source", {}).get("pages", [])
    if isinstance(pages, (int, float)):
        pages = [int(pages)]
    
    # Price
    price = safe_float(raw_data.get("price") or raw_data.get("price_eur"))
    
    # Build specs array (or use existing if already has it)
    specs = raw_data.get("specs", [])
    if not specs:
        specs = []
        for key, value in attributes.items():
            if value is not None and key not in ["materials", "connection_types"]:
                label = key.replace("_", " ").replace("m3", "m³").title()
                if isinstance(value, float):
                    specs.append({"label": label, "value": f"{value:.1f}".rstrip('0').rstrip('.')})
                else:
                    specs.append({"label": label, "value": str(value)})
    
    # Build product
    product = {
        "id": f"{catalog}:{sku}",
        "sku": sku,
        "name": name,
        "brand": brand,
        "catalog": catalog,
        "product_category": category,
        "category": category,
        "description": description,
        "pdf_source": pdf_source,
        "source_pages": pages,
        "imageUrl": media[0]["url"] if media else None,
        "media": media,
        "image_paths": image_paths,
        "price": price,
        "inStock": True if price else None,
        "priceMode": "fixed" if price else "request_quote",
        "specs": specs,
    }
    
    # Add attributes as flat fields for filtering
    product.update(attributes)
    
    return product


def transform_product_group(group: Dict[str, Any]) -> Dict[str, Any]:
    """Transform product group into webshop format"""
    
    catalog = group.get("catalog", "")
    brand = CATALOG_BRANDS.get(catalog, "Dema")
    category = CATALOG_CATEGORIES.get(catalog, catalog.replace("-", " ").title())
    family = group.get("family", "")
    
    # Media - shared across all variants
    media = []
    for item in group.get("media", []):
        url = fix_image_url(item.get("url", ""), catalog) if Config.FIX_IMAGE_URLS else item.get("url")
        media.append({
            "url": url,
            "role": item.get("role", "main"),
            "type": "image",
            "format": "webp"
        })
    
    # Extract common attributes
    attrs = {}
    common_props = group.get("common_properties", {})
    for key, value in common_props.items():
        if value is not None and not key.endswith("_display"):
            attrs[key] = value
    
    # Transform variants
    variants = []
    for variant in group.get("variants", []):
        variant_attrs = {}
        for key, value in variant.get("properties", {}).items():
            if not key.endswith("_display") and value is not None:
                variant_attrs[key] = value
        
        variants.append({
            "sku": variant.get("sku"),
            "label": variant.get("label"),
            "attributes": variant_attrs,
            "page_in_pdf": variant.get("page_in_pdf"),
        })
    
    # Build specs from common attributes
    specs = []
    for key, value in attrs.items():
        if value is not None:
            label = key.replace("_", " ").title()
            specs.append({"label": label, "value": str(value)})
    
    return {
        "id": group.get("group_id", f"{catalog}:{family}"),
        "type": "product_group",
        "sku": group.get("default_variant_sku"),
        "name": group.get("name", f"{family} Series"),
        "brand": brand,
        "catalog": catalog,
        "product_category": category,
        "category": category,
        "description": f"{group.get('name', family)} - Verkrijgbaar in {len(variants)} varianten",
        "family": family,
        "attributes": attrs,
        "specs": specs,
        "media": media,
        "imageUrl": media[0]["url"] if media else None,
        "variants": variants,
        "variant_count": len(variants),
        "default_variant_sku": group.get("default_variant_sku"),
        "price": None,
        "priceMode": "request_quote",
        "inStock": None,
    }


# ============================================================================
# MAIN BUILD FUNCTION
# ============================================================================

def build_webshop_feed() -> List[Dict[str, Any]]:
    """Build complete webshop feed from all sources"""
    
    products = []
    
    print("=" * 80)
    print("BUILDING UNIFIED WEBSHOP FEED")
    print("=" * 80)
    
    # 1. Load and transform raw products
    if Config.RAW_EXTRACTION.exists():
        print(f"\n📂 Loading raw extraction: {Config.RAW_EXTRACTION.name}")
        with Config.RAW_EXTRACTION.open("r", encoding="utf-8") as f:
            raw_products = json.load(f)
        
        print(f"   Loaded {len(raw_products)} raw products")
        print(f"   Transforming...")
        
        for raw in raw_products:
            product = transform_individual_product(raw)
            if product:
                products.append(product)
        
        print(f"   ✓ Transformed {len(products)} individual products")
    
    # 2. Load and transform product groups
    if Config.INCLUDE_GROUPS and Config.GROUPED_PRODUCTS.exists():
        print(f"\n📦 Loading product groups: {Config.GROUPED_PRODUCTS.name}")
        with Config.GROUPED_PRODUCTS.open("r", encoding="utf-8") as f:
            groups = json.load(f)
        
        print(f"   Loaded {len(groups)} product groups")
        print(f"   Transforming...")
        
        group_products = []
        for group in groups:
            transformed = transform_product_group(group)
            group_products.append(transformed)
        
        products.extend(group_products)
        print(f"   ✓ Added {len(group_products)} product groups")
    
    # Sort by catalog and SKU
    products.sort(key=lambda x: (x.get("catalog", ""), x.get("sku", "")))
    
    return products


def main():
    """Main entry point"""
    
    # Build feed
    products = build_webshop_feed()
    
    # Save to output
    Config.SHOP_FEED.parent.mkdir(parents=True, exist_ok=True)
    with Config.SHOP_FEED.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    # Statistics
    print(f"\n{'='*80}")
    print("STATISTICS")
    print("=" * 80)
    print(f"Total products:        {len(products)}")
    
    product_groups = [p for p in products if p.get("type") == "product_group"]
    individual = [p for p in products if p.get("type") != "product_group"]
    
    print(f"Product groups:        {len(product_groups)}")
    print(f"Individual products:   {len(individual)}")
    
    with_images = len([p for p in products if p.get("media")])
    with_descriptions = len([p for p in products if p.get("description")])
    with_price = len([p for p in products if p.get("price")])
    
    print(f"\nWith images:           {with_images} ({with_images/len(products)*100:.1f}%)")
    print(f"With descriptions:     {with_descriptions} ({with_descriptions/len(products)*100:.1f}%)")
    print(f"With prices:           {with_price} ({with_price/len(products)*100:.1f}%)")
    
    categories = len(set(p.get("product_category") for p in products))
    brands = len(set(p.get("brand") for p in products if p.get("brand")))
    
    print(f"\nCategories:            {categories}")
    print(f"Brands:                {brands}")
    
    print(f"\n💾 Output saved to:")
    print(f"   {Config.SHOP_FEED}")
    
    print(f"\n{'='*80}")
    print("✅ BUILD COMPLETE")
    print("=" * 80)
    
    # Show sample
    if products:
        sample = next((p for p in products if p.get("media") and p.get("specs")), products[0])
        print(f"\n📋 Sample product:")
        print(f"   SKU:         {sample.get('sku')}")
        print(f"   Name:        {sample.get('name')}")
        print(f"   Category:    {sample.get('product_category')}")
        print(f"   Brand:       {sample.get('brand', 'N/A')}")
        print(f"   Images:      {len(sample.get('media', []))}")
        print(f"   Specs:       {len(sample.get('specs', []))}")
        print(f"   Price:       {sample.get('price') or 'Request Quote'}")


if __name__ == "__main__":
    main()
