/**
 * MAKITA BATTERY PRODUCTS - REACT COMPONENTS
 * ===========================================
 * Ready-to-use React/TypeScript components for displaying battery products
 */

import React, { useState } from 'react';

// Types
interface Property {
  value: string;
  icon: string;
  label: string;
}

interface BatteryProduct {
  sku: string;
  category: 'batteries' | 'powerpacks' | 'chargers' | 'adapters';
  product_name: string;
  specifications: string;
  properties: Record<string, Property>;
  prices: {
    excl_vat: number;
    incl_vat: number;
    vat_rate: number;
  };
  display: {
    price_excl: string;
    price_incl: string;
    full_spec: string;
    properties: Record<string, string>;
  };
}

interface BatteryData {
  metadata: {
    source: string;
    note: string;
    total_products: number;
  };
  products: BatteryProduct[];
}

// ============================================================================
// BATTERY CARD COMPONENT
// ============================================================================

export const BatteryCard: React.FC<{ product: BatteryProduct }> = ({ product }) => {
  return (
    <div className="battery-card">
      {/* Header */}
      <div className="battery-card__header">
        <span className="battery-card__category">{product.category}</span>
        <h3 className="battery-card__sku">{product.sku}</h3>
      </div>

      {/* Product Name */}
      <h4 className="battery-card__name">{product.product_name}</h4>

      {/* Properties with Icons */}
      <div className="battery-card__properties">
        {Object.entries(product.properties).map(([key, prop]) => (
          <div key={key} className="property">
            <span className="property__icon">{prop.icon}</span>
            <div className="property__content">
              <span className="property__label">{prop.label}</span>
              <span className="property__value">{prop.value}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Pricing */}
      <div className="battery-card__pricing">
        <div className="price price--excl">
          <span className="price__label">Ex BTW</span>
          <span className="price__value">€ {product.prices.excl_vat.toFixed(2)}</span>
        </div>
        <div className="price price--incl">
          <span className="price__label">Incl BTW</span>
          <span className="price__value">€ {product.prices.incl_vat.toFixed(2)}</span>
        </div>
      </div>

      {/* Add to Cart Button */}
      <button className="battery-card__button">
        Add to Cart
      </button>
    </div>
  );
};

// ============================================================================
// BATTERY GRID COMPONENT
// ============================================================================

export const BatteryGrid: React.FC<{ data: BatteryData; category?: string }> = ({
  data,
  category
}) => {
  const filteredProducts = category
    ? data.products.filter(p => p.category === category)
    : data.products;

  return (
    <div className="battery-grid">
      <div className="battery-grid__header">
        <h2>{category ? category.charAt(0).toUpperCase() + category.slice(1) : 'All Products'}</h2>
        <p className="battery-grid__count">{filteredProducts.length} products</p>
      </div>

      <div className="battery-grid__items">
        {filteredProducts.map(product => (
          <BatteryCard key={product.sku} product={product} />
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// BATTERY TABLE COMPONENT
// ============================================================================

export const BatteryTable: React.FC<{ data: BatteryData; category?: string }> = ({
  data,
  category
}) => {
  const filteredProducts = category
    ? data.products.filter(p => p.category === category)
    : data.products;

  return (
    <div className="battery-table">
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Product Name</th>
            <th>Properties</th>
            <th>Price (Ex BTW)</th>
            <th>Price (Incl BTW)</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredProducts.map(product => (
            <tr key={product.sku}>
              <td className="battery-table__sku">{product.sku}</td>
              <td className="battery-table__name">{product.product_name}</td>
              <td className="battery-table__properties">
                <div className="properties-inline">
                  {Object.values(product.display.properties).map((prop, i) => (
                    <span key={i} className="property-tag">{prop}</span>
                  ))}
                </div>
              </td>
              <td className="battery-table__price">€ {product.prices.excl_vat.toFixed(2)}</td>
              <td className="battery-table__price">€ {product.prices.incl_vat.toFixed(2)}</td>
              <td className="battery-table__actions">
                <button className="btn-small">Add</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ============================================================================
// CATEGORY TABS COMPONENT
// ============================================================================

export const BatteryCategoryTabs: React.FC<{ data: BatteryData }> = ({ data }) => {
  const [activeCategory, setActiveCategory] = useState<string>('all');

  const categories = [
    { key: 'all', label: 'All Products', count: data.products.length },
    { key: 'batteries', label: 'Batteries', count: data.products.filter(p => p.category === 'batteries').length },
    { key: 'powerpacks', label: 'Powerpacks', count: data.products.filter(p => p.category === 'powerpacks').length },
    { key: 'chargers', label: 'Chargers', count: data.products.filter(p => p.category === 'chargers').length },
    { key: 'adapters', label: 'Adapters', count: data.products.filter(p => p.category === 'adapters').length },
  ];

  return (
    <div className="battery-categories">
      <div className="tabs">
        {categories.map(cat => (
          <button
            key={cat.key}
            className={`tab ${activeCategory === cat.key ? 'tab--active' : ''}`}
            onClick={() => setActiveCategory(cat.key)}
          >
            {cat.label}
            <span className="tab__count">{cat.count}</span>
          </button>
        ))}
      </div>

      <div className="tab-content">
        <BatteryGrid
          data={data}
          category={activeCategory === 'all' ? undefined : activeCategory}
        />
      </div>
    </div>
  );
};

// ============================================================================
// PROPERTY DISPLAY COMPONENT (Reusable)
// ============================================================================

export const PropertyDisplay: React.FC<{ properties: Record<string, Property> }> = ({
  properties
}) => {
  return (
    <div className="property-display">
      {Object.entries(properties).map(([key, prop]) => (
        <div key={key} className="property-item">
          <span className="property-item__icon" aria-label={prop.label}>
            {prop.icon}
          </span>
          <div className="property-item__details">
            <span className="property-item__label">{prop.label}</span>
            <span className="property-item__value">{prop.value}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

// ============================================================================
// CSS STYLES (Add to your stylesheet)
// ============================================================================

export const batteryStyles = `
/* Battery Card */
.battery-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  background: white;
  transition: box-shadow 0.2s;
}

.battery-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.battery-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.battery-card__category {
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.battery-card__sku {
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.battery-card__name {
  font-size: 18px;
  margin-bottom: 16px;
  color: #333;
}

.battery-card__properties {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.property {
  display: flex;
  align-items: center;
  gap: 12px;
}

.property__icon {
  font-size: 24px;
  width: 32px;
  text-align: center;
}

.property__content {
  display: flex;
  flex-direction: column;
}

.property__label {
  font-size: 12px;
  color: #999;
  text-transform: uppercase;
  font-weight: 600;
}

.property__value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.battery-card__pricing {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.price {
  display: flex;
  flex-direction: column;
}

.price__label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.price__value {
  font-size: 18px;
  font-weight: 700;
}

.price--incl .price__value {
  font-size: 20px;
}

.battery-card__button {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.battery-card__button:hover {
  background: #5568d3;
}

/* Battery Grid */
.battery-grid {
  padding: 20px;
}

.battery-grid__header {
  margin-bottom: 24px;
}

.battery-grid__items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 8px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 24px;
}

.tab {
  padding: 12px 24px;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab--active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab__count {
  margin-left: 8px;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.tab--active .tab__count {
  background: #667eea;
  color: white;
}
`;

// Example usage:
/*
import batteryData from './makita_batteries_formatted.json';
import { BatteryCategoryTabs, BatteryGrid, BatteryTable } from './BatteryProducts';

function App() {
  return (
    <div>
      <h1>Makita Battery Products</h1>
      <BatteryCategoryTabs data={batteryData} />
      
      {/* Or use individual components *\/}
      <BatteryGrid data={batteryData} category="batteries" />
      <BatteryTable data={batteryData} category="powerpacks" />
    </div>
  );
}
*/
