// Supabase browser client. Reads:
//   VITE_SUPABASE_URL  = https://<project>.supabase.co
//   VITE_SUPABASE_ANON_KEY = <anon public key>
// Both set in .env.local for local dev, and in Vercel project settings for prod.

import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anon = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!url || !anon) {
  // Loud warning in dev only; don't throw so pages that don't need auth still render.
  if (import.meta.env.DEV) {
    console.warn(
      '[supabase] VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set. ' +
      'Copy .env.example to .env.local and fill them in.'
    )
  }
}

export const supabase = createClient(
  url || 'https://placeholder.supabase.co',
  anon || 'placeholder-anon-key',
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  }
)

// Ingest server base URL — the FastAPI service that owns device-flow endpoints.
export const INGEST_URL =
  import.meta.env.VITE_INGEST_URL || 'http://localhost:8100'

// Helper: build an Authorization header carrying the Supabase JWT for the
// currently signed-in user. Used when the browser calls the FastAPI ingest
// server to approve device-flow logins or manage CLI tokens.
export async function authHeaders() {
  const { data } = await supabase.auth.getSession()
  const token = data?.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}
