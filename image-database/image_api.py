"""
PYTHON API FOR IMAGE DATABASE
==============================
Flask/FastAPI endpoints for serving product images

Usage:
    python image_api.py
    
Then access:
    http://localhost:5000/api/image/{sku}
    http://localhost:5000/api/gallery/{sku}
"""

import json
from pathlib import Path
from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
IMAGE_INDEX = PROJECT_ROOT / "image-database" / "image_index.json"
IMAGES_BASE = PROJECT_ROOT / "product-images-by-pdf"

# ============================================================================
# IMAGE DATABASE LOADER
# ============================================================================

class ImageDatabase:
    def __init__(self, index_path):
        self.index_path = index_path
        self.db = None
        self.load()
    
    def load(self):
        """Load the image database"""
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)
        print(f"✅ Loaded image database: {self.db['metadata']['total_images']} images")
    
    def normalize_sku(self, sku):
        """Normalize SKU for flexible search"""
        return sku.upper().replace(' ', '').replace('-', '').replace('_', '')
    
    def get_image(self, sku):
        """Get primary image for SKU"""
        # Try exact match
        entry = self.db['sku_index'].get(sku)
        
        # Try normalized search
        if not entry:
            normalized = self.normalize_sku(sku)
            actual_sku = self.db['search_index'].get(normalized)
            if actual_sku:
                entry = self.db['sku_index'].get(actual_sku)
        
        if entry and entry.get('primary_image'):
            return entry['primary_image']
        
        return None
    
    def get_gallery(self, sku):
        """Get all images for SKU"""
        # Try exact match
        entry = self.db['sku_index'].get(sku)
        
        # Try normalized search
        if not entry:
            normalized = self.normalize_sku(sku)
            actual_sku = self.db['search_index'].get(normalized)
            if actual_sku:
                entry = self.db['sku_index'].get(actual_sku)
        
        if entry and entry.get('all_images'):
            return entry['all_images']
        
        return []
    
    def search(self, term, limit=20):
        """Search for SKUs"""
        normalized_term = self.normalize_sku(term)
        results = []
        
        for sku in self.db['sku_index'].keys():
            if normalized_term in self.normalize_sku(sku):
                results.append(sku)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_stats(self):
        """Get database statistics"""
        return self.db['metadata']

# ============================================================================
# FLASK API
# ============================================================================

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load database
image_db = ImageDatabase(IMAGE_INDEX)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'database_loaded': image_db.db is not None,
        'stats': image_db.get_stats()
    })

@app.route('/api/image/<sku>', methods=['GET'])
def get_image(sku):
    """Get primary image URL for SKU"""
    image = image_db.get_image(sku)
    
    if not image:
        return jsonify({
            'error': 'Image not found',
            'sku': sku
        }), 404
    
    return jsonify({
        'sku': sku,
        'image': image,
        'url': f"/api/serve/{sku}"
    })

@app.route('/api/gallery/<sku>', methods=['GET'])
def get_gallery(sku):
    """Get all images for SKU (image gallery)"""
    images = image_db.get_gallery(sku)
    
    if not images:
        return jsonify({
            'error': 'No images found',
            'sku': sku
        }), 404
    
    return jsonify({
        'sku': sku,
        'images': images,
        'count': len(images)
    })

@app.route('/api/serve/<sku>', methods=['GET'])
def serve_image(sku):
    """Serve the actual image file"""
    image = image_db.get_image(sku)
    
    if not image:
        abort(404)
    
    # Construct full path
    image_path = PROJECT_ROOT / image['source_path']
    
    if not image_path.exists():
        abort(404)
    
    return send_file(
        image_path,
        mimetype='image/webp',
        as_attachment=False
    )

@app.route('/api/search/<term>', methods=['GET'])
def search_skus(term):
    """Search for SKUs by partial match"""
    results = image_db.search(term)
    
    return jsonify({
        'query': term,
        'results': results,
        'count': len(results)
    })

@app.route('/api/catalog/<catalog_name>', methods=['GET'])
def get_catalog(catalog_name):
    """Get all images from a catalog"""
    catalog = image_db.db['catalog_index'].get(catalog_name)
    
    if not catalog:
        return jsonify({
            'error': 'Catalog not found',
            'catalog': catalog_name
        }), 404
    
    return jsonify({
        'catalog': catalog_name,
        'data': catalog
    })

@app.route('/api/index', methods=['GET'])
def get_full_index():
    """Get the complete image database (for frontend caching)"""
    return jsonify(image_db.db)

# ============================================================================
# FASTAPI ALTERNATIVE
# ============================================================================

"""
# If you prefer FastAPI:

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

image_db = ImageDatabase(IMAGE_INDEX)

@app.get("/api/image/{sku}")
async def get_image(sku: str):
    image = image_db.get_image(sku)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"sku": sku, "image": image}

@app.get("/api/serve/{sku}")
async def serve_image(sku: str):
    image = image_db.get_image(sku)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_path = PROJECT_ROOT / image['source_path']
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(image_path, media_type="image/webp")
"""

# ============================================================================
# COMMAND-LINE TOOL
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'search' and len(sys.argv) > 2:
            # Search for SKU
            term = sys.argv[2]
            results = image_db.search(term, limit=10)
            print(f"\n🔍 Search results for '{term}':")
            for i, sku in enumerate(results, 1):
                print(f"  {i}. {sku}")
        
        elif command == 'get' and len(sys.argv) > 2:
            # Get image info for SKU
            sku = sys.argv[2]
            image = image_db.get_image(sku)
            if image:
                print(f"\n✅ Image found for '{sku}':")
                print(json.dumps(image, indent=2))
            else:
                print(f"\n❌ No image found for '{sku}'")
        
        elif command == 'gallery' and len(sys.argv) > 2:
            # Get gallery for SKU
            sku = sys.argv[2]
            images = image_db.get_gallery(sku)
            if images:
                print(f"\n📸 Gallery for '{sku}' ({len(images)} images):")
                for i, img in enumerate(images, 1):
                    print(f"  {i}. {img['filename']} ({img['width']}x{img['height']})")
            else:
                print(f"\n❌ No images found for '{sku}'")
        
        elif command == 'stats':
            # Show statistics
            stats = image_db.get_stats()
            print("\n📊 Database Statistics:")
            print(json.dumps(stats, indent=2))
        
        else:
            print("Usage:")
            print("  python image_api.py search <term>")
            print("  python image_api.py get <sku>")
            print("  python image_api.py gallery <sku>")
            print("  python image_api.py stats")
            print("  python image_api.py  (start API server)")
    
    else:
        # Start API server
        print("\n" + "="*80)
        print("🚀 STARTING IMAGE API SERVER")
        print("="*80)
        print(f"\nImage database: {IMAGE_INDEX}")
        print(f"Total images: {image_db.get_stats()['total_images']}")
        print(f"\nAPI Endpoints:")
        print(f"  http://localhost:5000/api/health")
        print(f"  http://localhost:5000/api/image/<sku>")
        print(f"  http://localhost:5000/api/gallery/<sku>")
        print(f"  http://localhost:5000/api/serve/<sku>")
        print(f"  http://localhost:5000/api/search/<term>")
        print(f"  http://localhost:5000/api/index")
        print(f"\n{'='*80}\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
