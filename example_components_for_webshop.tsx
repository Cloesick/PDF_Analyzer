/**
 * Example React/Next.js Components for DemaWebshop
 * 
 * Copy these into your webshop's src/components/ folder
 */

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Product } from '@/types/product';

// ============================================================================
// EXAMPLE 1: Enhanced Product Card with Multiple Images
// ============================================================================

interface ProductCardWithImagesProps {
  product: Product;
}

export function ProductCardWithImages({ product }: ProductCardWithImagesProps) {
  const images = product.media || [];
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const hasImages = images.length > 0;
  const hasMultipleImages = images.length > 1;
  const currentImage = images[currentImageIndex]?.url || '/images/placeholder.png';

  return (
    <div className="group relative bg-white rounded-lg shadow hover:shadow-xl transition-shadow overflow-hidden">
      {/* Image Section */}
      <Link href={`/products/${product.sku}`}>
        <div className="relative aspect-square bg-gray-50">
          <Image
            src={`/${currentImage}`}
            alt={product.name}
            fill
            className="object-contain p-4"
          />
          
          {/* Image Counter Badge */}
          {hasMultipleImages && (
            <div className="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded shadow">
              {currentImageIndex + 1} / {images.length}
            </div>
          )}
          
          {/* No Image Badge */}
          {!hasImages && (
            <div className="absolute top-2 right-2 bg-gray-400 text-white text-xs px-2 py-1 rounded shadow">
              No image
            </div>
          )}
          
          {/* Image Navigation (on hover) */}
          {hasMultipleImages && (
            <div className="absolute inset-0 flex items-center justify-between px-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={(e) => {
                  e.preventDefault();
                  setCurrentImageIndex((i) => (i - 1 + images.length) % images.length);
                }}
                className="bg-white/90 hover:bg-white p-2 rounded-full shadow"
              >
                ←
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  setCurrentImageIndex((i) => (i + 1) % images.length);
                }}
                className="bg-white/90 hover:bg-white p-2 rounded-full shadow"
              >
                →
              </button>
            </div>
          )}
        </div>
      </Link>

      {/* Product Info */}
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-gray-900 line-clamp-2">
          {product.name}
        </h3>
        
        <p className="text-sm text-gray-600 line-clamp-2">
          {product.description}
        </p>
        
        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-gray-500">
            SKU: {product.sku}
          </span>
          
          {/* Catalog Badge */}
          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
            {product.catalog}
          </span>
        </div>
        
        {/* Image Thumbnails */}
        {hasMultipleImages && (
          <div className="flex gap-1 pt-2">
            {images.slice(0, 4).map((img, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentImageIndex(idx)}
                className={`
                  relative w-12 h-12 rounded border-2 overflow-hidden
                  ${idx === currentImageIndex ? 'border-blue-500' : 'border-gray-200'}
                `}
              >
                <Image
                  src={`/${img.url}`}
                  alt={`Thumbnail ${idx + 1}`}
                  fill
                  className="object-cover"
                />
              </button>
            ))}
            {images.length > 4 && (
              <div className="w-12 h-12 bg-gray-100 rounded border-2 border-gray-200 flex items-center justify-center text-xs text-gray-600">
                +{images.length - 4}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}


// ============================================================================
// EXAMPLE 2: Product Image Gallery (for detail pages)
// ============================================================================

interface ProductImageGalleryProps {
  product: Product;
}

export function ProductImageGallery({ product }: ProductImageGalleryProps) {
  const images = product.media || [];
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isZoomed, setIsZoomed] = useState(false);

  if (images.length === 0) {
    return (
      <div className="w-full aspect-square bg-gray-100 rounded-lg flex flex-col items-center justify-center">
        <div className="text-6xl text-gray-300 mb-4">📦</div>
        <p className="text-gray-400">No image available</p>
      </div>
    );
  }

  const currentImage = images[selectedIndex];

  return (
    <div className="space-y-4">
      {/* Main Image */}
      <div 
        className="relative w-full aspect-square bg-white rounded-lg overflow-hidden border-2 border-gray-200 cursor-zoom-in"
        onClick={() => setIsZoomed(!isZoomed)}
      >
        <Image
          src={`/${currentImage.url}`}
          alt={`${product.name} - Image ${selectedIndex + 1}`}
          fill
          className={`object-contain transition-transform ${isZoomed ? 'scale-150' : 'scale-100'}`}
          priority
        />
        
        {/* Zoom Hint */}
        <div className="absolute bottom-4 right-4 bg-black/50 text-white text-xs px-2 py-1 rounded">
          {isZoomed ? 'Click to zoom out' : 'Click to zoom in'}
        </div>
      </div>

      {/* Thumbnail Grid */}
      {images.length > 1 && (
        <div className="grid grid-cols-5 gap-2">
          {images.map((img, idx) => (
            <button
              key={idx}
              onClick={() => {
                setSelectedIndex(idx);
                setIsZoomed(false);
              }}
              className={`
                relative aspect-square rounded overflow-hidden border-2 transition-all
                ${idx === selectedIndex 
                  ? 'border-blue-500 ring-2 ring-blue-200' 
                  : 'border-gray-200 hover:border-blue-300'
                }
              `}
            >
              <Image
                src={`/${img.url}`}
                alt={`Thumbnail ${idx + 1}`}
                fill
                className="object-cover"
              />
            </button>
          ))}
        </div>
      )}

      {/* Image Info */}
      <div className="text-center text-sm text-gray-600">
        <p>Image {selectedIndex + 1} of {images.length}</p>
        {currentImage.format && (
          <p className="text-xs text-gray-400">Format: {currentImage.format.toUpperCase()}</p>
        )}
      </div>
    </div>
  );
}


// ============================================================================
// EXAMPLE 3: Coverage Stats Component
// ============================================================================

interface CoverageStatsProps {
  products: Product[];
  className?: string;
}

export function CoverageStats({ products, className = '' }: CoverageStatsProps) {
  const total = products.length;
  const withImages = products.filter(p => p.media && p.media.length > 0).length;
  const withoutImages = total - withImages;
  const coverage = total > 0 ? (withImages / total * 100).toFixed(1) : '0.0';
  
  const totalImages = products.reduce((sum, p) => sum + (p.media?.length || 0), 0);
  const avgImages = withImages > 0 ? (totalImages / withImages).toFixed(2) : '0.00';

  return (
    <div className={`bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-blue-900 mb-4">
        📊 Image Coverage Statistics
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          value={coverage + '%'}
          label="Coverage"
          color="blue"
        />
        <StatCard
          value={withImages.toLocaleString()}
          label="With Images"
          color="green"
        />
        <StatCard
          value={totalImages.toLocaleString()}
          label="Total Images"
          color="purple"
        />
        <StatCard
          value={avgImages}
          label="Avg per Product"
          color="orange"
        />
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>{withImages} products with images</span>
          <span>{withoutImages} without images</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${coverage}%` }}
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({ value, label, color }: { value: string; label: string; color: string }) {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg p-4 text-center shadow-sm">
      <div className={`text-2xl font-bold ${colorClasses[color as keyof typeof colorClasses]}`}>
        {value}
      </div>
      <div className="text-xs text-gray-600 mt-1">{label}</div>
    </div>
  );
}


// ============================================================================
// EXAMPLE 4: Image Filter Toggle
// ============================================================================

interface ImageFilterProps {
  showOnlyWithImages: boolean;
  onToggle: (value: boolean) => void;
  totalProducts: number;
  productsWithImages: number;
}

export function ImageFilter({ 
  showOnlyWithImages, 
  onToggle,
  totalProducts,
  productsWithImages 
}: ImageFilterProps) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border">
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={showOnlyWithImages}
          onChange={(e) => onToggle(e.target.checked)}
          className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
        />
        <span className="text-sm font-medium text-gray-700">
          Show only products with images
        </span>
      </label>
      
      <span className="text-xs text-gray-500 ml-auto">
        ({productsWithImages} / {totalProducts} have images)
      </span>
    </div>
  );
}


