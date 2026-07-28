// ProfileGate — sits inside AuthGate. After a user is authenticated, it
// checks their profile. If they haven't entered their name yet
// (profile_complete === false), it shows a blocking modal asking for it
// before letting them into the app.
//
// Also exposes the loaded profile (incl. is_admin) via context so other
// components (e.g. the admin nav item) can read it.

import { createContext, useContext, useEffect, useState } from 'react'
import { INGEST_URL, authHeaders } from './lib/supabase'

const ProfileContext = createContext(null)
export const useProfile = () => useContext(ProfileContext)

async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(await authHeaders()), ...(opts.headers || {}) }
  const resp = await fetch(`${INGEST_URL}${path}`, { ...opts, headers })
  if (!resp.ok) throw new Error(`${resp.status}: ${await resp.text()}`)
  return resp.json()
}

function NameModal({ onSaved, email }) {
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const submit = async () => {
    if (!name.trim()) { setErr('Please enter your name.'); return }
    setBusy(true); setErr('')
    try {
      await api('/api/v1/profile', { method: 'POST', body: JSON.stringify({ full_name: name.trim() }) })
      onSaved(name.trim())
    } catch (e) {
      setErr(String(e)); setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="max-w-md w-full mx-4 bg-slate-900 border border-slate-800 rounded-lg p-8">
        <h1 className="text-xl font-semibold text-white mb-1">Welcome to GLI Flow</h1>
        <p className="text-sm text-slate-400 mb-6">
          Signed in as {email}. What should we call you?
        </p>
        <label className="block text-sm text-slate-400 mb-2">Your full name</label>
        <input
          autoFocus
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder="e.g. Sanjai Murugan"
          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-slate-100 mb-4"
        />
        {err && <div className="text-sm text-red-400 mb-3">{err}</div>}
        <button
          onClick={submit}
          disabled={busy}
          className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded font-medium"
        >
          {busy ? 'Saving…' : 'Continue'}
        </button>
      </div>
    </div>
  )
}

export default function ProfileGate({ children }) {
  const [profile, setProfile] = useState(undefined) // undefined = loading

  const load = async () => {
    try {
      const p = await api('/api/v1/profile')
      setProfile(p)
    } catch (e) {
      // If the profile endpoint is unreachable, don't hard-block the app —
      // let them in and treat profile as unknown/complete.
      setProfile({ profile_complete: true, is_admin: false, _error: String(e) })
    }
  }

  useEffect(() => { load() }, [])

  if (profile === undefined) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Loading your profile…
      </div>
    )
  }

  if (!profile.profile_complete) {
    return (
      <NameModal
        email={profile.email || ''}
        onSaved={(name) => setProfile({ ...profile, full_name: name, profile_complete: true })}
      />
    )
  }

  return (
    <ProfileContext.Provider value={profile}>
      {children}
    </ProfileContext.Provider>
  )
}
