import { useState, useEffect } from "react"
import { Settings, Bell, Database, RefreshCw, Globe, Cpu, CheckCircle, XCircle } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

function AIProvidersCard() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/ai/health`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { setHealth(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const statusIcon = health?.status === "READY"
    ? <CheckCircle size={16} className="text-green-600" />
    : <XCircle size={16} className="text-red-500" />

  const statusText = health?.status === "READY" ? "Connected" : "Disconnected"

  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <Cpu size={16} className="text-[#6B7280]" />
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">AI Providers</h3>
      </div>
      {loading ? (
        <p className="text-xs text-[#6B7280]">Loading...</p>
      ) : health ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1">Provider</p>
              <p className="text-xs font-medium text-abyss-ink">{health.provider || "bharatcode"}</p>
            </div>
            <div className="flex items-center gap-1.5">
              {statusIcon}
              <span className={`text-[10px] font-medium ${health.status === "READY" ? "text-green-600" : "text-red-500"}`}>
                {statusText}
              </span>
            </div>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1">Model</p>
            <p className="text-xs text-abyss-ink">{health.model_configured ? "Configured" : "Not configured"}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1">API Key</p>
            <p className="text-xs text-abyss-ink">{health.api_key_present ? "Configured" : "Missing"}</p>
          </div>
          {health.status !== "READY" && (
            <div className="bg-amber-50 border border-amber-200 rounded p-2 mt-2">
              <p className="text-[10px] text-amber-700">
                <span className="font-medium">Status:</span> {health.reason}
              </p>
              <p className="text-[10px] text-amber-700 mt-0.5">
                <span className="font-medium">Fix:</span> {health.fix}
              </p>
            </div>
          )}
        </div>
      ) : (
        <p className="text-xs text-red-500">Failed to check AI provider status</p>
      )}
    </div>
  )
}

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Settings</h1>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Globe size={16} className="text-[#6B7280]" />
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">API Configuration</h3>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1">API Base URL</p>
              <code className="text-[11px] bg-[#F3F2ED] px-3 py-2 rounded block font-mono text-abyss-ink">{API_BASE || "(default)"}</code>
            </div>
            <div>
              <p className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1">Poll Interval</p>
              <code className="text-[11px] bg-[#F3F2ED] px-3 py-2 rounded block font-mono text-abyss-ink">{import.meta.env.VITE_POLL_INTERVAL || "2000"}ms</code>
            </div>
          </div>
        </div>

        <AIProvidersCard />

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Database size={16} className="text-[#6B7280]" />
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Database Configuration</h3>
          </div>
          <p className="text-xs text-[#6B7280] leading-relaxed">
            The dashboard uses an SQLite database at <code className="bg-[#F3F2ED] px-1 rounded text-[10px]">gli_flow.db</code>.
            Set the <code className="bg-[#F3F2ED] px-1 rounded text-[10px]">GLI_FLOW_DB_PATH</code> environment variable to use a custom path.
          </p>
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Bell size={16} className="text-[#6B7280]" />
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Notifications</h3>
          </div>
          <p className="text-xs text-[#6B7280] leading-relaxed">
            Notification bell shows regression count and connection errors. Configure alert thresholds in the governance policies.
          </p>
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <RefreshCw size={16} className="text-[#6B7280]" />
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Environment</h3>
          </div>
          <div className="space-y-2 text-xs text-[#6B7280]">
            <p><span className="font-medium text-abyss-ink">Mode:</span> {import.meta.env.MODE}</p>
            <p><span className="font-medium text-abyss-ink">Dev:</span> {import.meta.env.DEV ? "Yes" : "No"}</p>
            <p><span className="font-medium text-abyss-ink">Prod:</span> {import.meta.env.PROD ? "Yes" : "No"}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
