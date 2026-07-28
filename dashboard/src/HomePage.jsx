// Signed-in landing page. Replaces the legacy App.jsx as the default view.
// Shows:
//   - Who you're signed in as + sign out
//   - CLI install / login snippets (copyable)
//   - Your most recent runs (from /api/v1/runs on the ingest server)
//   - Links to CLI Tokens

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

function CopyBlock({ children }) {
  const [copied, setCopied] = useState(false)
  const text = typeof children === 'string' ? children : String(children)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {}
  }
  return (
    <div className="relative group">
      <pre className="bg-slate-950 border border-slate-800 rounded p-3 text-xs text-slate-100 overflow-x-auto">
        <code>{children}</code>
      </pre>
      <button
        onClick={copy}
        className="absolute top-2 right-2 text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 opacity-0 group-hover:opacity-100 transition"
      >
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  )
}

function fmtDate(iso) {
  if (!iso) return '—'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}
function fmtNum(v, digits = 2) {
  if (v === null || v === undefined || v === '') return '—'
  const n = Number(v)
  if (Number.isNaN(n)) return String(v)
  return n.toFixed(digits)
}

function RunRow({ r }) {
  const statusColor = r.run_completed ? 'text-green-400' : 'text-yellow-400'
  return (
    <tr className="border-t border-slate-800 hover:bg-slate-900/50">
      <td className="py-2 px-3 font-mono text-xs text-slate-300">{r.run_id}</td>
      <td className="py-2 px-3 text-slate-200">{r.design_name}</td>
      <td className={`py-2 px-3 ${statusColor}`}>
        {r.run_completed ? '✓ completed' : '… in progress'}
      </td>
      <td className="py-2 px-3 text-slate-300">{r.stages_completed}</td>
      <td className="py-2 px-3 text-slate-300">{fmtNum(r.qor_score, 3)}</td>
      <td className="py-2 px-3 text-slate-500 text-xs">{fmtDate(r.last_seen)}</td>
    </tr>
  )
}

export default function HomePage() {
  const session = useSession()
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  const load = async () => {
    setLoading(true); setErr('')
    try {
      const data = await api('/api/v1/runs?limit=50')
      setRuns(data.runs || [])
    } catch (e) {
      setErr(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (session) load() }, [session])

  const signOut = async () => {
    await supabase.auth.signOut()
    window.location.reload()
  }

  const email = session?.user?.email || '(unknown)'

  // These get baked in at build; students see the production URLs.
  const ingestUrl = INGEST_URL
  const webUrl = typeof window !== 'undefined' ? window.location.origin : ''

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top bar */}
      <div className="border-b border-slate-800 bg-slate-900/50">
        <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="font-semibold">GLI Flow</div>
          <div className="flex items-center gap-4 text-sm">
            <a href="/tokens" className="text-slate-300 hover:text-white">CLI Tokens</a>
            <span className="text-slate-500">{email}</span>
            <button onClick={signOut} className="text-slate-400 hover:text-red-400">
              Sign out
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-10">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-semibold mb-1">Welcome, {email.split('@')[0]}.</h1>
          <p className="text-slate-400 text-sm">
            Runs from your <code className="text-slate-300">gli-flow</code> CLI show up here, scoped to your account.
          </p>
        </div>

        {/* Getting started */}
        <div>
          <h2 className="text-lg font-semibold mb-3">Get started on your machine</h2>
          <ol className="text-sm text-slate-300 space-y-4 list-decimal pl-5">
            <li>
              <div className="mb-2">Clone the repo and install:</div>
              <CopyBlock>{`git clone https://github.com/Sanjai-1903/gli-flow-1.0
cd gli-flow-1.0
python3 -m venv .venv && source .venv/bin/activate
pip install -e .`}</CopyBlock>
            </li>
            <li>
              <div className="mb-2">Point the CLI at this server and sign in:</div>
              <CopyBlock>{`export GLI_INGEST_URL='${ingestUrl}'
export GLI_WEB_URL='${webUrl}'
gli-flow login`}</CopyBlock>
              <div className="text-xs text-slate-500 mt-1">
                A browser opens for approval. Or use <code>gli-flow login --token gfp_…</code>{' '}
                with a token generated from{' '}
                <a href="/tokens" className="text-blue-400 hover:text-blue-300">CLI Tokens</a>.
              </div>
            </li>
            <li>
              <div className="mb-2">Run a design — data auto-syncs to this account:</div>
              <CopyBlock>{`gli-flow run examples/counter --mock`}</CopyBlock>
            </li>
          </ol>
        </div>

        {/* Runs */}
        <div>
          <div className="flex items-baseline justify-between mb-3">
            <h2 className="text-lg font-semibold">Your recent runs</h2>
            <button
              onClick={load}
              disabled={loading}
              className="text-sm text-slate-400 hover:text-slate-200 disabled:opacity-50"
            >
              {loading ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>

          {err && (
            <div className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded p-3 mb-4">
              {err}
            </div>
          )}

          {!loading && !err && runs.length === 0 && (
            <div className="text-center py-16 border border-dashed border-slate-800 rounded">
              <p className="text-slate-400 mb-2">No runs yet.</p>
              <p className="text-slate-500 text-sm">
                Run <code className="text-slate-300">gli-flow run examples/counter --mock</code> on your machine.
              </p>
            </div>
          )}

          {runs.length > 0 && (
            <div className="border border-slate-800 rounded overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-900 text-slate-400 text-xs uppercase">
                  <tr>
                    <th className="py-2 px-3 text-left">Run ID</th>
                    <th className="py-2 px-3 text-left">Design</th>
                    <th className="py-2 px-3 text-left">Status</th>
                    <th className="py-2 px-3 text-left">Stages</th>
                    <th className="py-2 px-3 text-left">QoR</th>
                    <th className="py-2 px-3 text-left">Last event</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((r) => <RunRow key={r.run_id} r={r} />)}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="text-xs text-slate-600 pt-6 border-t border-slate-900">
          Ingest: <code>{ingestUrl}</code>
        </div>
      </div>
    </div>
  )
}
