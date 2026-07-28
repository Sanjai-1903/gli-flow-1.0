// Root entrypoint. Tiny path-based router so we don't pay React/lib cost
// on the /cli/device approval page (which needs to load fast for the
// terminal user waiting on it).
//
//   /               -> App              (legacy full dashboard — Runs, QoR, Failures…)
//   /welcome        -> HomePage         (signed-in landing + install steps)
//   /tokens         -> CliTokensPage    (manage CLI Bearer tokens)
//   /admin          -> AdminPage        (master users only)
//   /cli/device     -> DeviceApprovalPage (device-flow approval)
//
// AuthGate  = must be signed in (Google).
// ProfileGate = must have entered their name (first-login capture).

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import AuthGate from './AuthGate.jsx'
import ProfileGate from './ProfileGate.jsx'
import HomePage from './HomePage.jsx'
import CliTokensPage from './CliTokensPage.jsx'
import DeviceApprovalPage from './DeviceApprovalPage.jsx'
import AdminPage from './AdminPage.jsx'
import { installLegacyFetch } from './lib/legacy-fetch.js'

// Install the global fetch shim BEFORE any component mounts so that
// legacy pages transparently talk to the multi-tenant ingest server
// with the signed-in user's Bearer token.
installLegacyFetch()

function Gated({ children, skipProfile = false }) {
  // Device approval must load fast and doesn't need the profile gate.
  if (skipProfile) return <AuthGate>{children}</AuthGate>
  return (
    <AuthGate>
      <ProfileGate>{children}</ProfileGate>
    </AuthGate>
  )
}

function Root() {
  const path = window.location.pathname

  if (path === '/cli/device') {
    return <Gated skipProfile><DeviceApprovalPage /></Gated>
  }
  if (path === '/tokens' || path === '/settings/tokens') {
    return <Gated><CliTokensPage /></Gated>
  }
  if (path === '/admin') {
    return <Gated><AdminPage /></Gated>
  }
  if (path === '/welcome' || path === '/home') {
    return <Gated><HomePage /></Gated>
  }
  return <Gated><App /></Gated>
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>
)
