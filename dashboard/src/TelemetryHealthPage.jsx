import { useState, useEffect } from "react"
import { Activity, Shield, CheckCircle, AlertTriangle, XCircle, RefreshCw } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

function StatusBadge({ status }) {
  const colors = {
    healthy: "bg-emerald-100 text-emerald-700 border-emerald-200",
    warning: "bg-amber-100 text-amber-700 border-amber-200",
    critical: "bg-red-100 text-red-700 border-red-200",
    inactive: "bg-gray-100 text-gray-500 border-gray-200",
  }
  const icons = {
    healthy: CheckCircle,
    warning: AlertTriangle,
    critical: XCircle,
    inactive: AlertTriangle,
  }
  const cls = colors[status] || colors.inactive
  const Icon = icons[status] || icons.inactive
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-medium border ${cls}`}>
      <Icon size={12} />
      {status}
    </span>
  )
}

export default function TelemetryHealthPage() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchHealth = () => {
    setLoading(true)
    fetch(`${API_BASE}/telemetry/health`)
      .then(r => r.json())
      .then(data => {
        setHealth(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { fetchHealth() }, [])

  if (loading) return <div className="p-6 text-xs text-[#6B7280]">Loading telemetry health...</div>
  
  const isInvalid = !health || health.detail === "Not Found" || health.collected_events === undefined
  if (isInvalid) return <div className="p-6 text-xs text-red-600">Failed to load telemetry health. Please ensure the backend is running and the endpoint is accessible.</div>

  if (health.collected_events === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">Telemetry Health</h2>
            <p className="text-[10px] text-[#6B7280] mt-0.5">Pipeline health status and operational metrics.</p>
          </div>
          <button onClick={fetchHealth} className="flex items-center gap-1 px-3 py-1.5 text-[10px] font-medium text-[#6B7280] border border-stone-ridge rounded-lg hover:bg-gray-50">
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
        <div className="bg-white border border-dashed border-stone-ridge rounded-lg p-12 flex flex-col items-center text-center">
          <Activity size={32} className="text-[#6B7280] mb-4 opacity-20" />
          <h3 className="text-sm font-medium text-abyss-ink">No telemetry has been collected yet</h3>
          <p className="text-xs text-[#6B7280] mt-2 max-w-xs">
            Telemetry is automatically collected when you run designs, use the AI assistant, or record resolutions.
          </p>
          <div className="mt-6 grid grid-cols-2 gap-3 w-full max-w-md text-left">
            <div className="p-3 bg-gray-50 rounded border border-stone-ridge">
              <p className="text-[10px] font-semibold text-abyss-ink">Run a design</p>
              <p className="text-[9px] text-[#6B7280] mt-1">Use the Run Design page to start a new flow.</p>
            </div>
            <div className="p-3 bg-gray-50 rounded border border-stone-ridge">
              <p className="text-[10px] font-semibold text-abyss-ink">Export data</p>
              <p className="text-[9px] text-[#6B7280] mt-1">Visit the Settings page to export local telemetry.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const metrics = [
    { label: "Collected Events", value: (health.collected_events ?? 0).toLocaleString(), status: (health.collected_events ?? 0) > 0 ? "healthy" : "inactive" },
    { label: "Events Today", value: (health.events_today ?? 0).toLocaleString(), status: (health.events_today ?? 0) > 0 ? "healthy" : "warning" },
    { label: "Sanitized Events", value: (health.sanitized_events ?? 0).toLocaleString(), status: "healthy" },
    { label: "Blocked Fields", value: (health.blocked_fields ?? 0).toLocaleString(), status: (health.blocked_fields ?? 0) > 0 ? "warning" : "healthy" },
    { label: "Upload Success Rate", value: `${((health.upload_success_rate ?? 0) * 100).toFixed(0)}%`, status: (health.upload_success_rate ?? 0) >= 0.9 ? "healthy" : (health.upload_success_rate ?? 0) >= 0.5 ? "warning" : "critical" },
    { label: "Upload Failures", value: (health.upload_failures ?? 0).toLocaleString(), status: (health.upload_failures ?? 0) === 0 ? "healthy" : (health.upload_failures ?? 0) < 10 ? "warning" : "critical" },
    { label: "Queued Events", value: (health.queued_events ?? 0).toLocaleString(), status: (health.queued_events ?? 0) === 0 ? "healthy" : (health.queued_events ?? 0) < 100 ? "warning" : "critical" },
    { label: "Avg Upload Latency", value: `${(health.average_upload_latency_ms ?? 0).toFixed(0)}ms`, status: (health.average_upload_latency_ms ?? 0) < 1000 ? "healthy" : "warning" },
    { label: "Total Escalations", value: (health.total_escalations ?? 0).toLocaleString(), status: "healthy" },
    { label: "Open Escalations", value: (health.open_escalations ?? 0).toLocaleString(), status: (health.open_escalations ?? 0) === 0 ? "healthy" : "warning" },
    { label: "Dataset Entries", value: (health.dataset_entries ?? 0).toLocaleString(), status: "healthy" },
    { label: "Resolution Patterns", value: (health.resolution_patterns ?? 0).toLocaleString(), status: "healthy" },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">Telemetry Health</h2>
          <p className="text-[10px] text-[#6B7280] mt-0.5">
            Pipeline health status and operational metrics.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={health.overall_status} />
          <button
            onClick={fetchHealth}
            className="flex items-center gap-1 px-3 py-1.5 text-[10px] font-medium text-[#6B7280] hover:text-abyss-ink border border-stone-ridge rounded-lg hover:bg-gray-50"
          >
            <RefreshCw size={12} />
            Refresh
          </button>
        </div>
      </div>

      {/* Key Timestamps */}
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <p className="text-[10px] font-semibold text-abyss-ink mb-2">Timeline</p>
        <div className="grid grid-cols-3 gap-4 text-[10px]">
          <div>
            <span className="text-[#6B7280]">Last Event</span>
            <p className="font-mono text-abyss-ink mt-0.5">{health.last_event_time ? new Date(health.last_event_time).toLocaleString() : "Never"}</p>
          </div>
          <div>
            <span className="text-[#6B7280]">Last Upload</span>
            <p className="font-mono text-abyss-ink mt-0.5">{health.last_upload_time ? new Date(health.last_upload_time).toLocaleString() : "Never"}</p>
          </div>
          <div>
            <span className="text-[#6B7280]">Last Sanitization</span>
            <p className="font-mono text-abyss-ink mt-0.5">{health.last_sanitization_time ? new Date(health.last_sanitization_time).toLocaleString() : "Never"}</p>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-3">
        {metrics.map((m, i) => (
          <div key={i} className={`bg-white border rounded-lg p-4 ${
            m.status === "healthy" ? "border-emerald-200" :
            m.status === "warning" ? "border-amber-200" :
            m.status === "critical" ? "border-red-200" : "border-stone-ridge"
          }`}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-[#6B7280]">{m.label}</span>
              <StatusBadge status={m.status} />
            </div>
            <p className="text-lg font-semibold text-abyss-ink">{m.value}</p>
          </div>
        ))}
      </div>

      {/* Pipeline Status */}
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h3 className="text-xs font-semibold text-abyss-ink mb-3">Pipeline Flow</h3>
        <div className="flex items-center gap-2 text-[10px]">
          <div className="flex items-center gap-1 px-3 py-2 bg-blue-50 rounded border border-blue-200">
            <Activity size={12} className="text-blue-600" />
            <span>Collect</span>
            <span className="text-blue-600 font-medium">{health.collected_events}</span>
          </div>
          <div className="text-[#6B7280]">→</div>
          <div className="flex items-center gap-1 px-3 py-2 bg-purple-50 rounded border border-purple-200">
            <Shield size={12} className="text-purple-600" />
            <span>Sanitize</span>
            <span className="text-purple-600 font-medium">{health.sanitized_events}</span>
          </div>
          <div className="text-[#6B7280]">→</div>
          <div className={`flex items-center gap-1 px-3 py-2 rounded border ${
            health.upload_failures > 0 ? "bg-red-50 border-red-200" : "bg-emerald-50 border-emerald-200"
          }`}>
            <CheckCircle size={12} className={health.upload_failures > 0 ? "text-red-600" : "text-emerald-600"} />
            <span>Upload</span>
            <span className={health.upload_failures > 0 ? "text-red-600 font-medium" : "text-emerald-600 font-medium"}>
              {health.upload_failures > 0 ? `${health.upload_failures} failed` : `${((health.upload_success_rate || 0) * 100).toFixed(0)}%`}
            </span>
          </div>
        </div>
      </div>

      <p className="text-[9px] text-[#6B7280] text-right">
        Last checked: {new Date(health.checked_at).toLocaleString()}
      </p>
    </div>
  )
}
