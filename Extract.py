import pdfplumber
import re
import json
import os
import base64
import io
from collections import defaultdict
import numpy as np
import cv2
from PIL import Image

from openai import OpenAI

_openai_client: "OpenAI | None" = None


def _get_openai_client() -> OpenAI:
    """Lazily instantiate and cache the OpenAI client.

    Expects OPENAI_API_KEY to be set in the environment.
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


# --- Configuration ---
# Root of this project (folder where this script lives)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Folder containing the input PDFs (in the project root)
INPUT_FOLDER = os.path.join(PROJECT_ROOT, "input_pdfs")

# Folder where JSON output will be written (in the project root)
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "output")  # You can change this folder name if needed

# Folder where cropped images will be written (one image per PDF/page/index)
IMAGES_FOLDER = os.path.join(PROJECT_ROOT, "product-images")
# --- Generate Versioned Output Filename (based on Input Folder name) ---
# ... bestaande code ...
input_folder_name = os.path.basename(os.path.normpath(INPUT_FOLDER))
base_output_name = f"{input_folder_name}_analysis" # Base name for the output

version = 1
output_filename = f"{base_output_name}_v{version}.json"
JSON_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, output_filename)

# Check if file exists and increment version if needed
while os.path.exists(JSON_OUTPUT_PATH):
    version += 1
    output_filename = f"{base_output_name}_v{version}.json"
    JSON_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, output_filename)

print(f"Input folder: {INPUT_FOLDER}")
print(f"Output will be saved to: {JSON_OUTPUT_PATH}")

# --- Regular Expressions for Attribute Extraction ---
# ... bestaande code ...
sku_patterns = [
    re.compile(r'\b([A-Z]{2,}\d+[-A-Z0-9]*)\b'), # ABS...
    re.compile(r'\b(\d{5,}(?:-[A-Z0-9]+)?)\b'), # 36744-E, 45424
    re.compile(r'\b(X\d+)\b'),                   # X0817015
    re.compile(r'\b([A-Z]{1,2}\s?\d{2,}[-A-Z0-9/]*)\b'), # HL 150-24, K11 VA2801A
    re.compile(r'\b(\d+-\d+(?:-[A-Z]+)?)\b') # 79853-L
]
pressure_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*(?:-|tot|to)\s*(\d+(?:[.,]\d+)?)\s*bar', re.IGNORECASE)
pressure_single_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*bar', re.IGNORECASE)
dimension_mm_pattern = re.compile(r'\b(\d+(?:[.,]\d+)?)\s*mm\b', re.IGNORECASE)
dimensions_mm_mult_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*x\s*(\d+(?:[.,]\d+)?)\s*x\s*(\d+(?:[.,]\d+)?)\s*mm', re.IGNORECASE)
dimensions_mixed_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*mm\s*x\s*(\d+(?:[.,]\d+)?)\s*mm', re.IGNORECASE)
size_inch_pattern = re.compile(r'(\d+(?:[.,]\d+)?(?:/\d+)?)"', re.IGNORECASE)
power_hp_kw_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*hp\s*/\s*(\d+(?:[.,]\d+)?)\s*kW', re.IGNORECASE)
power_hp_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*hp', re.IGNORECASE)
power_kw_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*kW', re.IGNORECASE)
voltage_pattern = re.compile(r'(\d+)\s*V', re.IGNORECASE)
frequency_pattern = re.compile(r'(\d+)\s*Hz', re.IGNORECASE)
flow_l_min_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*L/min', re.IGNORECASE)
flow_m3_hour_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*m³/hour', re.IGNORECASE)
rpm_pattern = re.compile(r'(\d+)\s*rpm', re.IGNORECASE)
volume_l_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*L(?!\s*[/])', re.IGNORECASE)
weight_kg_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*kg', re.IGNORECASE)
noise_db_pattern = re.compile(r'(\d+)\s*dB\(A\)', re.IGNORECASE)
dew_point_pattern = re.compile(r'(-?\d+)\s*°C', re.IGNORECASE)
length_m_pattern = re.compile(r'(\d+)\s*m(?!\s*m|\s*³)', re.IGNORECASE)
temperature_c_pattern = re.compile(r'(-?\d+(?:[.,]\d+)?)\s*°C', re.IGNORECASE)
material_pattern = re.compile(r'(staal|steel|aluminium|aluminum|kunststof|plastic|messing|brass|koper|copper|gietijzer|cast iron|rubber|polyurethaan|polyurethane)', re.IGNORECASE)
connection_type_pattern = re.compile(r'(binnendraad|female thread|buitendraad|male thread|lijmmof|solvent socket|lijmspie|solvent spigot)', re.IGNORECASE)
feature_pattern = re.compile(r'(olie(vrij|loos)|oil-?free|geluids?gedempt|silenced|versterkt|reinforced|galvanized|gegalvaniseerd|hybride|hybrid)', re.IGNORECASE)

# --- <-- HIER NIEUWE REGEX-PATRONEN TOEVOEGEN --> ---
pistons_pattern = re.compile(r'(\d+)\s*(?:pistons?|zuigers?)', re.IGNORECASE)
cylinders_pattern = re.compile(r'(\d+)\s*(?:cyl|cilinders?|cylinders?)', re.IGNORECASE)
connection_inch_pattern = re.compile(r'(?:connection|aansluiting)\s*(\d+(?:[.,]\d+)?(?:/\d+)?)"', re.IGNORECASE)


# --- Helper Functions ---
def smart_crop_image(pil_image):
    """Find the main object on a light background and crop tightly around it."""
    open_cv_image = np.array(pil_image)
    if open_cv_image.ndim == 2:
        gray = open_cv_image
        color_bgr = cv2.cvtColor(open_cv_image, cv2.COLOR_GRAY2BGR)
    else:
        if open_cv_image.shape[2] == 4:
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGBA2RGB)
        color_bgr = open_cv_image[:, :, ::-1].copy()
        gray = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2GRAY)

    gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return pil_image

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    if w < 20 or h < 20:
        return pil_image

    mask_object = np.zeros_like(gray, dtype=np.uint8)
    cv2.drawContours(mask_object, [largest_contour], -1, 255, thickness=cv2.FILLED)

    white_bg = np.full_like(color_bgr, 255)
    mask_3c = cv2.merge([mask_object, mask_object, mask_object])
    obj_on_white = np.where(mask_3c == 255, color_bgr, white_bg)

    padding = 10
    h_img, w_img = gray.shape[:2]
    x_new = max(0, x - padding)
    y_new = max(0, y - padding)
    x_max = min(w_img, x + w + padding)
    y_max = min(h_img, y + h + padding)

    obj_on_white_rgb = obj_on_white[:, :, ::-1]
    pil_obj_on_white = Image.fromarray(obj_on_white_rgb)
    return pil_obj_on_white.crop((x_new, y_new, x_max, y_max))

def clean_text(text):
# ... bestaande code ...
    if not text:
        return ""
    text = str(text) # Ensure it's a string
    text = text.replace('$', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_value(value_str):
# ... bestaande code ...
    if isinstance(value_str, (int, float)):
        return value_str
    if isinstance(value_str, str):
        cleaned_value = value_str.strip().replace(',', '.')
        try:
            if '-' in cleaned_value or '/' in cleaned_value:
                if re.match(r'^[\d.,]+[-/][\d.,]+$', cleaned_value):
                    return value_str
            if '.' in cleaned_value:
                return float(cleaned_value)
            else:
                return int(cleaned_value)
        except ValueError:
            return value_str # Return original string if conversion fails
    return value_str

def find_printed_page_num(page_obj):
# ... bestaande code ...
    """
    Tries to find the physical page number printed on the page, 
    by cropping to the bottom 10% of the page.
    """
    try:
        page_height = page_obj.height
        page_width = page_obj.width
        
        # Define footer area (bottom 10%)
        footer_y_start = page_height * 0.9
        
        # Crop the entire footer to get text
        footer_crop = page_obj.crop((0, footer_y_start, page_width, page_height))
        # Use a generous x_tolerance for page numbers that might be far apart
        footer_text = footer_crop.extract_text(x_tolerance=5, y_tolerance=3)
        
        if not footer_text:
            return None
        
        footer_text = clean_text(footer_text)
        
        # Find all standalone numbers (1-4 digits)
        matches = re.findall(r'\b(\d{1,4})\b', footer_text)
        if not matches:
            return None
        
        # Filter out numbers that look like years (e.g., 1990-2030)
        non_year_matches = []
        for num_str in matches:
            try:
                num_int = int(num_str)
                # Filter out common year ranges
                if not (1990 <= num_int <= 2030): 
                    non_year_matches.append(num_str)
            except ValueError:
                continue 
        
        if non_year_matches:
            # Return the first non-year number found
            # This handles "Page 10 of 120" (returns "10")
            return non_year_matches[0]
        else:
            # Fallback: return the first number found, even if it looks like a year
            return matches[0]
            
    except Exception as e:
        # print(f"Error finding physical page num: {e}")
        return None # Fail silently

def parse_pressure(text):
# ... bestaande code ...
    """Extracts min/max pressure in bar."""
    min_p, max_p = None, None
    attributes = {} 
    match_range = pressure_pattern.search(text)
    if match_range:
        min_p = normalize_value(match_range.group(1))
        max_p = normalize_value(match_range.group(2))
    else:
        matches_single = pressure_single_pattern.findall(text)
        if matches_single:
            pressures = [normalize_value(p) for p in matches_single]
            if len(pressures) == 1:
                max_p = pressures[0]
            else:
                numeric_pressures = [p for p in pressures if isinstance(p, (int, float))]
                if numeric_pressures:
                    min_val = min(numeric_pressures)
                    max_val = max(numeric_pressures)
                    if min_val != max_val:
                        min_p = min_val
                    max_p = max_val
                else: 
                    attributes['pressure_bar_list'] = pressures
    if min_p is not None: attributes['pressure_min_bar'] = min_p
    if max_p is not None: attributes['pressure_max_bar'] = max_p
    return attributes

def parse_dimensions(text):
# ... bestaande code ...
    """Extracts dimensions, prioritizing LxWxH format."""
    dims = {}
    match_mult = dimensions_mm_mult_pattern.search(text)
    if match_mult:
        dims['length_mm'] = normalize_value(match_mult.group(1))
        dims['width_mm'] = normalize_value(match_mult.group(2))
        dims['height_mm'] = normalize_value(match_mult.group(3))
    else:
        match_single = dimension_mm_pattern.findall(text)
        if len(match_single) == 1:
            dims['dimension_mm'] = normalize_value(match_single[0])
        elif len(match_single) > 1:
            dims['dimensions_mm_list'] = [normalize_value(d) for d in match_single]
        match_mixed = dimensions_mixed_pattern.search(text)
        if match_mixed:
            dims['size_mm_1'] = normalize_value(match_mixed.group(1))
            dims['size_mm_2'] = normalize_value(match_mixed.group(2))
            
    match_inch = size_inch_pattern.findall(text)
    if match_inch:
        unique_inches = sorted(list(set(s.strip() for s in match_inch)))
        dims['size_inch'] = unique_inches if len(unique_inches) > 1 else unique_inches[0]
    
    return dims if dims else None

def parse_power(text):
    """Extracts power in HP and kW."""
    hp, kw = None, None
    match_both = power_hp_kw_pattern.search(text)
    if match_both:
        hp = normalize_value(match_both.group(1))
        kw = normalize_value(match_both.group(2))
    else:
        match_hp = power_hp_pattern.search(text)
        if match_hp:
            hp = normalize_value(match_hp.group(1))
        match_kw = power_kw_pattern.search(text)
        if match_kw:
            kw = normalize_value(match_kw.group(1))
    return hp, kw

def find_sku(text):
# ... bestaande code ...

    """Finds the most likely SKU in a text using multiple patterns."""
    text = clean_text(text)
    if not text:
        return None
    for pattern in sku_patterns:
        matches = pattern.findall(text)

        potential_skus = [m for m in matches if isinstance(m, str)]
        potential_skus = [m for m in potential_skus if not (m.isdigit() and len(m) < 5)]
        potential_skus = [m for m in potential_skus if not (m.isdigit() and 1900 < int(m) < 2100)]
        potential_skus = [s for s in potential_skus if len(s) > 3 or s.startswith(('X', 'x'))]
        if potential_skus:
            non_name_like = [s for s in potential_skus if not (s.startswith(('HL ', 'APS ', 'BM ', 'KM ', 'LM ', 'VK ', 'HK ', 'GK ','DSL ','EPDM ')))]
            if non_name_like:
                if non_name_like[0].upper() == 'ABS' and len(non_name_like) > 1:
                    return non_name_like[1] 
                return non_name_like[0]
            return potential_skus[0]
    return None

def find_all_skus(text):
    """Returns a set of all SKU-like strings found in the given text using sku_patterns."""
    text = clean_text(text)
    if not text:
        return set()
    found = set()
    for pattern in sku_patterns:
        matches = pattern.findall(text)
        for m in matches:
            sku = m if isinstance(m, str) else None
            if not sku:
                continue
            # Apply same basic filters as in find_sku
            if sku.isdigit() and len(sku) < 5:
                continue
            if sku.isdigit() and 1900 < int(sku) < 2100:
                continue
            if len(sku) <= 3 and not sku.startswith(("X", "x")):
                continue
            found.add(sku)
    return found

def _center(bbox):
    """Helper function to calculate the center point of a bounding box."""
    if not bbox or len(bbox) < 4:
        return (0, 0)
    x0, y0, x1, y1 = bbox[0], bbox[1], bbox[2], bbox[3]
    return ((x0 + x1) / 2, (y0 + y1) / 2)

# ... bestaande code ...

def extract_attributes_from_text(text, existing_keys=None):
    """
    Extracts various attributes from a block of text using regex.
    Optionally skips extraction if key exists in existing_keys set.
    """
    if existing_keys is None:
        existing_keys = set()
    
    attrs = {}
    
    # Extract pressure
    if 'pressure_min_bar' not in existing_keys or 'pressure_max_bar' not in existing_keys:
        pressure_data = parse_pressure(text)
        for key, value in pressure_data.items():
            if key not in existing_keys:
                attrs[key] = value
    
    # Extract dimensions
    if 'dimensions_mm_raw' not in existing_keys:
        dim_data = parse_dimensions(text)
        if dim_data:
            attrs['dimensions_mm_raw'] = text
            for key, value in dim_data.items():
                if key not in existing_keys:
                    attrs[key] = value
    
    # Extract power
    if 'power_hp' not in existing_keys or 'power_kw' not in existing_keys:
        hp, kw = parse_power(text)
        if hp is not None and 'power_hp' not in existing_keys:
            attrs['power_hp'] = hp
        if kw is not None and 'power_kw' not in existing_keys:
            attrs['power_kw'] = kw
        if (hp or kw) and 'power_raw' not in existing_keys:
            attrs['power_raw'] = text
    
    # Extract voltage
    if 'voltage' not in existing_keys:
        match = voltage_pattern.search(text)
        if match:
            attrs['voltage'] = normalize_value(match.group(1))
    
    # Extract frequency
    if 'frequency_hz' not in existing_keys:
        match = frequency_pattern.search(text)
        if match:
            attrs['frequency_hz'] = normalize_value(match.group(1))
    
    # Extract flow rates
    if 'flow_l_min' not in existing_keys:
        match = flow_l_min_pattern.search(text)
        if match:
            attrs['flow_l_min'] = normalize_value(match.group(1))
    
    if 'flow_m3_hour' not in existing_keys:
        match = flow_m3_hour_pattern.search(text)
        if match:
            attrs['flow_m3_hour'] = normalize_value(match.group(1))
    
    # Extract RPM
    if 'rpm' not in existing_keys:
        match = rpm_pattern.search(text)
        if match:
            attrs['rpm'] = normalize_value(match.group(1))
    
    # Extract volume
    if 'volume_l' not in existing_keys:
        match = volume_l_pattern.search(text)
        if match:
            attrs['volume_l'] = normalize_value(match.group(1))
    
    # Extract weight
    if 'weight_kg' not in existing_keys:
        match = weight_kg_pattern.search(text)
        if match:
            attrs['weight_kg'] = normalize_value(match.group(1))
    
    # Extract noise level
    if 'noise_db' not in existing_keys:
        match = noise_db_pattern.search(text)
        if match:
            attrs['noise_db'] = normalize_value(match.group(1))
    
    # Extract temperature
    if 'temperature_c' not in existing_keys:
        matches = temperature_c_pattern.findall(text)
        if matches:
            temps = [normalize_value(t) for t in matches]
            if len(temps) == 1:
                attrs['temperature_c'] = temps[0]
            else:
                attrs['temperature_c_list'] = temps
    
    # Extract length
    if 'length_m' not in existing_keys:
        match = length_m_pattern.search(text)
        if match:
            attrs['length_m'] = normalize_value(match.group(1))
    
    # Extract materials
    if 'materials' not in existing_keys:
        materials = material_pattern.findall(text)
        if materials:
            unique_materials = list(set([m.lower() for m in materials]))
            attrs['materials'] = unique_materials if len(unique_materials) > 1 else unique_materials[0]
    
    # Extract connection types
    if 'connection_types' not in existing_keys:
        connections = connection_type_pattern.findall(text)
        if connections:
            unique_connections = list(set([c.lower() for c in connections]))
            attrs['connection_types'] = unique_connections if len(unique_connections) > 1 else unique_connections[0]
    
    # Extract features
    if 'features' not in existing_keys:
        features = feature_pattern.findall(text)
        if features:
            unique_features = list(set([f.lower() for f in features]))
            attrs['features'] = unique_features if len(unique_features) > 1 else unique_features[0]
    
    # Extract pistons/cylinders
    if 'pistons' not in existing_keys:
        match = pistons_pattern.search(text)
        if match:
            attrs['pistons'] = normalize_value(match.group(1))
    
    if 'cylinders' not in existing_keys:
        match = cylinders_pattern.search(text)
        if match:
            attrs['cylinders'] = normalize_value(match.group(1))
    
    # Extract connection size in inches
    if 'connection_inch' not in existing_keys:
        match = connection_inch_pattern.search(text)
        if match:
            attrs['connection_inch'] = match.group(1)
    
    return attrs

def _gpt_is_product_image(image_bytes: bytes) -> bool:
    """Use GPT-4o to decide if an image is a real product vs logo/decorative.

    Returns True if the image is likely a hardware/tool/pipe/tube/etc. product
    photo or drawing, False if it is mainly a logo, icon, or decorative graphic.
    """
    client = _get_openai_client()

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "You see an image extracted from a hardware / tools / pipes catalog. "
        "Classify it as either a real product (tool, hardware component, pipe, "
        "tube, fitting, hose, compressor, pump, connector, etc.) or as a "
        "non-product like a logo, icon, brand mark, schematic arrow, or "
        "purely decorative graphic. Respond ONLY as strict JSON with key "
        "'keep' (boolean) where keep=true means it is a product image that "
        "should be kept, and keep=false means it should be discarded."
    )

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image": {"format": "webp", "data": image_b64},
                        },
                    ],
                }
            ],
        )

        text_outputs = []
        for out in getattr(response, "output", []) or []:
            for c in getattr(out, "content", []) or []:
                if getattr(c, "type", None) == "output_text":
                    text_outputs.append(getattr(c, "text", ""))

        if not text_outputs:
            return True

        raw = text_outputs[0]
        data = json.loads(raw)
        keep = data.get("keep")
        if isinstance(keep, bool):
            return keep
        return True
    except Exception:
        # On any API or parsing error, default to keeping the image so
        # downstream steps can still operate using existing heuristics.
        return True


def _gpt_match_image_to_skus(image_bytes: bytes, skus: list[str], page_text: str) -> list[str]:
    """Ask GPT-4o which SKUs on the page best match this image.

    skus: list of SKU strings present on the page/table.
    page_text: raw text of the page to give GPT extra context.

    Returns a subset of skus. If it cannot decide, returns an empty list.
    """
    if not skus:
        return []

    client = _get_openai_client()

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    sku_list_str = "\n".join(f"- {s}" for s in skus)

    prompt = (
        "You are helping to match product images to SKUs on a hardware/tools/pipes catalog page. "
        "Below is the full page text, which may contain descriptions, tables, and SKUs. "
        "You are also given a list of SKUs that appear on this page, and a single image. "
        "Decide which of the given SKUs best match the product shown in the image. "
        "Respond ONLY as strict JSON with key 'matched_skus' as an array of SKU strings "
        "chosen from the provided list. If you are unsure, return an empty array.\n\n"
        f"SKUs on this page:\n{sku_list_str}\n\n"
        f"Page text:\n{page_text[:4000]}"
    )

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image": {"format": "webp", "data": image_b64},
                        },
                    ],
                }
            ],
        )

        text_outputs = []
        for out in getattr(response, "output", []) or []:
            for c in getattr(out, "content", []) or []:
                if getattr(c, "type", None) == "output_text":
                    text_outputs.append(getattr(c, "text", ""))

        if not text_outputs:
            return []

        raw = text_outputs[0]
        data = json.loads(raw)
        matched = data.get("matched_skus")
        if isinstance(matched, list):
            return [str(s) for s in matched if str(s) in skus]
        return []
    except Exception:
        # On any error, fall back to no decision so heuristics can be used.
        return []


def process_pdf_file(pdf_path, product_map):
    # ... (rest of the code remains the same)

    """Processes a single PDF file and updates the main product_map."""
    PDF_FILENAME = os.path.basename(pdf_path)
    print(f"\n--- Processing file: {PDF_FILENAME} ---")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            print(f"Total pages: {num_pages}")

            # Debug counters for image handling within this PDF
            total_page_images = 0
            skipped_small_images = 0
            skipped_layout_images = 0
            dropped_by_gpt_images = 0
            kept_product_images = 0

            for i, page in enumerate(pdf.pages):
                current_page_num = i + 1
                # Track all SKUs that appear on this page so we can link images
                page_skus = set()

                # --- 1. Extract text from page ---
                try:
                    page_text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                except Exception:
                    page_text = ""

                # --- 2. Extract and parse tables ---
                table_groups = []
                try:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if not table or len(table) < 2:
                                continue

                            # Try to identify description column from header row
                            header_row = table[0] if table else []
                            desc_col_indices = []
                            if header_row:
                                for idx, cell in enumerate(header_row):
                                    if cell and isinstance(cell, str):
                                        cell_lower = cell.lower()
                                        if any(keyword in cell_lower for keyword in ['description', 'omschrijving', 'product', 'type', 'toepassing', 'application']):
                                            desc_col_indices.append(idx)

                            # Find SKUs in each row of the table
                            table_skus = set()
                            for row_idx, row in enumerate(table):
                                if not row:
                                    continue
                                
                                # Skip header row in data extraction
                                if row_idx == 0:
                                    continue
                                    
                                row_text = " ".join([str(cell) if cell else "" for cell in row])
                                row_skus = find_all_skus(row_text)
                                table_skus.update(row_skus)

                                # Extract description from identified columns
                                description_parts = []
                                if desc_col_indices:
                                    for idx in desc_col_indices:
                                        if idx < len(row) and row[idx]:
                                            desc_text = str(row[idx]).strip()
                                            if desc_text and desc_text not in description_parts:
                                                description_parts.append(desc_text)
                                
                                # If no specific description column, use cells that are longer text (likely descriptions)
                                if not description_parts:
                                    for cell in row:
                                        if cell and isinstance(cell, str):
                                            cell_text = str(cell).strip()
                                            # Consider cells with > 20 chars as potential descriptions
                                            if len(cell_text) > 20 and not find_all_skus(cell_text):
                                                description_parts.append(cell_text)
                                
                                description = " ".join(description_parts) if description_parts else row_text

                                # Also extract product attributes from rows with SKUs
                                for sku in row_skus:
                                    if sku not in product_map:
                                        product_map[sku] = {
                                            "sku": sku,
                                            "pdf_source": PDF_FILENAME,
                                            "merged_pdf_page": [current_page_num],
                                        }
                                    else:
                                        if current_page_num not in product_map[sku].get("merged_pdf_page", []):
                                            product_map[sku]["merged_pdf_page"].append(current_page_num)

                                    # Store description
                                    if description and 'description' not in product_map[sku]:
                                        product_map[sku]['description'] = description
                                    elif description and product_map[sku].get('description'):
                                        # Append if different
                                        existing_desc = product_map[sku]['description']
                                        if description not in existing_desc:
                                            product_map[sku]['description'] = existing_desc + " | " + description

                                    # Extract attributes from the row text and description
                                    full_text = row_text + " " + description
                                    attrs = extract_attributes_from_text(
                                        full_text,
                                        existing_keys=set(product_map[sku].keys())
                                    )
                                    for key, value in attrs.items():
                                        if value is not None and (key not in product_map[sku] or product_map[sku][key] is None):
                                            product_map[sku][key] = value

                            if table_skus:
                                # Get table bounding box (approximate based on page bbox)
                                try:
                                    table_bbox = (
                                        page.bbox[0],  # x0
                                        page.bbox[1],  # y0
                                        page.bbox[2],  # x1
                                        page.bbox[3],  # y1
                                    )
                                except Exception:
                                    table_bbox = None

                                table_groups.append({
                                    "skus": table_skus,
                                    "bbox": table_bbox,
                                })

                                page_skus.update(table_skus)

                except Exception:
                    # If table extraction fails, fall back to text-based SKU search
                    pass

                # Also search for SKUs in the full page text (not just tables)
                if page_text:
                    page_text_skus = find_all_skus(page_text)
                    for sku in page_text_skus:
                        if sku not in product_map:
                            product_map[sku] = {
                                "sku": sku,
                                "pdf_source": PDF_FILENAME,
                                "merged_pdf_page": [current_page_num],
                            }
                        else:
                            if current_page_num not in product_map[sku].get("merged_pdf_page", []):
                                product_map[sku]["merged_pdf_page"].append(current_page_num)

                    page_skus.update(page_text_skus)

                # --- 3. Associate page images with SKUs on this page ---
                try:
                    page_images = getattr(page, "images", []) or []
                except Exception:
                    page_images = []

                total_page_images += len(page_images or [])

                if page_images and page_skus:

                    safe_pdf_name = os.path.splitext(os.path.basename(PDF_FILENAME))[0]

                    # Precompute cropped images once per page image
                    cropped_cache = {}
                    for img_index, img in enumerate(page_images):
                        x0 = img.get("x0")
                        y0 = img.get("y0")
                        x1 = img.get("x1")
                        y1 = img.get("y1")
                        if None in (x0, y0, x1, y1):
                            continue
                        # Simple heuristic: skip very small images (likely icons/logos)
                        try:
                            width = x1 - x0
                            height = y1 - y0
                            area = width * height
                            # You can tune this threshold based on your catalogs
                            MIN_IMAGE_AREA = 10000  # e.g. ~100x100 px at PDF coordinates
                            if area < MIN_IMAGE_AREA:
                                skipped_small_images += 1
                                continue
                        except Exception:
                            pass

                        try:
                            # Look for SKUs in text very close to the image (including below it).
                            nearby_skus = set()
                            try:
                                margin_x = 5
                                margin_y = 10
                                page_height = page.height
                                page_width = page.width

                                region_top = max(0, y0 - margin_y)
                                region_bottom = min(page_height, y1 + 40)
                                region_left = max(0, x0 - margin_x)
                                region_right = min(page_width, x1 + margin_x)

                                text_region = page.crop((region_left, region_top, region_right, region_bottom))
                                local_text = text_region.extract_text(x_tolerance=2, y_tolerance=2)
                                if local_text:
                                    nearby_skus = find_all_skus(local_text)
                            except Exception:
                                nearby_skus = set()

                            cropped = page.crop((x0, y0, x1, y1))
                            pil_img_base = cropped.to_image(resolution=150).original
                            pil_img_cropped = smart_crop_image(pil_img_base)

                            gray = pil_img_cropped.convert("L")
                            gray_arr = np.array(gray)
                            h_arr, w_arr = gray_arr.shape[:2]
                            short_side = min(w_arr, h_arr)
                            long_side = max(w_arr, h_arr)
                            aspect_ratio_img = long_side / short_side if short_side > 0 else 0
                            hist = np.bincount(gray_arr.ravel(), minlength=256)
                            dominant_frac = hist.max() / float(gray_arr.size)
                            std_gray = gray_arr.std()
                            if (
                                short_side < 200
                                and aspect_ratio_img > 3.0
                                and dominant_frac > 0.75
                                and std_gray < 60
                            ):
                                skipped_layout_images += 1
                                continue

                            buf = io.BytesIO()
                            pil_img_cropped.save(buf, format="WEBP")
                            image_bytes = buf.getvalue()

                            # GPT filter: keep only real product images
                            if not _gpt_is_product_image(image_bytes):
                                dropped_by_gpt_images += 1
                                continue

                            kept_product_images += 1

                            cropped_cache[img_index] = (
                                pil_img_cropped,
                                {
                                    "x0": x0,
                                    "y0": y0,
                                    "x1": x1,
                                    "y1": y1,
                                    "image_bytes": image_bytes,
                                    "gpt_filter": "kept_product_image",
                                    "nearby_skus": sorted(nearby_skus) if nearby_skus else [],
                                },
                            )

                        except Exception:
                            continue

                    if not cropped_cache:
                        continue

                    # ... (rest of the code remains the same)

                    # 3a. Table-level association: for each table group, pick the nearest image
                    used_skus_in_tables = set()
                    for tbl in table_groups:
                        
                        skus_in_table = tbl.get("skus") or set()
                        if not skus_in_table:
                            continue

                        tbl_bbox = tbl.get("bbox")
                        if not tbl_bbox:
                            continue

                        txc, tyc = _center(tbl_bbox)

                        # Find closest image center to this table center
                        best_idx = None
                        best_dist_sq = None
                        for img_index, (_, bbox) in cropped_cache.items():
                            ix, iy = _center((bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]))

                            dx = ix - txc
                            dy = iy - tyc
                            dist_sq = dx * dx + dy * dy
                            if best_dist_sq is None or dist_sq < best_dist_sq:
                                best_dist_sq = dist_sq
                                best_idx = img_index

                        if best_idx is None:
                            continue

                        image_obj, bbox = cropped_cache[best_idx]
                        image_bytes = bbox.get("image_bytes")

                        # Combine table SKUs with SKUs detected very close to this image.
                        nearby_skus = set(bbox.get("nearby_skus") or [])
                        candidate_skus = set(skus_in_table) | nearby_skus
                        if not candidate_skus:
                            continue

                        # Optional GPT-based SKU matching: try to narrow down which SKUs
                        # in this table best match this image. If GPT cannot decide,
                        # fall back to using all SKUs in the table as before.
                        matched_skus = []
                        if image_bytes is not None:
                            matched_skus = _gpt_match_image_to_skus(
                                image_bytes,
                                skus=list(candidate_skus),
                                page_text=page_text or "",
                            )

                        bbox["gpt_matched_skus"] = matched_skus or None

                        target_skus = candidate_skus if not matched_skus else set(matched_skus)

                        for sku in target_skus:

                            sku_entry = product_map.get(sku)
                            if not sku_entry:
                                continue

                            used_skus_in_tables.add(sku)

                            existing_images = sku_entry.get("images", [])
                            existing_keys = set(
                                (img.get("pdf_source"), img.get("page"), img.get("index_on_page"))
                                for img in existing_images
                            )

                            key = (PDF_FILENAME, current_page_num, best_idx)
                            if key in existing_keys:
                                continue

                            safe_sku = re.sub(r"[^A-Za-z0-9_-]", "_", str(sku))[:40]

                            try:
                                os.makedirs(IMAGES_FOLDER, exist_ok=True)
                                filename = f"{safe_sku}_{safe_pdf_name}_p{current_page_num:03d}_img{best_idx:03d}.webp"
                                image_path = os.path.join(IMAGES_FOLDER, filename)
                                image_obj.save(image_path, format="WEBP")
                            except Exception:
                                image_path = None

                            existing_images.append(
                                {
                                    "pdf_source": PDF_FILENAME,
                                    "page": current_page_num,
                                    "index_on_page": best_idx,
                                    "bbox": bbox,
                                    "image_path": image_path,
                                }
                            )

                            sku_entry["images"] = existing_images

                    # 3b. For SKUs not in any table group on this page, fall back to one representative image per page
                    remaining_skus = [s for s in page_skus if s not in used_skus_in_tables]
                    if remaining_skus:
                        first_img_index = sorted(cropped_cache.keys())[0]
                        image_obj, bbox = cropped_cache[first_img_index]
                        image_bytes = bbox.get("image_bytes")

                        nearby_skus = set(bbox.get("nearby_skus") or [])
                        candidate_skus = set(remaining_skus) | nearby_skus
                        if not candidate_skus:
                            continue

                        # Optional GPT-based SKU matching for remaining SKUs on page.
                        matched_skus = []
                        if image_bytes is not None:
                            matched_skus = _gpt_match_image_to_skus(
                                image_bytes,
                                skus=list(candidate_skus),
                                page_text=page_text or "",
                            )

                        bbox["gpt_matched_skus"] = matched_skus or None

                        target_skus = list(candidate_skus) if not matched_skus else matched_skus

                        for sku in target_skus:

                            sku_entry = product_map.get(sku)
                            if not sku_entry:
                                continue

                            existing_images = sku_entry.get("images", [])
                            existing_keys = set(
                                (img.get("pdf_source"), img.get("page"), img.get("index_on_page"))
                                for img in existing_images
                            )

                            key = (PDF_FILENAME, current_page_num, first_img_index)
                            if key in existing_keys:
                                continue

                            safe_sku = re.sub(r"[^A-Za-z0-9_-]", "_", str(sku))[:40]

                            try:
                                os.makedirs(IMAGES_FOLDER, exist_ok=True)
                                filename = f"{safe_sku}_{safe_pdf_name}_p{current_page_num:03d}_img{first_img_index:03d}.webp"
                                image_path = os.path.join(IMAGES_FOLDER, filename)
                                image_obj.save(image_path, format="WEBP")
                            except Exception:
                                image_path = None

                            existing_images.append(
                                {
                                    "pdf_source": PDF_FILENAME,
                                    "page": current_page_num,
                                    "index_on_page": first_img_index,
                                    "bbox": bbox,
                                    "image_path": image_path,
                                }
                            )

                            sku_entry["images"] = existing_images

        # Print summary image stats for this PDF
        print(
            f"Image stats for {PDF_FILENAME}: total={total_page_images}, "
            f"skipped_small={skipped_small_images}, "
            f"skipped_layout={skipped_layout_images}, "
            f"dropped_by_gpt={dropped_by_gpt_images}, kept={kept_product_images}"
        )

    except FileNotFoundError:
        # ... (rest of the code remains the same)
        print(f"Error: PDF file not found at {pdf_path}")

    except Exception as e:
        # ... (rest of the code remains the same)
        import traceback
        traceback.print_exc()


# --- Main Execution ---
def main():
# ... bestaande code ...
    product_map = {}

    try:
        pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    except FileNotFoundError:
# ... bestaande code ...
        print(f"Error: Input folder not found at {INPUT_FOLDER}")
        print("Please set the 'INPUT_FOLDER' variable at the top of the script.")
        return
    except Exception as e:
# ... bestaande code ...
        print(f"Error reading input folder: {e}")
        return

    if not pdf_files:
# ... bestaande code ...
        print(f"No PDF files found in {INPUT_FOLDER}")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    for pdf_file in pdf_files:
# ... bestaande code ...
        full_pdf_path = os.path.join(INPUT_FOLDER, pdf_file)
        process_pdf_file(full_pdf_path, product_map) 

    print("\nFinished all PDF processing. Starting post-processing...")

    # (Post-processing logic remains unchanged)
    for sku, data in product_map.items():
# ... bestaande code ...
        desc_to_parse = data.get('description', '') 
        if 'description_raw' in data and data.get('description_raw') not in desc_to_parse:
             desc_to_parse += "\n" + data['description_raw']
        if desc_to_parse:
# ... bestaande code ...
            existing_keys = set(k for k, v in data.items() if v is not None)
            description_attrs = extract_attributes_from_text(desc_to_parse, existing_keys=existing_keys)
            for key, value in description_attrs.items():
                if value is not None and (key not in data or data[key] is None):
# ... bestaande code ...
                    if key.endswith('_list') and key[:-5] in data: continue
                    data[key] = value
        if 'power_raw' in data and isinstance(data['power_raw'], str):
# ... bestaande code ...
            hp, kw = parse_power(data['power_raw'])
            if hp is not None and ('power_hp' not in data or data['power_hp'] is None): data['power_hp'] = hp
            if kw is not None and ('power_kw' not in data or data['power_kw'] is None): data['power_kw'] = kw
            if (hp or kw) and 'description' not in data.get('power_raw', ''):
                 data.pop('power_raw', None) 
        if 'pressure_raw' in data and isinstance(data['pressure_raw'], str):
# ... bestaande code ...
             pressure_data = parse_pressure(data['pressure_raw'])
             for key, value in pressure_data.items():
                  if key not in data or data[key] is None:
# ... bestaande code ...
                       data[key] = value
             data.pop('pressure_raw', None)
        if 'dimensions_mm_raw' in data and isinstance(data['dimensions_mm_raw'], str):
# ... bestaande code ...
             dim_data = parse_dimensions(data['dimensions_mm_raw'])
             for key, value in dim_data.items():
                  if key not in data or data[key] is None:
# ... bestaande code ...
                       data[key] = value
             data.pop('dimensions_mm_raw', None)
        
        # Derived numeric fields
        if 'power_hp' in data and 'power_kw' not in data and isinstance(data['power_hp'], (int, float)):
            # Approximate conversion: 1 HP ≈ 0.7457 kW
            data['power_kw_derived'] = round(data['power_hp'] * 0.7457, 3)

        if 'flow_l_min' in data and 'flow_m3_hour' not in data and isinstance(data['flow_l_min'], (int, float)):
            # Convert L/min to m3/hour
            data['flow_m3_hour_derived'] = round(data['flow_l_min'] * 60.0 / 1000.0, 3)

        # Catalog / ID fields
        pdf_source = data.get('pdf_source')
        if pdf_source and 'catalog_name' not in data:
            catalog_name = os.path.splitext(os.path.basename(pdf_source))[0]
            data['catalog_name'] = catalog_name
        if sku and 'product_id' not in data:
            catalog_name = data.get('catalog_name') or ''
            data['product_id'] = f"{catalog_name}:{sku}"

        # Image presence flag
        if 'images' in data and data['images']:
            data['has_images'] = True

        # *** GEWIJZIGD: Sorteer de 'merged_pdf_page' lijst ***
        if 'merged_pdf_page' in data:
            data['merged_pdf_page'].sort() 

    print("Finished post-processing.")
# ... bestaande code ...
    final_product_list = list(product_map.values())
    print(f"Refined data for {len(final_product_list)} unique SKUs from all files.")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# ... bestaande code ...
    print(f"Ensuring output folder exists: {OUTPUT_FOLDER}")

    print(f"Attempting to write combined JSON to: {JSON_OUTPUT_PATH}")
    try:
# ... bestaande code ...
        with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_product_list, f, ensure_ascii=False, indent=4)
        print(f"Successfully wrote combined product data to {JSON_OUTPUT_PATH}")
    except Exception as e:
# ... bestaande code ...
        print(f"Error writing final JSON: {e}")

# --- Script execution ---
if __name__ == "__main__":
    main()