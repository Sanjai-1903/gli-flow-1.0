# Layout Image Pipeline — End-to-End Trace

Date: 2026-06-12

## Overview

Layout images flow through 5 stages: OpenROAD generation → filesystem artifacts → backend API → browser network → React render. This document traces every stage.

---

## Stage 1: Image Generation

### Path A — Real OpenROAD Run (GUI-capable)

**Source:** ORFS `save_images.tcl` (`~/.gli-flow/orfs/flow/scripts/save_images.tcl`)

**Trigger:** Called from `final_report.tcl` only when `[ord::openroad_gui_compiled]` is true.

**Command:**
```tcl
save_image -resolution 500 $::env(REPORTS_DIR)/final_all.webp
```

**Output:** `reports/final_all.webp.png`

**Bug:** OpenROAD appends `.png` to the requested filename. Despite requesting `final_all.webp`, the file is saved as `final_all.webp.png`.

### Path B — Mock Run

**Source:** `gli_flow/testing/layout_images.py:generate_placeholder_images()`

**Trigger:** Called from `mock_adapter.py:112` and `orchestrator.py:1161` (mock mode only).

**Mechanism:** Uses PIL (`PIL.Image`) to generate colored placeholder images.

**Output:** `reports/final_all.webp` (if PIL available, WebP format) or `reports/final_all.png` (fallback).

**Bug:** If PIL is not installed, generation silently fails — no images are created and no error is raised.

### Path C — Real OpenROAD Run (no GUI)

**Result:** No images generated at all. `save_images.tcl` is gated by `[ord::openroad_gui_compiled]`. No fallback exists.

---

## Stage 2: Filesystem Storage

**Base directory:** `<project>/outputs/runs/<run_id>/`

**Image location:** `<run_dir>/reports/<filename>`

**Expected filenames:**
- `final_all.webp` or `final_all.png`
- `final_placement.webp` or `final_placement.png`
- `final_routing.webp` or `final_routing.png`
- `final_clocks.webp` or `final_clocks.png`
- `final_ir_drop.webp` or `final_ir_drop.png`

**Actual filenames (real ORFS run):**
- `final_all.webp.png` ← double extension bug
- `final_placement.webp.png`
- `final_routing.webp.png`
- `final_clocks.webp.png`
- `final_ir_drop.webp.png`

---

## Stage 3: Backend API

**Endpoint:** `GET /runs/{run_id}/image/{image_name}`  
**Source:** `backend/server.py:340-349`

**Resolution logic:**
1. `_OUTPUTS_DIR` = absolute path to `outputs/runs/` (from `__file__`)
2. `_safe_run_path()` resolves candidate and checks path traversal
3. Iterates extensions: `""`, `.webp`, `.png`, `.jpg`
4. Checks `<run_dir>/reports/<name><ext>` first, then `<run_dir>/<name><ext>`

**Bug:** Extension list does **not** include `.webp.png`. Files named `final_all.webp.png` are never matched.

---

## Stage 4: Browser Fetch

**Frontend URL construction:** `` `${API_BASE}/runs/${run.run_id}/image/${name}` ``

**Example URL:** `/runs/run_abc123/image/final_all`

**API_BASE:** `import.meta.env.VITE_API_URL || ""` (empty string in dev → relative URLs)

**Vite proxy:** Maps `/runs/*` to `http://127.0.0.1:8000` (hardcoded in `vite.config.js`)

**Response:**
- Success: 200, `Content-Type: image/webp` (or `image/png`)
- Failure: 404, `Content-Type: application/json` `{"detail": "Image not found"}`

---

## Stage 5: React Rendering

**Component:** `LayoutImagesTab` in `dashboard/src/RunDetail.jsx:173-189`

```jsx
function LayoutImagesTab({ run }) {
  const images = ["final_all", "final_placement", "final_routing", "final_clocks", "final_ir_drop"]
  return (
    <div className="grid grid-cols-2 gap-4">
      {images.map((name) => (
        <div key={name} className="bg-white border border-stone-ridge rounded-lg p-3">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] mb-2">{name}</p>
          <img
            src={`${API_BASE}/runs/${run.run_id}/image/${name}`}
            alt={name}
            className="w-full rounded border border-stone-ridge"
            onError={(e) => { e.target.style.display = "none" }}
          />
        </div>
      ))}
    </div>
  )
}
```

**Error handling:** On 404/error, `<img>` is hidden via `display: none`. No placeholder, no error message, no console log.

---

## Summary Diagram

```
OpenROAD save_images.tcl
  │ if GUI-compiled → final_all.webp.png  (BUG: double ext)
  │ if no GUI       → nothing             (BUG: no fallback)
  ▼
reports/final_all.webp.png
  │
  ▼
GET /runs/{id}/image/final_all
  │ searches .webp, .png, .jpg → none match .webp.png (BUG)
  │ returns 404
  ▼
<img src="/runs/{id}/image/final_all">
  │ 404 → onError fires
  ▼
display: none  ── user sees empty card
```
