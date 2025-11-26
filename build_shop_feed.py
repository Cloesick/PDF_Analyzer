import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
INPUT_JSON = OUTPUT_DIR / "input_pdfs_analysis_v5.json"
SHOP_FEED_JSON = OUTPUT_DIR / "products_for_shop.json"

# Public URL prefix for images – adjust to your environment
BASE_MEDIA_URL = "https://example.com/media/"

# Map catalog base names to brands
CATALOG_TO_BRAND = {
    "makita-catalogus-2022-nl": "Makita",
    "airpress-catalogus-nl-fr": "Airpress",
    "bronpompen": "Dema",
    "centrifugaalpompen": "Dema",
    "digitale-versie-pompentoebehoren-compressed": "Dema",
    "dompelpompen": "Dema",
    "drukbuizen": "Dema",
}

# Simple categorization rules based on catalog name or product_type

def guess_product_type(item: Dict[str, Any]) -> str:
    catalog = (item.get("catalog_name") or "").lower()
    ptype = (item.get("product_type") or "").lower()

    if "compressor" in ptype or "airpress" in catalog:
        return "compressor"
    if any(x in catalog for x in ["bronpompen", "centrifugaalpompen", "dompelpompen", "pompentoebehoren", "pomp-specials"]):
        return "pump"
    if any(x in catalog for x in ["drukbuizen", "pe-buizen", "verzinkte-buizen", "kunststof-afvoerleidingen"]):
        return "pipe"
    return "other"


# --- Normalization helpers -------------------------------------------------

def to_float(val: Any) -> Optional[float]:
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip().replace(",", ".")
        # keep only first token (before space)
        s = s.split()[0]
        try:
            return float(s)
        except ValueError:
            return None
    return None


def parse_mm_raw(val: Any) -> Optional[float]:
    # "50 mm" -> 50.0
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).lower().replace("mm", "").strip()
    return to_float(s)


def parse_m_raw(val: Any) -> Optional[float]:
    # "5 m" -> 5.0
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).lower().replace("m3/h", "").replace("m3/uur", "").replace("m3", "").replace("m", "").strip()
    return to_float(s)


def parse_bar_raw(val: Any) -> Optional[float]:
    # "7,5 bar" -> 7.5
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).lower().replace("bar", "").strip()
    return to_float(s)


def parse_boolean_ja_nee(val: Any) -> Optional[bool]:
    if not isinstance(val, str):
        return None
    s = val.strip().lower()
    if s.startswith("ja"):
        return True
    if s.startswith("nee"):
        return False
    return None


def file_path_to_url(image_path: str) -> str:
    filename = os.path.basename(image_path)
    return BASE_MEDIA_URL + filename


# --- Attribute builders ----------------------------------------------------


def build_compressor_attributes(item: Dict[str, Any]) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}

    # Power
    power_kw = item.get("power_kw") or item.get("power_kw_derived")
    v = to_float(power_kw)
    if v is not None:
        attrs["power_kw"] = v

    v = to_float(item.get("power_hp"))
    if v is not None:
        attrs["power_hp"] = v

    # Flow
    v = to_float(item.get("flow_l_min"))
    if v is not None:
        attrs["flow_l_min"] = v

    flow_m3 = item.get("flow_m3_hour") or item.get("flow_m3_hour_derived")
    v = to_float(flow_m3)
    if v is not None:
        attrs["flow_m3_hour"] = v

    # Pressure
    v = to_float(item.get("pressure_max_bar"))
    if v is not None:
        attrs["pressure_max_bar"] = v

    v = to_float(item.get("pressure_min_bar"))
    if v is not None:
        attrs["pressure_min_bar"] = v

    # Tank volume
    v = to_float(item.get("tank_volume_l") or item.get("volume_l"))
    if v is not None:
        attrs["tank_volume_l"] = v

    # Electrical
    v = to_float(item.get("voltage_v"))
    if v is not None:
        attrs["voltage_v"] = v

    v = to_float(item.get("frequency_hz"))
    if v is not None:
        attrs["frequency_hz"] = v

    # Noise
    v = to_float(item.get("noise_db_a"))
    if v is not None:
        attrs["noise_db_a"] = v

    # Weight
    v = to_float(item.get("weight_kg"))
    if v is not None:
        attrs["weight_kg"] = v

    # Series
    if item.get("series"):
        attrs["series"] = item["series"]

    return attrs


