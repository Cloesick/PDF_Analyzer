# Image Database Integration Guide

## 🎯 Overview

You now have a **centralized, searchable image database** with:
- ✅ 5,610 product images indexed
- ✅ 2,849 unique SKUs/product numbers
- ✅ 26 catalogs covered
- ✅ Flexible search (ignores spaces, dashes, case)
- ✅ Ready-to-use frontend/backend components

## 📁 Database Structure

```
image-database/
├── image_index.json          # Main searchable database (5.6k images)
├── image-helper.js           # Frontend JavaScript helper
├── ProductImage.tsx          # React/TypeScript component
├── image_api.py              # Python Flask API server
├── README.md                 # Usage documentation
└── INTEGRATION_GUIDE.md      # This file
```

## 🚀 Quick Start

### Option 1: Frontend Only (Static)

**1. Copy files to your frontend:**
```bash
cp image-database/image_index.json public/
cp image-database/image-helper.js src/lib/
```

**2. Use in your app:**
```javascript
import { ImageDB } from './lib/image-helper';

const imageDB = new ImageDB('/image_index.json');
await imageDB.load();

// Get image for any product
const imageUrl = imageDB.getImage('GA005GM201');
// Result: '/product-images-by-pdf/makita-catalogus-2022-nl/GA005GM201_...'
```

### Option 2: With Backend API

**1. Start the Python API:**
```bash
cd image-database
pip install flask flask-cors
python image_api.py
```

**2. Access from frontend:**
```javascript
// Get image URL
const response = await fetch(`http://localhost:5000/api/image/GA005GM201`);
const data = await response.json();
console.log(data.image.source_path);

// Or serve image directly
<img src="http://localhost:5000/api/serve/GA005GM201" />
```

## 🔑 Key Features

### 1. Flexible SKU Search
All these work identically:
```javascript
imageDB.getImage('GA005GM201');     // Exact
imageDB.getImage('ga-005-gm-201');  // With dashes
imageDB.getImage('GA 005 GM201');   // With spaces
imageDB.getImage('ga005gm201');     // Lowercase
// All return the same image!
```

### 2. Multiple Images Per Product
```javascript
// Get primary (best) image
const primaryImg = imageDB.getImage('GA005GM201');

// Get all images (for gallery)
const gallery = imageDB.getGallery('GA005GM201');
// Returns: [{ url: '...', width: 800, height: 600, ... }, ...]
```

### 3. Metadata Access
```javascript
const metadata = imageDB.getMetadata('GA005GM201');
// Returns:
// {
//   primary_image: { filename: '...', width: 800, height: 600, ... },
//   all_images: [...],
//   image_count: 2
// }
```

## 🛠️ Integration Examples

### React Component
```tsx
import { ProductImage } from './ProductImage';

function ProductCard({ sku, name }) {
  return (
    <div className="product-card">
      <ProductImage 
        sku={sku}
        alt={name}
        width={400}
        height={300}
        showGallery={true}
        fallbackSrc="/placeholder.webp"
      />
      <h3>{name}</h3>
    </div>
  );
}
```

### Vue Component
```vue
<template>
  <div class="product-image">
    <img :src="imageSrc" :alt="sku" @error="handleError" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ImageDB } from './image-helper';

const props = defineProps(['sku']);
const imageSrc = ref('/placeholder.webp');
const imageDB = new ImageDB();

onMounted(async () => {
  await imageDB.load();
  const img = imageDB.getImage(props.sku);
  if (img) imageSrc.value = `/product-images-by-pdf/${img}`;
});
</script>
```

### Plain JavaScript
```html
<script src="image-helper.js"></script>
<script>
const imageDB = new ImageDB();

imageDB.load().then(() => {
  // Display product images
  document.querySelectorAll('[data-sku]').forEach(el => {
    const sku = el.dataset.sku;
    const imageUrl = imageDB.getImage(sku);
    
    if (imageUrl) {
      const img = document.createElement('img');
      img.src = `/product-images-by-pdf/${imageUrl}`;
      img.alt = sku;
      el.appendChild(img);
    }
  });
});
</script>

<!-- Usage -->
<div data-sku="GA005GM201"></div>
<div data-sku="HR005G"></div>
```

### Python Backend
```python
from image_api import ImageDatabase

# Load database
image_db = ImageDatabase('image-database/image_index.json')

# Get image in your route
@app.route('/product/<sku>')
def product_page(sku):
    image = image_db.get_image(sku)
    gallery = image_db.get_gallery(sku)
    
    return render_template('product.html',
        sku=sku,
        image=image,
        gallery=gallery
    )
