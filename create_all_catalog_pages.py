"""
Create all missing catalog page.tsx files for the webshop
"""

from pathlib import Path
import json

# Paths
WEBSHOP_ROOT = Path(r"C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop")
CATALOG_APP_DIR = WEBSHOP_ROOT / "src" / "app" / "catalog"
DATA_DIR = WEBSHOP_ROOT / "public" / "data"

# Catalog display names
CATALOG_NAMES = {
    "abs-persluchtbuizen": "ABS Persluchtbuizen",
    "aandrijftechniek": "Aandrijftechniek",
    "airpress-catalogus-eng": "Airpress Catalog (EN)",
    "airpress-catalogus-nl-fr": "Airpress Catalog (NL/FR)",
    "bronpompen": "Bronpompen",
    "catalogus-aandrijftechniek-150922": "Catalogus Aandrijftechniek",
    "centrifugaalpompen": "Centrifugaalpompen",
    "digitale-versie-pompentoebehoren-compressed": "Pompentoebehoren",
    "dompelpompen": "Dompelpompen",
    "drukbuizen": "Drukbuizen",
    "kranzle-catalogus-2021-nl-1": "Kränzle Catalog",
    "kunststof-afvoerleidingen": "Kunststof Afvoerleidingen",
    "makita-catalogus-2022-nl": "Makita Catalog 2022",
    "makita-tuinfolder-2022-nl": "Makita Tuinfolder 2022",
    "messing-draadfittingen": "Messing Draadfittingen",
    "pe-buizen": "PE Buizen",
    "plat-oprolbare-slangen": "Plat Oprolbare Slangen",
    "pomp-specials": "Pomp Specials",
    "pu-afzuigslangen": "PU Afzuigslangen",
    "rubber-slangen": "Rubber Slangen",
    "rvs-draadfittingen": "RVS Draadfittingen",
    "slangklemmen": "Slangklemmen",
    "slangkoppelingen": "Slangkoppelingen",
    "verzinkte-buizen": "Verzinkte Buizen",
    "zuigerpompen": "Zuigerpompen",
    "zwarte-draad-en-lasfittingen": "Zwarte Draad en Lasfittingen"
}

# Icon mapping
CATALOG_ICONS = {
    "abs-persluchtbuizen": "🔧",
    "aandrijftechniek": "⚙️",
    "airpress-catalogus-eng": "💨",
    "airpress-catalogus-nl-fr": "💨",
    "bronpompen": "💧",
    "catalogus-aandrijftechniek-150922": "⚙️",
    "centrifugaalpompen": "🌊",
    "digitale-versie-pompentoebehoren-compressed": "🔩",
    "dompelpompen": "💦",
    "drukbuizen": "🚰",
    "kranzle-catalogus-2021-nl-1": "🚿",
    "kunststof-afvoerleidingen": "🚿",
    "makita-catalogus-2022-nl": "🔨",
    "makita-tuinfolder-2022-nl": "🌱",
    "messing-draadfittingen": "🔧",
    "pe-buizen": "🚰",
    "plat-oprolbare-slangen": "🔗",
    "pomp-specials": "💧",
    "pu-afzuigslangen": "🌬️",
    "rubber-slangen": "🔗",
    "rvs-draadfittingen": "⚡",
    "slangklemmen": "🔩",
    "slangkoppelingen": "🔗",
    "verzinkte-buizen": "🔩",
    "zuigerpompen": "💧",
    "zwarte-draad-en-lasfittingen": "🔧"
}


