'use client';

/**
 * ImageFilterToggle Component
 * 
 * Toggles between showing all products vs only products with images.
 * Perfect for demo purposes to showcase products with proper images.
 * 
 * Usage:
 *   import ImageFilterToggle from '@/components/products/ImageFilterToggle';
 *   
 *   <ImageFilterToggle />
 * 
 * Copy this file to: src/components/products/ImageFilterToggle.tsx
 */

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

interface ImageFilterStats {
  total: number;
  withImages: number;
  percentage: number;
}

export default function ImageFilterToggle() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const hasImagesFilter = searchParams.get('hasImages') === 'true';
  const [stats, setStats] = useState<ImageFilterStats | null>(null);

  // Fetch stats (optional - remove if you don't want to show stats)
  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch('/api/products?limit=99999'); // Get all products
        const data = await res.json();
        
        const total = data.total || 0;
        const withImages = data.products.filter((p: any) => 
          (p.media && p.media.length > 0) || (p.image_paths && p.image_paths.length > 0)
        ).length;
        
        setStats({
          total,
          withImages,
          percentage: total > 0 ? (withImages / total * 100) : 0
        });
      } catch (error) {
        console.error('Failed to fetch product stats:', error);
      }
    }
    
    // Uncomment to enable stats:
    // fetchStats();
  }, []);

  const handleToggle = (checked: boolean) => {
    const params = new URLSearchParams(searchParams.toString());
    
    if (checked) {
      params.set('hasImages', 'true');
    } else {
      params.delete('hasImages');
    }
    
    // Reset to first page when changing filters
    params.delete('skip');
    params.set('page', '1');
    
    router.push(`/products?${params.toString()}`);
  };

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between gap-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="hasImages"
            checked={hasImagesFilter}
            onChange={(e) => handleToggle(e.target.checked)}
            className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
          />
          <label 
            htmlFor="hasImages" 
            className="text-sm font-medium text-blue-900 cursor-pointer select-none"
          >
            <span className="text-lg mr-2">📷</span>
            Show only products with images
            {hasImagesFilter && (
              <span className="ml-2 text-xs text-blue-600 font-normal">(Demo mode)</span>
            )}
          </label>
        </div>

        {/* Stats Badge (optional) */}
        {stats && (
          <div className="text-xs text-blue-700 bg-white px-3 py-1 rounded-full border border-blue-200">
            {stats.withImages.toLocaleString()} / {stats.total.toLocaleString()} 
            <span className="ml-1 font-semibold">({stats.percentage.toFixed(1)}%)</span>
          </div>
        )}
      </div>

      {/* Active Filter Badge */}
      {hasImagesFilter && (
        <div className="mt-2 flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
            </svg>
            Images only
            <button
              onClick={() => handleToggle(false)}
              className="ml-1 hover:text-blue-900"
              aria-label="Clear filter"
            >
              ×
            </button>
          </span>
        </div>
      )}
    </div>
  );
}
