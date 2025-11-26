# DemaWebshop Integration Guide

## 🎯 Overview

Your `products_for_shop.json` now has **8,598 products with linked images** (49.8% coverage). Here's how to use it in your Next.js webshop.

---

## 📂 **Current Webshop Structure**

```
DemaWebshop/dema-webshop/
├── public/
│   ├── data/
│   │   └── products_for_shop.json ← Your product data
│   └── product-images/           ← Your product images
│       ├── airpress-catalogus-eng.pdf/
│       ├── abs-persluchtbuizen.pdf/
│       └── ...
├── src/
│   ├── types/product.ts          ← Product TypeScript interface
│   ├── lib/products.ts           ← Product loading functions
│   └── components/products/
│       ├── ProductCard.tsx       ← Product card component
│       ├── ProductDetailsCard.tsx ← Product detail page
│       └── ProductList.tsx       ← Product listing
```

---

## ✅ **Step 1: Copy Updated Products JSON**

```powershell
# Copy the updated products_for_shop.json to your webshop
Copy-Item "C:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json" `
          "C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\data\products_for_shop.json"
```

---

## ✅ **Step 2: Sync Product Images**

Your images are already in the webshop's `public/product-images/` folder, but let's ensure they're up to date:

```powershell
# Navigate to webshop
cd C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop

# Run the sync script (if you have one)
npm run sync-images
```

Or manually ensure images are in place:
```powershell
# Your images are at:
# C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\product-images\
```

---

## 🎨 **Step 3: Use Images in Product Cards**

Your `ProductCard.tsx` already uses the `media` field. Here's how it works:

### **Product Data Structure (from JSON):**

```json
{
  "sku": "ABSBU040",
  "name": "ABSBU040",
  "description": "ABS persluchtbuis",
  "catalog": "abs-persluchtbuizen",
  "media": [
    {
      "url": "product-images/abs-persluchtbuizen.pdf/abs_p005_img000.webp",
      "role": "main",
      "type": "image",
      "format": "webp"
    },
    {
      "url": "product-images/abs-persluchtbuizen.pdf/abs_p005_img001.webp",
      "role": "gallery",
      "type": "image",
      "format": "webp"
    }
  ],
  "image_paths": [
    "product-images/abs-persluchtbuizen.pdf/abs_p005_img000.webp",
    "product-images/abs-persluchtbuizen.pdf/abs_p005_img001.webp"
  ]
}
```

### **In ProductCard Component:**

```tsx
// src/components/products/ProductCard.tsx

export default function ProductCard({ product }: ProductCardProps) {
  // Get main image from media array
  const mainImage = product.media?.find(m => m.role === 'main')?.url;
  const fallbackImage = product.image_paths?.[0]; // Backward compatibility
  const imageUrl = mainImage || fallbackImage || '/images/placeholder-product.png';

  return (
    <div className="product-card">
      <Link href={`/products/${product.sku}`}>
        <ImageWithFallback
          src={`/${imageUrl}`}  // Add leading slash for public folder
          alt={product.name}
          width={300}
          height={300}
          className="product-image"
        />
        
        <h3>{product.name}</h3>
        <p>{product.description}</p>
        
        {/* Show multiple images indicator */}
        {product.media && product.media.length > 1 && (
          <span className="badge">
            {product.media.length} images
          </span>
        )}
      </Link>
    </div>
  );
}
```

---

## 🖼️ **Step 4: Product Detail Page with Image Gallery**

Create an image gallery for products with multiple images:

```tsx
// src/components/products/ProductImageGallery.tsx

'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Product } from '@/types/product';

interface ProductImageGalleryProps {
  product: Product;
}

export default function ProductImageGallery({ product }: ProductImageGalleryProps) {
  const images = product.media || [];
  const [selectedIndex, setSelectedIndex] = useState(0);

  if (images.length === 0) {
    return (
      <div className="w-full aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-400">No image available</p>
      </div>
    );
  }

  const currentImage = images[selectedIndex];

  return (
    <div className="space-y-4">
      {/* Main Image */}
      <div className="relative w-full aspect-square bg-white rounded-lg overflow-hidden border">
        <Image
          src={`/${currentImage.url}`}
          alt={product.name}
          fill
          className="object-contain p-4"
          priority
        />
      </div>

      {/* Thumbnail Gallery */}
      {images.length > 1 && (
        <div className="grid grid-cols-4 gap-2">
          {images.map((img, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedIndex(idx)}
              className={`
                relative aspect-square rounded border-2 overflow-hidden
                ${idx === selectedIndex ? 'border-blue-500' : 'border-gray-200'}
                hover:border-blue-300 transition-colors
              `}
            >
              <Image
                src={`/${img.url}`}
                alt={`${product.name} - Image ${idx + 1}`}
                fill
                className="object-cover"
              />
            </button>
          ))}
        </div>
      )}

      {/* Image Counter */}
      <p className="text-sm text-gray-500 text-center">
        Image {selectedIndex + 1} of {images.length}
      </p>
    </div>
  );
}
```

---

## 🔍 **Step 5: Update Product Detail Page**

```tsx
// src/app/products/[sku]/page.tsx

