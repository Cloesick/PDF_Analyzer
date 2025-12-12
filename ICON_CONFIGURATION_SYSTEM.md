# 🎨 Property Icon Configuration System

**Date:** December 5, 2025  
**Status:** ✅ COMPLETE - Centralized Icon Management

---

## 📋 Overview

Created a centralized configuration system for property icons that separates icon mapping logic from the component code.

---

## 🗂️ File Structure

### Configuration File:
```
src/config/propertyIcons.ts
```
**Purpose:** Central database of all icon mappings

### Component File:
```
src/components/products/PropertyBadges.tsx
```
**Purpose:** Uses the configuration to render badges

---

## 🎯 Key Features

### 1. **Priority-Based Matching**
Icons are checked by priority (highest first):
- **100** - Identification (SKU, EAN, etc.)
- **95** - Product Types (Pump, Compressor)
- **90** - Dimensions
- **85** - Power & Electrical
- **80** - Pressure & Air
- **75** - Mechanical
- **70** - Fasteners
- **65** - Consumables, Welding
- **60** - Fluids, Logistics
- **50** - Generic Specifications
- **0** - Default fallback

### 2. **Keyword Matching**
Each icon has multiple keywords (including Dutch):
```typescript
{
  icon: '⚡',
  keywords: ['power', 'wattage', 'kw', 'watt', 'vermogen'],
  priority: 85
}
```

### 3. **Category Organization**
Icons are grouped by category:
- IDENTIFICATION
- PRODUCT_TYPE
- DIMENSIONS
- PRESSURE_AIR
- POWER_ELECTRICAL
- MECHANICAL
- FASTENERS
- CONSUMABLES
- WELDING
- FLUIDS_CHEMICALS
- TEMP_ENVIRONMENT
- VOLUME_CAPACITY
- LOGISTICS
- MATERIALS
- CONNECTIONS
- SPECIFICATIONS

---

## 📊 Complete Icon Mappings

### IDENTIFICATION
| Icon | Keywords | Description |
|------|----------|-------------|
| 🏷️ | sku, art_nr, model, ref, bestelnr | Primary ID |
| 🏁 | ean, gtin, barcode, upc | Retail Scan |
| 🌐 | hs_code, customs_code, taric | Import/Export |
| 🏳️ | country_of_origin, made_in | Origin |
| 🏭 | manufacturer, brand, merk | Manufacturer |
| 🔍 | catalog_link, pdf, datasheet | Documentation |

### PRODUCT TYPES
| Icon | Keywords | Description |
|------|----------|-------------|
| ⛽ | pump, pomp, centrifugal | Pump Products |
| 🗜 | compressor | Compressor Products |

### DIMENSIONS
| Icon | Keywords | Description |
|------|----------|-------------|
| 📦 | dimensions, size, afmetingen | Box/Item Size |
| 📏 | length, depth, lengte | Length/Depth |
| ↔️ | width, breadth, breedte | Width |
| ↕️ | height, hoogte | Height |
| 🔘 | outer_diameter, od, buitendiameter | Outer Diameter |
| 🍩 | inner_diameter, id, bore, dn | Inner Diameter |
| ⭕ | diameter, ø | Diameter (General) |
| 📐 | wall_thickness, gauge, dikte | Wall Thickness |
| ⛡ | angle, chamfer, bevel, hoek | Angle/Geometry |

### PRESSURE & AIR
| Icon | Keywords | Description |
|------|----------|-------------|
| 🔺 | max_pressure, cut_out, burst | Maximum Pressure |
| 🔻 | min_pressure, cut_in | Minimum Pressure |
| 🔧 | pressure, bar, psi, druk | Operating Pressure |
| 👈 | intake, input, suction, aanzuig | Intake/Input |
| 👉 | outtake, output, exhaust | Outtake/Output |
| 🌬️ | air_consumption, flow, debiet | Air Flow |
| 📏 | opvoerhoogte, head, lift | Head/Lift Height |

