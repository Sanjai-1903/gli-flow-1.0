// Root entrypoint. Tiny path-based router so we don't pay React/lib cost
// on the /cli/device approval page (which needs to load fast for the
// terminal user waiting on it).
//
//   /               -> HomePage         (signed-in landing + my runs)
//   /tokens         -> CliTokensPage    (manage CLI Bearer tokens)
//   /cli/device     -> DeviceApprovalPage (device-flow approval)
//   /legacy         -> App              (old dashboard, kept for reference)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import AuthGate from './AuthGate.jsx'
import HomePage from './HomePage.jsx'
import CliTokensPage from './CliTokensPage.jsx'
import DeviceApprovalPage from './DeviceApprovalPage.jsx'

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
  if (path === '/legacy') {
    return (
      <AuthGate>
        <App />
      </AuthGate>
    )
  }
  return (
    <AuthGate>
      <HomePage />
    </AuthGate>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>
)
