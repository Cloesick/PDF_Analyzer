# Table Products Guide - Shared Images & Descriptions

## 📋 Concept: Product Variants in Tables

Many catalog PDFs have tables where each row represents a **variant** of the same product:

### Example: ABS Pressure Pipes

```
┌─────────────────────────────────────────┐
│  [Product Image: ABS Pipe]              │
│                                         │
└─────────────────────────────────────────┘

Product: ABS Persluchtbuizen (Pressure Pipes)
Description: High-quality ABS compressed air pipes

┌────────────┬──────────┬────────┬────────┐
│ Article    │ Diameter │ Length │ Price  │
├────────────┼──────────┼────────┼────────┤
│ ABSBU020   │ 20mm     │ 6m     │ €XX.XX │
│ ABSBU032   │ 32mm     │ 6m     │ €XX.XX │
│ ABSBU040   │ 40mm     │ 6m     │ €XX.XX │
│ ABSBU050   │ 50mm     │ 6m     │ €XX.XX │
│ ABSBU063   │ 63mm     │ 6m     │ €XX.XX │
└────────────┴──────────┴────────┴────────┘
```

### What Should Be Shared:
- ✅ **Same Product Image** (all show the ABS pipe)
- ✅ **Same Base Description** ("High-quality ABS compressed air pipes")
- ❌ **Different Dimensions** (20mm, 32mm, 40mm, etc.)
- ❌ **Different SKUs** (ABSBU020, ABSBU032, etc.)

---

## ✅ Current Implementation

### 1. **Images - Already Sharing Correctly ✓**

Your `link_images_to_products.py` matches images by **catalog + page number**:

```python
# All products from page 5 of abs-persluchtbuizen.pdf get the same images
key = ("abs-persluchtbuizen", 5)
images = catalog_page_to_images[key]

# ABSBU020, ABSBU032, ABSBU040 all on page 5 → all get same images ✓
```

**Result:** Product variants automatically share images from their page.

### 2. **Descriptions - Partially Sharing**

Extract.py currently extracts descriptions per table row:

```python
# Current behavior (line 687-711):
for row in table:
    description = extract_from_description_column(row)
    product_map[sku]['description'] = description
    # Each SKU might get slightly different description
```

**Issue:** Each variant might get:
- "ABS pipe 20mm diameter compressed air"
- "ABS pipe 32mm diameter compressed air"  
- "ABS pipe 40mm diameter compressed air"

Instead of sharing: "ABS compressed air pipe" + dimensions as attributes

---

## 🔧 Enhancement: Consolidate Table Descriptions

Use the new `enhance_table_descriptions.py` script:

### How It Works:

1. **Groups products from same table** (same catalog + page + SKU pattern)
2. **Finds common base description** (removes dimension variations)
3. **Shares base description** across all variants
4. **Keeps dimension info** as separate attributes

### Example Transformation:

**Before:**
```json
{
  "sku": "ABSBU020",
  "description": "ABS persluchtbuis 20mm diameter 6 meter",
  "dimension_mm": null
},
{
  "sku": "ABSBU032",
  "description": "ABS persluchtbuis 32mm diameter 6 meter",
  "dimension_mm": null
}
```

**After:**
```json
{
  "sku": "ABSBU020",
  "description": "ABS persluchtbuis",
  "dimension_mm": 20,
  "is_table_variant": true
},
{
  "sku": "ABSBU032",
  "description": "ABS persluchtbuis",
  "dimension_mm": 32,
  "is_table_variant": true
}
```

---

## 🚀 Usage

### Run Enhancement After Extraction:

```powershell
# 1. Extract products (as usual)
python Extract.py

# 2. Link images (as usual)
python link_images_to_products.py

# 3. NEW: Enhance table descriptions
python enhance_table_descriptions.py

# 4. Verify results
python analyze_products.py
```

### Options:

```powershell
# Preview without modifying (dry run)
python enhance_table_descriptions.py --input output/products_for_shop.json --output output/products_enhanced.json

# Apply to original file (with confirmation)
python enhance_table_descriptions.py
```

---

## 📊 Benefits

### For E-commerce:

