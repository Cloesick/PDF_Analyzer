# Coverage Improvement Guide

## 🎯 Current Coverage: 50% → Target: 95%+

### Quick Summary
- **Step 1:** Copy existing images (50% → 90-95%)
- **Step 2:** Extract missing catalogs (90% → 98%)
- **Step 3:** Fine-tune extraction (98% → 99%+)

---

## 📊 Strategy 1: Copy Existing Images (Immediate)

**Time:** 5 minutes  
**Effort:** Low  
**Gain:** +40-45% coverage

```powershell
# Copy images from DemaWebshop to PDF_Analyzer
python copy_existing_images.py --copy

# Re-link images
python link_images_to_products.py --report output/after_copy.json

# Check results
python analyze_products.py
```

**Expected Result:** 90-95% coverage

---

## 📊 Strategy 2: Extract Missing Catalogs Only

**Time:** 30-45 minutes  
**Effort:** Medium  
**Gain:** +5-8% coverage

### Catalogs with 0% Coverage (High Priority):
1. `offerteaanvraag-bronpomp.pdf` (2 products)
2. `plat-oprolbare-slangen.pdf` (75 products)
3. `pu-afzuigslangen.pdf` (126 products)
4. `rubber-slangen.pdf` (258 products)
5. `zuigerpompen (1).pdf` (30 products)
6. `zwarte-draad-en-lasfittingen (1).pdf` (307 products)

### Catalogs with Low Coverage (Medium Priority):
7. `abs-persluchtbuizen.pdf` (239/241 missing - 0.8%)
8. `bronpompen.pdf` (986/1041 missing - 5.3%)
9. `pomp-specials.pdf` (67/86 missing - 22%)
10. `rvs-draadfittingen.pdf` (26/34 missing - 23.5%)

### Quick Method:
```powershell
# Use the helper script
python extract_missing_catalogs.py
# Follow prompts to move PDFs, extract, then restore

# Or manual method:
# 1. Create temp folder, move well-covered catalogs there
# 2. Run Extract.py on remaining catalogs
# 3. Move catalogs back
```

---

## 📊 Strategy 3: Optimize Extract.py Settings

### A. Reduce Minimum Image Size Threshold

**Current:** Line 786 in Extract.py
```python
MIN_IMAGE_AREA = 10000  # ~100x100 px
```

**Try:**
```python
MIN_IMAGE_AREA = 5000  # ~70x70 px (captures smaller product images)
```

**Impact:** Captures smaller product images that might be missed

### B. Disable GPT Filtering Temporarily

**Current:** Lines 841-843
```python
if not _gpt_is_product_image(image_bytes):
    dropped_by_gpt_images += 1
    continue
```

**Temporarily comment out for catalogs with few images:**
```python
# Skip GPT filtering for catalogs with very few images
# if not _gpt_is_product_image(image_bytes):
#     dropped_by_gpt_images += 1
#     continue
```

**Impact:** Keeps more images (may include logos/decorations but increases coverage)

### C. Reduce Smart Crop Aggressiveness

**Current:** Lines 827-834 (layout image filter)
```python
if (
    short_side < 200
    and aspect_ratio_img > 3.0
    and dominant_frac > 0.75
    and std_gray < 60
):
    skipped_layout_images += 1
    continue
```

**Try:**
```python
if (
    short_side < 150  # Less strict on size
    and aspect_ratio_img > 4.0  # Less strict on aspect ratio
    and dominant_frac > 0.85  # More strict on dominance
    and std_gray < 40  # More strict on variance
):
    skipped_layout_images += 1
    continue
```

**Impact:** Keeps borderline images

---

## 📊 Strategy 4: Handle Special PDF Types

Some catalogs may have different structures:

### A. Images as Background (Not Extracted)

Some PDFs embed images as page backgrounds. Check:
```powershell
# Test if PDF has background images
python -c "
import pdfplumber
pdf = pdfplumber.open('input_pdfs/rubber-slangen.pdf')
page = pdf.pages[0]
print(f'Images found: {len(page.images)}')
print(f'Has figures: {len(page.figures) if hasattr(page, \"figures\") else \"N/A\"}')
"
```

**Solution:** Extract page as image, then crop:
```python
# Add to Extract.py for problematic PDFs
if len(page.images) == 0:
    # Render entire page as image
    page_img = page.to_image(resolution=150)
    # Save as fallback product image
```

### B. Text-Only Catalogs

Some catalogs might not have images at all (just tables).

