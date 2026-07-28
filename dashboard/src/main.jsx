// Root entrypoint. Tiny path-based router so we don't pay React/lib cost
// on the /cli/device approval page (which needs to load fast for the
// terminal user waiting on it).
//
//   /               -> App              (legacy full dashboard — Runs, QoR, Failures…)
//   /welcome        -> HomePage         (signed-in landing + install steps)
//   /tokens         -> CliTokensPage    (manage CLI Bearer tokens)
//   /cli/device     -> DeviceApprovalPage (device-flow approval)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import AuthGate from './AuthGate.jsx'
import HomePage from './HomePage.jsx'
import CliTokensPage from './CliTokensPage.jsx'
import DeviceApprovalPage from './DeviceApprovalPage.jsx'
import { installLegacyFetch } from './lib/legacy-fetch.js'

// Install the global fetch shim BEFORE any component mounts so that
// legacy pages transparently talk to the multi-tenant ingest server
// with the signed-in user's Bearer token.
installLegacyFetch()

function Root() {
  const path = window.location.pathname

  if (path === '/cli/device') {
    return (
      <AuthGate>
        <DeviceApprovalPage />
      </AuthGate>
    )
  }
  if (path === '/tokens' || path === '/settings/tokens') {
    return (
      <AuthGate>
        <CliTokensPage />
      </AuthGate>
    )
  }
  if (path === '/welcome' || path === '/home') {
    return (
      <AuthGate>
        <HomePage />
      </AuthGate>
    )
  }
  return (
    <AuthGate>
      <App />
    </AuthGate>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>
)
