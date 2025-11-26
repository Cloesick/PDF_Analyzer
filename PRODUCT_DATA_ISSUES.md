# Product Data Rendering Issues - Diagnosis & Fix

## 🔍 **Problem Identified**

Your products aren't rendering properly because the `products_for_shop.json` has incomplete data:

### Current Data (Bad):
```json
{
  "sku": "DEBWST06",
  "name": "DEBWST06",  ← Just SKU, not descriptive!
  "category": "makita catalogus 2022 nl",  ← Catalog name, not category!
  "description": null,  ← No description!
  "attributes": {},  ← No specs!
  "media": [...]  ← Images are correct ✓
}
```

### How It Displays:
```
Title: "makita catalogus 2022 nl DEBWST06"  ← Ugly!
Description: (empty)
Specs: (none)
```

---

## 🎯 **Root Cause**

You have **TWO different `products_for_shop.json` files**:

### 1. **PDF_Analyzer version** (Raw extraction data)
- **Path:** `C:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json`
- **Created by:** `link_images_to_products.py`
- **Structure:** Flat dictionary with all extracted fields
- **Has:** Descriptions, attributes, technical specs
- **Images:** Linked via `image_paths` array

### 2. **Webshop version** (Structured format)
- **Path:** `C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\data\products_for_shop.json`
- **Created by:** `build_shop_feed.py` (different script)
- **Structure:** Nested objects (media, price, stock, seo, source)
- **Has:** Clean structure but MISSING data
- **Images:** Linked via `media` array

---

## 🔧 **What Needs to Happen**

You need to **merge** the rich data from PDF_Analyzer with the structured format your webshop expects.

### Option A: Create New Build Script

Create a new `build_webshop_products.py` that:
1. Reads raw extraction from `input_pdfs_analysis_v8.json`
2. Enriches each product with:
   - Proper `name` (not just SKU)
   - Actual `description`
   - Real `product_category` (not catalog name)
   - Populated `attributes` from extracted specs
3. Links images using the `link_images_to_products.py` logic
4. Outputs in webshop format

### Option B: Fix Existing Data Manually

For demo purposes, manually edit products to add:
```json
{
  "name": "Makita DHP484Z Klopboormachine",  // Real name
  "product_category": "Klopboormachines",    // Real category
  "description": "18V Li-Ion klopboormachine...",  // Description
  "power_kw": 0.6,
  "voltage_v": 18,
  "weight_kg": 1.7
}
```

---

## ✅ **Working Example**

I created a sample with proper data at:
```
DemaWebshop/dema-webshop/public/data/sample_product_working.json
```

This shows what products SHOULD look like:

```json
{
  "sku": "DHP484Z",
  "name": "Makita DHP484Z Klopboormachine",  ✓ Descriptive name
  "product_category": "Klopboormachines",    ✓ Real category
  "description": "18V Li-Ion klopboormachine...",  ✓ Description
  "imageUrl": "/product-images/makita.../img000.webp",  ✓ Image
  "price": 159.99,  ✓ Price
  "voltage_v": 18,  ✓ Specs
  "power_kw": 0.6,
  "weight_kg": 1.7
}
```

This will display as:
```
Title: "Klopboormachines DHP484Z"  (or just "Makita DHP484Z Klopboormachine")
Description: "18V Li-Ion klopboormachine..."
Specs: Power: 0.6 kW | Voltage: 18V | Weight: 1.7 kg
```

---

## 🎨 **How Your Frontend Works**

Your `formatProductForCard.ts` creates titles like this:

```typescript
// Line 57-58:
const type = deriveType(p);  // Gets category or derives from description
const title = `${type} ${p.sku || ''}`.trim();  // Combines them

// Examples:
// If product_category = "Compressoren" and sku = "HL425"
// → title = "Compressoren HL425" ✓

// If product_category = "makita-catalogus-2022-nl" and sku = "DHP484Z"
// → title = "makita-catalogus-2022-nl DHP484Z" ✗ BAD!
```

**Solution:** Put proper categories in `product_category`:
- ✓ "Compressoren", "Klopboormachines", "Hogedrukreinigers"
- ✗ "makita-catalogus-2022-nl", "abs-persluchtbuizen"

---

## 📊 **Data Comparison**

### What You Have Now:
| Field | Current Value | What Frontend Shows |
|-------|--------------|---------------------|
| `name` | "DEBWST06" | (not used directly) |
| `product_category` | "makita catalogus 2022 nl" | Title: "makita catalogus 2022 nl DEBWST06" |
| `description` | null | (empty) |
| `attributes` | {} | (no specs shown) |
| `media` | ✓ correct | ✓ Images show |

### What You Need:
| Field | Should Be | What Frontend Shows |
|-------|-----------|---------------------|
| `name` | "Makita DHP484Z Klopboormachine" | Used in alt text, meta |
| `product_category` | "Klopboormachines" | Title: "Klopboormachines DHP484Z" |
| `description` | "18V Li-Ion klopboormachine..." | Shows under title |
| `voltage_v` | 18 | Spec: "Electrical: 18V" |
| `power_kw` | 0.6 | Spec: "Power: 0.6 kW" |
| `media` | ✓ correct | ✓ Images show |

---

## 🚀 **Quick Test**

To verify the format works, temporarily replace your products JSON with the sample:

```powershell
# Backup current
Copy-Item public/data/products_for_shop.json public/data/products_for_shop.json.backup

# Use sample
Copy-Item public/data/sample_product_working.json public/data/products_for_shop.json

# Test in browser
# http://localhost:3000/products

# Restore
Move-Item -Force public/data/products_for_shop.json.backup public/data/products_for_shop.json
```

You should see the sample products render beautifully with proper names, descriptions, and specs!

---

## 💡 **Next Steps**

1. **Immediate (Demo):** Use `sample_product_working.json` to show how it should look
2. **Short-term:** Manually enrich top 50 products for demo
3. **Long-term:** Create a proper build script that merges extraction data with webshop format

---

## 📝 **Build Script Needed**

You need a script like this:

```python
# build_enriched_webshop_products.py

import json
from pathlib import Path

# Load raw extraction (has descriptions, specs)
raw_products = json.load(open('output/input_pdfs_analysis_v8.json'))

# Load current webshop products (has structure, images)
webshop_products = json.load(open('../DemaWebshop/public/data/products_for_shop.json'))

# Create lookup
raw_by_sku = {p['sku']: p for p in raw_products}

# Enrich webshop products
for product in webshop_products:
    sku = product['sku']
    if sku in raw_by_sku:
        raw = raw_by_sku[sku]
        
        # Add missing data
        product['name'] = raw.get('name') or sku
        product['description'] = raw.get('description')
        product['product_category'] = derive_category(raw)  # Clean category
        
        # Add specs
        for key in ['power_kw', 'voltage_v', 'pressure_max_bar', 'weight_kg']:
            if key in raw:
                product[key] = raw[key]

# Save enriched
json.dump(webshop_products, open('output/products_enriched.json', 'w'), indent=2)
```

---

## 🎯 **Summary**

**Problem:** Products use catalog names as categories and have no descriptions/specs  
**Cause:** Two different JSON formats from different scripts  
**Solution:** Merge rich extraction data with structured webshop format  
**Quick Fix:** Use `sample_product_working.json` to test/demo  

Your images are linked correctly! You just need to enrich the product metadata. 🎨
