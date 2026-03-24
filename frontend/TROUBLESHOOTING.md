# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. **Build/Compilation Errors**

If you see TypeScript or build errors:

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .vite
npm install
npm run dev
```

### 2. **Hook Import Errors**

If `useRipple` hook isn't found:
- Check that the file exists: `src/hooks/useRipple.ts`
- Verify the import path: `@/hooks/useRipple`

### 3. **Animation Not Working**

If ripple animation doesn't show:
- Check browser console for CSS errors
- Verify `@keyframes ripple` exists in `src/index.css`
- Make sure button has `overflow-hidden` class

### 4. **Button Click Issues**

If buttons don't respond:
- Check browser console for JavaScript errors
- Verify onClick handlers are properly defined
- Check if buttons are disabled

### 5. **Type Errors**

If you see MouseEvent type errors:
```typescript
// The hook now accepts MouseEvent<HTMLElement>
// which works with all button types
```

## Quick Fixes

### Fix 1: Restart Dev Server
```bash
# Stop current server (Ctrl+C)
npm run dev
```

### Fix 2: Clear Browser Cache
- Hard refresh: `Ctrl + Shift + R` (Windows/Linux)
- Or: `Cmd + Shift + R` (Mac)

### Fix 3: Check Console
Open browser DevTools (F12) and check:
- Console tab for JavaScript errors
- Network tab for failed requests
- Elements tab for CSS issues

## Verification Steps

1. **Check if app is running:**
   - Visit `http://localhost:5173` (or your dev URL)
   - Page should load with cream background

2. **Test buttons:**
   - Click "Get Started" on home page
   - Should see ripple effect from click point
   - Button should scale down slightly

3. **Check animations:**
   - Cards should slide in on page load
   - Hover effects should work smoothly
   - Scroll reveals should trigger

## Error Messages & Solutions

### "Cannot find module '@/hooks/useRipple'"
**Solution:** Check tsconfig.json has the @ alias configured:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### "ripple is not defined"
**Solution:** Animation is missing from CSS. Verify line 91-100 in index.css

### "addRipple is not a function"
**Solution:** Hook not properly imported. Check:
```typescript
import { useRipple } from '@/hooks/useRipple'
```

### Build fails with CSS errors
**Solution:** The `@tailwind` warnings are normal - they don't affect functionality.

## Still Having Issues?

Please provide:
1. **Error message** (from browser console or terminal)
2. **Which page** the error occurs on
3. **What action** triggers the error
4. **Browser** and version you're using

## Quick Health Check

Run this in browser console on any page:
```javascript
// Check if React is loaded
console.log('React:', typeof React !== 'undefined')

// Check if animations are defined
console.log('Has ripple:', !!document.querySelector('[style*="animation: ripple"]'))

// Check button count
console.log('Buttons:', document.querySelectorAll('button').length)
```

## Common Browser Issues

### Chrome/Edge
- May cache aggressively - use hard refresh
- DevTools has good debugging

### Firefox
- May handle transforms differently
- Check for vendor prefixes

### Safari
- May need -webkit- prefixes
- Check mobile responsiveness

## Performance Issues

If app is slow:
1. Check Network tab for large files
2. Verify no console errors
3. Check CPU usage in Task Manager
4. Clear browser data

---

**Need Help?** Check the console for specific error messages and share them for targeted help!
