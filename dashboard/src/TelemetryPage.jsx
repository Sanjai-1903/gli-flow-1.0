import { useState, useEffect } from "react"
import { Eye, Shield, CheckCircle, AlertTriangle, ChevronDown, ChevronRight, Download, Terminal, Info, FileDown } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

function FieldRow({ field, classification }) {
  const colors = {
    SAFE: "bg-green-100 text-green-700 border-green-200",
    REDACT: "bg-yellow-100 text-yellow-700 border-yellow-200",
    HASH: "bg-blue-100 text-blue-700 border-blue-200",
    BLOCK: "bg-red-100 text-red-700 border-red-200",
    DERIVE: "bg-purple-100 text-purple-700 border-purple-200",
  }
  const cls = colors[classification] || "bg-gray-100 text-gray-600 border-gray-200"
  return (
    <div className="flex items-center gap-2 text-[10px] py-1">
      <span className={`px-1.5 py-0.5 rounded font-medium border ${cls}`}>{classification}</span>
      <code className="text-abyss-ink font-mono">{field}</code>
    </div>
  )
}

function PayloadViewer({ label, payload }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="border border-stone-ridge rounded-lg">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 text-xs font-medium text-abyss-ink hover:bg-gray-50"
      >
        <span>{label}</span>
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>
      {expanded && (
        <pre className="px-4 pb-3 text-[10px] font-mono text-[#6B7280] overflow-x-auto max-h-96 overflow-y-auto">
          {JSON.stringify(payload, null, 2)}
        </pre>
      )}
    </div>
  )
}

function eventToPayload(event) {
  return {
    event: event.event,
    failure_type: event.failure_type || "",
    tool: event.tool || "",
    details: event.details ? JSON.parse(event.details) : {},
    created_at: event.created_at,
  }
}

