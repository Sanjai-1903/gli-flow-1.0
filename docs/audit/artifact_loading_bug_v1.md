# Artifact Viewer Infinite Loading Bug v1

**Date:** 2026-06-20
**Severity:** Medium — some artifacts show "Loading..." forever with no error or timeout fallback

---

## Root Cause

**Missing effect dependency:** The `useEffect` that loads artifact previews in `ArtifactViewer.jsx:415` depends on `[runId, selectedPath]` but **not** on `artifacts`. When `initialPath` is provided before the artifact list has loaded (e.g., navigating from another tab like DRC/LVS), the effect runs with an empty `artifacts` array, finds no matching artifact, and silently returns without setting any preview state. When the artifact list loads later, `selectedPath` is already the correct value so React's `useState` skips the re-render, and the effect never re-runs. `preview` stays `null` forever → "Loading..." rendered at line 522 permanently.

### Tracing the Race

```
Time ────────────────────────────────────────────────────────────────────>
         │                          │                          │
    ArtifactsTab mounts        Artifact list fetch        Artifact list
    with initialPath =         starts (useEffect 390)     resolves
    "telemetry/lvs.json"                                    (setArtifacts)
         │                          │                          │
         ▼                          ▼                          ▼
┌──────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│ selectedPath =   │    │ useEffect 415 fires  │    │ setArtifacts(data)  │
│ "telemetry/     │    │ artifacts = []        │    │ selectedPath already│
│ lvs.json"        │    │ artifact = undefined  │    │ = "telemetry/      │
│ artifacts = []   │    │ line 418: if(!artifact)│   │ lvs.json"           │
│ preview = null   │    │   → return 🛑         │    │ setSelectedPath not │
│                  │    │ preview stays null    │    │ called (same value)│
│                  │    │ previewLoading false  │    │ useEffect 415 does │
│                  │    │ previewError null     │    │ NOT re-run          │
│                  │    │                       │    │ (artifacts missing  │
│                  │    │                       │    │  from deps array)   │
└──────────────────┘    └──────────────────────┘    └─────────────────────┘
                                                           │
                                                           ▼
                                                  preview = null  ──→  "Loading..."
                                                  previewLoading = false   forever
                                                  previewError = null
```

### Affected File and Line

**`dashboard/src/ArtifactViewer.jsx:434`** — the `useEffect` dependency array is `[runId, selectedPath]`. It should include `artifacts` so the effect re-runs when the artifact list loads.

Additionally, the early-return at **line 418** (`if (!artifact) return`) silently abandons preview state without clearing it, leaving stale `null` state.

---

## All Loading Exit Paths (Before Fix)

| Path | Condition | Clears loading? |
|------|-----------|----------------|
| `line 419` | image/pdf/html, artifact found | Yes — `setPreview` immediately |
| `line 427-429` | text, fetch succeeds | Yes — `setPreviewLoading(false)` |
| `line 430` | text, fetch fails | Yes — `setPreviewLoading(false)` |
| `line 433` | unknown type, artifact found | Yes — `setPreview` immediately |
| `line 418` | **artifact not found** | **NO — silent return, preview stays null** |
| `line 416` | `!runId \|\| !selectedPath` | **NO — silent return, preview stays null** |

---

## Fix Applied

### `dashboard/src/ArtifactViewer.jsx` lines 415-434

**Before:**
```js
useEffect(() => {
    if (!runId || !selectedPath) return       // line 416 — silent abandon
    const artifact = artifacts.find(a => a.path === selectedPath)
    if (!artifact) return                      // line 418 — silent abandon
    if (artifact.is_image || ...) { ...; return }
    if (artifact.is_text) {
      setPreviewLoading(true)
      fetch(...)
        .then(data => { setPreview(...); setPreviewLoading(false) })
        .catch(e => { setPreviewError(e.message); setPreviewLoading(false) })
      return
    }
    setPreview({ type: "unknown", path: selectedPath })
}, [runId, selectedPath])                     // line 434 — missing artifacts dep
```

**After:**
```js
useEffect(() => {
    if (!runId || !selectedPath) {
      setPreview(null)                         // reset preview on exit
      setPreviewLoading(false)
      setPreviewError(null)
      return
    }
    const artifact = artifacts.find(a => a.path === selectedPath)
    if (!artifact) {
      setPreview(null)                         // reset preview on exit
      setPreviewLoading(false)
      setPreviewError(null)
      return
    }
    // ... same logic ...
}, [runId, selectedPath, artifacts])           // artifacts added to deps
```

### What changed:

1. **`artifacts` added to dependency array** (line 434) — ensures the effect re-runs when the artifact list eventually loads, even if `selectedPath` hasn't changed
2. **Both early-return paths now reset preview state** (lines 416-421 and 423-428) — `setPreview(null); setPreviewLoading(false); setPreviewError(null)` — so the UI shows a fresh state instead of whatever stale state was left from a previous selection

---

## Reproduction Steps

1. Open any run in Run Detail
2. Click a tab that navigates to Artifacts with a specific file path (e.g., click a DRC report link in DRC/LVS tab, or use `onNavigateToArtifact` from another tab)
3. Observe: Artifacts tab shows the file list, right panel shows "Loading..." on some files
4. Wait 30+ seconds — still "Loading..."
5. Click a different file in the left sidebar → that file loads immediately
6. Click back to the original file → still "Loading..." (because the same race condition triggers again)

---

## Before/After

| Scenario | Before | After |
|----------|--------|-------|
| `initialPath` set before artifacts load | "Loading..." forever | Previews loads after artifacts arrive |
| Click artifact, switch tab, come back | "Loading..." stuck | Preview loads correctly |
| Network error on preview | Error shown | Error shown (unchanged) |
| `runId` cleared while preview loading | Silent hang | Preview state reset |

---

## Verification

- [x] Effect re-runs when `artifacts` state changes (list loaded)
- [x] Preview loads for artifact selected via `initialPath`
- [x] Preview loads for artifact selected by clicking in list
- [x] Error state cleared when switching between artifacts
- [x] No infinite re-renders (effect only fires when `artifacts` reference changes, which only happens on fetch)
- [x] All early-return paths reset `preview`, `previewLoading`, `previewError` to defaults
