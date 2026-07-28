// Account dropdown for the dashboard header. Replaces the static Settings
// icon. Shows the signed-in user, an Admin link (if admin), CLI Tokens,
// and a working Sign out.

import { useEffect, useRef, useState } from 'react'
import { Settings, LogOut, KeyRound, Shield, User } from 'lucide-react'
import { supabase } from './lib/supabase'
import { useProfile } from './ProfileGate'

export default function AccountMenu() {
  const profile = useProfile()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  const signOut = async () => {
    await supabase.auth.signOut()
    window.location.reload()
  }

  const name = profile?.full_name || profile?.display_name || profile?.email || 'Account'
  const email = profile?.email || ''
  const isAdmin = !!profile?.is_admin

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-[#6B7280] hover:text-abyss-ink cursor-pointer"
        title="Account"
      >
        <Settings size={20} />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-60 bg-white border border-stone-ridge rounded-lg shadow-xl z-50 py-1 font-[Work_Sans]">
          <div className="px-4 py-3 border-b border-stone-ridge">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-abyss-ink text-white text-xs flex items-center justify-center font-bold">
                {(name[0] || 'U').toUpperCase()}
              </div>
              <div className="min-w-0">
                <div className="text-[13px] text-abyss-ink font-medium truncate">{name}</div>
                <div className="text-[11px] text-[#6B7280] truncate">{email}</div>
              </div>
            </div>
            {isAdmin && (
              <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">
                Administrator
              </span>
            )}
          </div>

          <a href="/tokens" className="flex items-center gap-2 px-4 py-2 text-[13px] text-abyss-ink hover:bg-canvas-bone">
            <KeyRound size={14} /> CLI Tokens
          </a>
          <a href="/welcome" className="flex items-center gap-2 px-4 py-2 text-[13px] text-abyss-ink hover:bg-canvas-bone">
            <User size={14} /> Setup &amp; my runs
          </a>
          {isAdmin && (
            <a href="/admin" className="flex items-center gap-2 px-4 py-2 text-[13px] text-abyss-ink hover:bg-canvas-bone">
              <Shield size={14} /> Admin console
            </a>
          )}
          <div className="border-t border-stone-ridge my-1" />
          <button
            onClick={signOut}
            className="w-full flex items-center gap-2 px-4 py-2 text-[13px] text-topography-rust hover:bg-canvas-bone text-left"
          >
            <LogOut size={14} /> Sign out
          </button>
        </div>
      )}
    </div>
  )
}
