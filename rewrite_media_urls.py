import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
input_path = BASE_DIR / "output" / "products_for_shop.json"
output_path = BASE_DIR / "output" / "products_for_shop_rewritten.json"

with input_path.open("r", encoding="utf-8") as f:
    products = json.load(f)

for product in products:
    media_list = product.get("media") or []
    for item in media_list:
        url = item.get("url")
        if not url:
            continue

        # Find the part after 'airpress-style-images/'
        marker = "airpress-style-images/"
        if marker not in url:
            continue

        relative_path = url.split(marker, 1)[1]

        # Only touch webp images
        if not relative_path.endswith(".webp"):
            continue

        # New URL keeps subfolders
        item["url"] = f"/product-images/{relative_path}"

with output_path.open("w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Rewritten file saved to: {output_path}")