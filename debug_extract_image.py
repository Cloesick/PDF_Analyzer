import os
import random
from pathlib import Path

import pdfplumber

from classify_images_with_gpt import classify_image_with_gpt


PROJECT_ROOT = r"C:\Users\prova\Documents\Projects\PDF_Analyzer"
INPUT_FOLDER = os.path.join(PROJECT_ROOT, "input_pdfs")
DEBUG_IMG_FOLDER = os.path.join(PROJECT_ROOT, "debug_images")

os.makedirs(DEBUG_IMG_FOLDER, exist_ok=True)

pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".pdf")]
if not pdf_files:
    print("No PDFs in input_pdfs")
    raise SystemExit

pdf_path = os.path.join(INPUT_FOLDER, pdf_files[0])
print("Using PDF:", pdf_path)

with pdfplumber.open(pdf_path) as pdf:
    num_pages = len(pdf.pages)
    # Prefer non-cover pages: 1..num_pages-1
    page_indices = list(range(1, num_pages)) if num_pages > 1 else [0]
    random.shuffle(page_indices)

    saved_count = 0
    max_samples = 10

    for page_index in page_indices:
        if saved_count >= max_samples:
            break

        page = pdf.pages[page_index]
        page_x0, page_y0, page_x1, page_y1 = page.bbox
        if not page.images:
            continue

        for img_idx, img in enumerate(page.images):
            if saved_count >= max_samples:
                break

            x0, y0, x1, y1 = img.get("x0"), img.get("y0"), img.get("x1"), img.get("y1")
            if None in (x0, y0, x1, y1):
                continue

            # Clamp bbox to page
            x0 = max(page_x0, min(x0, page_x1))
            x1 = max(page_x0, min(x1, page_x1))
            y0 = max(page_y0, min(y0, page_y1))
            y1 = max(page_y0, min(y1, page_y1))

            if x1 <= x0 or y1 <= y0:
                continue

            cropped = page.crop((x0, y0, x1, y1))
            image_obj = cropped.to_image(resolution=150)
            out_path = os.path.join(
                DEBUG_IMG_FOLDER,
                f"page{page_index+1:03d}_img{img_idx+1:03d}.webp",
            )
            image_obj.save(out_path, format="WEBP")

            is_tool, labels, confidence = classify_image_with_gpt(Path(out_path))
            if not is_tool:
                # Skip non-tool images; optionally delete if you don't even
                # want to see them.
                # os.remove(out_path)
                print("Skipped non-tool image:", out_path)
                continue

            print(
                "Saved TOOL image:",
                out_path,
                "labels=",
                labels,
                "confidence=",
                confidence,
            )
            saved_count += 1

    if saved_count == 0:
        print("No tool images found by GPT on non-cover pages")
    else:
        print(f"Saved {saved_count} TOOL images to {DEBUG_IMG_FOLDER}")