# Layout Image Portability Audit

Date: 2026-06-12

## Portability Issues

### Issue 1: `vite.config.js` hardcodes `127.0.0.1:8000`

**File:** `dashboard/vite.config.js`

```js
server: {
    proxy: {
      "/runs": "http://127.0.0.1:8000",
      ...
    },
  },
```

**Impact:** The Vite dev server assumes the backend lives on `127.0.0.1:8000`. If the backend runs on a different host/port, the proxy fails silently and all API calls (including images) return errors.

**Mitigation:** The `VITE_API_URL` env var allows overriding the backend URL in production builds.

---

### Issue 2: Backend uses absolute `__file__`-relative path

**File:** `backend/server.py:249`

```python
_OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs" / "runs"
```

**Impact:** The backend hardcodes the path relative to its own source location. If the project is symlinked, mounted, or the `outputs/runs/` directory is moved, images will not be found.

---

### Issue 3: `RunDirectoryManager` uses relative path

**File:** `gli_flow/runtime/run_directory.py:13`

```python
self.run_dir = Path("outputs/runs") / self.run_id
```

**Impact:** Uses CWD-relative path. If GLI-FLOW is invoked from a different working directory, run directories are created in the wrong location. The backend (which uses absolute path) won't find them.

---

### Issue 4: ORFS `REPORTS_DIR` dependency

**File:** `~/.gli-flow/orfs/flow/scripts/save_images.tcl`

```tcl
save_image -resolution $resolution $::env(REPORTS_DIR)/final_all.webp
```

**Impact:** Image generation depends on:
- `REPORTS_DIR` env variable being set correctly
- OpenROAD being compiled with GUI support (`ord::openroad_gui_compiled`)
- OpenROAD version that doesn't double-append `.png`

---

### Issue 5: PIL dependency not declared

**File:** `gli_flow/testing/layout_images.py`

```python
from PIL import Image, ImageDraw
```

**Impact:** PIL/Pillow is not a declared dependency. Placeholder image generation silently fails on machines without PIL installed, producing no images and no error.

---

### Issue 6: No MIME type assertion for WebP

**File:** `backend/server.py:345`

```python
return FileResponse(str(candidate))
```

**Impact:** `FileResponse` relies on starlette's MIME type guessing. If the system's MIME database doesn't recognize `.webp`, the browser receives `application/octet-stream` and may refuse to display the image.

---

### Issue 7: Hardcoded image name list in frontend

**File:** `dashboard/src/RunDetail.jsx:174`

```jsx
const images = ["final_all", "final_placement", "final_routing", "final_clocks", "final_ir_drop"]
```

**Impact:** The list of expected image names is hardcoded in the React component with no backend-driven discovery. If new image types are added by ORFS, they won't appear in the dashboard.

---

### Issue 8: Silent error on image load failure

**File:** `dashboard/src/RunDetail.jsx:186`

```jsx
onError={(e) => { e.target.style.display = "none" }}
```

**Impact:** When an image fails to load (e.g., 404), the error is silently swallowed. The user sees an empty card with no indication of what went wrong. No console error is logged.

---

## Summary of Portability Blockers

| # | Issue | Severity | Fix Required |
|---|-------|----------|-------------|
| 1 | `127.0.0.1:8000` hardcoded in proxy | High | Already mitigated by `VITE_API_URL` |
| 2 | Absolute `__file__` path | Medium | Use env var or relative fallback |
| 3 | CWD-relative run dir | Medium | Normalize to project root |
| 4 | ORFS GUI dependency | High | Add fallback image generation |
| 5 | Missing PIL dependency | Critical | Add SVG fallback or declare dependency |
| 6 | No explicit WebP MIME type | Low | Set `media_type="image/webp"` |
| 7 | Hardcoded image names | Low | Acceptable for known names |
| 8 | Silent error on 404 | Medium | Show placeholder + console warning |
