// Settings → CLI Tokens
// List existing tokens, create new ones, revoke. Token secret is shown ONCE
// on creation — never again.

import { useEffect, useState } from 'react'
import { supabase, INGEST_URL, authHeaders } from './lib/supabase'
import { useSession } from './AuthGate'

async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(await authHeaders()), ...(opts.headers || {}) }
  const resp = await fetch(`${INGEST_URL}${path}`, { ...opts, headers })
  if (!resp.ok) {
    const body = await resp.text()
    throw new Error(`${resp.status}: ${body || resp.statusText}`)
  }
  return resp.json()
}

function TokenCard({ tk, onRevoke }) {
  const created = new Date(tk.created_at).toLocaleString()
  const lastUsed = tk.last_used_at ? new Date(tk.last_used_at).toLocaleString() : 'Never'
  const revoked = tk.revoked_at

  return (
    <div className={`border rounded-md p-4 ${revoked ? 'border-slate-800 bg-slate-950/50 opacity-60' : 'border-slate-800 bg-slate-900'}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium text-slate-100">{tk.name || 'CLI token'}</div>
          <div className="text-xs text-slate-400 font-mono mt-1">
            {tk.token_prefix}…
          </div>
        </div>
        {!revoked && (
          <button
            onClick={() => onRevoke(tk.id)}
            className="text-sm text-red-400 hover:text-red-300 border border-red-900/50 hover:border-red-800 rounded px-3 py-1"
          >
            Revoke
          </button>
        )}
        {revoked && <span className="text-xs text-slate-500">Revoked</span>}
      </div>
      <div className="grid grid-cols-2 gap-4 text-xs text-slate-500 mt-3">
        <div>Created: {created}</div>
        <div>Last used: {lastUsed}</div>
      </div>
    </div>
  )
}

function CreateTokenModal({ onCreated, onClose }) {
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [freshToken, setFreshToken] = useState(null)

  const submit = async () => {
    setBusy(true)
    setErr('')
    try {
      const result = await api('/api/v1/tokens/create', {
        method: 'POST',
        body: JSON.stringify({ name: name || 'CLI token' }),
      })
      setFreshToken(result)
      onCreated()
    } catch (e) {
      setErr(String(e))
    } finally {
      setBusy(false)
    }
  }

  const copy = () => {
    navigator.clipboard.writeText(freshToken.access_token)
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 max-w-lg w-full mx-4" onClick={(e) => e.stopPropagation()}>
        {!freshToken ? (
          <>
            <h2 className="text-lg font-semibold text-white mb-4">Create CLI token</h2>
            <label className="block text-sm text-slate-400 mb-2">Name (optional)</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My laptop"
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-slate-100 mb-4"
            />
            {err && <div className="text-sm text-red-400 mb-3">{err}</div>}
            <div className="flex gap-2 justify-end">
              <button onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-slate-200">Cancel</button>
              <button onClick={submit} disabled={busy} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50">
                {busy ? 'Creating…' : 'Create'}
              </button>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold text-white mb-2">Your new token</h2>
            <p className="text-sm text-yellow-400 mb-4">
              Copy this token now — it will not be shown again.
            </p>
            <div className="bg-slate-950 border border-slate-800 rounded p-3 font-mono text-sm text-slate-100 break-all mb-3">
              {freshToken.access_token}
            </div>
            <div className="text-xs text-slate-500 mb-4">
              On your machine, run: <code className="text-slate-300">gli-flow login --token &lt;paste&gt;</code>
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={copy} className="px-4 py-2 bg-slate-800 text-slate-100 rounded hover:bg-slate-700">Copy</button>
              <button onClick={onClose} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500">Done</button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default function CliTokensPage() {
  const session = useSession()
  const [tokens, setTokens] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  const load = async () => {
    setLoading(true)
    setErr('')
    try {
      const data = await api('/api/v1/tokens/list')
      setTokens(data.tokens || [])
    } catch (e) {
      setErr(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (session) load()
  }, [session])

  const revoke = async (id) => {
    if (!confirm('Revoke this token? Any CLI signed in with it will stop working.')) return
    try {
      await api('/api/v1/tokens/revoke', {
        method: 'POST',
        body: JSON.stringify({ token_id: id }),
      })
      await load()
    } catch (e) {
      alert('Revoke failed: ' + e)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold">CLI Tokens</h1>
            <p className="text-sm text-slate-400 mt-1">
              Bearer tokens that let a machine's <code>gli-flow</code> CLI upload
              telemetry to your account.
            </p>
          </div>
          <div className="flex gap-2">
            <a href="/" className="text-sm text-slate-400 hover:text-slate-200 px-3 py-2">← Back to dashboard</a>
            <button
              onClick={() => setShowCreate(true)}
              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded"
            >
              + New token
            </button>
          </div>
        </div>

        {loading && <div className="text-slate-500">Loading…</div>}
        {err && (
          <div className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded p-3 mb-4">
            {err}
          </div>
        )}

        {!loading && !err && tokens.length === 0 && (
          <div className="text-center py-16 border border-dashed border-slate-800 rounded">
            <p className="text-slate-400 mb-4">No tokens yet.</p>
            <button onClick={() => setShowCreate(true)} className="text-blue-400 hover:text-blue-300">
              Create your first token
            </button>
          </div>
        )}

        <div className="space-y-3">
          {tokens.map((tk) => (
            <TokenCard key={tk.id} tk={tk} onRevoke={revoke} />
          ))}
        </div>

        {showCreate && (
          <CreateTokenModal
            onCreated={load}
            onClose={() => setShowCreate(false)}
          />
        )}
      </div>
    </div>
  )
}