def build_pump_attributes(item: Dict[str, Any]) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}

    # Power
    power_kw = item.get("power_kw") or item.get("power_kw_derived") or item.get("power_kw_raw")
    v = to_float(power_kw)
    if v is not None:
        attrs["power_kw"] = v

    # Flow
    flow_m3 = item.get("flow_m3_hour") or item.get("flow_m3_hour_derived") or item.get("flow_m3_hour_raw")
    v = to_float(flow_m3)
    if v is not None:
        attrs["flow_m3_hour"] = v

    # Head
    head = item.get("head_m") or item.get("head_m_raw")
    v = parse_m_raw(head)
    if v is not None:
        attrs["head_m"] = v

    # Connection size (inch)
    v = to_float(item.get("connection_inch") or item.get("connection_size_raw"))
    if v is not None:
        attrs["connection_inch"] = v

    # Particle size
    v = parse_mm_raw(item.get("particle_size_mm") or item.get("particle_size_mm_raw"))
    if v is not None:
        attrs["particle_size_mm"] = v

    # Cable length
    v = parse_m_raw(item.get("cable_length_m") or item.get("cable_length_m_raw"))
    if v is not None:
        attrs["cable_length_m"] = v

    # Float switch
    fs = item.get("float_switch_raw")
    b = parse_boolean_ja_nee(fs)
    if b is not None:
        attrs["float_switch"] = b

    return attrs


def build_pipe_attributes(item: Dict[str, Any]) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}

    # Diameter / bore
    v = parse_mm_raw(item.get("diameter_mm") or item.get("diameter_mm_raw") or item.get("bore_mm_raw") or item.get("size_mm_raw"))
    if v is not None:
        attrs["diameter_mm"] = v

    # Pressure
    v = parse_bar_raw(item.get("pressure_max_bar") or item.get("pressure_bar") or item.get("pressure_raw"))
    if v is not None:
        attrs["pressure_bar"] = v

    # Wall thickness
    v = parse_mm_raw(item.get("wall_thickness_mm") or item.get("wall_thickness_mm_raw"))
    if v is not None:
        attrs["wall_thickness_mm"] = v

    # Length
    v = parse_m_raw(item.get("length_m") or item.get("length_m_raw"))
    if v is not None:
        attrs["length_m"] = v

    # Size inch (for fittings)
    if item.get("size_inch"):
        attrs["size_inch"] = item["size_inch"]

    return attrs


def build_other_attributes(item: Dict[str, Any]) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}

    # Dimensions
    v = parse_mm_raw(item.get("dimension_mm") or item.get("dimension_mm_raw"))
    if v is not None:
        attrs["dimension_mm"] = v

    # Generic length / width / height in mm
    for key in ["length_mm", "width_mm", "height_mm"]:
        if key in item and item.get(key) is not None:
            val = to_float(item.get(key))
            if val is not None:
                attrs[key] = val

    # Temperature ranges
    v = to_float(item.get("temperature_c") or item.get("temperature_c_raw"))
    if v is not None:
        attrs["temperature_c"] = v

    v = to_float(item.get("dew_point_c") or item.get("dew_point_c_raw"))
    if v is not None:
        attrs["dew_point_c"] = v

    # RPM
    v = to_float(item.get("rpm") or item.get("rpm_raw"))
    if v is not None:
        attrs["rpm"] = v

    # Weight / volume if not already handled elsewhere
    v = to_float(item.get("weight_kg"))
    if v is not None and "weight_kg" not in attrs:
        attrs["weight_kg"] = v

    v = to_float(item.get("volume_l"))
    if v is not None and "volume_l" not in attrs:
        attrs["volume_l"] = v

    return attrs