import ProductImageGallery from '@/components/products/ProductImageGallery';
import { getProductBySku } from '@/lib/products';

export default async function ProductDetailPage({ 
  params 
}: { 
  params: { sku: string } 
}) {
  const product = await getProductBySku(params.sku);

  if (!product) {
    return <div>Product not found</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Image Gallery */}
        <ProductImageGallery product={product} />

        {/* Right: Product Info */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <p className="text-gray-600 mt-2">{product.description}</p>
          </div>

          {/* SKU and Catalog */}
          <div className="flex gap-4 text-sm text-gray-500">
            <span>SKU: {product.sku}</span>
            <span>Catalog: {product.catalog}</span>
          </div>

          {/* Specifications */}
          {product.attributes && (
            <div className="border-t pt-4">
              <h2 className="font-semibold mb-2">Specifications</h2>
              <dl className="grid grid-cols-2 gap-2 text-sm">
                {Object.entries(product.attributes).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-gray-600">{key}:</dt>
                    <dd className="font-medium">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {/* Add to Cart */}
          <button className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700">
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 📊 **Step 6: Show Coverage Status**

Display which products have images vs placeholders:

```tsx
// src/components/products/ProductCard.tsx

export default function ProductCard({ product }: ProductCardProps) {
  const hasImage = product.media && product.media.length > 0;
  const hasMultipleImages = product.media && product.media.length > 1;

  return (
    <div className="relative product-card">
      {/* Image Badge */}
      {hasMultipleImages && (
        <span className="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">
          {product.media.length} photos
        </span>
      )}
      
      {!hasImage && (
        <span className="absolute top-2 right-2 bg-gray-400 text-white text-xs px-2 py-1 rounded">
          No image
        </span>
      )}

      {/* Rest of card... */}
    </div>
  );
}
```

---

## 🎯 **Step 7: Filter Products by Image Availability**

Add a filter to show only products with images:

```tsx
// src/components/products/ProductFilters.tsx

export default function ProductFilters() {
  const [showOnlyWithImages, setShowOnlyWithImages] = useState(false);

  const handleFilterChange = (checked: boolean) => {
    setShowOnlyWithImages(checked);
    // Update filter in your product query
    router.push(`/products?hasImages=${checked}`);
  };

  return (
    <div className="filters">
      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={showOnlyWithImages}
          onChange={(e) => handleFilterChange(e.target.checked)}
        />
        Show only products with images
      </label>
    </div>
  );
}
```

```tsx
// src/lib/products.ts

export async function getProducts(filters: ProductFilters) {
  let products = await loadProducts();

  // Filter by image availability
  if (filters.hasImages) {
    products = products.filter(p => 
      p.media && p.media.length > 0
    );
  }

  return products;
}
```

---

## 🚀 **Step 8: Deploy**

### **Development:**
```powershell
cd C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop
npm run dev
```

Visit `http://localhost:3000/products` to see your products with images!

### **Production Build:**
```powershell
npm run build
npm start
```

---

## 📈 **Coverage Statistics Component**

Show coverage stats on your products page:

```tsx
// src/components/products/CoverageStats.tsx

'use client';

import { Product } from '@/types/product';

interface CoverageStatsProps {
  products: Product[];
}

export default function CoverageStats({ products }: CoverageStatsProps) {
  const total = products.length;
  const withImages = products.filter(p => p.media && p.media.length > 0).length;
  const coverage = (withImages / total * 100).toFixed(1);
  const totalImages = products.reduce((sum, p) => sum + (p.media?.length || 0), 0);
  const avgImagesPerProduct = (totalImages / withImages).toFixed(2);

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <h3 className="font-semibold text-blue-900 mb-2">Image Coverage</h3>
      <div className="grid grid-cols-4 gap-4 text-sm">
        <div>
          <div className="text-2xl font-bold text-blue-600">{coverage}%</div>
          <div className="text-gray-600">Coverage</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{withImages.toLocaleString()}</div>
          <div className="text-gray-600">With Images</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{totalImages.toLocaleString()}</div>
          <div className="text-gray-600">Total Images</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{avgImagesPerProduct}</div>
          <div className="text-gray-600">Avg per Product</div>
        </div>
      </div>
    </div>
  );
}
```

---

## 🔄 **Continuous Updates**

### **Update Products Workflow:**

Create a batch script to sync products regularly:

```batch
REM sync_products.bat

@echo off
echo Syncing products from PDF_Analyzer to DemaWebshop...

REM Copy updated products JSON
copy "C:\Users\prova\Documents\Projects\PDF_Analyzer\output\products_for_shop.json" ^
     "C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\data\products_for_shop.json"

REM Copy images if needed (only if using different folders)
REM robocopy "C:\Users\prova\Documents\Projects\PDF_Analyzer\product-images" ^
REM         "C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop\public\product-images" /MIR

echo Done! Products synced.
pause
```

---

## 📝 **Data Validation**

Check product data before deploying:

```typescript
// scripts/validate-products.ts

import fs from 'fs';
import path from 'path';

interface ValidationResult {
  total: number;
  withImages: number;
  withoutImages: number;
  invalidImagePaths: string[];
  duplicateSKUs: string[];
}

async function validateProducts(): Promise<ValidationResult> {
  const productsPath = path.join(process.cwd(), 'public/data/products_for_shop.json');
  const products = JSON.parse(fs.readFileSync(productsPath, 'utf-8'));

  const result: ValidationResult = {
    total: products.length,
    withImages: 0,
    withoutImages: 0,
    invalidImagePaths: [],
    duplicateSKUs: [],
  };

  const skuSet = new Set<string>();

  for (const product of products) {
    // Check for duplicates
    if (skuSet.has(product.sku)) {
      result.duplicateSKUs.push(product.sku);
    }
    skuSet.add(product.sku);

    // Check images
    if (product.media && product.media.length > 0) {
      result.withImages++;
      
      // Validate image paths exist
      for (const img of product.media) {
        const imgPath = path.join(process.cwd(), 'public', img.url);
        if (!fs.existsSync(imgPath)) {
          result.invalidImagePaths.push(img.url);
        }
      }
    } else {
      result.withoutImages++;
    }
  }

  return result;
}

// Run validation
validateProducts().then(result => {
  console.log('Validation Results:');
  console.log(`Total products: ${result.total}`);
  console.log(`With images: ${result.withImages} (${(result.withImages/result.total*100).toFixed(1)}%)`);
  console.log(`Without images: ${result.withoutImages}`);
  console.log(`Invalid image paths: ${result.invalidImagePaths.length}`);
  console.log(`Duplicate SKUs: ${result.duplicateSKUs.length}`);
  
  if (result.invalidImagePaths.length > 0) {
    console.log('\nInvalid paths (first 10):');
    console.log(result.invalidImagePaths.slice(0, 10));
  }
});
```

---

## 🎨 **Styling Tips**

### **Product Card with Images:**

```css
/* styles/products.css */

.product-card {
  @apply relative bg-white rounded-lg shadow hover:shadow-lg transition-shadow;
  @apply overflow-hidden;
}

.product-card-image {
  @apply w-full aspect-square object-contain bg-white;
  @apply border-b border-gray-200;
}

.product-card-image.no-image {
  @apply bg-gray-100 flex items-center justify-center;
}

.product-card-content {
  @apply p-4 space-y-2;
}

.product-image-badge {
  @apply absolute top-2 right-2;
  @apply bg-blue-500 text-white text-xs px-2 py-1 rounded;
  @apply shadow-sm;
}
```

---

## ✅ **Testing Checklist**

- [ ] Products JSON copied to webshop
- [ ] Images visible in product cards
- [ ] Product detail pages show all images
- [ ] Image gallery works (if multiple images)
- [ ] Fallback images work for products without images
- [ ] Filters work (show only with images)
- [ ] Coverage stats display correctly
- [ ] No broken image links
- [ ] SEO: Images have proper alt text
- [ ] Performance: Images are optimized (Next.js Image component)

---

## 🎯 **Summary**

**Your webshop now has:**
- ✅ 8,598 products with images (49.8% coverage)
- ✅ 31,500 total images linked
- ✅ Average 3.66 images per product
- ✅ Images automatically shared for table variants
- ✅ Ready to render in Next.js

**Quick Start:**
```powershell
# 1. Copy products
Copy-Item PDF_Analyzer\output\products_for_shop.json DemaWebshop\dema-webshop\public\data\

# 2. Start dev server
cd DemaWebshop\dema-webshop
npm run dev

# 3. Visit http://localhost:3000/products
```

---

Last Updated: November 26, 2025
