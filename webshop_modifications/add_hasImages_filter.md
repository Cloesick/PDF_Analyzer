# Add hasImages Filter to DemaWebshop

This guide shows how to filter products to show only those with images for demo purposes.

## Step 1: Update Product Types

**File:** `src/types/product.ts`

Add `hasImages` to the ProductFilters interface (around line 73):

```typescript
export interface ProductFilters {
  // ... existing filters ...
  
  // Image filter (NEW)
  hasImages?: boolean;  // Add this line
  
  // Pagination
  limit?: number;
  skip?: number;
  // ... rest of filters
}
```

---

## Step 2: Update API Route - Parse Query Params

**File:** `src/app/api/products/route.ts`

Add hasImages parsing in the `parseQueryParams` function (around line 65):

```typescript
function parseQueryParams(params: URLSearchParams): ProductFilters {
  // ... existing code ...
  
  return {
    // ... existing filters ...
    vlotter: getParam('vlotter', 'boolean'),
    debiet_m3_h: getParam('debiet_m3_h', 'number'),
    
    // Image filter (NEW - add before pagination)
    hasImages: getParam('hasImages', 'boolean'),
    
    // Pagination
    limit: Math.min(100, Math.max(1, getParam('limit', 'number') || 24)),
    skip: Math.max(0, getParam('skip', 'number') || 0),
    
    // Sorting
    sortBy: getParam('sortBy') || 'name',
    sortOrder: (getParam('sortOrder') as 'asc' | 'desc') || 'asc',
  };
}
```

---

## Step 3: Update API Route - Filter Logic

**File:** `src/app/api/products/route.ts`

Add image filtering in the `filterProducts` function (around line 225, before search term):

```typescript
function filterProducts(products: Product[], filters: ProductFilters): Product[] {
  // ... existing filter logic ...
  
  // Debiet m3/h
  if (filters.debiet_m3_h !== undefined && product['debiet_m3_h'] !== filters.debiet_m3_h) {
    return false;
  }
  
  // Filter by image availability (NEW - add this)
  if (filters.hasImages === true) {
    const hasMedia = product.media && Array.isArray(product.media) && product.media.length > 0;
    const hasImagePaths = product.image_paths && Array.isArray(product.image_paths) && product.image_paths.length > 0;
    
    if (!hasMedia && !hasImagePaths) {
      return false;
    }
  }
  
  // Search in multiple fields (case-insensitive)
  if (filters.searchTerm) {
    // ... existing search logic ...
  }
  
  return true;
}
```

---

## Step 4: Create Image Filter Component

**File:** `src/components/products/ImageFilterToggle.tsx` (NEW FILE)

```typescript
'use client';

import { useRouter, useSearchParams } from 'next/navigation';

export default function ImageFilterToggle() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const hasImagesFilter = searchParams.get('hasImages') === 'true';

  const handleToggle = (checked: boolean) => {
    const params = new URLSearchParams(searchParams.toString());
    
    if (checked) {
      params.set('hasImages', 'true');
    } else {
      params.delete('hasImages');
    }
    
    // Reset to first page when changing filters
    params.delete('skip');
    
    router.push(`/products?${params.toString()}`);
  };

  return (
    <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <input
        type="checkbox"
        id="hasImages"
        checked={hasImagesFilter}
        onChange={(e) => handleToggle(e.target.checked)}
        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
      />
      <label htmlFor="hasImages" className="text-sm font-medium text-blue-900 cursor-pointer">
        📷 Show only products with images (demo mode)
      </label>
    </div>
  );
}
```

---

## Step 5: Add Filter to Products Page

**File:** `src/app/products/page.tsx`

Import and use the component:

```typescript
import ImageFilterToggle from '@/components/products/ImageFilterToggle';

export default async function ProductsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Products</h1>
      
      {/* Add this component */}
      <ImageFilterToggle />
      
      {/* Your existing product list */}
      <ProductList />
    </div>
  );
}
```

---

## Step 6: Alternative - Direct URL Usage

You can also use the filter directly via URL without creating a component:

**Show only with images:**
```
http://localhost:3000/products?hasImages=true
```

**Show all products:**
```
http://localhost:3000/products
```

**Combine with other filters:**
```
http://localhost:3000/products?hasImages=true&category=pompen
http://localhost:3000/products?hasImages=true&searchTerm=airpress
```

---

## Testing

1. Start your dev server:
```bash
npm run dev
```

2. Test the filter:
- Visit `http://localhost:3000/products` (shows all 17,278 products)
- Visit `http://localhost:3000/products?hasImages=true` (shows only 8,598 with images)

3. Check the API directly:
```
http://localhost:3000/api/products?hasImages=true&limit=24
```

---

## Expected Results

**Without filter:**
- Total: 17,278 products
- Products shown: All products (with and without images)

**With filter (`hasImages=true`):**
- Total: 8,598 products
- Products shown: Only products with images
- Coverage: 49.8% of catalog

---

## Quick Demo Setup

For the fastest demo setup, just add this to your products page URL:

```
http://localhost:3000/products?hasImages=true&limit=50
```

This will show:
- First 50 products
- All with images
- Perfect for demo/presentation

---

Last updated: November 26, 2025
