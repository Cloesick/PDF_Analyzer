/**
 * IMAGE DATABASE HELPER LIBRARY
 * ==============================
 * Frontend JavaScript/TypeScript helper for accessing the image database
 * 
 * Usage:
 *   import { ImageDB } from './image-helper.js';
 *   const imageDB = new ImageDB();
 *   await imageDB.load();
 *   const imageUrl = imageDB.getImage('GA005GM201');
 */

class ImageDB {
  constructor(indexPath = '/image-database/image_index.json') {
    this.indexPath = indexPath;
    this.db = null;
    this.loaded = false;
  }

  /**
   * Load the image database
   */
  async load() {
    if (this.loaded) return this.db;
    
    try {
      const response = await fetch(this.indexPath);
      if (!response.ok) {
        throw new Error(`Failed to load image database: ${response.statusText}`);
      }
      
      this.db = await response.json();
      this.loaded = true;
      
      console.log(`✅ Image database loaded: ${this.db.metadata.total_images} images, ${this.db.metadata.total_skus} SKUs`);
      
      return this.db;
    } catch (error) {
      console.error('❌ Error loading image database:', error);
      throw error;
    }
  }

  /**
   * Ensure database is loaded
   */
  async ensureLoaded() {
    if (!this.loaded) {
      await this.load();
    }
  }

  /**
   * Normalize SKU for search (removes spaces, dashes, underscores, uppercase)
   */
  normalizeSKU(sku) {
    if (!sku) return '';
    return String(sku).toUpperCase().replace(/[\s\-_]/g, '');
  }

  /**
   * Get primary image URL for a product SKU
   * @param {string} sku - Product SKU/bestelnr
   * @param {string} basePath - Base path for images (default: '/product-images-by-pdf/')
   * @returns {string|null} Image URL or null if not found
   */
  getImage(sku, basePath = '/product-images-by-pdf/') {
    if (!this.loaded) {
      console.warn('⚠️ Image database not loaded. Call await imageDB.load() first');
      return null;
    }

    // Try exact match first
    let entry = this.db.sku_index[sku];
    
    // Try normalized search
    if (!entry) {
      const normalized = this.normalizeSKU(sku);
      const actualSKU = this.db.search_index[normalized];
      if (actualSKU) {
        entry = this.db.sku_index[actualSKU];
      }
    }

    if (entry && entry.primary_image) {
      return basePath + entry.primary_image.source_path.replace(/\\/g, '/');
    }

    return null;
  }

  /**
   * Get all images for a product SKU (for image gallery)
   * @param {string} sku - Product SKU/bestelnr
   * @param {string} basePath - Base path for images
   * @returns {Array<Object>} Array of image objects with url and metadata
   */
  getGallery(sku, basePath = '/product-images-by-pdf/') {
    if (!this.loaded) {
      console.warn('⚠️ Image database not loaded');
      return [];
    }

    // Try exact match first
    let entry = this.db.sku_index[sku];
    
    // Try normalized search
    if (!entry) {
      const normalized = this.normalizeSKU(sku);
      const actualSKU = this.db.search_index[normalized];
      if (actualSKU) {
        entry = this.db.sku_index[actualSKU];
      }
    }

    if (entry && entry.all_images) {
      return entry.all_images.map(img => ({
        url: basePath + img.source_path.replace(/\\/g, '/'),
        width: img.width,
        height: img.height,
        size_kb: img.file_size_kb,
        catalog: img.catalog,
        page: img.page
      }));
    }

    return [];
  }

  /**
   * Check if image exists for SKU
   * @param {string} sku - Product SKU/bestelnr
   * @returns {boolean}
   */
  hasImage(sku) {
    if (!this.loaded) return false;
    
    // Try exact match
    if (this.db.sku_index[sku]) return true;
    
    // Try normalized
    const normalized = this.normalizeSKU(sku);
    return !!this.db.search_index[normalized];
  }

  /**
   * Get image metadata
   * @param {string} sku - Product SKU/bestelnr
   * @returns {Object|null} Image metadata
   */
  getMetadata(sku) {
    if (!this.loaded) return null;

    // Try exact match
    let entry = this.db.sku_index[sku];
    
    // Try normalized
    if (!entry) {
      const normalized = this.normalizeSKU(sku);
      const actualSKU = this.db.search_index[normalized];
      if (actualSKU) {
        entry = this.db.sku_index[actualSKU];
      }
    }

    return entry || null;
  }

  /**
   * Search for products by partial SKU match
   * @param {string} searchTerm - Partial SKU to search for
   * @param {number} limit - Maximum results
   * @returns {Array<string>} Matching SKUs
   */
  search(searchTerm, limit = 10) {
    if (!this.loaded) return [];

    const normalized = this.normalizeSKU(searchTerm);
    const results = [];

    for (const sku in this.db.sku_index) {
      if (this.normalizeSKU(sku).includes(normalized)) {
        results.push(sku);
        if (results.length >= limit) break;
      }
    }

    return results;
  }

  /**
   * Get all images from a specific catalog
   * @param {string} catalogName - Catalog name
   * @returns {Array<Object>} Array of image objects
   */
  getCatalogImages(catalogName) {
    if (!this.loaded) return [];

    const catalog = this.db.catalog_index[catalogName];
    return catalog ? catalog.skus : [];
  }

  /**
   * Get database statistics
   * @returns {Object} Database metadata
   */
  getStats() {
    return this.loaded ? this.db.metadata : null;
  }
}

// Export for ES modules
export { ImageDB };

// Also support CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ImageDB };
}

// Example usage
/*
// Initialize
const imageDB = new ImageDB();
await imageDB.load();

// Get single image
const imageUrl = imageDB.getImage('GA005GM201');
// Returns: '/product-images-by-pdf/makita-catalogus-2022-nl/GA005GM201_makita-catalogus-2022-nl_p045_img02.webp'

// Get image gallery (all images for SKU)
const gallery = imageDB.getGallery('GA005GM201');
// Returns: [{ url: '...', width: 800, height: 600, ... }, ...]

// Check if image exists
if (imageDB.hasImage('GA005GM201')) {
  console.log('Image available!');
}

// Flexible search (ignores spaces, dashes, case)
const img1 = imageDB.getImage('GA005GM201');
const img2 = imageDB.getImage('ga-005-gm-201');  // Same result
const img3 = imageDB.getImage('GA 005 GM201');   // Same result

// Search for SKUs
const matches = imageDB.search('GA005', 10);
// Returns: ['GA005GM201', 'GA005GZ', ...]

// Get metadata
const metadata = imageDB.getMetadata('GA005GM201');
// Returns: { primary_image: {...}, all_images: [...], image_count: 2 }
*/