### POWER & ELECTRICAL
| Icon | Keywords | Description |
|------|----------|-------------|
| 🐴 | hp, horsepower, pk | Horsepower |
| ⚡ | power, wattage, kw, vermogen | Power (kW/Watts) |
| 🔌 | voltage, volt, spanning | Voltage |
| ⚡ | amperage, current, stroom | Current |
| 🔋 | battery, ah, accu | Battery Capacity |
| ⌛ | charger_time, recharge | Charging Time |
| 🛡️ | protection_class, ip_rating | IP Rating |
| 〰️ | frequency, hz | Frequency |

### MECHANICAL
| Icon | Keywords | Description |
|------|----------|-------------|
| 🔄 | rpm, speed, rotation, toeren | RPM/Speed |
| 🔃 | torque, nm, koppel | Torque |
| 🔨 | impact_energy, joules | Impact Energy |
| ↕️ | stroke_length, slaglengte | Stroke Length |
| 〰️ | vibration, trilling | Vibration Level |
| 🔧 | piston, zuiger | Piston |
| ⚙️ | cylinder, cilinder | Cylinder |

### FASTENERS
| Icon | Keywords | Description |
|------|----------|-------------|
| 🧬 | thread_size, schroefdraad, bsp | Thread Size |
| 📏 | thread_pitch, pitch, spoed | Thread Pitch |
| 🗝️ | drive_type, torx, hex | Drive Type |
| 🧢 | head_shape, countersunk, kop | Head Shape |
| 💪 | tensile_strength, grade | Tensile Strength |

### CONSUMABLES
| Icon | Keywords | Description |
|------|----------|-------------|
| 🏜️ | grit, grain, korrel | Grit/Grain |
| 🦷 | teeth, tpi, tanden | Teeth Count |
| 🔪 | kerf, cut_width | Kerf/Cut Width |
| 🧪 | bonding, matrix, resin | Bonding/Matrix |

### WELDING
| Icon | Keywords | Description |
|------|----------|-------------|
| ⚡ | welding_current, lasstroom | Welding Current |
| ⏱️ | duty_cycle, inschakelduur | Duty Cycle |
| 🧶 | wire_diameter, draaddiameter | Wire Diameter |
| ☁️ | shielding_gas, beschermgas | Shielding Gas |

### FLUIDS & CHEMICALS
| Icon | Keywords | Description |
|------|----------|-------------|
| 🍯 | viscosity, iso_vg, sae | Viscosity |
| 💥 | flash_point, vlampunt | Flash Point |
| 🧪 | ph_level, ph, zuurgraad | pH Level |
| 🛢️ | container_type, drum, can | Container Type |

### TEMPERATURE & ENVIRONMENT
| Icon | Keywords | Description |
|------|----------|-------------|
| 🔥 | max_temp, max_temperature | Maximum Temp |
| ❄️ | min_temp, min_temperature | Minimum Temp |
| 🌡️ | temp, temperature, liquid_temp | Temperature Range |
| 🔊 | noise, db, sound, geluid | Noise Level |

### VOLUME & CAPACITY
| Icon | Keywords | Description |
|------|----------|-------------|
| 🫙 | volume, tank, capacity, inhoud | Volume/Tank |
| 🫗 | liter, litre | Liters |

### LOGISTICS
| Icon | Keywords | Description |
|------|----------|-------------|
| 📦 | pack_qty, box_unit | Pack Quantity |
| 🏗️ | pallet_qty, pallet | Pallet Quantity |
| ⚖️ | net_weight, weight, gewicht | Net Weight |
| 📦 | gross_weight, bruto_gewicht | Gross Weight |

### MATERIALS
| Icon | Keywords | Description |
|------|----------|-------------|
| 🧱 | material, materiaal, housing | Material/Housing |

### CONNECTIONS
| Icon | Keywords | Description |
|------|----------|-------------|
| 🔗 | connection, aansluiting | Connection Type |

