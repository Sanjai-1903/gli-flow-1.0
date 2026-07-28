import { useState, useEffect } from "react"
import { Shield, Send, CheckCircle, AlertTriangle, ExternalLink, ArrowUp, FileText, TrendingUp, TrendingDown } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

function StatusBadge({ status }) {
  const colors = {
    open: "bg-amber-100 text-amber-700 border-amber-200",
    submitted: "bg-blue-100 text-blue-700 border-blue-200",
    responded: "bg-green-100 text-green-700 border-green-200",
    resolved: "bg-green-100 text-green-700 border-green-200",
    closed: "bg-gray-100 text-gray-700 border-gray-200",
  }
  const cls = colors[status] || "bg-gray-100 text-gray-700 border-gray-200"
  return <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${cls}`}>{status}</span>
}

function StatCard({ label, value, color }) {
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-4">
      <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">{label}</p>
      <p className={`text-xl font-semibold mt-1 ${color || "text-abyss-ink"}`}>{value}</p>
    </div>
  )
}

function EscalationRow({ esc, onSelect }) {
  return (
    <div
      className="flex items-center justify-between p-3 bg-white border border-stone-ridge rounded-lg hover:border-cyan-300 cursor-pointer transition-colors"
      onClick={() => onSelect?.(esc)}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <StatusBadge status={esc.status} />
          <span className="text-[10px] font-medium text-abyss-ink">{esc.failure_type}</span>
          {esc.tool && <span className="text-[10px] text-[#6B7280]">({esc.tool}/{esc.stage})</span>}
        </div>
        <p className="text-[9px] text-[#6B7280] truncate">{esc.id}</p>
      </div>
      <div className="text-right flex-shrink-0 text-[10px] text-[#6B7280]">
        <p>{esc.created_at?.slice(0, 10) || "—"}</p>
        {esc.engineer_response && esc.engineer_response !== "{}" && (
          <p className="text-green-600 text-[9px] mt-0.5">Has response</p>
        )}
      </div>
    </div>
  )
}

function EscalationDetail({ esc, onBack }) {
  const [response, setResponse] = useState("")
  const [saving, setSaving] = useState(false)

  const engResp = (() => {
    try { return typeof esc.engineer_response === "string" ? JSON.parse(esc.engineer_response) : esc.engineer_response || {} } catch { return {} }
  })()

  const saveResponse = () => {
    if (!response.trim()) return
    setSaving(true)
    const parsed = engResp
    parsed.notes = response
    parsed.responded_at = new Date().toISOString()
    fetch(`${API_BASE}/community/escalation/${esc.id}/response`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ response: parsed }),
    })
      .then(r => r.ok ? r.json() : null)
      .then(() => {
        engResp.notes = response
        engResp.responded_at = new Date().toISOString()
        setSaving(false)
      })
      .catch(() => setSaving(false))
  }

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-xs text-meridian-gold hover:underline mb-2">← Back to all escalations</button>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Shield size={16} className="text-cyan-600" />
            <h3 className="text-sm font-semibold text-abyss-ink">{esc.id}</h3>
          </div>
          <StatusBadge status={esc.status} />
        </div>

        <div className="grid grid-cols-3 gap-4 text-xs mb-4">
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase">Failure</p>
            <p className="font-medium text-abyss-ink">{esc.failure_type}</p>
          </div>
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase">Tool/Stage</p>
            <p className="font-medium text-abyss-ink">{esc.tool || "—"} / {esc.stage || "—"}</p>
          </div>
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase">Consent</p>
            <p className={`font-medium ${esc.consent_given ? "text-green-600" : "text-red-600"}`}>{esc.consent_given ? "Given" : "Not given"}</p>
          </div>
        </div>

        {esc.user_notes && (
          <div className="mb-4">
            <p className="text-[10px] font-semibold text-abyss-ink mb-1">User Notes</p>
            <p className="text-[10px] text-[#6B7280] bg-[#FAFAF8] p-2 rounded border border-stone-ridge">{esc.user_notes}</p>
          </div>
        )}

        {esc.bharatcode_submission_id && (
          <div className="mb-4 text-[10px]">
            <span className="text-[#6B7280]">BharatCode ID:</span>{" "}
            <span className="font-medium text-abyss-ink">{esc.bharatcode_submission_id}</span>
          </div>
        )}

        {Object.keys(engResp).length > 0 && (
          <div className="mb-4">
            <p className="text-[10px] font-semibold text-abyss-ink mb-1">Engineer Response</p>
            <div className="text-[10px] text-[#6B7280] bg-green-50 p-2 rounded border border-green-200">
              {Object.entries(engResp).map(([k, v]) => (
                <p key={k}><span className="font-medium text-abyss-ink">{k}:</span> {typeof v === "string" ? v : JSON.stringify(v)}</p>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-stone-ridge pt-3">
          <p className="text-[10px] font-semibold text-abyss-ink mb-2">Add Engineering Response</p>
          <textarea
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Document findings, root cause, and recommended fix..."
            className="w-full text-[10px] border border-stone-ridge rounded p-2 resize-none"
            rows={3}
          />
          <button
            onClick={saveResponse}
            disabled={!response.trim() || saving}
            className={`flex items-center gap-1 text-[10px] px-3 py-1.5 rounded font-medium mt-2 transition-colors ${
              response.trim() && !saving
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-gray-100 text-gray-400 cursor-not-allowed"
            }`}
          >
            {saving ? "Saving..." : <><CheckCircle size={10} /> Save Response</>}
          </button>
        </div>
      </div>
    </div>
  )
}

function KnowledgeGapRow({ gap }) {
  return (
    <div className="flex items-center justify-between p-2 bg-white border border-stone-ridge rounded">
      <div className="flex items-center gap-2 text-[10px]">
        <AlertTriangle size={10} className="text-amber-500" />
        <span className="font-medium text-abyss-ink">{gap.failure_type}</span>
        <span className="text-[#6B7280]">({gap.tool})</span>
      </div>
      <div className="flex items-center gap-3 text-[10px]">
        <span className="text-[#6B7280]">Freq: {gap.frequency}</span>
        <span className={`px-1.5 py-0.5 rounded text-[9px] ${
          gap.ai_helpfulness === "helpful" ? "bg-green-100 text-green-700" :
          gap.ai_helpfulness === "not_helpful" ? "bg-red-100 text-red-700" :
          "bg-gray-100 text-gray-700"
        }`}>
          {gap.ai_helpfulness}
        </span>
      </div>
    </div>
  )
}

export default function EngineeringDashboardPage() {
  const [escalations, setEscalations] = useState([])
  const [stats, setStats] = useState(null)
  const [knowledgeGaps, setKnowledgeGaps] = useState([])
  const [resolutionSummary, setResolutionSummary] = useState(null)
  const [topResolved, setTopResolved] = useState([])
  const [topUnresolved, setTopUnresolved] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedEsc, setSelectedEsc] = useState(null)
  const [statusFilter, setStatusFilter] = useState("")

  const fetchData = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (statusFilter) params.set("status", statusFilter)
    params.set("limit", "100")

    Promise.all([
      fetch(`${API_BASE}/community/escalations?${params}`).then(r => r.json()),
      fetch(`${API_BASE}/community/stats`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/community/knowledge-gaps?limit=20`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/resolutions/summary`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/resolutions/top-resolved?limit=5`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/resolutions/top-unresolved?limit=5`).then(r => r.ok ? r.json() : null),
    ])
      .then(([escData, statsData, gapsData, resSummary, resTop, resUnres]) => {
        setEscalations(escData.results || [])
        setStats(statsData)
        setKnowledgeGaps(gapsData?.gaps || [])
        setResolutionSummary(resSummary)
        setTopResolved(resTop?.patterns || [])
        setTopUnresolved(resUnres?.patterns || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, 30000)
    return () => clearInterval(id)
  }, [statusFilter])

  if (selectedEsc) {
    return <EscalationDetail esc={selectedEsc} onBack={() => setSelectedEsc(null)} />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">Engineering Dashboard</h2>
        <div className="text-[10px] text-[#6B7280]">
          Community Intelligence — {stats?.total_escalations || 0} total escalations
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <StatCard label="Total Escalations" value={stats?.total_escalations || 0} color="text-abyss-ink" />
        <StatCard label="Open" value={stats?.open_escalations || 0} color="text-amber-600" />
        <StatCard label="Responded" value={stats?.responded_escalations || 0} color="text-green-600" />
        <StatCard label="Dataset Entries" value={stats?.dataset_entries || 0} color="text-blue-600" />
        <StatCard label="Telemetry Events" value={stats?.telemetry_events || 0} color="text-purple-600" />
      </div>

      {resolutionSummary && (
        <div className="grid grid-cols-4 gap-4">
          <StatCard label="Resolution Patterns" value={resolutionSummary.total_patterns || 0} color="text-emerald-600" />
          <StatCard label="Total Successes" value={resolutionSummary.total_successes || 0} color="text-green-600" />
          <StatCard label="Overall Success Rate" value={`${resolutionSummary.overall_success_rate || 0}%`} color="text-emerald-600" />
          <StatCard label="Avg Confidence" value={`${((resolutionSummary.avg_confidence || 0) * 100).toFixed(0)}%`} color="text-blue-600" />
        </div>
      )}

      {(topResolved.length > 0 || topUnresolved.length > 0) && (
        <div className="grid grid-cols-2 gap-4">
          {topResolved.length > 0 && (
            <div className="bg-white border border-emerald-200 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp size={14} className="text-emerald-600" />
                <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Highest Confidence Fixes</h3>
              </div>
              <div className="space-y-2">
                {topResolved.map((p, i) => (
                  <div key={i} className="flex items-center justify-between text-[10px] p-2 bg-emerald-50 rounded border border-emerald-100">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-abyss-ink truncate">{p.resolution}</p>
                      <p className="text-[#6B7280]">{p.failure_type}</p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-2">
                      <p className="font-semibold text-emerald-700">{(p.confidence * 100).toFixed(0)}%</p>
                      <p className="text-[#6B7280]">{p.success_count}/{p.total_attempts}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {topUnresolved.length > 0 && (
            <div className="bg-white border border-red-200 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-3">
                <TrendingDown size={14} className="text-red-500" />
                <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Top Unresolved Failures</h3>
              </div>
              <div className="space-y-2">
                {topUnresolved.map((p, i) => (
                  <div key={i} className="flex items-center justify-between text-[10px] p-2 bg-red-50 rounded border border-red-100">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-abyss-ink truncate">{p.resolution}</p>
                      <p className="text-[#6B7280]">{p.failure_type}</p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-2">
                      <p className="font-semibold text-red-600">{p.failure_count} failed</p>
                      <p className="text-[#6B7280]">{p.total_attempts} attempts</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-[65%_35%] gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Open Escalations</h3>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-[10px] border border-stone-ridge rounded px-2 py-1"
            >
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="submitted">Submitted</option>
              <option value="responded">Responded</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          {loading ? (
            <p className="text-xs text-[#6B7280] py-4">Loading escalations...</p>
          ) : escalations.length === 0 ? (
            <p className="text-xs text-[#6B7280] py-8 text-center">No escalations found.</p>
          ) : (
            <div className="space-y-2">
              {escalations.map((esc, i) => (
                <EscalationRow key={esc.id || i} esc={esc} onSelect={setSelectedEsc} />
              ))}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="bg-white border border-stone-ridge rounded-lg p-5">
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Top Unknown Failures</h3>
            {stats?.top_unknown_failures?.length > 0 ? (
              <div className="space-y-2">
                {stats.top_unknown_failures.map((f, i) => (
                  <div key={i} className="flex items-center justify-between text-[10px]">
                    <span className="text-abyss-ink">{f.failure_type}</span>
                    <span className="text-[#6B7280]">x{f.frequency}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-[10px] text-[#6B7280]">No data yet.</p>
            )}
          </div>

          <div className="bg-white border border-stone-ridge rounded-lg p-5">
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Knowledge Gaps</h3>
            <p className="text-[10px] text-[#6B7280] mb-3">
              High-frequency failures with no resolved outcome — candidates for escalation.
            </p>
            {knowledgeGaps.length > 0 ? (
              <div className="space-y-1">
                {knowledgeGaps.map((g, i) => (
                  <KnowledgeGapRow key={i} gap={g} />
                ))}
              </div>
            ) : (
              <p className="text-[10px] text-[#6B7280]">No knowledge gaps identified.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
