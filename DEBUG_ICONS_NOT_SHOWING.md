# 🔍 Debug Icons Not Showing

**Date:** December 5, 2025  
**Issue:** Icons not appearing on frontend  
**Status:** 🔍 DEBUGGING

---

## 🛠️ I've Added Debug Logging

I've added console.log statements to the PropertyBadges component to help us diagnose the issue.

---

## 📋 Steps to Debug:

### 1. Open Browser Console
- Press **F12**
- Click the **Console** tab

### 2. Hard Refresh the Page
- **Windows:** `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`

### 3. Navigate to a Catalog Page
```
http://localhost:3000/catalog/centrifugaalpompen-grouped
```

### 4. Check Console Output

**Look for these messages:**

#### Message 1: Component Rendering
```
PropertyBadges render: {
  properties: {...},
  maxDisplay: 12,
  hasProperties: true
}
```

#### Message 2: Entries Count
```
PropertyBadges entries to render: 11 [Array...]
```

#### Message 3: Individual Badges
```
Rendering badge: {
  key: "bestelnr",
  value: "03730025",
  icon: "🏷️",
  colorClasses: "bg-slate-50 text-slate-800 border-slate-200"
}
```

---

## 🎯 What to Report Back

### If You See Console Logs:

**Tell me:**
1. How many entries are being rendered?
2. What icons are showing in the console? (e.g., "⚡", "🔌", "💨")
3. Are the badges actually rendering in the HTML but just not visible?

### If You DON'T See Console Logs:

**This means PropertyBadges is not rendering at all!**

**Check:**
1. Is the component being called?
2. Are there any React errors in the console?
3. Is the dev server running?

---

## 🔧 Possible Issues & Solutions

### Issue 1: Component Not Rendering
**Symptom:** No console logs at all

**Check:**
```
Look for errors like:
- "PropertyBadges is not defined"
- "Cannot read property of undefined"
- React hydration errors
```

**Solution:** Component import issue

---

### Issue 2: Properties Empty
**Symptom:** Log shows "No properties, returning null"

**Possible causes:**
- `selectedVariant.properties` is undefined
- `selectedVariant.properties` is empty object `{}`

**Check in console:**
```javascript
// Type this in console:
document.querySelectorAll('[data-product-group]')
```

---

### Issue 3: Badges Rendering But Icons Not Visible
**Symptom:** Console shows badges rendering, but no icons on page

**Possible causes:**
- Font/emoji not loading
- CSS hiding the icons
- Browser emoji support issue

**Solution:** Check browser support for emojis

---

### Issue 4: React Not Picking Up Changes
**Symptom:** Old code still running

**Solutions:**
1. Kill dev server (Ctrl+C)
2. Delete `.next` folder
3. Restart: `npm run dev`

---

## 🧪 Quick Tests in Browser Console

### Test 1: Check if Component Exists
```javascript
// Open console and type:
typeof PropertyBadges
// Should return: "function" or "object"
```

### Test 2: Check Property Data
```javascript
// In console:
JSON.parse(document.body.innerText).variants[0].properties
// Should show all properties
```

### Test 3: Check DOM
```javascript
// In console:
document.querySelectorAll('.inline-flex.items-center').length
// Should return number of badges
```

---

## 📸 What Good Output Looks Like

### Console Should Show:
```
PropertyBadges render: {properties: {…}, maxDisplay: 12, hasProperties: true}
PropertyBadges entries to render: 11 (11) […]
Rendering badge: {key: 'bestelnr', value: '03730025', icon: '🏷️', colorClasses: 'bg-slate-50 text-slate-800 border-slate-200'}
Rendering badge: {key: 'spanning_v', value: '1x230V', icon: '🔌', colorClasses: 'bg-amber-50 text-amber-800 border-amber-200'}
Rendering badge: {key: 'vermogen_kw', value: '1,1', icon: '⚡', colorClasses: 'bg-yellow-50 text-yellow-800 border-yellow-200'}
...
```

### HTML Should Show:
```html
<div class="mb-2 flex flex-wrap gap-1.5">
  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border bg-slate-50 text-slate-800 border-slate-200">
    🏷️ 03730025
  </span>
  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border bg-amber-50 text-amber-800 border-amber-200">
    🔌 1x230V
  </span>
  ...
</div>
```

---

## 🚨 Common Problems

### Problem 1: Old Code Cached
```bash
# Solution:
cd C:\Users\prova\Documents\Projects\DemaWebshop\dema-webshop
Remove-Item .next -Recurse -Force
npm run dev
```

### Problem 2: Import Error
**Check:** `ProductGroupCard.tsx` line 8:
```typescript
import { PropertyBadges } from './products/PropertyBadges';
```

Should be importing from correct path!

### Problem 3: TypeScript Error
**Check terminal** for TypeScript compilation errors

### Problem 4: Browser Not Supporting Emojis
**Test:** Can you see this emoji? 🏷️
If not, browser may not support emoji rendering

---

## 📋 Checklist

Before reporting back, check:

- [ ] Hard refreshed browser (Ctrl+Shift+R)
- [ ] Opened browser console (F12)
- [ ] Looked for console.log messages
- [ ] Checked for React errors in console
- [ ] Verified dev server is running
- [ ] Checked HTML inspector for badge elements
- [ ] Tried different catalog page
- [ ] Cleared browser cache

---

## 💬 What to Tell Me

**Copy and paste the console output here:**
```
[Paste console logs]
```

**Screenshot or describe what you see:**
- Do you see ANY badges at all?
- Do you see text without icons?
- Do you see nothing?
- Do you see errors?

---

## 🔄 Next Steps

After you check the console, tell me what you find and I'll provide the specific fix!

**The debug logs will show us exactly where the problem is.** 🔍✨