export default function TelemetryPage() {
  const [activeTab, setActiveTab] = useState("events")
  const [events, setEvents] = useState([])
  const [unknowns, setUnknowns] = useState([])
  const [escalations, setEscalations] = useState([])
  const [patterns, setPatterns] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchAll = () => {
    setLoading(true)
    Promise.all([
      fetch(`${API_BASE}/telemetry/events`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/community/unknown-dataset`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/community/escalations`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/resolutions/summary`).then(r => r.ok ? r.json() : null),
    ])
      .then(([evts, unk, esc, pat]) => {
        setEvents(Array.isArray(evts) ? evts : evts.events || [])
        setUnknowns(Array.isArray(unk) ? unk : unk.dataset || [])
        setEscalations(Array.isArray(esc) ? esc : esc.escalations || [])
        setPatterns(pat)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { fetchAll() }, [])

  const tabs = [
    { id: "events", label: "Telemetry Events" },
    { id: "unknowns", label: "Unknown Failures" },
    { id: "escalations", label: "Escalations" },
    { id: "patterns", label: "Resolution Patterns" },
    { id: "preview", label: "Upload Preview" },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">Telemetry Transparency Center</h2>
          <p className="text-[10px] text-[#6B7280] mt-0.5">
            Full visibility into what data is collected, stored, and uploaded.
            No customer IP ever leaves your machine without explicit consent.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const a = document.createElement("a")
              a.href = `${API_BASE}/telemetry/export`
              a.download = "telemetry_export.json"
              a.click()
            }}
            className="flex items-center gap-1 px-3 py-1.5 text-[10px] font-medium text-abyss-ink border border-stone-ridge rounded-lg hover:bg-gray-50"
          >
            <FileDown size={12} />
            Export JSON
          </button>
          <button
            onClick={() => {
              const a = document.createElement("a")
              a.href = `${API_BASE}/telemetry/export?format=csv`
              a.download = "telemetry_export.csv"
              a.click()
            }}
            className="flex items-center gap-1 px-3 py-1.5 text-[10px] font-medium text-abyss-ink border border-stone-ridge rounded-lg hover:bg-gray-50"
          >
            <FileDown size={12} />
            Export CSV
          </button>
          <Shield size={16} className="text-emerald-600" />
          <span className="text-[10px] text-emerald-700 font-medium">Privacy Protected</span>
        </div>
      </div>

      {/* Classification Legend */}
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <p className="text-[10px] font-semibold text-abyss-ink mb-2">Field Classification</p>
        <div className="flex flex-wrap gap-3">
          <FieldRow field="SAFE" classification="SAFE" />
          <FieldRow field="REDACT" classification="REDACT" />
          <FieldRow field="HASH" classification="HASH" />
          <FieldRow field="BLOCK" classification="BLOCK" />
          <FieldRow field="DERIVE" classification="DERIVE" />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-stone-ridge">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-[10px] font-medium transition-colors ${
              activeTab === tab.id
                ? "text-abyss-ink border-b-2 border-meridian-gold"
                : "text-[#6B7280] hover:text-abyss-ink"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-xs text-[#6B7280] py-4">Loading telemetry data...</p>}

      {!loading && activeTab === "events" && (
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-abyss-ink">Telemetry Events ({events.length})</h3>
            <span className="text-[10px] text-[#6B7280]">Metadata only — no design data</span>
          </div>
          {events.length === 0 ? (
            <p className="text-xs text-[#6B7280]">No telemetry events recorded.</p>
          ) : (
            <div className="space-y-1">
              {events.slice(0, 50).map((evt, i) => (
                <PayloadViewer key={i} label={evt.event || "event"} payload={eventToPayload(evt)} />
              ))}
            </div>
          )}
        </div>
      )}

      {!loading && activeTab === "unknowns" && (
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-abyss-ink">Unknown Failures Dataset ({unknowns.length})</h3>
            <span className="text-[10px] text-[#6B7280]">Signature + frequency only — no logs</span>
          </div>
          {unknowns.length === 0 ? (
            <p className="text-xs text-[#6B7280]">No unknown failures recorded.</p>
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="text-[10px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">Tool</th>
                  <th className="text-left pb-2 font-medium">Failure Type</th>
                  <th className="text-left pb-2 font-medium">Signature</th>
                  <th className="text-right pb-2 font-medium">Frequency</th>
                  <th className="text-right pb-2 font-medium">Last Seen</th>
                </tr>
              </thead>
              <tbody>
                {unknowns.map((u, i) => (
                  <tr key={i} className="border-b border-stone-ridge/50">
                    <td className="py-2 text-abyss-ink">{u.tool}</td>
                    <td className="py-2">{u.failure_type}</td>
                    <td className="py-2 font-mono text-[9px] text-[#6B7280]">{u.signature || "—"}</td>
                    <td className="py-2 text-right">{u.frequency}</td>
                    <td className="py-2 text-right text-[#6B7280]">{u.last_seen?.slice(0, 10)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {!loading && activeTab === "escalations" && (
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-abyss-ink">Escalations ({escalations.length})</h3>
            <span className="text-[10px] text-[#6B7280]">Consent-gated — no data sent without permission</span>
          </div>
          {escalations.length === 0 ? (
            <p className="text-xs text-[#6B7280]">No escalations recorded.</p>
          ) : (
            <div className="space-y-2">
              {escalations.map((esc, i) => (
                <div key={i} className="border border-stone-ridge rounded p-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium">{esc.failure_type}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                      esc.status === "sent" ? "bg-blue-100 text-blue-700" :
                      esc.status === "resolved" ? "bg-emerald-100 text-emerald-700" :
                      "bg-gray-100 text-gray-600"
                    }`}>{esc.status}</span>
                  </div>
                  {esc.consent_given ? (
                    <div className="flex items-center gap-1 mt-1">
                      <CheckCircle size={10} className="text-emerald-500" />
                      <span className="text-[9px] text-emerald-600">Consent given</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 mt-1">
                      <Info size={10} className="text-[#6B7280]" />
                      <span className="text-[9px] text-[#6B7280]">No consent — never uploaded</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!loading && activeTab === "patterns" && (
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-abyss-ink">Resolution Patterns — Trust Distribution</h3>
            <span className="text-[10px] text-[#6B7280]">Aggregate only — no design data</span>
          </div>
          {patterns ? (
            <div className="grid grid-cols-3 gap-4 text-xs">
              <div className="p-3 bg-emerald-50 rounded border border-emerald-200">
                <p className="text-emerald-700 font-semibold">{patterns.avg_trust_score?.toFixed(3) || "—"}</p>
                <p className="text-[10px] text-emerald-600">Avg Trust Score</p>
              </div>
              <div className="p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-blue-700 font-semibold">{patterns.total_patterns || "—"}</p>
                <p className="text-[10px] text-blue-600">Total Patterns</p>
              </div>
              <div className="p-3 bg-gray-50 rounded border border-stone-ridge">
                <p className="text-gray-700 font-semibold">{patterns.overall_success_rate || "—"}%</p>
                <p className="text-[10px] text-gray-600">Success Rate</p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-[#6B7280]">No resolution patterns.</p>
          )}
        </div>
      )}

      {!loading && activeTab === "preview" && (
        <div className="space-y-4">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Eye size={14} className="text-amber-600 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-amber-800">Upload Preview</p>
                <p className="text-[10px] text-amber-700 mt-1">
                  Below is an example of the exact JSON payload that would be uploaded during a community intelligence escalation.
                  Nothing more than these fields is ever sent. All data is sanitized before upload.
                </p>
              </div>
            </div>
          </div>

          <PayloadViewer
            label="📦 Escalation Upload Payload (sanitized)"
            payload={{
              package_version: "1.0",
              consent_record: {
                consent_given: true,
                consent_timestamp: "2026-06-15T12:00:00Z",
                user_acknowledged_no_sensitive_data: true,
              },
              failure: {
                tool: "openroad",
                stage: "ROUTING",
                failure_type: "DRC_VIOLATION",
                error_text: "[REDACTED FILE PATHS]",
                log_excerpt: "[REDACTED — 100 lines, paths removed]",
                metrics: { wns: -0.05, tns: -12.3, utilization: 72.5 },
                design_metadata: {
                  design_name: "[HASHED]",
                  top_module: "[HASHED]",
                  pdk: "sky130A",
                  clock_period_ns: 10.0,
                  utilization_target: 70,
                  threads: 4,
                },
                run_metadata: {
                  run_id: "[HASHED]",
                  timestamp: "2026-06-15T10:00:00Z",
                  backend: "openroad",
                  gli_version: "1.0.0",
                  status: "FAILED",
                  current_stage: "ROUTING",
                },
              },
              ai_suggestions: {},
              user_notes: "",
            }}
          />

          <PayloadViewer
            label="📊 Telemetry Event Payload"
            payload={{
              event: "failure_atlas_miss",
              details: {
                signature: "drc:li.3",
                error_class: "DRC",
                confidence: 0.0,
                severity: "HIGH",
                stage: "ROUTING",
                tool: "openroad",
                failure_type: "DRC_VIOLATION",
                frequency: 3,
                ai_helpfulness: "unknown",
                resolution_outcome: "",
              },
            }}
          />

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <CheckCircle size={14} className="text-emerald-600 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-emerald-800">Privacy Guarantee</p>
                <ul className="text-[10px] text-emerald-700 mt-1 space-y-0.5 list-disc list-inside">
                  <li>No RTL, SystemVerilog, Verilog, VHDL ever collected</li>
                  <li>No GDS, DEF, LEF, netlists ever collected</li>
                  <li>No Liberty files, constraints, or source code ever collected</li>
                  <li>Design names and run IDs are hashed before upload</li>
                  <li>File paths and instance paths are redacted</li>
                  <li>All uploads require explicit user consent</li>
                  <li>Consent is enforced at 7 independent layers</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