**Check:**
```powershell
# List PDFs by image count
Get-ChildItem product-images -Directory | ForEach-Object { 
    $count = (Get-ChildItem $_.FullName -File).Count
    [PSCustomObject]@{Catalog=$_.Name; Images=$count}
} | Sort-Object Images
```

---

## 📊 Strategy 5: Manual Image Association

For the remaining ~1-2% without images:

### A. Products That Genuinely Have No Images

Some products might just be in text tables without accompanying images.

**Identify them:**
```powershell
python -c "
import json
missing = json.load(open('output/missing_images.json'))
# Filter to products from catalogs with good overall coverage
good_coverage_cats = ['makita-catalogus-2022-nl', 'airpress-catalogus-eng']
suspect = [p for p in missing if p['catalog'] in good_coverage_cats]
print(f'Products missing images in well-covered catalogs: {len(suspect)}')
"
```

### B. Use Generic/Placeholder Images

For products without specific images, use category-generic images:
```python
# Add fallback logic to link_images_to_products.py
if not matching_images:
    # Use category-based generic image
    category = product.get('category', '')
    generic_img = f'generic/{category.replace(" ", "_")}.webp'
    if os.path.exists(generic_img):
        product['media'] = [{'url': generic_img, 'role': 'placeholder'}]
```

---

## 📊 Strategy 6: Multi-Page Product Images

Some products span multiple pages. Enhance page detection:

```python
# In Extract.py, associate products with adjacent pages too
for page_num in [current_page, current_page-1, current_page+1]:
    if 0 < page_num <= num_pages:
        # Check for images on adjacent pages
        pass
```

---

## 🎯 Recommended Action Plan

### Phase 1: Quick Wins (Today - 1 hour)
```powershell
# 1. Copy existing images
python copy_existing_images.py --copy

# 2. Re-link
python link_images_to_products.py

# 3. Analyze gaps
python extract_missing_catalogs.py analyze
```

**Expected: 50% → 92%**

### Phase 2: Fill Gaps (Tomorrow - 2 hours)
```powershell
# 1. Extract only missing catalogs
python extract_missing_catalogs.py
python Extract.py
python extract_missing_catalogs.py restore

# 2. Link again
python link_images_to_products.py

# 3. Check coverage
python analyze_products.py
```

**Expected: 92% → 98%**

### Phase 3: Fine-Tuning (If needed - 1 hour)
```powershell
# 1. Adjust Extract.py thresholds
# 2. Re-extract problematic catalogs
# 3. Add generic placeholder images
```

**Expected: 98% → 99%+**

---

## 📈 Coverage Metrics to Track

After each step, run:
```powershell
python -c "
import json
products = json.load(open('output/products_for_shop.json'))
with_images = sum(1 for p in products if p.get('image_paths'))
total = len(products)
print(f'Coverage: {with_images}/{total} = {with_images/total*100:.1f}%')
print(f'Missing: {total-with_images} products')
"
```

---

## 🐛 Troubleshooting Low Coverage

### Issue: Catalog extracted but 0 images linked

**Diagnosis:**
```powershell
# Check if images were actually extracted
Get-ChildItem "product-images\catalog-name.pdf"

# Check page numbers in JSON vs image filenames
```

**Common Causes:**
1. Page number mismatch (PDF page ≠ logical page)
2. Images in subfolder with different name
3. Catalog name doesn't match between JSON and folder

### Issue: Images extracted but appear corrupted

**Diagnosis:**
Look for Extract.py error messages about:
- Smart crop failures
- GPT API errors
- Image format issues

**Solution:**
Reduce image processing complexity or skip smart cropping.

---

## 💡 Pro Tips

1. **Start with copy_existing_images.py** - Easiest 40% gain
2. **Focus on high-value catalogs first** - Extract catalogs with most products
3. **Check image quality after extraction** - Some may need parameter tuning
4. **Keep backups** - Extraction is time-consuming
5. **Monitor API costs** - GPT filtering adds up for large catalogs

---

## 📞 Expected Final Results

After all optimizations:
- ✅ **95-98%** coverage is achievable
- ✅ **99%+** with manual fallbacks/placeholders
- ✅ **100%** not realistic (some PDFs truly have no images)

**Acceptable coverage:** 95%+ is excellent for e-commerce
**Great coverage:** 98%+ is professional-grade
**Perfect coverage:** 99%+ requires manual work

---

Last Updated: November 26, 2025
