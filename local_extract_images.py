import os
import io
import re
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
import pdfplumber
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_FOLDER = PROJECT_ROOT / "input_pdfs"
OUTPUT_ROOT = PROJECT_ROOT / "airpress-style-images"

HEADER_SEARCH_HEIGHT = 150  # For category detection (like airpress-catalogus-eng.py)


def _is_grayscale_only(pil_image: Image.Image) -> bool:
    """Return True if the image has no color information (pure grayscale).

    We treat an image as grayscale-only if, after converting to RGB, all
    pixels have R == G == B. These are skipped.
    """
    rgb = pil_image.convert("RGB")
    arr = np.array(rgb)
    if arr.size == 0:
        return True
    r = arr[..., 0]
    g = arr[..., 1]
    b = arr[..., 2]
    return np.all(r == g) and np.all(g == b)


def _sanitize_text(text: str) -> str:
    """Cleans text for use in filenames (similar to airpress-catalogus-eng)."""
    if not text:
        return "Unknown_Category"
    text = text.replace("www.airpress.net", "").replace("compressoren", "")
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
    return re.sub(r"\s+", "_", text.strip())[:40] or "Unknown_Category"


def _page_category_and_sku_tag(pdf_path: Path, page_index: int) -> tuple[str, str]:
    """Return (category_name, sku_tag) for a given page using pdfplumber.

    - category_name: derived from top HEADER_SEARCH_HEIGHT of the page.
    - sku_tag: SKUs aggregated from all tables on the page, similar to
      airpress-catalogus-eng.py (primary SKUs from first column first).
    """
    category_name = f"Page_{page_index + 1}"
    ordered_skus: list[str] = []

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            if page_index >= len(pdf.pages):
                return category_name, "Unknown"

            page = pdf.pages[page_index]

            # Category from header strip
            header_crop = page.crop((0, 0, page.width, HEADER_SEARCH_HEIGHT))
            raw_header = header_crop.extract_text()
            cat = _sanitize_text(raw_header or "")
            if len(cat) >= 3:
                category_name = cat

            # Collect SKUs from all tables on this page
            tables = page.find_tables()
            primary_skus: list[str] = []
            extra_skus_set: set[str] = set()
            for table in tables or []:
                table_data = table.extract()
                if not table_data:
                    continue
                for row in table_data:
                    if not row:
                        continue
                    first_cell = row[0]
                    if first_cell is not None:
                        text_first = str(first_cell).strip()
                        if len(text_first) >= 3:
                            for token in re.findall(r"\b\d{5}(?:-[A-Z])?\b", text_first):
                                primary_skus.append(token)
                    for cell in row:
                        if cell is None:
                            continue
                        text = str(cell).strip()
                        if len(text) < 3:
                            continue
                        for token in re.findall(r"\b\d{5}(?:-[A-Z])?\b", text):
                            extra_skus_set.add(token)

            seen: set[str] = set()
            ordered_skus = []
            for sku in primary_skus:
                if sku not in seen:
                    seen.add(sku)
                    ordered_skus.append(sku)
            for sku in sorted(extra_skus_set):
                if sku not in seen:
                    seen.add(sku)
                    ordered_skus.append(sku)

    except Exception:
        return category_name, "Unknown"

    if not ordered_skus:
        return category_name, "Unknown"

    max_sku_tag_len = 120
    sku_pieces: list[str] = []
    for sku in ordered_skus:
        sku_clip = sku[:30]
        tentative = sku_clip if not sku_pieces else "+".join(sku_pieces + [sku_clip])
        if len(tentative) > max_sku_tag_len:
            break
        sku_pieces.append(sku_clip)
    if not sku_pieces:
        sku_pieces = ["Unknown"]
    sku_tag = "+".join(sku_pieces)
    return category_name, sku_tag


def extract_images_from_pdf(pdf_path: Path, output_dir: Path) -> int:
    """Extract all embedded images from one PDF into output_dir.

    Core behavior (like before / PDF24-style):
      - Use PyMuPDF to iterate embedded images.
      - One file per image, per page.
      - Save as WEBP.
      - Skip pure grayscale images.

    Enhancement:
      - For each page, derive a category + aggregated SKU tag from
        pdfplumber tables and include them in the filename so that
        naming is SKU-aware.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    written = 0

    safe_pdf_stem = re.sub(r"[^A-Za-z0-9_-]", "_", pdf_path.stem)[:80]

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        # Derive category + SKU tag once per page
        category_name, sku_tag = _page_category_and_sku_tag(pdf_path, page_index)
        safe_category = re.sub(r"[^A-Za-z0-9_-]", "_", category_name)[:60]
        safe_sku_tag = re.sub(r"[^A-Za-z0-9_+.-]", "_", sku_tag)[:80]

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image.get("image")
            if not img_bytes:
                continue

            try:
                pil_img = Image.open(io.BytesIO(img_bytes))
            except Exception:
                continue

            if _is_grayscale_only(pil_img):
                continue

            filename_parts = [safe_pdf_stem]
            if safe_category:
                filename_parts.append(safe_category)
            if safe_sku_tag and safe_sku_tag != "Unknown":
                filename_parts.append(safe_sku_tag)
            filename_core = "_".join(filename_parts)

            filename = f"{filename_core}_p{page_index + 1:03d}_img{img_index:03d}.webp"
            out_path = output_dir / filename

            try:
                pil_img.convert("RGB").save(out_path, format="WEBP")
                written += 1
            except Exception:
                continue

    doc.close()
    return written


def main() -> None:
    if not INPUT_FOLDER.exists():
        print(f"Input folder not found: {INPUT_FOLDER}")
        return

    pdf_files = sorted(p for p in INPUT_FOLDER.iterdir() if p.suffix.lower() == ".pdf")
    if not pdf_files:
        print(f"No PDF files found in {INPUT_FOLDER}")
        return

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    total_images = 0
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name}...")
        per_pdf_dir = OUTPUT_ROOT / pdf_path.name
        written = extract_images_from_pdf(pdf_path, per_pdf_dir)
        total_images += written
        print(f"  -> saved {written} images in {per_pdf_dir}")

    print(f"Done. Total images saved across all PDFs: {total_images}")


if __name__ == "__main__":
    main()
