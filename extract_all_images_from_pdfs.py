"""
Extract All Images from Product_pdfs
=====================================
Extracts images from all PDF catalogs and saves them to:
- Product_pdfs/images/[catalog]/
- Webshop: public/product-images-by-pdf/[catalog]/

This populates the image folders so products can display correctly.
"""

import fitz  # PyMuPDF
import json
from pathlib import Path
from PIL import Image
import io

PROJECT_ROOT = Path(__file__).parent
PRODUCT_PDFS_DIR = PROJECT_ROOT / "output" / "Product_pdfs"
OUTPUT_IMAGES = PRODUCT_PDFS_DIR / "images"
WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")
WEBSHOP_IMAGES = WEBSHOP_ROOT / "public" / "product-images-by-pdf"


def extract_images_from_pdf(pdf_path: Path, catalog_name: str) -> int:
    """Extract all images from a PDF"""
    
    print(f"\n📄 Processing: {catalog_name}")
    
    # Create output directories
    output_dir = OUTPUT_IMAGES / catalog_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    webshop_dir = WEBSHOP_IMAGES / catalog_name
    webshop_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        doc = fitz.open(str(pdf_path))
        total_images = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                try:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    
                    if not base_image:
                        continue
                    
                    # Get image data
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Check minimum size (filter out tiny logos/icons)
                    try:
                        img = Image.open(io.BytesIO(image_bytes))
                        width, height = img.size
                        
                        if width < 50 or height < 50:
                            continue  # Skip tiny images
                        
                        # Convert to WebP for smaller size
                        output_filename = f"{catalog_name}_page{page_num+1:03d}_img{img_index:02d}.webp"
                        
                        # Save to Product_pdfs/images
                        output_path = output_dir / output_filename
                        img.save(output_path, "WEBP", quality=85)
                        
                        # Copy to webshop
                        webshop_path = webshop_dir / output_filename
                        img.save(webshop_path, "WEBP", quality=85)
                        
                        total_images += 1
                        
                    except Exception as e:
                        continue
                
                except Exception as e:
                    continue
            
            # Progress indicator
            if (page_num + 1) % 10 == 0:
                print(f"   Page {page_num + 1}/{len(doc)} - {total_images} images extracted")
        
        doc.close()
        
        print(f"   ✓ Extracted {total_images} images from {len(doc)} pages")
        return total_images
    
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return 0


def extract_all_catalogs() -> None:
    """Extract images from all PDF catalogs"""
    
    print("="*80)
    print("📸 EXTRACT ALL IMAGES FROM PRODUCT_PDFS")
    print("="*80)
    
    pdf_files = sorted(PRODUCT_PDFS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("\n❌ No PDF files found in Product_pdfs/")
        return
    
    print(f"\nFound {len(pdf_files)} PDF catalogs to process")
    
    total_pdfs = 0
    total_images = 0
    
    for pdf_file in pdf_files:
        catalog_name = pdf_file.stem
        
        # Skip very small files
        if pdf_file.stat().st_size < 1000:
            print(f"\n⚠️  Skipping {catalog_name} (file too small)")
            continue
        
        images_extracted = extract_images_from_pdf(pdf_file, catalog_name)
        
        if images_extracted > 0:
            total_pdfs += 1
            total_images += images_extracted
    
    print(f"\n{'='*80}")
    print("✅ IMAGE EXTRACTION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   PDFs processed:     {total_pdfs}")
    print(f"   Images extracted:   {total_images:,}")
    print(f"   Avg images/catalog: {total_images / total_pdfs if total_pdfs > 0 else 0:.1f}")
    
    print(f"\n📁 Images saved to:")
    print(f"   1. {OUTPUT_IMAGES.relative_to(PROJECT_ROOT)}")
    print(f"   2. {WEBSHOP_IMAGES.relative_to(WEBSHOP_ROOT)}")
    
    print(f"\n💡 Images are now available at:")
    print(f"   /product-images-by-pdf/[catalog]/[catalog]_pageXXX_imgXX.webp")
    
    print("="*80)


def main():
    """Main entry point"""
    
    # Check dependencies
    try:
        import fitz
        from PIL import Image
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("   pip install PyMuPDF Pillow")
        return
    
    # Check directories
    if not PRODUCT_PDFS_DIR.exists():
        print(f"❌ Product_pdfs directory not found: {PRODUCT_PDFS_DIR}")
        return
    
    # Extract images
    extract_all_catalogs()


if __name__ == "__main__":
    main()
