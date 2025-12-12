"""
Universal Catalog Extractor with Advanced Image-SKU Matching
=============================================================
Consolidates multiple extraction scripts into one configurable extractor.

Replaces:
- extract_makita_improved.py
- extract_makita_tools_only.py
- extract_makita_batteries.py
- extract_makita_tuinfolder.py
- extract_makita_final.py
- extract_makita_tables_smart.py
- extract_kranzle_airpress.py
- improve_image_sku_matching.py (merged)
- ... and more

Features:
- Table-based extraction
- Image extraction with smart SKU matching
- Advanced proximity-based image-SKU linking
- Property detection
- Multi-pattern SKU recognition (Makita, Dema, Airpress, fittings, etc.)
- Confidence scoring for matches
- Multi-catalog support

Usage:
    python extract_catalog_universal.py <catalog_name> [options]
    python extract_catalog_universal.py makita-catalogus-2022-nl --match-images
    python extract_catalog_universal.py pompentoebehoren --match-images --verbose
    python extract_catalog_universal.py --list  # List available PDFs
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys
import fitz  # PyMuPDF
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
INPUT_PDF_DIR = PROJECT_ROOT / "input_pdfs"
OUTPUT_DIR = PROJECT_ROOT / "output"
IMAGE_OUTPUT = PROJECT_ROOT / "product-images-ultimate"


class ExtractionConfig:
    """Configuration for extraction"""
    
    def __init__(self):
        self.extract_tables = True
        self.extract_images = True
        self.extract_text = True
        self.detect_skus = True
        self.detect_properties = True
        self.match_images_to_skus = False  # Advanced image-SKU matching
        self.min_image_size = 50  # Minimum image dimension in pixels
        self.verbose = False


class UniversalExtractor:
    """Universal PDF extractor for product catalogs"""
    
    def __init__(self, pdf_path: Path, config: ExtractionConfig):
        self.pdf_path = pdf_path
        self.config = config
        self.catalog_name = pdf_path.stem
        self.products = []
        self.images = []
        self.image_sku_matches = []  # Advanced image-SKU matches
        self.stats = {
            "pages_processed": 0,
            "products_found": 0,
            "images_extracted": 0,
            "tables_found": 0,
            "image_matches": 0,
            "high_confidence_matches": 0,
        }
    
    def extract(self) -> Dict[str, Any]:
        """Run complete extraction"""
        
        print(f"\n{'='*80}")
        print(f"EXTRACTING: {self.catalog_name}")
        print("=" * 80)
        
        try:
            doc = fitz.open(str(self.pdf_path))
            total_pages = len(doc)
            print(f"📄 Total pages: {total_pages}")
            
            for page_num in range(total_pages):
                if self.config.verbose:
                    print(f"\n📄 Processing page {page_num + 1}/{total_pages}...")
                
                page = doc[page_num]
                self._extract_page(page, page_num + 1)
                self.stats["pages_processed"] += 1
                
                # Progress indicator for non-verbose mode
                if not self.config.verbose and (page_num + 1) % 10 == 0:
                    print(f"   Processed {page_num + 1}/{total_pages} pages...")
            
            doc.close()
            
            print(f"\n✅ Extraction complete!")
            self._print_stats()
            
            return {
                "catalog": self.catalog_name,
                "products": self.products,
                "images": self.images,
                "stats": self.stats,
            }
        
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            raise
    
    def _extract_page(self, page: fitz.Page, page_num: int) -> None:
        """Extract data from a single page"""
        
        # Extract text
        if self.config.extract_text:
            text = page.get_text("text")
            
            # Detect SKUs in text
            if self.config.detect_skus:
                skus = self._detect_skus(text)
                for sku in skus:
                    self._add_product(sku, page_num, {})
        
        # Extract tables
        if self.config.extract_tables:
            tables = self._extract_tables(page)
            if tables:
                self.stats["tables_found"] += len(tables)
                for table in tables:
                    self._process_table(table, page_num)
        
        # Extract images
        if self.config.extract_images:
            images = self._extract_images(page, page_num)
            self.images.extend(images)
            self.stats["images_extracted"] += len(images)
        
        # Advanced image-SKU matching
        if self.config.match_images_to_skus and self.config.extract_images:
            self._match_images_to_skus_on_page(page, page_num)
    
    def _detect_skus(self, text: str) -> List[str]:
        """Detect SKU patterns in text - Enhanced with multiple catalog types"""
        import re
        
        # Enhanced SKU patterns for various catalog types
        patterns = [
            r'\b[A-Z]{2,}[0-9]{3,}[A-Z]{0,2}\b',  # Makita: GA005GM201, DHP482Z
            r'\b[A-Z0-9]{2,}[-][0-9]{2,}\b',       # Dema: 1234-5678, ABC-123
            r'\b[0-9]{4,6}\b',                      # Numeric: 12345, 123456
            r'\b[A-Z]{2,}\s*[0-9]{2,}[-]?[0-9]*\b', # Airpress/Kränzle: HL 425-50
            r'\b[0-9]{1,2}[/][0-9]{1,2}[""]?\b',   # Fittings inch: 1/4", 3/8"
            r'\bM[0-9]{1,2}[x][0-9.]{1,3}\b',      # Fittings metric: M10x1
            r'Ø\s*[0-9]{1,3}[\s]?[m]{0,2}',        # Diameter: Ø10, Ø25mm
        ]
        
        skus = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            skus.update(matches)
        
        # Filter out false positives
        false_positives = {
            "PAGE", "PAGINA", "ARTIKEL", "CODE", "TYPE", "MODEL",
            "DESCRIPTION", "PRIJS", "PRICE", "2022", "2023", "2024", "2025"
        }
        
        skus = {sku for sku in skus if sku.upper() not in false_positives}
        skus = {sku for sku in skus if 2 <= len(sku) <= 25}
        
        return list(skus)
    
    def _extract_tables(self, page: fitz.Page) -> List[List[List[str]]]:
        """Extract tables from page"""
        try:
            # Use PyMuPDF's table extraction
            tables = page.find_tables()
            
            extracted = []
            for table in tables:
                table_data = table.extract()
                if table_data and len(table_data) > 1:  # At least header + 1 row
                    extracted.append(table_data)
            
            return extracted
        except Exception as e:
            if self.config.verbose:
                print(f"   Warning: Could not extract tables - {e}")
            return []
    
    def _process_table(self, table: List[List[str]], page_num: int) -> None:
        """Process table data and extract products"""
        
        if not table or len(table) < 2:
            return
        
        # Assume first row is header
        headers = [str(h).strip().lower() if h else "" for h in table[0]]
        
        # Find SKU column
        sku_col = None
        for i, header in enumerate(headers):
            if any(x in header for x in ["sku", "artikel", "code", "type", "model"]):
                sku_col = i
                break
        
        if sku_col is None:
            # Try first column
            sku_col = 0
        
        # Process rows
        for row in table[1:]:
            if not row or len(row) <= sku_col:
                continue
            
            sku = str(row[sku_col]).strip()
            if not sku or len(sku) < 2:
                continue
            
            # Extract properties from other columns
            properties = {}
            for i, (header, value) in enumerate(zip(headers, row)):
                if i == sku_col or not header:
                    continue
                
                if value and str(value).strip():
                    properties[header] = str(value).strip()
            
            self._add_product(sku, page_num, properties)
    
    def _extract_images(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from page"""
        
        images = []
        image_list = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_list):
            try:
                xref = img_info[0]
                base_image = page.parent.extract_image(xref)
                
                if not base_image:
                    continue
                
                # Check image size
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                
                if width < self.config.min_image_size or height < self.config.min_image_size:
                    continue
                
                # Save image info
                image_data = {
                    "page": page_num,
                    "index": img_index,
                    "width": width,
                    "height": height,
                    "format": base_image.get("ext", "png"),
                    "xref": xref,
                }
                
                images.append(image_data)
            
            except Exception as e:
                if self.config.verbose:
                    print(f"   Warning: Could not extract image {img_index} - {e}")
        
        return images
    
    def _add_product(self, sku: str, page_num: int, properties: Dict[str, Any]) -> None:
        """Add or update product"""
        
        # Check if product already exists
        existing = next((p for p in self.products if p["sku"] == sku), None)
        
        if existing:
            # Merge properties
            existing["properties"].update(properties)
            if page_num not in existing["pages"]:
                existing["pages"].append(page_num)
        else:
            # Create new product
            self.products.append({
                "sku": sku,
                "catalog_name": self.catalog_name,
                "pages": [page_num],
                "properties": properties,
            })
            self.stats["products_found"] += 1
    
    def _match_images_to_skus_on_page(self, page: fitz.Page, page_num: int) -> None:
        """Advanced image-SKU matching using proximity and context"""
        import re
        
        # Get text blocks with positions
        text_blocks = page.get_text("dict")["blocks"]
        
        # Get images for this page
        page_images = [img for img in self.images if img["page"] == page_num]
        
        if not page_images:
            return
        
        # Find all SKUs with their positions
        skus_with_pos = []
        
        for block in text_blocks:
            if block.get("type") != 0:  # Only text blocks
                continue
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    bbox = span.get("bbox", [0, 0, 0, 0])
                    
                    # Detect SKUs in this span
                    detected_skus = self._detect_skus(text)
                    
                    for sku in detected_skus:
                        skus_with_pos.append({
                            "sku": sku,
                            "bbox": bbox,
                            "x": bbox[0],
                            "y": bbox[1],
                            "text_context": text,
                        })
        
        if not skus_with_pos:
            return
        
        # Match each image to best SKU
        page_rect = page.rect
        
        for img_data in page_images:
            # Get image position (approximate from page)
            img_rects = page.get_image_rects(img_data["xref"])
            
            if not img_rects:
                continue
            
            img_rect = img_rects[0]
            img_x, img_y = img_rect.x0, img_rect.y0
            
            # Find closest SKUs
            best_match = None
            best_score = 0
            
            for sku_data in skus_with_pos:
                # Calculate distance
                distance = ((img_x - sku_data["x"]) ** 2 + (img_y - sku_data["y"]) ** 2) ** 0.5
                normalized_dist = distance / (page_rect.width + page_rect.height)
                
                # Calculate score based on proximity and alignment
                score = 0
                
                # Proximity score (inverse of distance)
                if normalized_dist < 0.1:
                    score += 10.0
                elif normalized_dist < 0.2:
                    score += 5.0
                elif normalized_dist < 0.3:
                    score += 2.0
                else:
                    score += 1.0 / (normalized_dist + 0.1)
                
                # Alignment bonus (same row/column)
                threshold = page_rect.width * 0.05
                if abs(img_y - sku_data["y"]) < threshold:  # Same row
                    score += 8.0 if sku_data["x"] < img_x else 6.0
                if abs(img_x - sku_data["x"]) < threshold:  # Same column
                    score += 7.0 if sku_data["y"] < img_y else 5.0
                
                if score > best_score:
                    best_score = score
                    best_match = sku_data
            
            if best_match:
                # Determine confidence
                if best_score >= 15.0:
                    confidence = "high"
                    self.stats["high_confidence_matches"] += 1
                elif best_score >= 8.0:
                    confidence = "medium"
                else:
                    confidence = "low"
                
                # Create match
                match = {
                    "image": {
                        "page": page_num,
                        "index": img_data["index"],
                        "width": img_data["width"],
                        "height": img_data["height"],
                    },
                    "sku": best_match["sku"],
                    "confidence": confidence,
                    "score": best_score,
                    "image_path": f"/product-images-by-pdf/{self.catalog_name}/{self.catalog_name}_page{page_num:03d}_img{img_data['index']:02d}.webp"
                }
                
                self.image_sku_matches.append(match)
                self.stats["image_matches"] += 1
    
    def _print_stats(self) -> None:
        """Print extraction statistics"""
        
        print(f"\n📊 STATISTICS")
        print(f"   Pages processed:    {self.stats['pages_processed']}")
        print(f"   Products found:     {self.stats['products_found']}")
        print(f"   Images extracted:   {self.stats['images_extracted']}")
        print(f"   Tables found:       {self.stats['tables_found']}")
        
        if self.config.match_images_to_skus:
            print(f"\n📸 IMAGE-SKU MATCHING:")
            print(f"   Matches created:    {self.stats['image_matches']}")
            print(f"   High confidence:    {self.stats['high_confidence_matches']}")
            if self.stats['image_matches'] > 0:
                high_pct = self.stats['high_confidence_matches'] / self.stats['image_matches'] * 100
                print(f"   Quality:            {high_pct:.1f}% high confidence")
    
    def save_results(self) -> None:
        """Save extraction results"""
        
        # Save products
        products_file = OUTPUT_DIR / f"{self.catalog_name}_extracted.json"
        with products_file.open("w", encoding="utf-8") as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved products: {products_file.name}")
        
        # Save images metadata
        if self.images:
            images_file = OUTPUT_DIR / f"{self.catalog_name}_images.json"
            with images_file.open("w", encoding="utf-8") as f:
                json.dump(self.images, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved images: {images_file.name}")
        
        # Save image-SKU matches
        if self.image_sku_matches:
            matches_file = OUTPUT_DIR / f"{self.catalog_name}_image_sku_matches.json"
            match_data = {
                "catalog": self.catalog_name,
                "stats": {
                    "total_matches": self.stats["image_matches"],
                    "high_confidence": self.stats["high_confidence_matches"],
                },
                "matches": self.image_sku_matches
            }
            with matches_file.open("w", encoding="utf-8") as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved image matches: {matches_file.name}")


def list_available_pdfs() -> None:
    """List all available PDFs"""
    
    print("\n📚 AVAILABLE PDF CATALOGS:")
    print("=" * 80)
    
    pdfs = sorted(INPUT_PDF_DIR.glob("*.pdf"))
    
    if not pdfs:
        print("❌ No PDFs found in input_pdfs/")
        return
    
    for pdf in pdfs:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"   • {pdf.stem:50} ({size_mb:.1f} MB)")
    
    print(f"\n📊 Total: {len(pdfs)} PDFs")
    print("=" * 80)


