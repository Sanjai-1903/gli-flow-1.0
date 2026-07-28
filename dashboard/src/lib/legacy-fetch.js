// Global fetch shim.
//
// The legacy dashboard (App.jsx and its pages) makes bare fetch calls like
//   fetch(`${API_BASE}/runs?limit=10`)
//   fetch(`${API_BASE}/health`)
//   fetch(`${API_BASE}/failures/${id}/resolution`)
//
// where API_BASE is empty in production. We rewrite those to hit the
// FastAPI ingest server's legacy-shape endpoints, and we attach the
// signed-in user's Supabase JWT as a Bearer token.
//
// This lets the entire legacy dashboard become multi-tenant without
// touching any of its component code.

import { supabase, INGEST_URL } from './supabase'

// Paths the legacy dashboard calls that should be rewritten to
// /api/v1/legacy on the ingest server.
const LEGACY_PATH_PREFIXES = [
  '/runs',
  '/live_runs',
  '/trends',
  '/releases',
  '/health',
  '/failures',
  '/analytics',
  '/regressions',
  '/knowledge',
  '/similar-failures',
  '/telemetry',
  '/ai',
  '/provenance',
  '/reliability',
]

function shouldRewrite(url) {
  // Absolute URL → leave alone (HomePage / tokens etc. use INGEST_URL directly).
  if (/^https?:\/\//i.test(url)) return false
  // Already targeting our new API namespace.
  if (url.startsWith('/api/')) return false
  return LEGACY_PATH_PREFIXES.some((p) => url === p || url.startsWith(p + '/') || url.startsWith(p + '?'))
}

async function bearerHeader() {
  try {
    const { data } = await supabase.auth.getSession()
    const token = data?.session?.access_token
    return token ? { Authorization: `Bearer ${token}` } : {}
  } catch {
    return {}
  }
}

export function installLegacyFetch() {
  if (typeof window === 'undefined') return
  if (window.__legacyFetchInstalled) return
  window.__legacyFetchInstalled = true

  const originalFetch = window.fetch.bind(window)

  window.fetch = async function patched(input, init = {}) {
    const url = typeof input === 'string' ? input : (input && input.url) || ''

    if (!shouldRewrite(url)) {
      return originalFetch(input, init)
    }

    const rewritten = INGEST_URL.replace(/\/$/, '') + '/api/v1/legacy' + url
    const authHeaders = await bearerHeader()

    const nextInit = {
      ...init,
      headers: {
        ...(init.headers || {}),
        ...authHeaders,
      },
    }
    return originalFetch(rewritten, nextInit)
  }
}