### SPECIFICATIONS
| Icon | Keywords | Description |
|------|----------|-------------|
| 📋 | spec_, specification | Generic Specs |

---

## 💻 How to Use

### Import the Function:
```typescript
import { getPropertyIcon } from '@/config/propertyIcons';
```

### Get Icon for a Property:
```typescript
const icon = getPropertyIcon('vermogen_kw');  // Returns: ⚡
const icon2 = getPropertyIcon('inner_diameter');  // Returns: 🍩
const icon3 = getPropertyIcon('hp');  // Returns: 🐴
```

### Get Mappings by Category:
```typescript
import { getMappingsByCategory } from '@/config/propertyIcons';

const powerIcons = getMappingsByCategory('POWER_ELECTRICAL');
// Returns all power/electrical icon mappings
```

### Get All Categories:
```typescript
import { getAllCategories } from '@/config/propertyIcons';

const categories = getAllCategories();
// Returns: ['IDENTIFICATION', 'PRODUCT_TYPE', 'DIMENSIONS', ...]
```

---

## 🔧 How to Add New Icons

### Edit: `src/config/propertyIcons.ts`

Add a new entry to the `PROPERTY_ICON_MAPPINGS` array:

```typescript
{
  category: 'MECHANICAL',
  icon: '🔩',
  keywords: ['bolt', 'screw', 'bout', 'schroef'],
  description: 'Bolts and Screws',
  priority: 75
}
```

**That's it!** The component will automatically use the new mapping.

---

## 🎯 Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| **100** | Critical identifiers (SKU, EAN) |
| **95** | Product type classification |
| **90-85** | Core specifications (dimensions, power) |
| **80-75** | Important operating parameters |
| **70-65** | Technical details |
| **60** | Supporting info (logistics, fluids) |
| **50** | Generic/fallback categories |

**Higher priority = checked first**

---

## 📊 Matching Logic

### How Keywords Are Matched:
1. Convert property key to lowercase
2. Sort mappings by priority (highest first)
3. For each mapping, check if ANY keyword is included in the key
4. Return icon of first match
5. If no match, return default icon (▪️)

### Example:
```typescript
Property key: "vermogen_kw"
↓ (lowercase)
"vermogen_kw"
↓ (check mappings by priority)
Priority 85: keywords: ['power', 'wattage', 'kw', 'vermogen']
↓ (match found: 'vermogen' and 'kw')
Return: ⚡
```

---

## ✅ Benefits

### 1. **Centralized Management**
- All icons in one file
- Easy to update
- No need to edit component code

### 2. **Easy to Extend**
Just add new entries to the array!

### 3. **Priority Control**
Higher priority rules checked first

### 4. **Bilingual Support**
Dutch and English keywords together

### 5. **Category Organization**
Logical grouping for maintenance

### 6. **Type Safety**
TypeScript interfaces ensure consistency

### 7. **Reusable**
Can be used by any component

---

## 🧪 Testing

After adding new icons:

1. **Hard Refresh:**
   ```
   Ctrl + Shift + R (Windows)
   Cmd + Shift + R (Mac)
   ```

2. **Check Console:**
   No errors should appear

3. **Verify Icons:**
   Visit catalog pages and confirm new icons display

---

## 📝 Files Modified

### Created:
- ✅ `src/config/propertyIcons.ts` - Icon configuration database

### Updated:
- ✅ `src/components/products/PropertyBadges.tsx` - Now imports from config

---

## 🎉 Summary

**Before:**
- Icons hardcoded in component
- 80+ lines of if statements
- Hard to maintain
- Scattered logic

**After:**
- ✅ Centralized configuration file
- ✅ 600+ lines of organized mappings
- ✅ Priority-based matching
- ✅ Easy to extend
- ✅ Type-safe
- ✅ Well-documented
- ✅ Bilingual support
- ✅ Category organization

**Total Icons Configured: 60+**  
**Total Keywords: 300+**  
**Categories: 16**

---

**The icon system is now fully modular and maintainable!** 🎨✨
