# Image Database

## 📊 Statistics

- **Total Images**: 5610
- **Unique SKUs**: 2849
- **Catalogs**: 26

## 🔍 Usage

### Frontend JavaScript/TypeScript

```javascript
// Load image database
const imageDB = await fetch('/image_index.json').then(r => r.json());

// Get primary image for SKU
function getProductImage(sku) {
  const entry = imageDB.sku_index[sku];
  if (entry && entry.primary_image) {
    return `/images/${entry.primary_image.source_path}`;
  }
  return '/placeholder.webp';
}

// Get all images for SKU (for gallery)
function getProductGallery(sku) {
  const entry = imageDB.sku_index[sku];
  if (entry && entry.all_images) {
    return entry.all_images.map(img => `/images/${img.source_path}`);
  }
  return [];
}

// Search by normalized SKU (flexible)
function searchBySKU(skuInput) {
  const normalized = skuInput.toUpperCase().replace(/[\s\-_]/g, '');
  const actualSKU = imageDB.search_index[normalized];
  return actualSKU ? imageDB.sku_index[actualSKU] : null;
}
```

### Python

```python
import json

# Load database
with open('image_index.json') as f:
    image_db = json.load(f)

# Get image for SKU
def get_product_image(sku):
    entry = image_db['sku_index'].get(sku)
    if entry:
        return entry['primary_image']['source_path']
    return None

# Search flexible
def search_sku(sku_input):
    normalized = sku_input.upper().replace(' ', '').replace('-', '').replace('_', '')
    actual_sku = image_db['search_index'].get(normalized)
    return image_db['sku_index'].get(actual_sku) if actual_sku else None
```

## 📁 Structure

```
image-database/
├── image_index.json          # Main searchable index
├── README.md                 # This file
└── images/                   # (symbolic links to source images)
```

## 🔑 Index Structure

### sku_index
Maps SKU -> Image data
- `primary_image`: Best/largest image for the SKU
- `all_images`: Array of all available images
- `image_count`: Total images available

### catalog_index
Maps catalog name -> Statistics
- `image_count`: Images in catalog
- `sku_count`: Unique SKUs
- `skus`: Array of all SKUs

### search_index
Normalized SKU -> Original SKU mapping
- Enables flexible searching (ignores spaces, dashes, case)

## 📋 Image Entry Format

```json
{
  "sku": "GA005GM201",
  "sku_normalized": "GA005GM201",
  "catalog": "makita-catalogus-2022-nl",
  "page": 45,
  "img_index": 2,
  "filename": "GA005GM201_makita-catalogus-2022-nl_p045_img02.webp",
  "source_path": "product-images-by-pdf/makita-catalogus-2022-nl/GA005GM201_...",
  "width": 800,
  "height": 600,
  "file_size_kb": 45.2,
  "format": "WEBP"
}
```