def main():
    """Main entry point"""
    
    # Parse arguments
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print("Universal Catalog Extractor with Advanced Image-SKU Matching")
        print("\nUsage:")
        print("   python extract_catalog_universal.py <catalog_name> [options]")
        print("\nOptions:")
        print("   --no-tables      Skip table extraction")
        print("   --no-images      Skip image extraction")
        print("   --no-skus        Skip SKU detection")
        print("   --match-images   Enable advanced image-SKU matching (recommended)")
        print("   --verbose, -v    Verbose output")
        print("   --list           List available PDFs")
        print("\nExamples:")
        print("   python extract_catalog_universal.py makita-catalogus-2022-nl")
        print("   python extract_catalog_universal.py pompentoebehoren --match-images")
        print("   python extract_catalog_universal.py slangkoppelingen --match-images -v")
        return
    
    if "--list" in sys.argv:
        list_available_pdfs()
        return
    
    catalog_name = sys.argv[1]
    
    # Find PDF
    pdf_path = INPUT_PDF_DIR / f"{catalog_name}.pdf"
    if not pdf_path.exists():
        # Try without .pdf extension
        possible = list(INPUT_PDF_DIR.glob(f"{catalog_name}*.pdf"))
        if possible:
            pdf_path = possible[0]
        else:
            print(f"❌ PDF not found: {catalog_name}")
            print("Use --list to see available PDFs")
            return
    
    # Configure extraction
    config = ExtractionConfig()
    config.extract_tables = "--no-tables" not in sys.argv
    config.extract_images = "--no-images" not in sys.argv
    config.detect_skus = "--no-skus" not in sys.argv
    config.match_images_to_skus = "--match-images" in sys.argv
    config.verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Run extraction
    extractor = UniversalExtractor(pdf_path, config)
    extractor.extract()
    extractor.save_results()
    
    print(f"\n{'='*80}")
    print("✅ EXTRACTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