def get_page_template(catalog_key: str, catalog_name: str, icon: str) -> str:
    """Generate page.tsx content for a catalog"""
    
    # Convert catalog key to component name (PascalCase)
    component_name = ''.join(word.capitalize() for word in catalog_key.replace('-', '_').split('_'))
    
    template = f"""'use client';

import {{ useState, useEffect }} from 'react';
import ProductGroupCard from '@/components/ProductGroupCard';
import SimpleProductFilters from '@/components/products/SimpleProductFilters';
import {{ Grid, List, Search }} from 'lucide-react';

export default function {component_name}CatalogPage() {{
  const [productGroups, setProductGroups] = useState<any[]>([]);
  const [filteredGroups, setFilteredGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, string[]>>({{}});

  useEffect(() => {{
    fetch('/data/{catalog_key}_grouped.json')
      .then(res => res.json())
      .then(data => {{
        setProductGroups(data);
        setFilteredGroups(data);
        setLoading(false);
      }})
      .catch(err => {{
        console.error('Error loading product groups:', err);
        setLoading(false);
      }});
  }}, []);

  // Convert product groups to flat products for filtering
  const flatProducts = productGroups.flatMap(group =>
    group.variants.map((v: any) => ({{
      ...v.properties,
      ...v.attributes,
      sku: v.sku,
      name: v.label || v.sku,
      group_id: group.group_id,
      group_name: group.name,
      catalog: group.catalog,
      brand: group.brand,
      category: group.category,
      pdf_source: '{catalog_key}.pdf',
      page_in_pdf: v.page_in_pdf
    }}))
  );

  // Apply search and filters
  useEffect(() => {{
    let filtered = productGroups;

    // Search filter
    if (searchQuery) {{
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(group =>
        group.name.toLowerCase().includes(query) ||
        group.family.toLowerCase().includes(query) ||
        group.variants.some((v: any) =>
          v.sku.toLowerCase().includes(query) ||
          v.label.toLowerCase().includes(query)
        )
      );
    }}

    // Advanced filters
    if (Object.keys(filters).length > 0) {{
      const matchingGroupIds = new Set(
        flatProducts
          .filter(product => {{
            return Object.entries(filters).every(([filterType, filterValues]) => {{
              if (!filterValues || filterValues.length === 0) return true;

              return filterValues.some(value => {{
                switch (filterType) {{
                  case 'pdf_source':
                    return product.pdf_source === value;
                  case 'pressure_max_bar':
                    const pressure = product.pressure_max_bar || product.pressure_bar;
                    if (!pressure || pressure <= 0) return false;
                    return String(Math.round(pressure)) === value;
                  case 'weight_kg':
                    const weight = product.weight_kg;
                    if (!weight || weight <= 0) return false;
                    return String(Math.round(weight * 10) / 10) === value;
                  default:
                    return false;
                }}
              }});
            }});
          }})
          .map(p => p.group_id)
      );

      filtered = filtered.filter(group => matchingGroupIds.has(group.group_id));
    }}

    setFilteredGroups(filtered);
  }}, [searchQuery, filters, productGroups]);

  if (loading) {{
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#00ADEF] border-t-transparent"></div>
      </div>
    );
  }}

  const totalVariants = productGroups.reduce((sum, g) => sum + g.variant_count, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      {{/* Header */}}
      <div className="bg-gradient-to-r from-[#00ADEF] to-blue-500 text-white">
        <div className="container mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold mb-4">{icon} {catalog_name} - Product Groups</h1>
          <p className="text-xl opacity-90">
            {{productGroups.length}} product groups with {{totalVariants}} variants
          </p>
        </div>
      </div>

      {{/* Stats Bar */}}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-[#00ADEF]">{{filteredGroups.length}}</div>
              <div className="text-gray-600">Product Groups</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#00ADEF]">{{totalVariants}}</div>
              <div className="text-gray-600">Total Variants</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#00ADEF]">
                {{(totalVariants / productGroups.length).toFixed(1)}}
              </div>
              <div className="text-gray-600">Avg Variants/Group</div>
            </div>
          </div>
        </div>
      </div>

      {{/* Search & View Toggle */}}
      <div className="bg-white border-b sticky top-0 z-20 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="🔍 Search product groups by name, SKU, or variant..."
                value={{searchQuery}}
                onChange={{(e) => setSearchQuery(e.target.value)}}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ADEF] focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={{() => setViewMode('grid')}}
                className={{`p-3 rounded-lg border-2 transition ${{
                  viewMode === 'grid'
                    ? 'bg-[#00ADEF] border-[#00ADEF] text-white'
                    : 'border-gray-300 hover:border-[#00ADEF]'
                }}`}}
              >
                <Grid className="h-5 w-5" />
              </button>
              <button
                onClick={{() => setViewMode('list')}}
                className={{`p-3 rounded-lg border-2 transition ${{
                  viewMode === 'list'
                    ? 'bg-[#00ADEF] border-[#00ADEF] text-white'
                    : 'border-gray-300 hover:border-[#00ADEF]'
                }}`}}
              >
                <List className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {{/* Main Content */}}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {{/* Filters Sidebar */}}
          <aside className="lg:w-80 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-32">
              <h2 className="text-lg font-bold mb-4 text-gray-900">Filters</h2>
              <SimpleProductFilters
                products={{flatProducts}}
                onFilterChange={{setFilters}}
                onSearch={{setSearchQuery}}
              />
            </div>
          </aside>

          {{/* Product Groups Grid/List */}}
          <section className="flex-1">
            {{filteredGroups.length === 0 ? (
              <div className="text-center py-20">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">No product groups found</h3>
                <p className="text-gray-600">Try adjusting your search or filters</p>
              </div>
            ) : (
              <div
                className={{
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                    : 'space-y-4'
                }}
              >
                {{filteredGroups.map(group => (
                  <ProductGroupCard
                    key={{group.group_id}}
                    productGroup={{group}}
                    viewMode={{viewMode}}
                  />
                ))}}
              </div>
            )}}
          </section>
        </div>
      </div>
    </div>
  );
}}
"""
    return template


def create_catalog_pages():
    """Create all missing catalog pages"""
    
    print("="*80)
    print("📄 CREATING ALL CATALOG PAGES")
    print("="*80)
    
    # Get list of JSON files
    json_files = list(DATA_DIR.glob("*_grouped.json"))
    
    if not json_files:
        print("\n❌ No grouped JSON files found!")
        return
    
    created = 0
    skipped = 0
    
    for json_file in sorted(json_files):
        catalog_key = json_file.stem.replace("_grouped", "")
        
        # Get display name
        display_name = CATALOG_NAMES.get(catalog_key, catalog_key.replace("-", " ").title())
        icon = CATALOG_ICONS.get(catalog_key, "📦")
        
        # Create directory if needed
        page_dir = CATALOG_APP_DIR / f"{catalog_key}-grouped"
        page_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if page.tsx already exists
        page_file = page_dir / "page.tsx"
        
        if page_file.exists():
            print(f"   ⏭️  {catalog_key}-grouped (exists)")
            skipped += 1
            continue
        
        # Create page.tsx
        content = get_page_template(catalog_key, display_name, icon)
        page_file.write_text(content, encoding='utf-8')
        
        print(f"   ✅ {catalog_key}-grouped")
        created += 1
    
    print(f"\n{'='*80}")
    print("✅ CATALOG PAGES CREATION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   Created: {created}")
    print(f"   Skipped (existing): {skipped}")
    print(f"   Total: {len(json_files)}")
    
    print(f"\n🌐 All catalog pages available at:")
    print(f"   http://localhost:3000/catalog/[catalog-name]-grouped")
    print("="*80)


if __name__ == "__main__":
    create_catalog_pages()
