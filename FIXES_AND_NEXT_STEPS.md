# Image Linking Fixes & Next Steps

## 🎯 Problem Summary

You ran `link_images_to_products.py` and got:
- ✅ **8,598 products** with images (49.7%)
- ❌ **8,680 products** without images (50.3%)

### Root Cause
`Extract.py` was saving images to a **different location** than where `link_images_to_products.py` looks:

- **Extract.py saves to:** `C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\product-images`
- **Linker looks in:** `C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images`

Only some catalogs' images were manually copied, resulting in 50% coverage.

---

## ✅ Fixes Applied

### 1. **Updated Extract.py (Line 39)**
```python
# OLD (hardcoded path to DemaWebshop):
IMAGES_FOLDER = r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\product-images"

# NEW (project-relative path):
IMAGES_FOLDER = os.path.join(PROJECT_ROOT, "product-images")
```

**Result:** Extract.py will now save images to the correct location.

### 2. **Fixed link_images_to_products.py**
Changed matching strategy from SKU-based to **catalog+page-based** because your image filenames don't contain SKUs:

- **Before:** Tried to extract SKU from filename → Failed (0 matches)
- **After:** Matches images by `(catalog_name, page_number)` → Success (8,598 matches)

### 3. **Created copy_existing_images.py**
New utility to copy already-extracted images from DemaWebshop folder to PDF_Analyzer folder.

---

## 🚀 Next Steps (Choose Your Approach)

### **Option A: Copy Existing Images + Extract Missing Catalogs** ⭐ RECOMMENDED

This preserves work already done and only processes what's missing.

```powershell
# Step 1: Copy already-extracted images (preview first)
python copy_existing_images.py

# Step 2: Actually copy them
python copy_existing_images.py --copy

# Step 3: Re-run image linking to get 100% coverage
python link_images_to_products.py --report output/missing_after_copy.json

# Step 4: Check which catalogs still need extraction
# (Should be much fewer now)
```

**Why this approach:**
- ✅ Doesn't waste time re-extracting existing images
- ✅ Faster (only process missing catalogs)
- ✅ Preserves GPT filtering already done

### **Option B: Full Re-extraction from Scratch**

Start fresh and extract everything again with the fixed Extract.py.

```powershell
# WARNING: This will take 30-60 minutes and use OpenAI API credits

# Step 1: Backup existing images (optional)
Move-Item product-images product-images-backup

# Step 2: Run full extraction
python Extract.py

# Step 3: Link images
python link_images_to_products.py --report output/missing.json

# Step 4: Verify results
python analyze_products.py
```

**Why this approach:**
- ✅ Clean slate with corrected paths
- ❌ Takes much longer
- ❌ Uses more API credits (GPT filtering)
- ❌ Might get different results due to GPT variations

---

## 📊 Expected Results After Fix

### Current Status (Before Fix):
```
Total products:              17,278
Products with images:        8,598 (49.7%)
Products without images:     8,680 (50.3%)
```

### After Option A (Copy + Link):
```
Total products:              17,278
Products with images:        ~17,000+ (98%+)
Products without images:     <300 (catalogs with no images extracted)
```

### After Option B (Full Re-extraction):
```
Total products:              17,278
Products with images:        ~16,500-17,000 (95-98%)
Products without images:     <500 (products genuinely without images)
```

---

## 🔍 Catalogs Currently Missing Images

Top 10 catalogs without images:
1. **slangkoppelingen** - 1,555 products
2. **digitale-versie-pompentoebehoren-compressed** - 1,138 products
3. **bronpompen** - 986 products
4. **catalogus-aandrijftechniek-150922** - 655 products (partial)
5. **drukbuizen** - 568 products (partial)
6. **verzinkte-buizen** - 510 products (partial)
7. **pe-buizen** - 485 products (partial)
8. **kunststof-afvoerleidingen** - 421 products (partial)
9. **zwarte-draad-en-lasfittingen** - 307 products
10. **rubber-slangen** - 258 products

Note: "Partial" means some products from that catalog have images, others don't.

---

## 📝 Quick Command Reference

### Copy Existing Images
```powershell
# Preview what will be copied (safe)
python copy_existing_images.py

# Actually copy
python copy_existing_images.py --copy
```

### Link Images
```powershell
# Standard linking with report
python link_images_to_products.py --report output/missing.json

# Or use the batch file
run_image_linking.bat
```

### Analyze Results
```powershell
# See detailed statistics
python analyze_products.py

# Export stats to file
python analyze_products.py --export-stats output/stats.json
```

### Extract Images from PDFs
```powershell
# Run full extraction (takes 30-60 min)
python Extract.py
```

---

## ⚠️ Important Notes

### 1. **API Costs**
Extract.py uses GPT-4o for:
- Filtering product images vs logos/decorations
- Matching images to SKUs on multi-product pages

**Cost estimate:** ~$0.50-2.00 per catalog depending on size

### 2. **Folder Structure**
After copying/extracting, your structure should be:
```
PDF_Analyzer/
├── product-images/
│   ├── airpress-catalogus-eng.pdf/
│   │   ├── airpress_..._p001_img000.webp
│   │   └── ...
│   ├── abs-persluchtbuizen.pdf/
│   └── ...
├── output/
│   ├── products_for_shop.json
│   └── missing.json
└── ...
```

### 3. **Webshop Deployment**
Once images are linked:
1. Copy `products_for_shop.json` to your webshop
2. Copy `product-images/` folder to webshop's public directory
3. Update webshop config to point to correct image paths

### 4. **Image Formats**
- Extract.py saves as **WebP** (modern, compressed format)
- Some older browsers may not support WebP
- Consider fallback to PNG/JPG if needed

---

## 🎯 Recommended Action Plan

**If you want results quickly (15 minutes):**
```powershell
# 1. Copy existing images (5 min)
python copy_existing_images.py --copy

# 2. Re-link images (2 min)
python link_images_to_products.py --report output/final_missing.json

# 3. Analyze results (1 min)
python analyze_products.py

# 4. Check what's still missing
cat output/final_missing.json
```

**If you want perfect results (60 minutes):**
```powershell
# Re-extract everything fresh
python Extract.py

# Link images
python link_images_to_products.py

# Analyze
python analyze_products.py
```

---

## ✅ Verification Checklist

After running the fix:
- [ ] Run `python link_images_to_products.py`
- [ ] Check statistics show >95% coverage
- [ ] Review `missing.json` for remaining gaps
- [ ] Run `python analyze_products.py`
- [ ] Spot-check a few products in the JSON have correct image paths
- [ ] Test image paths are accessible from webshop
- [ ] Deploy to webshop and verify images load

---

## 🆘 Troubleshooting

### "Copy script says source folder not found"
The DemaWebshop folder path might be different. Update `SOURCE_FOLDER` in `copy_existing_images.py`.

### "Still getting 0 images after copying"
1. Check that images were actually copied to `product-images/`
2. Verify folder names match PDF names (case-sensitive)
3. Run linking with verbose output

### "Some catalogs still missing all images"
Those catalogs probably were never extracted. Run Extract.py on just those PDFs:
1. Move other PDFs out of `input_pdfs/` temporarily
2. Leave only the missing catalog PDFs
3. Run `python Extract.py`
4. Move all PDFs back

---

Last Updated: November 26, 2025