1. **Better SEO** - Cleaner product titles and descriptions
2. **Easier Filtering** - Dimensions as structured attributes
3. **Consistent Display** - Variants look related
4. **Reduced Duplication** - Same description shared across variants

### For Data Quality:

1. **Normalized Descriptions** - No redundant dimension info in text
2. **Searchable Attributes** - Filter by dimension_mm instead of parsing text
3. **Variant Detection** - `is_table_variant` flag marks related products
4. **Cleaner JSON** - More structured data

---

## 📈 Expected Impact

### Example Catalog: abs-persluchtbuizen.pdf

**Before Enhancement:**
```
239 products with 239 unique descriptions
Average description length: 45 characters
```

**After Enhancement:**
```
239 products with ~30 unique base descriptions
Average description length: 25 characters
Products grouped into ~30 variant families
```

### Real-World Example:

For a catalog with 1,000 products in 50 tables:
- **Before:** 1,000 unique descriptions (mostly redundant)
- **After:** ~200 base descriptions + dimensional attributes
- **Benefit:** 80% reduction in description redundancy

---

## 🎯 Best Practices

### 1. Run Enhancement After Image Linking

```powershell
python Extract.py
python link_images_to_products.py
python enhance_table_descriptions.py  # <-- Run this last
```

### 2. Verify Results

Check a few products to ensure descriptions make sense:

```powershell
python -c "
import json
products = json.load(open('output/products_for_shop.json'))
variants = [p for p in products if p.get('is_table_variant')]
print(f'Table variants: {len(variants)}')
for p in variants[:5]:
    print(f\"  {p['sku']}: {p.get('description', 'N/A')}\")
"
```

### 3. Manual Review for Important Catalogs

Some tables might need manual description adjustment:
- Technical specifications tables
- Multi-product comparison tables
- Accessory/spare parts tables

---

## 🔍 How It Detects Tables

The script uses these heuristics:

1. **Same Page:** Products on the same PDF page
2. **Similar SKUs:** SKUs with common prefix (e.g., ABSBU*, ABSB*)
3. **Group Size:** At least 3 products (tables typically have multiple rows)
4. **Similar Descriptions:** Descriptions share common words

### Detection Example:

```
Page 5 products:
  ABSBU020 - "ABS pipe 20mm"  ─┐
  ABSBU032 - "ABS pipe 32mm"  ├─ Detected as table (same prefix, page, similar desc)
  ABSBU040 - "ABS pipe 40mm"  ─┘
  
  XYZ123   - "Different product" ─ Not grouped (different prefix)
```

---

## ⚙️ Configuration

You can adjust grouping sensitivity by editing `enhance_table_descriptions.py`:

### SKU Prefix Length (Line 85):
```python
# More strict (fewer groups, more precise):
prefix = sku[:6]  # ABSBU0*, ABSBU2*

# More lenient (more groups, catch more variants):
prefix = sku[:3]  # ABS*, XYZ*

# Current (balanced):
prefix = sku[:4]  # ABSB*, ABSC*
```

### Minimum Group Size (Line 95):
```python
# Only large tables:
if len(group) >= 5:

# Include smaller variant sets:
if len(group) >= 2:

# Current (3+ products):
if len(group) >= 3:
```

---

## 📝 Integration with Webshop

### Display Variants as Related Products:

```javascript
// In your webshop, group variants:
const variants = products.filter(p => 
  p.is_table_variant && 
  p.description === currentProduct.description
);

// Show: "Available in sizes: 20mm, 32mm, 40mm, 50mm"
const sizes = variants.map(v => v.dimension_mm);
```

### SEO-Friendly URLs:

```javascript
// Instead of:
/product/absbu020-abs-pipe-20mm-diameter-6-meter

// Use:
/product/abs-pipe/20mm  // Clean, variant-aware
```

---

## 🎯 Summary

**Key Insight:** Products in the same table are variants, not separate products.

**Current Status:**
- ✅ Images already shared correctly
- ⚠️ Descriptions partially shared (needs enhancement)

**Action:**
Run `enhance_table_descriptions.py` after extraction to:
- Share base descriptions across variants
- Extract dimensions as structured attributes
- Mark products as table variants

**Result:**
Cleaner, more structured product data that's easier to search, filter, and display! 🚀

---

Last Updated: November 26, 2025
