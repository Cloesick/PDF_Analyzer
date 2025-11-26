# Image Linking Quick Start

## 🚀 Quick Start (3 Steps)

### **1. Run Image Linking**

**Option A: Double-click the batch file**
```
run_image_linking.bat
```

**Option B: Use command line**
```powershell
python link_images_to_products.py
```

### **2. Check Results**

The script will:
- ✅ Scan `product-images/` folder for all images
- ✅ Match images to products by SKU
- ✅ Update JSON with actual image paths
- ✅ Generate statistics and missing images report

### **3. Review Output**

Check these files:
- `output/products_with_images.json` - Updated product data
- `output/missing_images_report.json` - Products without images

---

## 📊 What You'll Get

### Before (Current JSON):
```json
{
  "sku": "ABSBU040",
  "media": [
    {
      "url": "https://example.com/media/ABSBU040_abs-persluchtbuizen_p005_img000.webp",
      "role": "main"
    }
  ]
}
```

### After (Linked Images):
```json
{
  "sku": "ABSBU040",
  "media": [
    {
      "url": "../product-images/abs-persluchtbuizen.pdf/ABSBU040_abs-persluchtbuizen_p005_img000.webp",
      "role": "main",
      "type": "image",
      "format": "webp"
    },
    {
      "url": "../product-images/abs-persluchtbuizen.pdf/ABSBU040_abs-persluchtbuizen_p005_img001.webp",
      "role": "gallery",
      "type": "image",
      "format": "webp"
    }
  ],
  "image_paths": [
    "../product-images/abs-persluchtbuizen.pdf/ABSBU040_abs-persluchtbuizen_p005_img000.webp",
    "../product-images/abs-persluchtbuizen.pdf/ABSBU040_abs-persluchtbuizen_p005_img001.webp"
  ]
}
```

---

## 🎯 Smart Suggestions Summary

### **1. Organize Your Workflow in Stages**

Instead of one big script, use this pipeline:

```
Extract PDFs → Clean Images → Link Images → Validate → Deploy
```

### **2. Key Improvements**

✅ **Separate concerns**: Extraction vs. enrichment vs. validation  
✅ **Streaming analysis**: Handle 32MB+ JSON files efficiently  
✅ **Quality control**: Automated image cleaning and data validation  
✅ **Incremental updates**: Only process what changed  
✅ **Better debugging**: Reports for missing data  

### **3. Best Practices**

| Do ✅ | Don't ❌ |
|-------|----------|
| Use relative paths for portability | Hardcode absolute paths |
| Run analysis before/after changes | Skip validation |
| Keep image linking separate | Mix extraction & linking |
| Generate missing data reports | Ignore data quality |
| Process PDFs in batches | Load everything at once |

---

## 🔧 Command Reference

### **Link Images**
```powershell
# Basic usage (updates original JSON)
python link_images_to_products.py

# Save to different file
python link_images_to_products.py --output output/new_products.json

# Use absolute paths instead of relative
python link_images_to_products.py --absolute-paths

# Generate missing images report
python link_images_to_products.py --report output/missing.json

# Custom paths
python link_images_to_products.py \
    --json output/products.json \
    --images C:\Path\To\Images \
    --output output/updated.json
```

### **Analyze Data Quality**
```powershell
# Quick analysis
python analyze_products.py

# With statistics export
python analyze_products.py --export-stats output/stats.json

# Analyze different file
python analyze_products.py output/products_with_images.json
```

### **Clean Low-Quality Images**
```powershell
# Preview what would be deleted (safe)
python clean_airpress_images.py product-images

# Actually delete
python clean_airpress_images.py product-images --delete
```

---

## 📁 File Structure