```

## 📊 Database Schema

### image_index.json Structure
```json
{
  "metadata": {
    "total_images": 5610,
    "total_skus": 2849,
    "catalogs": 26
  },
  
  "sku_index": {
    "GA005GM201": {
      "primary_image": {
        "sku": "GA005GM201",
        "filename": "GA005GM201_makita-catalogus-2022-nl_p045_img02.webp",
        "source_path": "product-images-by-pdf/makita-catalogus-2022-nl/...",
        "width": 800,
        "height": 600,
        "file_size_kb": 45.2,
        "catalog": "makita-catalogus-2022-nl",
        "page": 45
      },
      "all_images": [...],
      "image_count": 2
    }
  },
  
  "catalog_index": {
    "makita-catalogus-2022-nl": {
      "image_count": 3523,
      "sku_count": 1245,
      "skus": ["GA005GM201", "HR005G", ...]
    }
  },
  
  "search_index": {
    "GA005GM201": "GA005GM201",
    "GA005GM201": "GA005GM201"  // Normalized -> Original
  }
}
```

## 🔍 Search & Lookup Methods

### 1. Direct Lookup
```javascript
imageDB.getImage('GA005GM201')  // Fast O(1) lookup
```

### 2. Flexible Search
```javascript
// Works with variations
imageDB.getImage('ga-005-gm-201')
imageDB.getImage('GA 005 GM201')
```

### 3. Partial Search
```javascript
const matches = imageDB.search('GA005', limit=10);
// Returns: ['GA005GM201', 'GA005GZ', ...]
```

### 4. Catalog Browse
```javascript
const skus = imageDB.getCatalogImages('makita-catalogus-2022-nl');
// Returns all SKUs from this catalog
```

## 🎨 Frontend Styling Tips

### Responsive Images
```css
.product-image {
  width: 100%;
  height: auto;
  object-fit: contain;
  background: white;
}

@media (max-width: 768px) {
  .product-image {
    max-height: 300px;
  }
}
```

### Loading State
```jsx
{loading ? (
  <div className="skeleton-loader" />
) : (
  <img src={imageSrc} />
)}
```

### Gallery Lightbox
```jsx
const [lightboxOpen, setLightboxOpen] = useState(false);

<ProductImage 
  sku={sku}
  showGallery={true}
  onImageClick={() => setLightboxOpen(true)}
/>
```

## 🔄 Updating the Database

When you add new PDFs or re-extract images:

```bash
# 1. Extract new images
python extract_all_images_universal.py

# 2. Rebuild database
python build_image_database.py

# 3. (Optional) Clear frontend cache
# Update version number or add cache-busting
```

## ⚡ Performance Tips

### 1. Load Database Once
```javascript
// Good - Load once on app start
const imageDB = new ImageDB();
await imageDB.load();

// Bad - Loading repeatedly
function Component({ sku }) {
  const imageDB = new ImageDB();
  await imageDB.load();  // Don't do this!
}
```

### 2. Cache in Memory
```javascript
// React Context
const ImageDBContext = createContext(null);

function App() {
  const [imageDB] = useState(() => {
    const db = new ImageDB();
    db.load();
    return db;
  });
  
  return (
    <ImageDBContext.Provider value={imageDB}>
      <YourApp />
    </ImageDBContext.Provider>
  );
}
```

### 3. Lazy Load Images
```jsx
<img 
  src={imageUrl}
  loading="lazy"  // Browser-native lazy loading
/>
```

## 🐛 Troubleshooting

### Image not found?
```javascript
const imageUrl = imageDB.getImage('YOUR-SKU');
if (!imageUrl) {
  console.log('Image not found for SKU:', 'YOUR-SKU');
  
  // Try search
  const matches = imageDB.search('YOUR');
  console.log('Similar SKUs:', matches);
}
```

### CORS issues?
If serving from different domain:
```python
# In image_api.py
from flask_cors import CORS
CORS(app)  # Already included!
```

### Path issues?
Check the base path:
```javascript
const imageDB = new ImageDB();
await imageDB.load();

// Adjust base path if needed
const imageUrl = imageDB.getImage('SKU', '/static/images/');
```

## 📝 Summary

✅ **5,610 images** indexed and searchable
✅ **2,849 SKUs** with flexible lookup
✅ **26 catalogs** covered
✅ **Ready-to-use** components for React, Vue, plain JS
✅ **Python API** included for backend integration
✅ **Type-safe** with TypeScript support

Your images are now perfectly organized and searchable by SKU/product number/bestelnr! 🎉
