'use client';

import { useState, useEffect } from 'react';
import ProductGroupCard from '@/components/ProductGroupCard';
import SimpleProductFilters from '@/components/products/SimpleProductFilters';
import { Grid, List, Search } from 'lucide-react';

export default function AandrijftechniekCatalogPage() {
  const [productGroups, setProductGroups] = useState<any[]>([]);
  const [filteredGroups, setFilteredGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, string[]>>({});
  const [imageMapping, setImageMapping] = useState<Record<string, string>>({});

  // Load image mapping for unconventionally named images
  useEffect(() => {
    fetch('/data/aandrijftechniek_image_mapping.json')
      .then(res => res.json())
      .then(data => {
        setImageMapping(data);
      })
      .catch(err => {
        console.error('Image mapping not found, using fallback:', err);
      });
  }, []);

  useEffect(() => {
    fetch('/data/aandrijftechniek_grouped.json')
      .then(res => res.json())
      .then(data => {
        // Apply image mapping to fix unconventional image URLs
        const dataWithImages = data.map((group: any) => ({
          ...group,
          variants: group.variants.map((variant: any) => {
            const mappedImage = imageMapping[variant.sku];
            if (mappedImage) {
              return {
                ...variant,
                image: mappedImage,
                media: [{ url: mappedImage, role: 'main', type: 'image' }]
              };
            }
            return variant;
          })
        }));
        
        setProductGroups(dataWithImages);
        setFilteredGroups(dataWithImages);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading product groups:', err);
        setLoading(false);
      });
  }, [imageMapping]);

  // Convert product groups to flat products for filtering
  const flatProducts = productGroups.flatMap(group =>
    group.variants.map((v: any) => ({
      ...v.properties,
      ...v.attributes,
      sku: v.sku,
      name: v.label || v.sku,
      group_id: group.group_id,
      group_name: group.name,
      catalog: group.catalog,
      brand: group.brand,
      category: group.category,
      pdf_source: 'aandrijftechniek.pdf',
      page_in_pdf: v.page_in_pdf
    }))
  );

  // Apply search and filters
  useEffect(() => {
    let filtered = productGroups;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(group =>
        group.name.toLowerCase().includes(query) ||
        group.family.toLowerCase().includes(query) ||
        group.variants.some((v: any) =>
          v.sku.toLowerCase().includes(query) ||
          v.label.toLowerCase().includes(query)
        )
      );
    }

    // Advanced filters
    if (Object.keys(filters).length > 0) {
      const matchingGroupIds = new Set(
        flatProducts
          .filter(product => {
            return Object.entries(filters).every(([filterType, filterValues]) => {
              if (!filterValues || filterValues.length === 0) return true;

              return filterValues.some(value => {
                switch (filterType) {
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
                }
              });
            });
          })
          .map(p => p.group_id)
      );

      filtered = filtered.filter(group => matchingGroupIds.has(group.group_id));
    }

    setFilteredGroups(filtered);
  }, [searchQuery, filters, productGroups]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#00ADEF] border-t-transparent"></div>
      </div>
    );
  }

  const totalVariants = productGroups.reduce((sum, g) => sum + g.variant_count, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#00ADEF] to-blue-500 text-white">
        <div className="container mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold mb-4">⚙️ Aandrijftechniek - Product Groups</h1>
          <p className="text-xl opacity-90">
            {productGroups.length} product groups with {totalVariants} variants
          </p>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-[#00ADEF]">{filteredGroups.length}</div>
              <div className="text-gray-600">Product Groups</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#00ADEF]">{totalVariants}</div>
              <div className="text-gray-600">Total Variants</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#00ADEF]">
                {(totalVariants / productGroups.length).toFixed(1)}
              </div>
              <div className="text-gray-600">Avg Variants/Group</div>
            </div>
          </div>
        </div>
      </div>

      {/* Search & View Toggle */}
      <div className="bg-white border-b sticky top-0 z-20 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="🔍 Search product groups by name, SKU, or variant..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ADEF] focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-3 rounded-lg border-2 transition ${
                  viewMode === 'grid'
                    ? 'bg-[#00ADEF] border-[#00ADEF] text-white'
                    : 'border-gray-300 hover:border-[#00ADEF]'
                }`}
              >
                <Grid className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-3 rounded-lg border-2 transition ${
                  viewMode === 'list'
                    ? 'bg-[#00ADEF] border-[#00ADEF] text-white'
                    : 'border-gray-300 hover:border-[#00ADEF]'
                }`}
              >
                <List className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <aside className="lg:w-80 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-32">
              <h2 className="text-lg font-bold mb-4 text-gray-900">Filters</h2>
              <SimpleProductFilters
                products={flatProducts}
                onFilterChange={setFilters}
                onSearch={setSearchQuery}
              />
            </div>
          </aside>

          {/* Product Groups Grid/List */}
          <section className="flex-1">
            {filteredGroups.length === 0 ? (
              <div className="text-center py-20">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">No product groups found</h3>
                <p className="text-gray-600">Try adjusting your search or filters</p>
              </div>
            ) : (
              <div
                className={
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                    : 'space-y-4'
                }
              >
                {filteredGroups.map(group => (
                  <ProductGroupCard
                    key={group.group_id}
                    productGroup={group}
                    viewMode={viewMode}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
