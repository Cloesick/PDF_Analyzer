"""
Setup Webshop to Use Product_pdfs Folder
=========================================
Configures the webshop to use PDFs and JSON from Product_pdfs:
1. Generate catalog metadata for catalogs page
2. Ensure products JSON is ready for products page  
3. Copy/symlink PDFs to webshop public folder
4. Create image mappings
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
PRODUCT_PDFS_DIR = PROJECT_ROOT / "output" / "Product_pdfs"
PRODUCT_PDFS_JSON = PRODUCT_PDFS_DIR / "json"
PRODUCT_PDFS_IMAGES = PRODUCT_PDFS_DIR / "images"

WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")
WEBSHOP_PUBLIC = WEBSHOP_ROOT / "public"
WEBSHOP_DATA = WEBSHOP_PUBLIC / "data"
WEBSHOP_PDFS = WEBSHOP_PUBLIC / "catalogs"


def analyze_catalog_json(json_file: Path) -> Dict[str, Any]:
    """Analyze a catalog JSON to extract metadata"""
    
    catalog_name = json_file.stem
    
    try:
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle different formats
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict) and "products" in data:
            products = data["products"]
        else:
            products = []
        
        # Count products with images
        products_with_images = sum(
            1 for p in products 
            if p.get("image") or p.get("series_image") or p.get("imageUrl")
        )
        
        # Count total images
        total_images = sum(
            1 for p in products 
            if p.get("image") or p.get("series_image")
        )
        
        # Get unique pages
        pages = set(p.get("page") for p in products if p.get("page"))
        
        # Get categories
        categories = set()
        for p in products:
            if p.get("type"):
                categories.add(p["type"])
            if p.get("application"):
                categories.add(p["application"])
        
        return {
            "name": catalog_name,
            "total_products": len(products),
            "products_with_images": products_with_images,
            "total_images": total_images,
            "image_coverage": (products_with_images / len(products) * 100) if products else 0,
            "unique_pages": len(pages),
            "categories": len(categories),
            "avg_images_per_product": (total_images / len(products)) if products else 0
        }
    
    except Exception as e:
        print(f"   ✗ Error analyzing {catalog_name}: {e}")
        return None


def generate_catalog_metadata() -> List[Dict]:
    """Generate catalog metadata for catalogs page"""
    
    print("📊 Generating catalog metadata...")
    
    # Category mapping
    category_map = {
        "slangkoppelingen": ("hoses", "🔗 Hose Couplings & Connections"),
        "slangklemmen": ("hoses", "🔒 Hose Clamps"),
        "rubber-slangen": ("hoses", "🎗️ Rubber Hoses"),
        "pu-afzuigslangen": ("hoses", "🌀 PU Suction Hoses"),
        "plat-oprolbare-slangen": ("hoses", "📦 Flat Reelable Hoses"),
        
        "bronpompen": ("pumps", "🚰 Well Pumps"),
        "dompelpompen": ("pumps", "⬇️ Submersible Pumps"),
        "centrifugaalpompen": ("pumps", "💧 Centrifugal Pumps"),
        "zuigerpompen": ("pumps", "🔄 Piston Pumps"),
        "pomp-specials": ("pumps", "⭐ Pump Specials"),
        
        "digitale-versie-pompentoebehoren-compressed": ("pumps", "🔧 Pump Accessories"),
        
        "verzinkte-buizen": ("pipes", "🔩 Galvanized Pipes"),
        "pe-buizen": ("pipes", "⚪ PE Pipes"),
        "drukbuizen": ("pipes", "💨 Pressure Pipes"),
        "kunststof-afvoerleidingen": ("pipes", "🚿 Plastic Drainage Pipes"),
        "abs-persluchtbuizen": ("pipes", "🌬️ ABS Compressed Air Pipes"),
        
        "messing-draadfittingen": ("hoses", "🔩 Brass Thread Fittings"),
        "rvs-draadfittingen": ("hoses", "✨ Stainless Steel Fittings"),
        "zwarte-draad-en-lasfittingen": ("hoses", "⚫ Black Thread & Weld Fittings"),
        
        "airpress-catalogus-eng": ("tools", "🔧 Airpress Compressors (EN)"),
        "airpress-catalogus-nl-fr": ("tools", "🔧 Airpress Compressors (NL/FR)"),
        "kranzle-catalogus-2021-nl-1": ("tools", "💦 Kränzle Pressure Washers"),
        
        "makita-catalogus-2022-nl": ("tools", "🔨 Makita Power Tools 2022"),
        "makita-tuinfolder-2022-nl": ("tools", "🌱 Makita Garden Tools 2022"),
        
        "catalogus-aandrijftechniek-150922": ("technical", "⚙️ Drive Technology"),
    }
    
    catalogs = []
    json_files = sorted(PRODUCT_PDFS_JSON.glob("*.json"))
    
    for json_file in json_files:
        catalog_name = json_file.stem
        
        # Skip empty or invalid files
        if json_file.stat().st_size < 10:
            continue
        
        analysis = analyze_catalog_json(json_file)
        
        if not analysis:
            continue
        
        # Get category and description
        category, description = category_map.get(
            catalog_name,
            ("other", catalog_name.replace("-", " ").replace("_", " ").title())
        )
        
        # Determine icon
        icon_map = {
            "pumps": "💧",
            "hoses": "🔗",
            "pipes": "🔩",
            "tools": "🔧",
            "technical": "⚙️",
            "other": "📦"
        }
        icon = icon_map.get(category, "📦")
        
        catalog_meta = {
            "id": catalog_name,
            "name": description.split(" ", 1)[1] if " " in description else catalog_name.replace("-", " ").title(),
            "slug": catalog_name,
            "url": f"/catalog/{catalog_name}-grouped",
            "icon": icon,
            "category": category,
            "totalProducts": analysis["total_products"],
            "productsWithImages": analysis["products_with_images"],
            "totalImages": analysis["total_images"],
            "imageCoverage": round(analysis["image_coverage"], 1),
            "categories": analysis["categories"],
            "avgImagesPerProduct": round(analysis["avg_images_per_product"], 1),
            "description": description.split(" ", 1)[1] if " " in description else f"Complete catalog of {catalog_name.replace('-', ' ')}"
        }
        
        catalogs.append(catalog_meta)
        print(f"   ✓ {catalog_name}: {analysis['total_products']} products, {analysis['image_coverage']:.1f}% coverage")
    
    return catalogs


def copy_pdfs_to_webshop() -> None:
    """Copy PDFs from Product_pdfs to webshop public folder"""
    
    print(f"\n📄 Setting up PDF access...")
    
    # Ensure webshop catalogs directory exists
    WEBSHOP_PDFS.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(PRODUCT_PDFS_DIR.glob("*.pdf"))
    copied = 0
    
    for pdf_file in pdf_files:
        dest = WEBSHOP_PDFS / pdf_file.name
        
        # Copy if doesn't exist or is different
        if not dest.exists() or dest.stat().st_size != pdf_file.stat().st_size:
            shutil.copy2(pdf_file, dest)
            copied += 1
    
    print(f"   ✓ Copied/updated {copied} PDFs to webshop")
    print(f"   📁 Location: {WEBSHOP_PDFS.relative_to(WEBSHOP_ROOT)}")


def setup_image_access() -> None:
    """Setup image access from Product_pdfs"""
    
    print(f"\n🖼️ Setting up image access...")
    
    images_src = PRODUCT_PDFS_IMAGES
    images_dest = WEBSHOP_PUBLIC / "product-images-by-pdf"
    
    if not images_src.exists():
        print(f"   ⚠️  Images folder not found: {images_src}")
        print(f"   💡 Run image extraction scripts to populate images")
        return
    
    # Create symlink or copy
    if images_dest.exists() and images_dest.is_symlink():
        print(f"   ✓ Symlink already exists")
    elif images_dest.exists():
        print(f"   ⚠️  Directory exists (not a symlink)")
        print(f"   💡 Images are at: {images_dest}")
    else:
        try:
            # Try to create symlink (Windows requires admin or developer mode)
            images_dest.symlink_to(images_src, target_is_directory=True)
            print(f"   ✓ Created symlink to images")
        except:
            # Fallback: suggest manual copy
            print(f"   ⚠️  Could not create symlink")
            print(f"   💡 Manually copy images from:")
            print(f"      {images_src}")
            print(f"   💡 To:")
            print(f"      {images_dest}")


def save_catalog_metadata(catalogs: List[Dict]) -> None:
    """Save catalog metadata to webshop"""
    
    print(f"\n💾 Saving catalog metadata...")
    
    output_file = WEBSHOP_PUBLIC / "catalogs_metadata.json"
    
    # Backup existing
    if output_file.exists():
        backup = output_file.parent / f"{output_file.stem}_backup.json"
        shutil.copy2(output_file, backup)
        print(f"   ✓ Backup created: {backup.name}")
    
    # Save new metadata
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(catalogs, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Saved to: {output_file.relative_to(WEBSHOP_ROOT)}")


def create_config_summary() -> None:
    """Create configuration summary"""
    
    print(f"\n📝 Creating configuration summary...")
    
    summary_file = WEBSHOP_ROOT / "PRODUCT_PDFS_CONFIG.md"
    
    content = f"""# Product PDFs Configuration

