"""
BUILD CENTRALIZED IMAGE DATABASE
=================================
Creates a single searchable image database with:
- Consolidated metadata for all product images
- SKU-based indexing for easy frontend lookup
- Organized directory structure
- Image validation and deduplication
"""

import json
from pathlib import Path
from collections import defaultdict
import shutil
from PIL import Image

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
SOURCE_IMAGES = PROJECT_ROOT / "product-images-by-pdf"
OUTPUT_DIR = PROJECT_ROOT / "image-database"
OUTPUT_IMAGES = OUTPUT_DIR / "images"
OUTPUT_INDEX = OUTPUT_DIR / "image_index.json"

# ============================================================================
# IMAGE DATABASE BUILDER
# ============================================================================

def parse_filename(filename):
    """
    Parse standardized filename: {SKU}_{catalog}_{page}_{img}.webp
    Example: GA005GM201_makita-catalogus-2022-nl_p045_img02.webp
    """
    try:
        parts = filename.replace('.webp', '').split('_')
        
        if len(parts) >= 4:
            sku = parts[0]
            
            # Find catalog name (everything between SKU and page marker)
            catalog_parts = []
            for i, part in enumerate(parts[1:], 1):
                if part.startswith('p') and part[1:].isdigit():
                    catalog_parts = parts[1:i]
                    page_part = part
                    img_part = parts[i+1] if i+1 < len(parts) else 'img00'
                    break
            
            catalog = '_'.join(catalog_parts) if catalog_parts else parts[1]
            page = int(page_part[1:]) if page_part.startswith('p') else 0
            img_idx = int(img_part.replace('img', '')) if 'img' in img_part else 0
            
            return {
                'sku': sku,
                'catalog': catalog,
                'page': page,
                'img_index': img_idx,
                'valid': True
            }
    except:
        pass
    
    return {'valid': False}

def get_image_info(image_path):
    """Get image dimensions and file size"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_size = image_path.stat().st_size
            
            return {
                'width': width,
                'height': height,
                'file_size_kb': round(file_size / 1024, 1),
                'format': img.format
            }
    except Exception as e:
        return None

def normalize_sku(sku):
    """Normalize SKU for consistent lookups"""
    # Remove common variations
    normalized = sku.upper().strip()
    normalized = normalized.replace(' ', '').replace('-', '').replace('_', '')
    return normalized

def build_image_database():
    """Build centralized image database with metadata"""
    
    print("="*80)
    print("BUILDING CENTRALIZED IMAGE DATABASE")
    print("="*80)
    
    if not SOURCE_IMAGES.exists():
        print(f"❌ Source images folder not found: {SOURCE_IMAGES}")
        return
    
    # Create output structure
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)
    
    # Collect all images
    all_images = []
    catalog_folders = [f for f in SOURCE_IMAGES.iterdir() if f.is_dir()]
    
    print(f"\n📁 Found {len(catalog_folders)} catalog folders")
    print(f"Scanning images...\n")
    
    stats = {
        'total_images': 0,
        'valid_images': 0,
        'skipped': 0,
        'catalogs_processed': 0,
        'unique_skus': set()
    }
    
    # Scan all images
    for catalog_folder in sorted(catalog_folders):
        catalog_name = catalog_folder.name
        image_files = list(catalog_folder.glob("*.webp"))
        
        print(f"  📂 {catalog_name}: {len(image_files)} images")
        
        for image_path in image_files:
            stats['total_images'] += 1
            
            # Parse filename
            parsed = parse_filename(image_path.name)
            
            if not parsed['valid']:
                stats['skipped'] += 1
                continue
            
            # Get image info
            img_info = get_image_info(image_path)
            if not img_info:
                stats['skipped'] += 1
                continue
            
            # Create image entry
            image_entry = {
                'sku': parsed['sku'],
                'sku_normalized': normalize_sku(parsed['sku']),
                'catalog': parsed['catalog'],
                'page': parsed['page'],
                'img_index': parsed['img_index'],
                'filename': image_path.name,
                'source_path': str(image_path.relative_to(PROJECT_ROOT)),
                'width': img_info['width'],
                'height': img_info['height'],
                'file_size_kb': img_info['file_size_kb'],
                'format': img_info['format']
            }
            
            all_images.append(image_entry)
            stats['valid_images'] += 1
            stats['unique_skus'].add(parsed['sku'])
        
        stats['catalogs_processed'] += 1
    
    print(f"\n✅ Scanned {stats['total_images']} images")
    print(f"   Valid: {stats['valid_images']}")
    print(f"   Skipped: {stats['skipped']}")
    
    # Build SKU index
    print(f"\n🔍 Building SKU index...")
    
    sku_index = defaultdict(list)
    sku_primary = {}  # Best image per SKU
    
    for img in all_images:
        sku = img['sku']
        sku_norm = img['sku_normalized']
        
        sku_index[sku].append(img)
        
        # Select primary image (largest, or first if same size)
        if sku not in sku_primary:
            sku_primary[sku] = img
        else:
            current_area = sku_primary[sku]['width'] * sku_primary[sku]['height']
            new_area = img['width'] * img['height']
            if new_area > current_area:
                sku_primary[sku] = img
    
    # Build catalog index
    print(f"📚 Building catalog index...")
    
    catalog_index = defaultdict(lambda: {
        'images': [],
        'sku_count': 0,
        'total_size_mb': 0
    })
    
    for img in all_images:
        catalog = img['catalog']
        catalog_index[catalog]['images'].append(img)
        catalog_index[catalog]['total_size_mb'] += img['file_size_kb'] / 1024
    
    for catalog, data in catalog_index.items():
        data['sku_count'] = len(set(img['sku'] for img in data['images']))
        data['total_size_mb'] = round(data['total_size_mb'], 2)
    
    # Create database structure
    database = {
        'metadata': {
            'version': '1.0',
            'total_images': stats['valid_images'],
            'total_skus': len(stats['unique_skus']),
            'catalogs': stats['catalogs_processed'],
            'generated': 'auto'
        },
        'sku_index': {
            sku: {
                'primary_image': sku_primary[sku],
                'all_images': sku_index[sku],
                'image_count': len(sku_index[sku])
            }
            for sku in sorted(sku_index.keys())
        },
        'catalog_index': {
            catalog: {
                'image_count': len(data['images']),
                'sku_count': data['sku_count'],
                'total_size_mb': data['total_size_mb'],
                'skus': sorted(list(set(img['sku'] for img in data['images'])))
            }
            for catalog, data in catalog_index.items()
        },
        'search_index': {
            # Normalized SKU -> Original SKU mapping for flexible search
            normalize_sku(sku): sku
            for sku in sku_index.keys()
        }
    }
    
    # Save database
    print(f"\n💾 Saving image database...")
    
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved to: {OUTPUT_INDEX}")
    
    # Create README
    readme_content = f"""# Image Database

