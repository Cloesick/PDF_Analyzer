"""Show coverage statistics per PDF catalog."""

import json
from collections import Counter

# Load data
products = json.load(open('output/products_for_shop.json'))
missing = json.load(open('output/final_missing.json'))

# Calculate coverage per catalog
total_by_cat = Counter(p['catalog'] for p in products)
missing_by_cat = Counter(p['catalog'] for p in missing)
with_img_by_cat = {cat: total_by_cat[cat] - missing_by_cat.get(cat, 0) for cat in total_by_cat}

# Group by coverage tier
coverage_tiers = {
    '0% (No Images)': [],
    '1-25%': [],
    '26-50%': [],
    '51-75%': [],
    '76-100%': []
}

for cat in total_by_cat:
    total = total_by_cat[cat]
    with_img = with_img_by_cat[cat]
    cov = (with_img/total*100) if total > 0 else 0
    
    if cov == 0:
        coverage_tiers['0% (No Images)'].append((cat, total))
    elif cov <= 25:
        coverage_tiers['1-25%'].append((cat, total, cov))
    elif cov <= 50:
        coverage_tiers['26-50%'].append((cat, total, cov))
    elif cov <= 75:
        coverage_tiers['51-75%'].append((cat, total, cov))
    else:
        coverage_tiers['76-100%'].append((cat, total, cov))

# Print breakdown
print('\n' + '='*70)
print('COVERAGE BREAKDOWN BY TIER')
print('='*70 + '\n')

for tier, catalogs in coverage_tiers.items():
    if catalogs:
        print(f'{tier}:')
        count = len(catalogs)
        products_in_tier = sum(c[1] for c in catalogs)
        print(f'  Catalogs: {count}')
        print(f'  Products: {products_in_tier:,}')
        
        if tier == '0% (No Images)':
            for cat, total in sorted(catalogs, key=lambda x: x[1], reverse=True):
                print(f'    - {cat} ({total:,} products)')
        else:
            for cat, total, cov in sorted(catalogs, key=lambda x: x[2]):
                print(f'    - {cat} ({total:,} products, {cov:.1f}%)')
        print()

print('='*70)
