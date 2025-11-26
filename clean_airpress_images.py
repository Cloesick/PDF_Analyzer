import os
from pathlib import Path
import argparse

from PIL import Image
import numpy as np

# Thresholds – you can tweak these if needed
FULL_BLACK_MAX_MEAN = 5          # 0–255; how dark is "almost black"
GRAYSCALE_COLOR_DIFF_MAX = 5     # max difference between R,G,B to still be "grayscale"
EDGE_DENSITY_MAX = 0.12          # fraction of edge pixels considered "contour-only"
CONTENT_VARIANCE_MAX = 100       # low variance = mostly flat / lines

DARK_PIXEL_THRESHOLD = 40        # 0–255, below this is considered "dark"
DARK_FRACTION_MIN = 0.7          # at least 70% dark pixels

def is_fully_black(arr):
    # arr: HxWx3 uint8
    mean_val = arr.mean()
    return mean_val < FULL_BLACK_MAX_MEAN

def is_grayscale_only(arr):
    # use wider dtype to avoid overflow in differences
    r = arr[..., 0].astype(np.int16)
    g = arr[..., 1].astype(np.int16)
    b = arr[..., 2].astype(np.int16)

    diff_rg = np.abs(r - g)
    diff_rb = np.abs(r - b)
    diff_gb = np.abs(g - b)

    max_diff = np.maximum.reduce([diff_rg, diff_rb, diff_gb]).max()
    return max_diff < GRAYSCALE_COLOR_DIFF_MAX

def edge_density(arr_gray):
    # Simple Sobel-like gradient magnitude to approximate edges
    arr = arr_gray.astype(np.float32)
    gy = np.abs(np.diff(arr, axis=0, prepend=arr[0:1, :]))
    gx = np.abs(np.diff(arr, axis=1, prepend=arr[:, 0:1]))
    grad = np.hypot(gx, gy)
    # Threshold for "edge" pixels
    edge_mask = grad > 30
    return edge_mask.mean()

def is_contour_like(arr):
    # arr: HxWx3
    gray = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.uint8)

    # Downsample for speed
    h, w = gray.shape
    factor = max(1, int(max(h, w) / 512))
    if factor > 1:
        gray = gray[::factor, ::factor]

    ed = edge_density(gray)
    var = gray.var()

    # "Contour-like": primarily edges, little filled content
    return ed < EDGE_DENSITY_MAX and var < CONTENT_VARIANCE_MAX

def dark_fraction(arr):
    # arr: HxWx3 uint8
    gray = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.uint8)
    mask_dark = gray < DARK_PIXEL_THRESHOLD
    return mask_dark.mean()

def dominant_color_fraction(arr):
    # arr: HxWx3 uint8, compute fraction of most common quantized color
    h, w, _ = arr.shape
    # extra downsampling for very large images to keep it fast
    factor = max(1, int(max(h, w) / 512))
    if factor > 1:
        arr = arr[::factor, ::factor, :]

    flat = arr.reshape(-1, 3)
    # simple quantization to reduce number of unique colors
    q = (flat // 16).astype(np.uint8)  # 0-15 per channel
    # view as 3-byte records so np.unique works on rows
    q_view = q.view([("r", q.dtype), ("g", q.dtype), ("b", q.dtype)])
    _, counts = np.unique(q_view, return_counts=True)
    return counts.max() / counts.sum()

def should_delete_image(path: Path):
    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            arr = np.array(im)

        # Downsample for speed
        h, w, _ = arr.shape

        # Heuristic 1: extreme aspect ratios (very wide or very tall banners/strips)
        aspect = max(w, h) / min(w, h)
        if aspect > 4.0:
            return True, "extreme_aspect_ratio"

        factor = max(1, int(max(h, w) / 512))
        if factor > 1:
            arr = arr[::factor, ::factor, :]

        if is_fully_black(arr):
            return True, "fully_black"

        # mostly dark (>= 70% dark pixels) -> fully/mostly black or very dark backgrounds
        if dark_fraction(arr) >= DARK_FRACTION_MIN:
            return True, "mostly_dark"

        # dominant color (>= 70% of pixels share same quantized color) -> likely flat background
        if dominant_color_fraction(arr) >= 0.7:
            return True, "dominant_color"

        # very low detail / flat-looking images (e.g. blank-like or no-detail pages)
        gray_full = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.uint8)
        # compute variance on a downsampled grid for speed on very large images
        gh, gw = gray_full.shape
        gfactor = max(1, int(max(gh, gw) / 512))
        if gfactor > 1:
            gray_sample = gray_full[::gfactor, ::gfactor]
        else:
            gray_sample = gray_full
        if gray_sample.var() < 50:
            return True, "no_detail"

        if is_grayscale_only(arr) and is_contour_like(arr):
            return True, "grayscale_contour_or_bw"

        # TODO: fully_other_color
        # TODO: no_detail

        return False, None
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return False, None

def iter_images(root: Path):
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"}
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if Path(name).suffix.lower() in exts:
                yield Path(dirpath) / name

def main(root: Path, dry_run=True):
    to_delete = []
    count = 0

    for img_path in iter_images(root):
        count += 1
        if count % 100 == 0:
            print(f"Scanned {count} images...", flush=True)

        delete, reason = should_delete_image(img_path)
        if delete:
            to_delete.append((img_path, reason))

    print(f"Scanned total {count} images.")
    print(f"Found {len(to_delete)} images matching criteria.")
    for path, reason in to_delete:
        print(f"[{reason}] {path}")

    if not dry_run:
        confirm = input("Type 'yes' to confirm deletion of these files: ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            return
        for path, reason in to_delete:
            try:
                os.remove(path)
                print(f"Deleted [{reason}] {path}")
            except Exception as e:
                print(f"Failed to delete {path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean dark/contour images from a folder tree.")
    parser.add_argument(
        "root",
        help="Root folder to scan (e.g. C:\\Users\\prova\\Documents\\Projects\\PDF_Analyzer\\airpress-style-images)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete files (default is dry-run: only list).",
    )
    args = parser.parse_args()

    root_path = Path(args.root)
    if not root_path.exists():
        print(f"Root path does not exist: {root_path}")
    else:
        dry = not args.delete
        main(root_path, dry_run=dry)