// Onboarding card that lives at the top of the main dashboard.
//
// Shows students exactly what to do:
//   1. Install the CLI
//   2. Point it at the ingest server + sign in
//   3. Or paste a token generated from here
// Also has a "+ Generate CLI Token" button that pops a modal, generates
// a token via the ingest server, and shows it once for copy-paste.
//
// Dismissible via localStorage (per-browser). A small "Show setup" link
// re-opens it if it's hidden.

import { useEffect, useState } from 'react'
import { X, Copy, Check, Terminal, KeyRound } from 'lucide-react'
import { supabase, INGEST_URL, authHeaders } from './lib/supabase'
import { useSession } from './AuthGate'

const DISMISS_KEY = 'gli_onboarding_dismissed_v1'

async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(await authHeaders()), ...(opts.headers || {}) }
  const resp = await fetch(`${INGEST_URL}${path}`, { ...opts, headers })
  if (!resp.ok) throw new Error(`${resp.status}: ${await resp.text()}`)
  return resp.json()
}

function CopyBox({ label, text }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {}
  }
  return (
    <div>
      {label && <div className="text-[11px] font-[Work_Sans] text-[#6B7280] mb-1">{label}</div>}
      <div className="relative group">
        <pre className="bg-abyss-ink text-[11px] leading-relaxed text-white rounded-md px-3 py-2 overflow-x-auto font-mono">
{text}
        </pre>
        <button
          onClick={copy}
          className="absolute top-1.5 right-1.5 text-[10px] bg-white/10 hover:bg-white/20 text-white rounded px-2 py-0.5 flex items-center gap-1"
        >
          {copied ? <Check size={11} /> : <Copy size={11} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
    </div>
  )
}

function TokenModal({ onClose }) {
  const [name, setName] = useState('My laptop')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [tk, setTk] = useState(null)

  const submit = async () => {
    setBusy(true); setErr('')
    try {
      const r = await api('/api/v1/tokens/create', {
        method: 'POST',
        body: JSON.stringify({ name }),
      })
      setTk(r)
    } catch (e) {
      setErr(String(e))
    } finally {
      setBusy(false)
    }
  }

  const copy = () => {
    if (tk) navigator.clipboard.writeText(tk.access_token)
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center" onClick={onClose}>
      <div
        className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6 font-[Work_Sans]"
        onClick={(e) => e.stopPropagation()}
      >
        {!tk ? (
          <>
            <h3 className="text-lg font-[Eczar] text-abyss-ink mb-2">Generate a CLI token</h3>
            <p className="text-xs text-[#6B7280] mb-4">
              Give it a name so you can identify it later (e.g. "My laptop", "Lab workstation").
            </p>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-stone-ridge rounded px-3 py-2 text-sm mb-4"
              placeholder="Token name"
            />
            {err && <div className="text-xs text-topography-rust mb-3">{err}</div>}
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="px-4 py-2 text-[#6B7280] text-sm">Cancel</button>
              <button
                onClick={submit}
                disabled={busy}
                className="px-4 py-2 bg-meridian-gold text-abyss-ink text-sm rounded font-medium disabled:opacity-50"
              >
                {busy ? 'Creating…' : 'Create token'}
              </button>
            </div>
          </>
        ) : (
          <>
            <h3 className="text-lg font-[Eczar] text-abyss-ink mb-1">Your new token</h3>
            <p className="text-xs text-topography-rust mb-3">
              Copy it now — it won't be shown again.
            </p>
            <div className="bg-abyss-ink text-white rounded px-3 py-2 font-mono text-xs break-all mb-3">
              {tk.access_token}
            </div>
            <div className="text-xs text-[#6B7280] mb-4">
              Run on your machine: <code className="text-abyss-ink">gli-flow login --token &lt;paste&gt;</code>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={copy} className="px-4 py-2 text-sm border border-stone-ridge rounded">Copy</button>
              <button onClick={onClose} className="px-4 py-2 bg-meridian-gold text-abyss-ink text-sm rounded font-medium">Done</button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default function OnboardingCard() {
  const session = useSession()
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(DISMISS_KEY) === '1' } catch { return false }
  })
  const [showModal, setShowModal] = useState(false)

  const dismiss = () => {
    try { localStorage.setItem(DISMISS_KEY, '1') } catch {}
    setDismissed(true)
  }
  const restore = () => {
    try { localStorage.removeItem(DISMISS_KEY) } catch {}
    setDismissed(false)
  }

  if (dismissed) {
    return (
      <button
        onClick={restore}
        className="text-[11px] text-[#6B7280] hover:text-abyss-ink underline"
      >
        Show setup instructions
      </button>
    )
  }

  const email = session?.user?.email || ''
  const webOrigin = typeof window !== 'undefined' ? window.location.origin : ''

  const installSnippet = `git clone https://github.com/Sanjai-1903/gli-flow-1.0
cd gli-flow-1.0
python3 -m venv .venv && source .venv/bin/activate
pip install -e .`

  const loginSnippet = `export GLI_INGEST_URL='${INGEST_URL}'
export GLI_WEB_URL='${webOrigin}'
gli-flow login
gli-flow run examples/counter --mock`

  return (
    <>
      <div className="bg-white border border-stone-ridge rounded-lg shadow-sm p-5 relative font-[Work_Sans]">
        <button
          onClick={dismiss}
          className="absolute top-3 right-3 text-[#6B7280] hover:text-abyss-ink"
          title="Hide"
        >
          <X size={16} />
        </button>

        <div className="flex items-center gap-2 mb-1">
          <Terminal size={16} className="text-abyss-ink" />
          <h2 className="text-[18px] font-[Eczar] text-abyss-ink leading-tight">
            Get started with the gli-flow CLI
          </h2>
        </div>
        <p className="text-[12px] text-[#6B7280] mb-4">
          Signed in as {email || 'your account'}. Install the CLI, log in, and any run you do gets synced here automatically.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <div className="text-[12px] font-semibold text-abyss-ink mb-2">1. Install</div>
            <CopyBox text={installSnippet} />
          </div>
          <div>
            <div className="text-[12px] font-semibold text-abyss-ink mb-2">2. Login and run</div>
            <CopyBox text={loginSnippet} />
          </div>
        </div>

        <div className="mt-5 pt-4 border-t border-stone-ridge/60 flex items-center justify-between gap-3 flex-wrap">
          <div className="text-[12px] text-[#6B7280]">
            Prefer to paste a token? Generate one here — the CLI accepts it via{' '}
            <code className="text-abyss-ink">gli-flow login --token gfp_…</code>
          </div>
          <div className="flex items-center gap-2">
            <a
              href="/tokens"
              className="text-[11px] px-3 py-1.5 border border-stone-ridge rounded text-abyss-ink hover:bg-canvas-bone"
            >
              Manage tokens
            </a>
            <button
              onClick={() => setShowModal(true)}
              className="text-[11px] px-3 py-1.5 bg-meridian-gold text-abyss-ink rounded font-medium hover:brightness-95 flex items-center gap-1.5"
            >
              <KeyRound size={12} />
              Generate CLI token
            </button>
          </div>
        </div>
      </div>

      {showModal && <TokenModal onClose={() => setShowModal(false)} />}
    </>
  )
}
