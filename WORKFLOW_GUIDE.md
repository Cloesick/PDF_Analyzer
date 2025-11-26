# PDF Analyzer Workflow Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Smart Workflow Recommendations](#smart-workflow-recommendations)
3. [Complete Pipeline](#complete-pipeline)
4. [Usage Examples](#usage-examples)
5. [Troubleshooting](#troubleshooting)

---

## Overview

This project extracts product data from PDF catalogs and enriches it with images and structured data for e-commerce use.

### Current Tools

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `Extract.py` | Extract products & images from PDFs | Initial extraction from new PDFs |
| `link_images_to_products.py` | Link existing images to products | After extraction, to add image paths |
| `analyze_products.py` | Analyze data quality | Before/after processing to check quality |
| `clean_airpress_images.py` | Remove low-quality images | After extraction, before linking |

---

## Smart Workflow Recommendations

### ✅ **Recommended Approach: Modular Pipeline**

Instead of running everything at once, split your workflow into stages:

```
1. EXTRACT → 2. CLEAN → 3. LINK → 4. VALIDATE → 5. PUBLISH
```

### **Stage 1: Extract Products from PDFs**
```powershell
python Extract.py
```
- Processes all PDFs in `input_pdfs/`
- Creates versioned JSON output (e.g., `input_pdfs_analysis_v7.json`)
- Saves images to configured folder

**Best Practices:**
- ✅ Process PDFs in batches (5-10 at a time for large catalogs)
- ✅ Keep source PDFs organized by supplier/category
- ✅ Review extraction logs for errors

### **Stage 2: Clean Low-Quality Images** (Optional but Recommended)
```powershell
# Dry run (preview only)
python clean_airpress_images.py "C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images"

# Actually delete
python clean_airpress_images.py "C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images" --delete
```

**Removes:**
- Black/dark images (> 70% dark pixels)
- Grayscale contours (technical drawings without product photos)
- Dominant color images (flat backgrounds)
- Extreme aspect ratios (banners/dividers)

### **Stage 3: Link Images to Products**
```powershell
# Using relative paths (recommended for portability)
python link_images_to_products.py

# Using absolute paths
python link_images_to_products.py --absolute-paths

# Save report of products without images
python link_images_to_products.py --report "output/missing_images.json"
```

**This will:**
- Scan `product-images/` folder recursively
- Match images to products by SKU
- Update `media` field with actual image paths
- Generate statistics and optional report

### **Stage 4: Validate Data Quality**
```powershell
python analyze_products.py

# Export statistics
python analyze_products.py --export-stats "output/quality_stats.json"
```

**Checks:**
- Products with/without images
- Attribute coverage (dimensions, power, etc.)
- Brand/category distribution
- Data completeness

### **Stage 5: Publish** (Manual Step)
- Copy JSON to webshop backend
- Verify image paths are accessible
- Test product display

---

## Complete Pipeline

### **Option A: Full Automated Pipeline** (New Data)

For processing everything from scratch:

```powershell
# 1. Extract from PDFs
python Extract.py

# 2. Clean images (dry run first)
python clean_airpress_images.py "product-images"
python clean_airpress_images.py "product-images" --delete

# 3. Link images
python link_images_to_products.py --report "output/missing_images.json"

# 4. Validate
python analyze_products.py --export-stats "output/quality_stats.json"
```

### **Option B: Re-link Existing Images** (Image Location Changed)

If you moved images or need to re-process linking:

```powershell
# Just re-link without re-extracting
python link_images_to_products.py \
    --json "output/products_for_shop.json" \
    --images "C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images" \
    --output "output/products_with_images.json"
```

### **Option C: Incremental Update** (New PDFs Added)

For adding new products without re-processing everything:

1. Move new PDFs to `input_pdfs/`
2. Run `Extract.py` (creates new version)
3. Merge with existing data (manual or custom script)
4. Re-run image linking

---

## Usage Examples

### **Example 1: Quick Quality Check**
```powershell
# See overall statistics
python analyze_products.py
```

### **Example 2: Find Products Without Images**
```powershell
python link_images_to_products.py --report "output/no_images.json"

# Then review the report
cat output/no_images.json
```

### **Example 3: Process Single Catalog**
Temporarily move other PDFs out of `input_pdfs/`, leave only one:
```powershell
# Process just one catalog
python Extract.py
```

### **Example 4: Test Image Cleaning on Subset**
```powershell
# Test on one catalog's images
python clean_airpress_images.py "product-images\makita-catalogus-2022-nl.pdf"
```

---

## Configuration Tips

### **Image Paths in Extract.py**

⚠️ **Important:** Line 39 of `Extract.py` defines where images are saved:

```python
IMAGES_FOLDER = r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\product-images"
```

**Recommendations:**
1. ✅ **Keep extraction and storage separate**: Extract to `PDF_Analyzer\product-images`, then copy to webshop
2. ✅ **Use relative paths** when linking for easier deployment
3. ✅ **Symlink if needed**: Create a symlink from webshop to analyzer folder

### **Handling Large JSON Files**

Your `products_for_shop.json` is 32MB. Consider:

1. **Split by catalog:**
```python
# Custom script to split
products_by_catalog = {}
for product in products:
    catalog = product['catalog']
    if catalog not in products_by_catalog:
        products_by_catalog[catalog] = []
    products_by_catalog[catalog].append(product)

# Save separate files
for catalog, items in products_by_catalog.items():
    with open(f'output/{catalog}.json', 'w') as f:
        json.dump(items, f)
```

2. **Compress:**
```powershell
# Compress JSON with gzip (reduces to ~10% of size)
python -c "import gzip, json; data=json.load(open('products_for_shop.json')); gzip.open('products.json.gz', 'wt').write(json.dumps(data))"
```

3. **Use SQLite:**
Convert JSON to SQLite database for faster queries

---

## Troubleshooting

### **Issue: Images not linking**

**Symptoms:** `link_images_to_products.py` finds 0 matches

**Solutions:**
1. Check image filename pattern matches: `{SKU}_{catalog}_p{page}_img{index}.webp`
2. Verify SKUs in JSON match image filenames (case-insensitive matching)
3. Check image folder path is correct

### **Issue: Extract.py out of memory**

**Solutions:**
1. Process fewer PDFs at once
2. Reduce image resolution (line 815: change `resolution=150` to `100`)
3. Increase system RAM or use pagination

### **Issue: Too many low-quality images**

**Solutions:**
1. Run `clean_airpress_images.py` with default settings
2. Adjust thresholds in script if too aggressive/lenient
3. Review GPT filtering logic in `Extract.py` (line 841)

### **Issue: Wrong image linked to product**

**Causes:**
- Multiple products per page
- SKU detection errors
- Image too close to wrong product

**Solutions:**
1. Check GPT matching logic (line 912 in `Extract.py`)
2. Review nearby SKU detection (lines 796-812)
3. Manually correct in JSON if needed

---

## Performance Benchmarks

Based on your data:

| Task | Time (estimate) | Memory |
|------|-----------------|--------|
| Extract 25 PDFs | 30-60 min | 2-4 GB |
| Clean 1500 images | 5-10 min | 500 MB |
| Link images | 1-2 min | 1-2 GB |
| Analyze JSON | 10-30 sec | 500 MB |

---

## Next Steps & Improvements

### **Short-term (Do Now):**
1. ✅ Run image linking with report generation
2. ✅ Review products without images
3. ✅ Run analysis to check data quality
4. ✅ Clean low-quality images

### **Medium-term (This Week):**
1. Split large JSON by catalog for easier handling
2. Set up incremental update workflow
3. Create SKU→Product index for fast lookups
4. Standardize image paths (relative vs absolute)

### **Long-term (Future):**
1. Add fuzzy SKU matching for variants
2. Implement image deduplication
3. Add category auto-classification (ML-based)
4. Create web UI for manual corrections
5. Add translation support for descriptions

---

## Questions?

Common questions and answers:

**Q: Should I use relative or absolute paths?**  
A: Use relative paths for portability, absolute if images won't move.

**Q: How often should I re-run the full pipeline?**  
A: Only when adding new PDFs. Otherwise, just re-link images.

**Q: Can I customize SKU patterns?**  
A: Yes, edit regex patterns in `Extract.py` lines 60-65.

**Q: Why are some images not linking?**  
A: Check SKU naming consistency and run with `--report` flag to debug.

**Q: How do I add new attributes to extract?**  
A: Add regex patterns around line 90 in `Extract.py` and update extraction logic.

---

**Last Updated:** November 2024  
**Version:** 1.0