**Date:** {Path(__file__).stat().st_mtime}  
**Status:** ✅ CONFIGURED

---

## 📁 Directory Structure

### Source (PDF_Analyzer)
```
{PRODUCT_PDFS_DIR.relative_to(PROJECT_ROOT)}/
├── *.pdf                    # Original PDF catalogs
├── json/                    # Extracted product data
│   ├── *.json               # One JSON per catalog
└── images/                  # Extracted images
    └── [catalog]/           # Images by catalog
```

### Webshop (dema-webshop)
```
public/
├── catalogs/                # PDF files accessible at /catalogs/*.pdf
├── product-images-by-pdf/   # Images (symlink or copy)
├── data/
│   └── products_for_shop.json   # Main products feed
└── catalogs_metadata.json   # Catalog overview for /catalogs page
```

---

## 🔗 Page Mappings

### Products Page (`/products`)
- **Data source:** `/data/products_for_shop.json`
- **Generated by:** `rebuild_webshop_from_product_pdfs.py`
- **Content:** All products from Product_pdfs/json/*.json

### Catalogs Page (`/catalogs`)
- **Data source:** `/catalogs_metadata.json`
- **Generated by:** `setup_webshop_from_product_pdfs.py`
- **Content:** Catalog overview with stats

### Individual Catalog Pages (`/catalog/[name]-grouped`)
- **Data source:** `/data/products_for_shop.json` (filtered by catalog)
- **PDFs:** Available at `/catalogs/[name].pdf`

---

## 🔄 Update Workflow

### When PDFs are updated/added:

1. **Extract data** (if new PDFs):
   ```bash
   cd C:\\Users\\prova\\Documents\\Projects\\PDF_Analyzer
   python extract_catalog_universal.py [catalog-name] --match-images
   ```

2. **Rebuild webshop feed**:
   ```bash
   python rebuild_webshop_from_product_pdfs.py
   ```

3. **Update catalog metadata**:
   ```bash
   python setup_webshop_from_product_pdfs.py
   ```

4. **Restart webshop** (if dev server running):
   ```bash
   cd C:\\Users\\prova\\Documents\\Projects\\DemaWebshop\\dema-webshop
   npm run dev
   ```

---

## ✅ Verification

Check these URLs in the webshop:
- http://localhost:3000/products - All products
- http://localhost:3000/catalogs - Catalog overview
- http://localhost:3000/catalog/slangkoppelingen-grouped - Example catalog page
- http://localhost:3000/catalogs/slangkoppelingen.pdf - PDF viewer

---

## 📊 Current Status

Run `python setup_webshop_from_product_pdfs.py` to see current statistics.

---

**Last configured:** Auto-generated by setup script
"""
    
    with summary_file.open("w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"   ✓ Summary saved: {summary_file.name}")


def print_final_summary(catalogs: List[Dict]) -> None:
    """Print final configuration summary"""
    
    total_products = sum(c["totalProducts"] for c in catalogs)
    total_images = sum(c["totalImages"] for c in catalogs)
    avg_coverage = sum(c["imageCoverage"] for c in catalogs) / len(catalogs) if catalogs else 0
    
    print(f"\n{'='*80}")
    print("✅ WEBSHOP CONFIGURED FOR PRODUCT_PDFS")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"   Catalogs configured:    {len(catalogs)}")
    print(f"   Total products:         {total_products:,}")
    print(f"   Total images:           {total_images:,}")
    print(f"   Average coverage:       {avg_coverage:.1f}%")
    
    print(f"\n📁 Webshop Files:")
    print(f"   Products:               public/data/products_for_shop.json")
    print(f"   Catalog metadata:       public/catalogs_metadata.json")
    print(f"   PDFs:                   public/catalogs/*.pdf")
    print(f"   Images:                 public/product-images-by-pdf/")
    
    print(f"\n🌐 Pages Updated:")
    print(f"   /products               Products page (all catalogs)")
    print(f"   /catalogs               Catalogs overview page")
    print(f"   /catalog/[name]-grouped Individual catalog pages")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Start webshop: cd {WEBSHOP_ROOT} && npm run dev")
    print(f"   2. Visit: http://localhost:3000/products")
    print(f"   3. Visit: http://localhost:3000/catalogs")
    
    print(f"\n{'='*80}")


def main():
    """Main entry point"""
    
    print("="*80)
    print("🔧 SETUP WEBSHOP TO USE PRODUCT_PDFS")
    print("="*80)
    
    # Check directories
    if not PRODUCT_PDFS_JSON.exists():
        print(f"\n❌ JSON directory not found: {PRODUCT_PDFS_JSON}")
        return
    
    # Generate catalog metadata
    catalogs = generate_catalog_metadata()
    
    if not catalogs:
        print("\n❌ No catalogs found!")
        return
    
    # Copy PDFs
    copy_pdfs_to_webshop()
    
    # Setup images
    setup_image_access()
    
    # Save metadata
    save_catalog_metadata(catalogs)
    
    # Create config summary
    create_config_summary()
    
    # Final summary
    print_final_summary(catalogs)


if __name__ == "__main__":
    main()