```
PDF_Analyzer/
├── input_pdfs/                    # Source PDF catalogs
├── product-images/                # Extracted product images
│   ├── catalog1.pdf/
│   │   ├── SKU1_catalog1_p001_img000.webp
│   │   └── SKU2_catalog1_p002_img000.webp
│   └── catalog2.pdf/
│       └── ...
├── output/
│   ├── products_for_shop.json     # Original extracted data
│   ├── products_with_images.json  # After image linking
│   ├── missing_images_report.json # Products without images
│   └── quality_stats.json         # Data quality statistics
├── Extract.py                     # Main extraction script
├── link_images_to_products.py     # NEW: Link images
├── analyze_products.py            # NEW: Quality analysis
├── clean_airpress_images.py       # Clean bad images
├── run_image_linking.bat          # NEW: Quick launcher
├── WORKFLOW_GUIDE.md              # NEW: Detailed guide
└── README_IMAGE_LINKING.md        # This file
```

---

## 🎓 How Image Matching Works

The script matches images to products using this logic:

1. **Extract SKU from filename**: `ABSBU040_catalog_p005_img000.webp` → SKU: `ABSBU040`
2. **Normalize for comparison**: Convert to uppercase, trim whitespace
3. **Find all images for each SKU**: Group by normalized SKU
4. **Sort images**: First image becomes "main", rest are "gallery"
5. **Calculate relative path**: From JSON location to image location
6. **Update product data**: Add to `media` and `image_paths` fields

### Filename Pattern Expected:
```
{SKU}_{catalog_name}_p{page_number}_img{image_index}.{extension}
```

Examples:
- ✅ `ABSBU040_abs-persluchtbuizen_p005_img000.webp`
- ✅ `X0817015_makita-catalogus_p123_img002.png`
- ✅ `HL-150-24_airpress-eng_p045_img001.webp`

---

## 🐛 Troubleshooting

### Problem: "Found 0 images matching SKU patterns"

**Solution:**
1. Check image filenames match the expected pattern
2. Verify images exist in the specified folder
3. Check SKUs in JSON match image filenames

### Problem: "Products without images: 500+"

**Solutions:**
1. Run with `--report` to see which SKUs are missing
2. Check if images were generated during extraction
3. Verify image folder path is correct
4. Check if SKUs match between JSON and filenames

### Problem: "Script uses too much memory"

**Solutions:**
1. Use `analyze_products.py` instead (streams data)
2. Process in smaller batches
3. Split JSON by catalog first

### Problem: "Wrong images linked to products"

**Investigation:**
1. Check the `image_paths` field in the product
2. Verify SKU is correct in both JSON and filename
3. Look for duplicate/similar SKUs

---

## 📈 Expected Results

Based on your current data:

- **Total products**: ~7,000-10,000 (estimate from 32MB JSON)
- **Images found**: ~1,500 images in product-images folder
- **Match rate**: 50-80% (depends on extraction quality)
- **Processing time**: 1-2 minutes

After running the script, you should see output like:

```
Scanning image folder: C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images
Found 1537 total images
Matched 1489 images to SKU patterns
Unique SKUs with images: 1234

Linking images to products...

==============================================================
RESULTS
==============================================================
Total products:              8542
Products with images:        1234 (14.4%)
Products without images:     7308 (85.6%)
Total images linked:         1489
Products updated:            1234
Average images per product:  1.21
==============================================================
```

---

## 🎯 Next Steps

After linking images:

1. **Review the report**: Check `missing_images_report.json` for products without images
2. **Run quality analysis**: `python analyze_products.py`
3. **Test in webshop**: Copy JSON to your web application
4. **Iterate**: Re-extract PDFs with missing products or adjust matching logic

---

## 💡 Pro Tips

1. **Backup your JSON before running** - The script can overwrite files
2. **Use relative paths** - Makes deployment easier
3. **Generate reports** - Helps identify data quality issues
4. **Run analysis regularly** - Track improvement over time
5. **Process incrementally** - Don't re-process everything each time

---

## 📞 Need Help?

Check the detailed workflow guide: `WORKFLOW_GUIDE.md`

Common issues are documented in the troubleshooting section above.