def build_universal_attributes(item: Dict[str, Any]) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}

    # Materials and connection types are already normalized lists
    if item.get("materials"):
        attrs["materials"] = item["materials"]
    if item.get("connection_types"):
        attrs["connection_types"] = item["connection_types"]

    return attrs


# --- Main transform --------------------------------------------------------


def transform_item(item: Dict[str, Any]) -> Dict[str, Any]:
    sku = item["sku"]
    catalog = item.get("catalog_name") or ""
    brand = CATALOG_TO_BRAND.get(catalog, None)

    images = item.get("images", [])
    media: List[Dict[str, Any]] = []
    for idx, img in enumerate(images):
        image_path = img.get("image_path")
        if not image_path:
            continue
        url = file_path_to_url(image_path)
        role = "main" if idx == 0 else "gallery"
        media.append({"url": url, "role": role})

    # Aggregate all pdf sources this SKU came from
    pdf_sources = sorted({
        src for src in ([item.get("pdf_source")] + [img.get("pdf_source") for img in images]) if src
    })

    # Guess product type and build attributes
    ptype = guess_product_type(item)
    attrs: Dict[str, Any] = {}
    attrs.update(build_universal_attributes(item))
    if ptype == "compressor":
        attrs.update(build_compressor_attributes(item))
    elif ptype == "pump":
        attrs.update(build_pump_attributes(item))
    elif ptype == "pipe":
        attrs.update(build_pipe_attributes(item))
    else:
        # Fallback for all other product types: try to surface useful generic fields.
        attrs.update(build_other_attributes(item))

    name = item.get("type_raw") or item.get("type") or sku

    category = item.get("product_category") or catalog.replace("-", " ")

    # Build display-ready specs from attributes
    specs = []
    for key, value in attrs.items():
        if value is None:
            continue
        specs.append({
            "key": key,
            "label": key,
            "value": value,
        })

    # Determine price: use any numeric price from the source if available,
    # otherwise expose a request-quote style price.
    raw_price = item.get("price_eur") or item.get("price") or item.get("price_raw")
    price_amount = to_float(raw_price)
    if price_amount is not None:
        price_block = {
            "amount": price_amount,
            "currency": "EUR",
            "vat_included": True,
            "mode": "fixed",
        }
    else:
        price_block = {
            "amount": None,
            "currency": "EUR",
            "vat_included": True,
            "mode": "request_quote",
        }

    return {
        "id": item.get("product_id") or f"{catalog}:{sku}",
        "sku": sku,
        "name": name,
        "brand": brand,
        "catalog": catalog,
        "category": category,
        "description": item.get("description"),
        "attributes": attrs,
        "specs": specs,
        "media": media,
        "price": price_block,
        "stock": {
            "status": "unknown",
            "quantity": None,
        },
        "seo": {
            "slug": f"{sku}".lower().replace(" ", "-"),
            "meta_title": f"{sku} | {category}",
            "meta_description": f"{sku} from {category}.",
        },
        "source": {
            "pdf_sources": pdf_sources,
            "pages": item.get("merged_pdf_page", []),
        },
    }


def main() -> None:
    if not INPUT_JSON.exists():
        print(f"Input JSON not found: {INPUT_JSON}")
        return

    with INPUT_JSON.open("r", encoding="utf-8") as f:
        raw_products = json.load(f)

    shop_products: List[Dict[str, Any]] = []
    for item in raw_products:
        if "sku" not in item:
            continue
        shop_products.append(transform_item(item))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SHOP_FEED_JSON.open("w", encoding="utf-8") as f:
        json.dump(shop_products, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(shop_products)} products to {SHOP_FEED_JSON}")


if __name__ == "__main__":
    main()
