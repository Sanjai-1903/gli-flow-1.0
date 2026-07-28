// Root entrypoint. Tiny path-based router before anything else so we don't
// pay React/lib cost on the /cli/device approval page (which needs to load
// fast for the terminal user waiting on it).

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import AuthGate from './AuthGate.jsx'
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