## 📊 Statistics

- **Total Images**: {stats['valid_images']}
- **Unique SKUs**: {len(stats['unique_skus'])}
- **Catalogs**: {stats['catalogs_processed']}

## 🔍 Usage

### Frontend JavaScript/TypeScript

```javascript
// Load image database
const imageDB = await fetch('/image_index.json').then(r => r.json());

// Get primary image for SKU
function getProductImage(sku) {{
  const entry = imageDB.sku_index[sku];
  if (entry && entry.primary_image) {{
    return `/images/${{entry.primary_image.source_path}}`;
  }}
  return '/placeholder.webp';
}}

// Get all images for SKU (for gallery)
function getProductGallery(sku) {{
  const entry = imageDB.sku_index[sku];
  if (entry && entry.all_images) {{
    return entry.all_images.map(img => `/images/${{img.source_path}}`);
  }}
  return [];
}}

// Search by normalized SKU (flexible)
function searchBySKU(skuInput) {{
  const normalized = skuInput.toUpperCase().replace(/[\\s\\-_]/g, '');
  const actualSKU = imageDB.search_index[normalized];
  return actualSKU ? imageDB.sku_index[actualSKU] : null;
}}
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
{{
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
}}
```
"""
    
    readme_path = OUTPUT_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Summary
    print(f"\n{'='*80}")
    print("✅ IMAGE DATABASE BUILT SUCCESSFULLY")
    print(f"{'='*80}")
    print(f"\n📊 Database Statistics:")
    print(f"   Total Images:      {stats['valid_images']}")
    print(f"   Unique SKUs:       {len(stats['unique_skus'])}")
    print(f"   Catalogs:          {stats['catalogs_processed']}")
    print(f"\n📁 Output:")
    print(f"   📄 Index:          {OUTPUT_INDEX}")
    print(f"   📖 README:         {readme_path}")
    print(f"\n🔍 Sample SKUs:")
    for i, sku in enumerate(sorted(list(stats['unique_skus']))[:10], 1):
        img_count = len(sku_index[sku])
        print(f"   {i}. {sku} ({img_count} image{'s' if img_count > 1 else ''})")
    
    if len(stats['unique_skus']) > 10:
        print(f"   ... and {len(stats['unique_skus']) - 10} more")
    
    print(f"\n🎯 Usage:")
    print(f"   Frontend: imageDB.sku_index['YOUR_SKU'].primary_image")
    print(f"   Python:   image_db['sku_index']['YOUR_SKU']['primary_image']")
    print(f"\n{'='*80}\n")
    
    return database

if __name__ == "__main__":
    build_image_database()