// ============================================================================
// EXAMPLE 5: Product List with Coverage Indicator
// ============================================================================

interface ProductListProps {
  products: Product[];
  viewMode?: 'grid' | 'list';
}

export function ProductListWithCoverage({ products, viewMode = 'grid' }: ProductListProps) {
  const [showOnlyWithImages, setShowOnlyWithImages] = useState(false);

  const filteredProducts = showOnlyWithImages
    ? products.filter(p => p.media && p.media.length > 0)
    : products;

  const withImages = products.filter(p => p.media && p.media.length > 0).length;

  return (
    <div className="space-y-6">
      {/* Coverage Stats */}
      <CoverageStats products={products} />

      {/* Filter */}
      <ImageFilter
        showOnlyWithImages={showOnlyWithImages}
        onToggle={setShowOnlyWithImages}
        totalProducts={products.length}
        productsWithImages={withImages}
      />

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Showing {filteredProducts.length} of {products.length} products
      </div>

      {/* Product Grid */}
      <div className={
        viewMode === 'grid'
          ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
          : 'space-y-4'
      }>
        {filteredProducts.map((product) => (
          <ProductCardWithImages key={product.sku} product={product} />
        ))}
      </div>

      {/* Empty State */}
      {filteredProducts.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No products found
          </h3>
          <p className="text-gray-600">
            Try adjusting your filters
          </p>
        </div>
      )}
    </div>
  );
}


// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/*

// In your products page:
import { ProductListWithCoverage } from '@/components/ProductListWithCoverage';

export default async function ProductsPage() {
  const products = await getProducts();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Products</h1>
      <ProductListWithCoverage products={products} />
    </div>
  );
}

// In your product detail page:
import { ProductImageGallery } from '@/components/ProductImageGallery';

export default async function ProductDetailPage({ params }) {
  const product = await getProductBySku(params.sku);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ProductImageGallery product={product} />
        
        <div>
          <h1 className="text-3xl font-bold">{product.name}</h1>
          <p className="text-gray-600 mt-2">{product.description}</p>
          {/* ... rest of product info ... *\/}
        </div>
      </div>
    </div>
  );
}

*/
