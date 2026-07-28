// Admin console — visible only to master users (is_admin).
// Two tabs: Users (everyone + their run counts) and All Runs (every run
// across all users). Non-admins hitting /admin get a 403 from the server
// and see an access-denied message.

import { useEffect, useState } from 'react'
import { INGEST_URL, authHeaders } from './lib/supabase'
import { useProfile } from './ProfileGate'

async function api(path) {
  const headers = { 'Content-Type': 'application/json', ...(await authHeaders()) }
  const resp = await fetch(`${INGEST_URL}${path}`, { headers })
  if (!resp.ok) throw new Error(`${resp.status}: ${await resp.text()}`)
  return resp.json()
}

function fmt(iso) {
  if (!iso) return '—'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

export default function AdminPage() {
  const profile = useProfile()
  const [tab, setTab] = useState('users')
  const [users, setUsers] = useState([])
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  const load = async () => {
    setLoading(true); setErr('')
    try {
      const [u, r] = await Promise.all([api('/api/v1/admin/users'), api('/api/v1/admin/runs?limit=500')])
      setUsers(u.users || [])
      setRuns(r.runs || [])
    } catch (e) {
      setErr(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (profile && !profile.is_admin) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-xl text-white mb-2">Access denied</h1>
          <p className="text-slate-400 text-sm">This page is for administrators only.</p>
          <a href="/" className="text-blue-400 hover:text-blue-300 text-sm mt-4 inline-block">← Back to dashboard</a>
        </div>
      </div>
    )
  }

  const totalRuns = users.reduce((s, u) => s + (u.run_count || 0), 0)
  const totalEvents = users.reduce((s, u) => s + (u.event_count || 0), 0)

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="border-b border-slate-800 bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="font-semibold">GLI Flow — Admin</div>
          <div className="flex items-center gap-4 text-sm">
            <a href="/" className="text-slate-300 hover:text-white">Dashboard</a>
            <button onClick={load} className="text-slate-400 hover:text-white">Refresh</button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Summary */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <div className="text-xs text-slate-400">Users</div>
            <div className="text-2xl font-semibold">{users.length}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <div className="text-xs text-slate-400">Total runs</div>
            <div className="text-2xl font-semibold">{totalRuns}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <div className="text-xs text-slate-400">Total telemetry events</div>
            <div className="text-2xl font-semibold">{totalEvents}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          {['users', 'runs'].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-1.5 rounded text-sm ${tab === t ? 'bg-blue-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-white'}`}
            >
              {t === 'users' ? 'Users' : 'All Runs'}
            </button>
          ))}
        </div>

        {err && (
          <div className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded p-3 mb-4">{err}</div>
        )}
        {loading && <div className="text-slate-500">Loading…</div>}

        {!loading && tab === 'users' && (
          <div className="border border-slate-800 rounded overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-900 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="py-2 px-3 text-left">Name</th>
                  <th className="py-2 px-3 text-left">Email</th>
                  <th className="py-2 px-3 text-left">Role</th>
                  <th className="py-2 px-3 text-left">Runs</th>
                  <th className="py-2 px-3 text-left">Events</th>
                  <th className="py-2 px-3 text-left">Last run</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.user_id} className="border-t border-slate-800 hover:bg-slate-900/50">
                    <td className="py-2 px-3">{u.full_name || u.display_name || '—'}</td>
                    <td className="py-2 px-3 text-slate-300">{u.email}</td>
                    <td className="py-2 px-3">
                      {u.is_admin ? <span className="text-amber-400">admin</span> : <span className="text-slate-500">user</span>}
                    </td>
                    <td className="py-2 px-3">{u.run_count}</td>
                    <td className="py-2 px-3">{u.event_count}</td>
                    <td className="py-2 px-3 text-slate-500 text-xs">{fmt(u.last_run_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && tab === 'runs' && (
          <div className="border border-slate-800 rounded overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-900 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="py-2 px-3 text-left">Run ID</th>
                  <th className="py-2 px-3 text-left">User</th>
                  <th className="py-2 px-3 text-left">Design</th>
                  <th className="py-2 px-3 text-left">Status</th>
                  <th className="py-2 px-3 text-left">Stages</th>
                  <th className="py-2 px-3 text-left">When</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.run_id} className="border-t border-slate-800 hover:bg-slate-900/50">
                    <td className="py-2 px-3 font-mono text-xs text-slate-300">{r.run_id}</td>
                    <td className="py-2 px-3">
                      <div>{r.user_name || '—'}</div>
                      <div className="text-xs text-slate-500">{r.user_email}</div>
                    </td>
                    <td className="py-2 px-3 text-slate-200">{r.design_name}</td>
                    <td className={`py-2 px-3 ${r.completed ? 'text-green-400' : 'text-yellow-400'}`}>
                      {r.completed ? '✓ completed' : '… running'}
                    </td>
                    <td className="py-2 px-3">{r.stages_completed}</td>
                    <td className="py-2 px-3 text-slate-500 text-xs">{fmt(r.last_seen)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
