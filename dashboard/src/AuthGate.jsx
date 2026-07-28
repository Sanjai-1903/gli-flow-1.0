// AuthGate — renders a Google sign-in screen until the user is authenticated,
// then renders children. Used to wrap the main App and any auth-required page.

import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'

function SignInScreen() {
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')

  const signIn = async () => {
    setLoading(true)
    setErr('')
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + window.location.pathname,
      },
    })
    if (error) {
      setErr(error.message)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="max-w-md w-full mx-4 bg-slate-900 border border-slate-800 rounded-lg p-8 shadow-xl">
        <h1 className="text-2xl font-semibold text-white mb-2">GLI Flow</h1>
        <p className="text-slate-400 text-sm mb-6">
          Sign in to view your runs, manage CLI tokens, and approve device
          logins.
        </p>

        <button
          onClick={signIn}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 bg-white text-slate-900 font-medium py-2.5 px-4 rounded-md hover:bg-slate-100 disabled:opacity-50 transition"
        >
          <svg width="18" height="18" viewBox="0 0 48 48">
            <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.5-5.9 8-11.3 8-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/>
            <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>
            <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2c-2 1.5-4.5 2.4-7.2 2.4-5.4 0-9.9-3.4-11.3-8L6 32.6C9.4 39.6 16.1 44 24 44z"/>
            <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.1-2.1 3.9-3.8 5.3l6.2 5.2C41.4 35.4 44 30.1 44 24c0-1.3-.1-2.4-.4-3.5z"/>
          </svg>
          {loading ? 'Redirecting…' : 'Sign in with Google'}
        </button>

        {err && (
          <div className="mt-4 text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2">
            {err}
          </div>
        )}

        <p className="text-xs text-slate-500 mt-6 text-center">
          By signing in you agree to have your telemetry associated with your
          account. You can revoke access at any time from Settings → CLI Tokens.
        </p>
      </div>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="text-slate-400">Loading…</div>
    </div>
  )
}

export default function AuthGate({ children }) {
  const [session, setSession] = useState(undefined) // undefined = loading

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session))
    const { data: sub } = supabase.auth.onAuthStateChange((_evt, s) =>
      setSession(s)
    )
    return () => sub.subscription.unsubscribe()
  }, [])

  if (session === undefined) return <LoadingScreen />
  if (!session) return <SignInScreen />
  return children
}

export function useSession() {
  const [session, setSession] = useState(null)
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session))
    const { data: sub } = supabase.auth.onAuthStateChange((_evt, s) =>
      setSession(s)
    )
    return () => sub.subscription.unsubscribe()
  }, [])
  return session
}
