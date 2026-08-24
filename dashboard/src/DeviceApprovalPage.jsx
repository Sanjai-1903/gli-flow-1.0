// Device flow approval page — landed at from `gli-flow login`.
// URL: /cli/device?user_code=XXXX-XXXX
// User confirms the code matches what their CLI printed, then approves.

import { useEffect, useState } from 'react'
import { supabase, INGEST_URL, authHeaders } from './lib/supabase'
import { useSession } from './AuthGate'

function fmtCode(code) {
  if (!code) return ''
  const clean = code.replace(/[-\s]/g, '').toUpperCase()
  if (clean.length === 8) return clean.slice(0, 4) + '-' + clean.slice(4)
  return clean
}

export default function DeviceApprovalPage() {
  const session = useSession()
  const [userCode, setUserCode] = useState('')
  const [status, setStatus] = useState('idle') // idle | approving | approved | denied | error
  const [errMsg, setErrMsg] = useState('')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const uc = params.get('user_code') || ''
    setUserCode(fmtCode(uc))
  }, [])

  const approve = async () => {
    setStatus('approving')
    setErrMsg('')
    try {
      const resp = await fetch(`${INGEST_URL}/api/v1/cli/device/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(await authHeaders()),
        },
        body: JSON.stringify({ user_code: userCode.replace(/[-\s]/g, '') }),
      })
      if (!resp.ok) {
        const body = await resp.text()
        throw new Error(`${resp.status}: ${body}`)
      }
      setStatus('approved')
    } catch (e) {
      setStatus('error')
      setErrMsg(String(e))
    }
  }

  const deny = async () => {
    setStatus('approving')
    try {
      await fetch(`${INGEST_URL}/api/v1/cli/device/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(await authHeaders()),
        },
        body: JSON.stringify({
          user_code: userCode.replace(/[-\s]/g, ''),
          deny: true,
        }),
      })
    } catch {}
    setStatus('denied')
  }

  if (!session) return null // AuthGate handles the sign-in

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="max-w-lg w-full mx-4 bg-slate-900 border border-slate-800 rounded-lg p-8">
        <h1 className="text-xl font-semibold text-white mb-1">Approve CLI sign-in</h1>
        <p className="text-sm text-slate-400 mb-6">
          Signed in as <span className="text-slate-200">{session.user.email}</span>
          {' '}
          <button
            onClick={async () => {
              await supabase.auth.signOut()
              await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                  redirectTo: window.location.href,
                  queryParams: { prompt: 'select_account' },
                },
              })
            }}
            className="text-blue-400 hover:text-blue-300 underline ml-1"
          >
            Not you? Switch account
          </button>
        </p>

        <p className="text-sm text-slate-300 mb-2">
          Confirm that the code below matches the one shown in your terminal:
        </p>

        <input
          type="text"
          value={userCode}
          onChange={(e) => setUserCode(fmtCode(e.target.value))}
          className="w-full text-center text-3xl font-mono tracking-widest bg-slate-950 border border-slate-700 rounded-md py-4 mb-6 text-slate-100 focus:outline-none focus:border-blue-500"
          placeholder="XXXX-XXXX"
          maxLength={9}
        />

        {status === 'idle' && (
          <div className="flex gap-3">
            <button
              onClick={deny}
              className="flex-1 py-3 border border-slate-700 hover:border-slate-600 text-slate-300 rounded"
            >
              Cancel
            </button>
            <button
              onClick={approve}
              disabled={userCode.replace(/[-\s]/g, '').length !== 8}
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded"
            >
              Approve
            </button>
          </div>
        )}

        {status === 'approving' && (
          <div className="text-center text-slate-400">Approving…</div>
        )}

        {status === 'approved' && (
          <div className="text-center text-green-400 py-4">
            ✓ Approved. You can close this tab — your CLI should finish in a
            few seconds.
          </div>
        )}

        {status === 'denied' && (
          <div className="text-center text-yellow-400 py-4">
            Cancelled. Your CLI login has been denied.
          </div>
        )}

        {status === 'error' && (
          <div className="text-center py-4">
            <div className="text-red-400 mb-2">Something went wrong.</div>
            <div className="text-xs text-slate-500 mb-4">{errMsg}</div>
            <button
              onClick={() => setStatus('idle')}
              className="text-blue-400 hover:text-blue-300"
            >
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
