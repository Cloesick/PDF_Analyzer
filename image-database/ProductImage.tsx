/**
 * REACT/TYPESCRIPT PRODUCT IMAGE COMPONENT
 * =========================================
 * Ready-to-use React component with TypeScript
 */

import React, { useState, useEffect } from 'react';
import { ImageDB } from './image-helper';

interface ProductImageProps {
  sku: string;
  alt?: string;
  width?: number | string;
  height?: number | string;
  className?: string;
  fallbackSrc?: string;
  showGallery?: boolean;
  onError?: () => void;
}

const imageDB = new ImageDB();

export const ProductImage: React.FC<ProductImageProps> = ({
  sku,
  alt,
  width = 'auto',
  height = 'auto',
  className = '',
  fallbackSrc = '/placeholder.webp',
  showGallery = false,
  onError
}) => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [gallery, setGallery] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    const loadImage = async () => {
      try {
        // Ensure database is loaded
        await imageDB.ensureLoaded();

        if (!mounted) return;

        // Get primary image
        const imgUrl = imageDB.getImage(sku);
        
        if (imgUrl) {
          setImageSrc(imgUrl);
          
          // Load gallery if requested
          if (showGallery) {
            const galleryImages = imageDB.getGallery(sku);
            setGallery(galleryImages);
          }
        } else {
          setImageSrc(fallbackSrc);
          setError(true);
          onError?.();
        }
      } catch (err) {
        console.error('Error loading product image:', err);
        if (mounted) {
          setImageSrc(fallbackSrc);
          setError(true);
          onError?.();
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadImage();

    return () => {
      mounted = false;
    };
  }, [sku, fallbackSrc, showGallery, onError]);

  if (loading) {
    return (
      <div 
        className={`product-image-loading ${className}`}
        style={{ width, height, background: '#f0f0f0' }}
      >
        <span>Loading...</span>
      </div>
    );
  }

  if (showGallery && gallery.length > 1) {
    return (
      <div className={`product-gallery ${className}`}>
        <img
          src={imageSrc || fallbackSrc}
          alt={alt || `Product ${sku}`}
          width={width}
          height={height}
          onError={() => {
            setImageSrc(fallbackSrc);
            setError(true);
          }}
        />
        <div className="gallery-thumbnails">
          {gallery.map((img, idx) => (
            <img
              key={idx}
              src={img.url}
              alt={`${sku} view ${idx + 1}`}
              className="thumbnail"
              onClick={() => setImageSrc(img.url)}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <img
      src={imageSrc || fallbackSrc}
      alt={alt || `Product ${sku}`}
      width={width}
      height={height}
      className={`product-image ${className} ${error ? 'error' : ''}`}
      onError={() => {
        setImageSrc(fallbackSrc);
        setError(true);
      }}
    />
  );
};

// Hook for direct usage
export const useProductImage = (sku: string) => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [gallery, setGallery] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadImage = async () => {
      try {
        await imageDB.ensureLoaded();
        
        if (!mounted) return;

        const imgUrl = imageDB.getImage(sku);
        const galleryImages = imageDB.getGallery(sku);
        
        setImageSrc(imgUrl);
        setGallery(galleryImages);
      } catch (err) {
        console.error('Error loading product image:', err);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadImage();

    return () => {
      mounted = false;
    };
  }, [sku]);

  return { imageSrc, gallery, loading };
};

// Example usage:
/*
import { ProductImage, useProductImage } from './ProductImage';

// Component usage
<ProductImage 
  sku="GA005GM201" 
  alt="Makita Angle Grinder"
  width={400}
  height={300}
  showGallery={true}
/>

// Hook usage
function MyComponent({ productSKU }) {
  const { imageSrc, gallery, loading } = useProductImage(productSKU);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <img src={imageSrc} alt={productSKU} />
      {gallery.length > 1 && (
        <div className="gallery">
          {gallery.map((img, i) => (
            <img key={i} src={img.url} />
          ))}
        </div>
      )}
    </div>
  );
}
*/
