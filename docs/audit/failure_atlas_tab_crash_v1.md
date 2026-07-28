# Failure Atlas Tab Crash Investigation v1

**Date:** 2026-06-20
**Reporter:** UX bug — clicking Failure Atlas tab in any run detail causes blank screen
**Severity:** Critical (blank screen, no error boundary fallback)

---

## Root Cause

**Schema mismatch:** The backend API `GET /runs/{run_id}/failures` returns a paginated object `{ total, limit, offset, results: [...] }`, but the frontend `FailureAtlasTab` component expects a flat array and stores the raw API response directly as state.

When `failures` state is `{ total, limit, offset, results }`, the render path hits:
- `RunDetail.jsx:340` — `failures.every(...)` → **TypeError: failures.every is not a function**

The component crashes during render. React shows a blank screen with no error fallback.

---

## Affected Files

| File | Line(s) | Issue |
|------|---------|-------|
| `dashboard/src/RunDetail.jsx` | 287 | `.then(r => r.json())` passes full paginated object as array |
| `dashboard/src/FailureAtlasPage.jsx` | 928, 968, 561, 565 | Same pattern: state initialized as `{results: [], total: 0}`, API response stored whole, `FailureList` calls `.map()` on object |

---

## Trace (Browser → Backend → Database)

### 1. User clicks "Failure Atlas" tab
`RunDetail.jsx:1033` — tab key `"failure_atlas"`, component `FailureAtlasTab`

### 2. Component mounts, `useEffect` fires
`RunDetail.jsx:286` — fetches `GET /runs/{run_id}/failures?include_heuristic=false&include_unverified=false`

### 3. Backend handler: `backend/server.py:750`
```python
def get_run_failures(run_id, limit=50, offset=0, include_heuristic=False, include_unverified=False):
    # ... queries failure_atlas_entries table ...
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": results,        # list of row dicts
    }
```
Returns a **dict** with a `results` key, not a flat array.

### 4. Frontend receives response
`RunDetail.jsx:287`: `.then(r => r.ok ? r.json() : [])`

`r.json()` resolves to `{ total: 5, limit: 50, offset: 0, results: [{...}, ...] }`

`setFailures` stores this **object** as the `failures` state.

### 5. React re-renders with `failures` = `{ total, results, ... }`

**Render execution order:**
```
line 328: failures === null            → false (it's an object)
line 331: failures.length === 0        → undefined === 0 → false (skip empty state)
line 340: failures.every(...)          → TypeError: failures.every is not a function 🛑
```

Component throws, React unmounts, user sees blank page.

### 6. Database query
`backend/server.py:763-775`:
```sql
SELECT fa.*, r.is_important
FROM failure_atlas_entries fa
LEFT JOIN runs r ON fa.run_id = r.run_id
WHERE fa.run_id = ? AND fa.detection_classification IN (?)
ORDER BY detected_at DESC LIMIT ? OFFSET ?
```
Returns rows which are serialized into the `results` array. No DB error.

---

## Fix Applied

### Fix 1: `dashboard/src/RunDetail.jsx` (lines 287-290)

**Before:**
```js
.then(r => r.ok ? r.json() : [])
.then(setFailures)
.catch(() => setFailures([]))
```

**After:**
```js
.then(r => r.ok ? r.json() : { results: [] })
.then(data => Array.isArray(data) ? data : (data.results || []))
.then(setFailures)
.catch(() => setFailures([]))
```

The `Array.isArray(data)` guard provides backward compatibility if the API ever changes to return a flat array.

### Fix 2: `dashboard/src/FailureAtlasPage.jsx` (lines 928, 968)

**Before:**
```js
const [failures, setFailures] = useState({ results: [], total: 0 })
// ...
setFailures(f)    // f is the raw API response object
```

**After:**
```js
const [failures, setFailures] = useState([])
// ...
setFailures(Array.isArray(f) ? f : (f.results || []))
```

---

## Before/After Behavior

| State | Before | After |
|-------|--------|-------|
| Click Failure Atlas tab | Blank screen, console: `TypeError: failures.every is not a function` | Failure Atlas tab renders, shows failures or "No Failures Detected" |
| Run has 0 failures | Blank screen (`.length` undefined) | Green "No Failures Detected" message |
| Run has failures | Blank screen (`.every()`/`.map()` crash) | Failure list with expand/collapse, severity badges, resolution linking |
| Backfilled failures | Never reaches backfill check | Backfill banner shown correctly |
| Error handling workaround | Was needed: none existed before for response format mismatch | Not needed: proper response shape handling |

---

## Reproduction Steps

1. `gli-flow dashboard` — start backend
2. Open `http://127.0.0.1:8000/docs` (or frontend at `http://127.0.0.1:5173`)
3. Click any run to open Run Detail
4. Click the **Failure Atlas** tab
5. Observe: page goes blank, DevTools Console shows:
   ```
   TypeError: failures.every is not a function
   ```

---

## Related Vulnerabilities (same root cause pattern)

| Location | File | Status |
|----------|------|--------|
| `FailureAtlasPage.jsx` line 561-565 | `FailureList` component receiving raw API response | **Fixed** |
| `FailureAtlasPage.jsx` line 25-28 | `OverviewCards` — safe (guarded by `if (!analytics) return null`) | No issue |

---

## Verification

- [x] `failures` state after fetch is always `Array` (not `Object`)
- [x] `.every()` at line 340 works on array
- [x] `.map()` at line 375 works on array
- [x] `.length === 0` at line 331 correctly triggers empty state for `[]`
- [x] `.map()` in `handleResolve` at line 320 works on array
- [x] `FailureAtlasPage` `FailureList` receives array, `.map()` works
- [x] Backward-compatible: handles both array and `{results}` response shapes

---

**Root cause confirmed:** Backend returns `{ total, limit, offset, results }` but frontend treated response as flat array. Fix extracts `.results` with `Array.isArray` fallback.
