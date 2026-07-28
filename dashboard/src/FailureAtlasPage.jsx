import { useState, useEffect } from "react"
import { Search, Filter, AlertTriangle, CheckCircle, ChevronDown, ChevronRight, ExternalLink, ArrowUp, ArrowDown, Minus, Sparkles, ThumbsUp, ThumbsDown, MessageSquare, Send, Shield } from "lucide-react"
import AIAvailabilityGuard from "./components/AIAvailabilityGuard"

const API_BASE = import.meta.env.VITE_API_URL || ""

function _severityLevel(sev) {
  const map = { INFO: "INFO", LOW: "ADVISORY", WARNING: "WARNING", MEDIUM: "WARNING",
    PERFORMANCE_DEGRADATION: "WARNING", FUNCTIONAL_RISK: "ERROR", HIGH: "ERROR",
    UNDER_REVIEW: "ERROR", TAPEOUT_BLOCKING: "CRITICAL" }
  return map[sev] || "WARNING"
}

const severityStyles = {
  INFO: "bg-blue-100 text-blue-700 border-blue-200",
  ADVISORY: "bg-slate-100 text-slate-700 border-slate-200",
  WARNING: "bg-yellow-100 text-yellow-700 border-yellow-200",
  ERROR: "bg-orange-100 text-orange-700 border-orange-200",
  CRITICAL: "bg-red-100 text-red-700 border-red-200",
}

const severityOrder = { INFO: 0, ADVISORY: 1, WARNING: 2, ERROR: 3, CRITICAL: 4 }

function SeverityBadge({ severity }) {
  const level = _severityLevel(severity)
  const cls = severityStyles[level] || "bg-gray-100 text-gray-700 border-gray-200"
  return <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${cls}`}>{level}</span>
}

function OverviewCards({ analytics }) {
  if (!analytics) return null
  const cards = [
    { label: "Total Failures", value: analytics.total_failures, color: "text-red-600" },
    { label: "Resolved", value: analytics.fixed_count, color: "text-green-600" },
    { label: "Success Rate", value: `${analytics.success_rate ?? 0}%`, color: analytics.success_rate > 50 ? "text-green-600" : "text-orange-600" },
    { label: "High Confidence", value: analytics.high_confidence_resolutions || 0, color: "text-blue-600" },
  ]
  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {cards.map(c => (
        <div key={c.label} className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">{c.label}</p>
          <p className={`text-xl font-semibold mt-1 ${c.color}`}>{c.value}</p>
        </div>
      ))}
    </div>
  )
}

function SeveritySummary({ failures }) {
  const _severityLevel = (sev) => {
    const map = { INFO: "INFO", LOW: "ADVISORY", WARNING: "WARNING", MEDIUM: "WARNING",
      PERFORMANCE_DEGRADATION: "WARNING", FUNCTIONAL_RISK: "ERROR", HIGH: "ERROR",
      UNDER_REVIEW: "ERROR", TAPEOUT_BLOCKING: "CRITICAL" }
    return map[sev] || "WARNING"
  }
  const counts = { CRITICAL: 0, ERROR: 0, WARNING: 0, ADVISORY: 0, INFO: 0 }
  failures.forEach(f => { const l = _severityLevel(f.severity); if (counts[l] != null) counts[l]++ })
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  const colorMap = { CRITICAL: "text-red-600 bg-red-50 border-red-200",
    ERROR: "text-orange-600 bg-orange-50 border-orange-200",
    WARNING: "text-yellow-600 bg-yellow-50 border-yellow-200",
    ADVISORY: "text-slate-600 bg-slate-50 border-slate-200",
    INFO: "text-blue-600 bg-blue-50 border-blue-200" }
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5 mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Severity Breakdown</h3>
        <span className="text-[10px] text-[#6B7280]">{total} total entries</span>
      </div>
      <div className="flex gap-2">
        {["CRITICAL", "ERROR", "WARNING", "ADVISORY", "INFO"].map(level => {
          const c = counts[level]
          if (!c) return null
          return (
            <div key={level} className={`flex-1 border rounded-lg p-3 ${colorMap[level]}`}>
              <p className="text-[10px] font-semibold opacity-80">{level}</p>
              <p className="text-lg font-bold">{c}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function CommonFailures({ data }) {
  if (!data || data.length === 0) return null
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Most Common Failures</h3>
      <table className="w-full text-xs">
        <thead><tr className="text-[10px] text-[#6B7280] border-b border-stone-ridge">
          <th className="text-left pb-2 font-medium">Failure Type</th>
          <th className="text-right pb-2 font-medium">Count</th>
          <th className="text-right pb-2 font-medium">%</th>
        </tr></thead>
        <tbody>
          {data.map((f, i) => (
            <tr key={i} className="border-b border-stone-ridge/50">
              <td className="py-2 text-abyss-ink">{f.failure_type}</td>
              <td className="py-2 text-right">{f.count}</td>
              <td className="py-2 text-right text-[#6B7280]">{f.percentage}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function FixEffectiveness({ data }) {
  if (!data || data.message === "Insufficient Data") {
    return (
      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Most Effective Fixes</h3>
        <p className="text-xs text-[#6B7280]">Insufficient Data — need at least {data?.min_samples_required || 3} samples per fix type.</p>
      </div>
    )
  }
  const results = data?.results || []
  if (results.length === 0) return null
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Most Effective Fixes</h3>
      <table className="w-full text-xs">
        <thead><tr className="text-[10px] text-[#6B7280] border-b border-stone-ridge">
          <th className="text-left pb-2 font-medium">Failure Type</th>
          <th className="text-left pb-2 font-medium">Fix Type</th>
          <th className="text-right pb-2 font-medium">Success Rate</th>
          <th className="text-right pb-2 font-medium">Sample Size</th>
        </tr></thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={i} className="border-b border-stone-ridge/50">
              <td className="py-2 text-abyss-ink">{r.failure_type}</td>
              <td className="py-2 text-[#6B7280]">{r.fix_type}</td>
              <td className="py-2 text-right font-medium">{r.success_rate}%</td>
              <td className="py-2 text-right text-[#6B7280]">{r.sample_size}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function QoRImprovements({ data }) {
  if (!data || data.length === 0) return null
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">QoR Impact by Fix Type</h3>
      <table className="w-full text-xs">
        <thead><tr className="text-[10px] text-[#6B7280] border-b border-stone-ridge">
          <th className="text-left pb-2 font-medium">Fix Type</th>
          <th className="text-right pb-2 font-medium">Avg WNS Improvement</th>
          <th className="text-right pb-2 font-medium">Avg TNS Improvement</th>
          <th className="text-right pb-2 font-medium">Sample Size</th>
        </tr></thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={i} className="border-b border-stone-ridge/50">
              <td className="py-2 text-abyss-ink">{r.fix_type}</td>
              <td className={`py-2 text-right ${r.avg_wns_improvement > 0 ? "text-green-600" : "text-red-600"}`}>{r.avg_wns_improvement?.toFixed(3)} ns</td>
              <td className={`py-2 text-right ${r.avg_tns_improvement > 0 ? "text-green-600" : "text-red-600"}`}>{r.avg_tns_improvement?.toFixed(2)} ns</td>
              <td className="py-2 text-right text-[#6B7280]">{r.sample_size}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ResolutionConfidence({ data }) {
  if (!data) return null
  const { distribution, unresolved } = data
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Resolution Confidence</h3>
      <div className="space-y-2">
        {(distribution || []).map((d, i) => {
          const color = d.resolution_confidence === "HIGH" ? "bg-green-500" : d.resolution_confidence === "MEDIUM" ? "bg-yellow-500" : "bg-red-500"
          return (
            <div key={i} className="flex items-center gap-2 text-xs">
              <span className={`w-2 h-2 rounded-full ${color}`} />
              <span className="w-16">{d.resolution_confidence || "UNKNOWN"}</span>
              <span className="font-medium">{d.count}</span>
            </div>
          )
        })}
        {unresolved > 0 && (
          <div className="flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full bg-gray-300" />
            <span className="w-16">UNRESOLVED</span>
            <span className="font-medium">{unresolved}</span>
          </div>
        )}
      </div>
    </div>
  )
}

function FailureTrends({ data }) {
  if (!data) return null
  const { failure_distribution, daily_counts } = data
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Failure Trends</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-[10px] font-semibold text-[#6B7280] mb-2">Distribution</p>
          <div className="space-y-1">
            {(failure_distribution || []).slice(0, 5).map((f, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span>{f.failure_type}</span>
                <span className="text-[#6B7280]">{f.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-[10px] font-semibold text-[#6B7280] mb-2">Recent Activity</p>
          <div className="space-y-1">
            {(daily_counts || []).slice(0, 7).map((d, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span>{d.date}</span>
                <span className="text-[#6B7280]">{d.count} failure(s)</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function CoverageIntelligence({ data }) {
  if (!data) return null
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Coverage Intelligence</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-[10px] font-semibold text-[#6B7280] mb-2">Most Viewed Rules</p>
          <div className="space-y-1">
            {data.most_viewed.map((f, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span>{f.rule_id}</span>
                <span className="text-[#6B7280]">{f.views} views</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-[10px] font-semibold text-[#6B7280] mb-2">Most Requested Missing</p>
          <div className="space-y-1">
            {data.most_requested_missing.map((f, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-red-600">{f.rule_id}</span>
                <span className="text-[#6B7280]">{f.requests} reqs</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function AIInvestigationCard({ failure, onClose }) {
  const runId = failure?.run_id
  const [aiData, setAiData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchExisting = () => {
    if (!runId) return
    fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/investigation`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.investigation || data?.status) setAiData(data)
      })
      .catch(() => {})
  }

  useEffect(() => { fetchExisting() }, [runId])

  const triggerAI = () => {
    if (!runId) {
      setError("This failure is not associated with a run. AI investigation requires a run context.")
      return
    }
    setLoading(true)
    setError(null)
    fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/investigation`, { method: "POST" })
      .then(r => r.ok ? r.json() : r.json().then(e => { throw new Error(e.detail || "Investigation failed") }))
      .then(data => {
        setAiData(data)
        setLoading(false)
      })
      .catch(e => { setLoading(false); setError(e.message) })
  }

  const sendFeedback = (type) => {
    const resolved = type === "resolved"
    fetch(`${API_BASE}/ai/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        investigation_id: failure?.id || "unknown",
        feedback_type: type,
        resolved,
        run_id: runId || "",
        failure_type: failure?.failure_type || "",
      }),
    })
      .then(r => r.ok ? r.json() : null)
      .catch(() => {})
  }

  if (!aiData && !loading && !error) {
    return (
      <div className="p-4 bg-white border border-stone-ridge rounded-lg">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={14} className="text-purple-600" />
          <h4 className="text-xs font-semibold text-abyss-ink">AI Investigation Assistant</h4>
          <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded font-medium bg-amber-100 text-amber-700 border border-amber-200">EXPERIMENTAL</span>
        </div>
        {runId ? (
          <>
            <p className="text-[10px] text-[#6B7280] mb-3">No AI investigation has been run for this failure yet.</p>
            <button onClick={triggerAI} className="text-[10px] bg-purple-600 text-white px-3 py-1.5 rounded font-medium hover:bg-purple-700 transition-colors">
              Run AI Investigation
            </button>
          </>
        ) : (
          <p className="text-[10px] text-[#6B7280] mb-3">No associated run — AI investigation requires a run context.</p>
        )}
        <p className="text-[9px] text-[#6B7280] mt-2 italic">AI GENERATED · NOT VERIFIED — Always verify with manual inspection.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-4 bg-white border border-stone-ridge rounded-lg">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={14} className="text-purple-600 animate-pulse" />
          <h4 className="text-xs font-semibold text-abyss-ink">AI Investigation Assistant</h4>
        </div>
        <p className="text-[10px] text-[#6B7280]">Analyzing failure...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-white border border-red-200 rounded-lg">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={14} className="text-purple-600" />
          <h4 className="text-xs font-semibold text-abyss-ink">AI Investigation Assistant</h4>
        </div>
        <p className="text-[10px] text-red-600 mb-2">{error}</p>
        <button onClick={triggerAI} className="text-[10px] bg-purple-600 text-white px-3 py-1.5 rounded font-medium hover:bg-purple-700 transition-colors">
          Retry
        </button>
      </div>
    )
  }

  const inv = aiData?.investigation || {}
  const status = aiData?.status || inv?.status
  const summary = inv?.summary || ""
  const facts = inv?.facts || []
  const causes = inv?.possible_causes || []
  const steps = inv?.recommended_next_steps || []
  const missingInfo = inv?.missing_information || []
  const disclaimer = inv?.disclaimer || ""
  const failedAttempts = aiData?.failed_attempts || []

  return (
    <div className="p-4 bg-white border border-purple-200 rounded-lg shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={14} className="text-purple-600" />
          <h4 className="text-xs font-semibold text-abyss-ink">AI Investigation Assistant</h4>
          {runId && <span className="text-[9px] text-[#6B7280]">({runId.slice(0, 12)})</span>}
        </div>
        <div className="flex items-center gap-1">
          <span className="text-[8px] px-1 py-0.5 rounded font-medium bg-amber-100 text-amber-700 border border-amber-200">AI GENERATED</span>
          <span className="text-[8px] px-1 py-0.5 rounded font-medium bg-purple-100 text-purple-700 border border-purple-200">EXPERIMENTAL</span>
          <span className="text-[8px] px-1 py-0.5 rounded font-medium bg-gray-100 text-gray-700 border border-gray-200">NOT VERIFIED</span>
        </div>
      </div>

      {status && (
        <div className="text-[10px] mb-3">
          <span className="font-medium">Status: </span>
          <span className={`font-semibold ${status === "EXPERIMENTAL" ? "text-purple-600" : "text-amber-600"}`}>{status}</span>
          {aiData?.latency_sec > 0 && (
            <span className="text-[#6B7280] ml-2">({aiData.latency_sec.toFixed(1)}s)</span>
          )}
        </div>
      )}

      {summary && <p className="text-[10px] text-[#6B7280] mb-4 leading-relaxed">{summary}</p>}

      {facts.length > 0 && (
        <div className="mb-4">
          <p className="text-[10px] font-semibold text-abyss-ink mb-2">Facts ({facts.length})</p>
          <div className="space-y-1.5">
            {facts.map((f, i) => (
              <div key={i} className="text-[10px] pl-2 border-l-2 border-stone-ridge">
                <span className="text-[#6B7280]">{f.observation}</span>
                {f.source && <span className="text-[#6B7280] ml-1 italic">— {f.source}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {causes.length > 0 && (
        <div className="mb-4">
          <p className="text-[10px] font-semibold text-abyss-ink mb-2">Possible Causes</p>
          <div className="space-y-2">
            {causes.map((c, i) => (
              <div key={i} className="text-[10px] border border-stone-ridge rounded p-2">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-1.5 py-0.5 rounded font-medium ${
                    c.confidence === "HIGH" ? "bg-red-100 text-red-700" :
                    c.confidence === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
                    "bg-gray-100 text-gray-600"
                  }`}>{c.confidence || "MEDIUM"}</span>
                  <span className="font-medium">{c.cause}</span>
                </div>
                {c.reasoning && <p className="text-[#6B7280] mt-0.5">{c.reasoning}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {steps.length > 0 && (
        <div className="mb-4">
          <p className="text-[10px] font-semibold text-abyss-ink mb-2">Recommended Next Steps</p>
          <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
            {steps.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
      )}

      {missingInfo.length > 0 && (
        <div className="mb-4">
          <p className="text-[10px] font-semibold text-abyss-ink mb-1">Missing Information</p>
          <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
            {missingInfo.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </div>
      )}

      {disclaimer && (
        <p className="text-[10px] text-[#6B7280] italic mb-3">{disclaimer}</p>
      )}

      <div className="text-[9px] text-[#6B7280] italic mt-3 pt-2 border-t border-stone-ridge">
        This guidance is AI-generated and may be incorrect. Always verify with manual inspection.
      </div>

      <div className="flex items-center gap-2 mt-3 pt-2 border-t border-stone-ridge">
        <span className="text-[9px] text-[#6B7280]">Was this helpful?</span>
        <button onClick={() => sendFeedback("helpful")} className="flex items-center gap-1 text-[9px] px-2 py-0.5 rounded bg-green-50 text-green-700 border border-green-200 hover:bg-green-100">
          <ThumbsUp size={10} /> Yes
        </button>
        <button onClick={() => sendFeedback("not_helpful")} className="flex items-center gap-1 text-[9px] px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200 hover:bg-red-100">
          <ThumbsDown size={10} /> No
        </button>
      </div>

      {failedAttempts.length > 0 && (
        <details className="mt-2">
          <summary className="text-[9px] text-red-600 cursor-pointer hover:text-red-700">
            Failed attempts ({failedAttempts.length})
          </summary>
          <div className="mt-1 space-y-1">
            {failedAttempts.map((a, i) => (
              <div key={i} className="text-[9px] text-red-500">{a.error}</div>
            ))}
          </div>
        </details>
      )}

      <button onClick={triggerAI} disabled={loading} className="mt-2 text-[9px] text-purple-600 hover:text-purple-700 disabled:opacity-50">
        {loading ? "Running..." : "Run again"}
      </button>

      {onClose && (
        <button onClick={onClose} className="text-[9px] text-[#6B7280] mt-2 ml-2 hover:underline">Dismiss</button>
      )}
    </div>
  )
}

function EscalationCard({ failure, onClose }) {
  const [consent, setConsent] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [notes, setNotes] = useState("")

  const submitEscalation = () => {
    if (!consent) return
    setSubmitting(true)
    const ev = (() => { try { return typeof failure.evidence === "string" ? JSON.parse(failure.evidence) : failure.evidence || {} } catch { return {} } })()
    fetch(`${API_BASE}/community/escalate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        failure_type: failure.failure_type,
        tool: ev.tool || "",
        stage: ev.stage || failure.domain || "",
        run_id: failure.run_id || "",
        error_text: failure.description || failure.title || "",
        notes,
        consent,
      }),
    })
      .then(r => r.ok ? r.json() : null)
      .then(data => setResult(data || { status: "failed" }))
      .catch(() => setResult({ status: "failed" }))
      .finally(() => setSubmitting(false))
  }

  return (
    <div className="p-4 bg-white border border-cyan-200 rounded-lg shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Shield size={14} className="text-cyan-600" />
        <h4 className="text-xs font-semibold text-abyss-ink">Community Intelligence</h4>
        <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded font-medium bg-cyan-100 text-cyan-700 border border-cyan-200">EXPERIMENTAL</span>
      </div>

      {result ? (
        <div>
          {result.status === "submitted" ? (
            <div className="text-[10px]">
              <p className="text-green-700 font-medium">✓ Escalation submitted</p>
              <p className="text-[#6B7280] mt-1">ID: {result.id}</p>
              {result.bharatcode_submission_id && (
                <p className="text-[#6B7280]">BharatCode: {result.bharatcode_submission_id}</p>
              )}
            </div>
          ) : (
            <p className="text-[10px] text-red-600">Failed to submit escalation.</p>
          )}
          {onClose && (
            <button onClick={onClose} className="text-[9px] text-[#6B7280] mt-2 hover:underline">Dismiss</button>
          )}
        </div>
      ) : (
        <>
          <p className="text-[10px] text-[#6B7280] mb-3">
            This unknown failure can be escalated to GLI engineers for analysis.
            A sanitized failure package (no RTL, GDS, or source code) will be shared.
          </p>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional notes for engineers..."
            className="w-full text-[10px] border border-stone-ridge rounded p-2 mb-2 resize-none"
            rows={2}
          />
          <label className="flex items-start gap-2 mb-3 cursor-pointer">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-0.5"
            />
            <span className="text-[10px] text-[#6B7280]">
              I consent to share sanitized failure data (failure type, tool, stage, error text, metrics).
              No RTL, GDS, netlists, source code, or customer IP will be included.
            </span>
          </label>
          <div className="flex items-center gap-2">
            <button
              onClick={submitEscalation}
              disabled={!consent || submitting}
              className={`flex items-center gap-1 text-[10px] px-3 py-1.5 rounded font-medium transition-colors ${
                consent && !submitting
                  ? "bg-cyan-600 text-white hover:bg-cyan-700"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              }`}
            >
              {submitting ? "Submitting..." : <><Send size={10} /> Escalate to GLI Engineers</>}
            </button>
          </div>
          <p className="text-[9px] text-[#6B7280] mt-2 italic">
            AI GENERATED · NOT VERIFIED — This is an experimental feature. Always review before escalating.
          </p>
        </>
      )}
    </div>
  )
}

function FailureList({ failures, onSelect }) {
  if (!failures || failures.length === 0) return <p className="text-xs text-[#6B7280] py-8 text-center">No failures found matching filters.</p>
  
  return (
    <div className="space-y-2">
      {failures.map((fa) => {
        let ev = {}
        try { if (typeof fa.evidence === "string") { ev = JSON.parse(fa.evidence) } else if (fa.evidence) { ev = fa.evidence } } catch {}
        const stage = fa.detection_stage || ev.stage || fa.domain || "—"
        const errorText = fa.description || fa.title || ""
        const isGeneric = !fa.title || fa.title === `Pipeline failed at stage ${stage}` || fa.title.startsWith("Run")
        
        return (
          <div key={fa.id || fa.failure_id} className="bg-white border border-stone-ridge rounded-lg p-4 hover:border-red-300 cursor-pointer transition-colors" onClick={() => onSelect?.(fa)}>
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <SeverityBadge severity={fa.severity} />
                  {ev.classification === "VALIDATED_TOOL_DISAGREEMENT" && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-purple-100 text-purple-700 border border-purple-200">Known Tool Disagreement</span>
                  )}
                  <span className="text-[10px] font-medium text-[#6B7280] uppercase tracking-wider">{fa.domain || "PIPELINE"}</span>
                  {stage && <span className="text-[10px] text-[#6B7280]">· {stage}</span>}
                  {fa.fix_applied && <CheckCircle size={12} className="text-green-500 ml-1" />}
                  {fa.is_important === 1 && <span className="text-[10px] font-medium text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">Important Run</span>}
                </div>
                {isGeneric ? (
                  <p className="text-xs text-[#6B7280] italic">{errorText || "Pipeline execution failed"}</p>
                ) : (
                  <p className="text-xs font-medium text-[#991B1B] leading-relaxed">{fa.title}</p>
                )}
                {!isGeneric && fa.description && fa.description !== fa.title && (
                  <p className="text-[10px] text-[#6B7280] mt-1 line-clamp-2">{fa.description}</p>
                )}
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-[10px] text-[#6B7280]">{fa.run_id?.slice(0, 16)}</p>
                <p className="text-[9px] text-[#6B7280] mt-0.5">{fa.detected_at ? new Date(fa.detected_at).toLocaleDateString() : ""}</p>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function TrustBadge({ trustLevel, trustScore, trustReason }) {
  const colors = {
    HIGH: "bg-emerald-100 text-emerald-700 border-emerald-200",
    MEDIUM: "bg-amber-100 text-amber-700 border-amber-200",
    LOW: "bg-gray-100 text-gray-600 border-gray-200",
  }
  const cls = colors[trustLevel] || colors.LOW
  return (
    <div className="flex items-center gap-2" title={trustReason}>
      <span className={`text-[9px] px-1.5 py-0.5 rounded font-medium border ${cls}`}>
        Trust: {trustLevel} ({(trustScore * 100).toFixed(0)}%)
      </span>
      <span className="text-[9px] text-[#6B7280] max-w-[200px] truncate" title={trustReason}>
        {trustReason}
      </span>
    </div>
  )
}

function HistoricalResolutions({ failure }) {
  const [patterns, setPatterns] = useState(null)
  const [feedback, setFeedback] = useState({})
  const [submitting, setSubmitting] = useState({})

  const fingerprint = failure?.signature || failure?.failure_type || ""

  useEffect(() => {
    if (!fingerprint) return
    fetch(`${API_BASE}/resolutions/patterns?fingerprint=${encodeURIComponent(fingerprint)}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.patterns?.length > 0) setPatterns(data.patterns)
      })
      .catch(() => {})
  }, [fingerprint])

  const sendFeedback = (patternId, feedbackType) => {
    if (submitting[patternId]) return
    setSubmitting(s => ({ ...s, [patternId]: true }))
    fetch(`${API_BASE}/resolutions/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pattern_id: patternId, run_id: "", feedback_type: feedbackType }),
    })
      .then(r => r.ok ? r.json() : null)
      .then(() => {
        setFeedback(f => ({ ...f, [patternId]: feedbackType }))
        setSubmitting(s => ({ ...s, [patternId]: false }))
      })
      .catch(() => setSubmitting(s => ({ ...s, [patternId]: false })))
  }

  if (!patterns || patterns.length === 0) return null

  return (
    <div className="bg-white border border-emerald-200 rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <CheckCircle size={16} className="text-emerald-600" />
        <h3 className="text-sm font-semibold text-abyss-ink">Historical Resolutions</h3>
        <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded font-medium bg-emerald-100 text-emerald-700 border border-emerald-200">RESOLUTION INTELLIGENCE</span>
      </div>
      <p className="text-[10px] text-[#6B7280] mb-3">What historically fixed this type of failure:</p>
      <div className="space-y-2">
        {patterns.map((p, i) => (
          <div key={p.id} className="border border-stone-ridge rounded p-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-xs font-medium text-abyss-ink">{i + 1}. {p.resolution}</p>
                <div className="flex items-center gap-3 mt-1">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                    p.confidence >= 0.8 ? "bg-emerald-100 text-emerald-700" :
                    p.confidence >= 0.5 ? "bg-amber-100 text-amber-700" :
                    "bg-gray-100 text-gray-600"
                  }`}>
                    Success Rate: {(p.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="text-[10px] text-[#6B7280]">
                    {p.success_count} success{p.success_count !== 1 ? "es" : ""} / {p.total_attempts} attempt{p.total_attempts !== 1 ? "s" : ""}
                  </span>
                  {p.resolution_type && (
                    <span className="text-[10px] text-[#6B7280]">{p.resolution_type}</span>
                  )}
                </div>
                <div className="mt-1">
                  <TrustBadge trustLevel={p.trust_level} trustScore={p.trust_score} trustReason={p.trust_reason} />
                </div>
                {p.root_cause && (
                  <p className="text-[10px] text-[#6B7280] mt-1">Root cause: {p.root_cause}</p>
                )}
              </div>
            </div>
            {!feedback[p.id] ? (
              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-stone-ridge/50">
                <span className="text-[10px] text-[#6B7280]">Did this fix solve the issue?</span>
                <button
                  onClick={() => sendFeedback(p.id, "confirmed")}
                  disabled={submitting[p.id]}
                  className="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded hover:bg-emerald-700 disabled:opacity-50"
                >
                  ✓ Yes
                </button>
                <button
                  onClick={() => sendFeedback(p.id, "rejected")}
                  disabled={submitting[p.id]}
                  className="text-[10px] bg-red-500 text-white px-2 py-0.5 rounded hover:bg-red-600 disabled:opacity-50"
                >
                  ✗ No
                </button>
              </div>
            ) : (
              <p className="text-[10px] text-emerald-600 mt-2 pt-2 border-t border-stone-ridge/50">
                {feedback[p.id] === "confirmed" ? "Confirmed — fix recorded as successful" : "Rejected — fix recorded as unsuccessful"}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function FailureDetail({ failure, onBack }) {
  const [knowledge, setKnowledge] = useState(null)
  const [correlation, setCorrelation] = useState(null)

  useEffect(() => {
    if (failure) {
      const identifier = failure.signature || failure.failure_type;
      if (identifier) {
        let ev = {}
        try { if (typeof failure.evidence === "string") { ev = JSON.parse(failure.evidence) } else if (failure.evidence) { ev = failure.evidence } } catch {}
        const citation = ev.citation || ""
        const params = citation ? `?citation=${encodeURIComponent(citation)}` : ""
        fetch(`${API_BASE}/knowledge/failures/${identifier}${params}`)
          .then(r => r.ok ? r.json() : null)
          .then(setKnowledge)
          .catch(() => setKnowledge(null))
        
        fetch(`${API_BASE}/failures/correlation/${failure.failure_type}`)
          .then(r => r.ok ? r.json() : null)
          .then(setCorrelation)
          .catch(() => setCorrelation(null))
      }
    }
  }, [failure])

  if (!failure) return null

  let ev = {}
  try { if (typeof failure.evidence === "string") { ev = JSON.parse(failure.evidence) } else if (failure.evidence) { ev = failure.evidence } } catch {}

  const stage = ev.stage || failure.detection_stage || failure.domain || "—"
  const errorText = failure.description || failure.title || ""
  const isGeneric = !failure.title || failure.title === `Pipeline failed at stage ${stage}` || failure.title.startsWith("Run run_")

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-xs text-meridian-gold hover:underline mb-2">← Back to all failures</button>
      
      {correlation && correlation.statistics && (
        <div className="mt-5 p-4 bg-white border border-stone-ridge rounded">
          <h4 className="text-xs font-semibold text-abyss-ink mb-3">Historical Intelligence</h4>
          <div className="grid grid-cols-3 gap-4 text-xs mb-4">
            <div><p className="text-[#6B7280]">Seen</p><p className="font-medium">{correlation.statistics.total_occurrences}</p></div>
            <div><p className="text-[#6B7280]">Resolved</p><p className="font-medium text-green-600">{correlation.statistics.resolved_count}</p></div>
            <div><p className="text-[#6B7280]">Unresolved</p><p className="font-medium text-red-600">{correlation.statistics.unresolved_count}</p></div>
          </div>
          <div className="text-xs mb-4">
            <p><span className="text-[#6B7280]">First Seen:</span> {correlation.statistics.first_seen?.slice(0, 10) || "—"}</p>
            <p><span className="text-[#6B7280]">Last Seen:</span> {correlation.statistics.last_seen?.slice(0, 10) || "—"}</p>
          </div>

          {correlation.affected_designs && correlation.affected_designs.length > 0 && (
              <>
                  <p className="text-[10px] font-semibold text-abyss-ink mb-1">Affected Designs</p>
                  <div className="flex flex-wrap gap-1 mb-4">
                    {correlation.affected_designs.map((d, i) => (
                      <span key={i} className="text-[10px] bg-stone-ridge/20 px-1.5 py-0.5 rounded">{d.design_name} ({d.occurrences})</span>
                    ))}
                  </div>
              </>
          )}

          {correlation.resolution_effectiveness && correlation.resolution_effectiveness.length > 0 && (
              <div className="mt-4">
                  <p className="text-[10px] font-semibold text-abyss-ink mb-1">Most Successful Historical Fixes</p>
                  <table className="w-full text-[10px] text-left">
                      <thead><tr className="text-[#6B7280]"><th>Fix Type</th><th>Attempts</th><th>Success %</th><th>Imp. Runs</th></tr></thead>
                      <tbody>
                          {correlation.resolution_effectiveness.map((e, i) => (
                              <tr key={i} className="border-t border-stone-ridge/50">
                                  <td>{e.fix_type}</td>
                                  <td>{e.attempts}</td>
                                  <td className="text-green-600 font-medium">{e.success_rate}%</td>
                                  <td>{e.important_runs}</td>
                              </tr>
                          ))}
                      </tbody>
                  </table>
              </div>
          )}
        </div>
      )}

      <HistoricalResolutions failure={failure} />

      {knowledge && (
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={16} className="text-topography-rust" />
            <h3 className="text-sm font-semibold text-abyss-ink">Knowledge Base — {knowledge.failure_type}</h3>
            {knowledge.source && (
              <span className="ml-auto text-[10px] text-[#6B7280]">{knowledge.source}{knowledge.version ? ` v${knowledge.version}` : ""}</span>
            )}
          </div>

          {knowledge.description && (
            <p className="text-xs text-[#6B7280] mb-4 leading-relaxed">{knowledge.description}</p>
          )}

          {knowledge.common_causes && knowledge.common_causes.length > 0 && (
            <div className="mb-4">
              <p className="text-[10px] font-semibold text-abyss-ink mb-1">Common Causes</p>
              <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
                {knowledge.common_causes.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}

          {knowledge.remediation_strategies && knowledge.remediation_strategies.length > 0 && (
            <div className="mb-4">
              <p className="text-[10px] font-semibold text-abyss-ink mb-1">Remediation Strategies</p>
              <div className="space-y-2">
                {knowledge.remediation_strategies.map((s, i) => (
                  <div key={i} className="text-[10px] p-2 bg-[#FAFAF8] rounded border border-stone-ridge">
                    <p className="font-medium text-abyss-ink">{s.technique || s}</p>
                    {s.description && <p className="text-[#6B7280] mt-0.5">{s.description}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {knowledge.verification_steps && knowledge.verification_steps.length > 0 && (
            <div className="mb-4">
              <p className="text-[10px] font-semibold text-abyss-ink mb-1">Verification Steps</p>
              <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
                {knowledge.verification_steps.map((v, i) => <li key={i}>{typeof v === "string" ? v : JSON.stringify(v)}</li>)}
              </ul>
            </div>
          )}

          {knowledge.references && knowledge.references.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold text-abyss-ink mb-1">References</p>
              <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
                {knowledge.references.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {(!knowledge || !correlation || (correlation?.statistics?.total_occurrences || 0) === 0) && (
        <>
          <AIAvailabilityGuard>
            <AIInvestigationCard failure={failure} />
          </AIAvailabilityGuard>
          <EscalationCard failure={failure} />
        </>
      )}

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle size={16} className="text-topography-rust" />
          <h3 className="text-sm font-semibold text-abyss-ink">Root Cause Analysis</h3>
        </div>

        <div className="bg-[#FEF2F2] border border-[#FECACA] rounded-lg p-4 mb-5">
          <p className="text-[10px] font-semibold text-[#991B1B] uppercase tracking-wider mb-2">Error</p>
          {isGeneric ? (
            <p className="text-xs italic text-[#6B7280]">{errorText || "Pipeline execution failed"}</p>
          ) : (
            <>
              <p className="text-sm font-medium text-[#991B1B] leading-relaxed">{failure.title}</p>
              {failure.description && failure.description !== failure.title && (
                <p className="text-xs text-[#6B7280] mt-2 leading-relaxed">{failure.description}</p>
              )}
            </>
          )}
        </div>
        
        <div className="grid grid-cols-4 gap-4 text-xs mb-5">
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase tracking-wider mb-0.5">Stage</p>
            <p className="font-medium text-abyss-ink">{stage}</p>
          </div>
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase tracking-wider mb-0.5">Severity</p>
            <div className="flex items-center gap-1.5">
              <SeverityBadge severity={failure.severity} />
              {ev.classification === "VALIDATED_TOOL_DISAGREEMENT" && (
                <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-purple-100 text-purple-700 border border-purple-200">Known Tool Disagreement</span>
              )}
            </div>
          </div>
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase tracking-wider mb-0.5">Confidence</p>
            <p className="font-medium text-abyss-ink">{failure.confidence != null ? `${(failure.confidence * 100).toFixed(0)}%` : "—"}</p>
          </div>
          <div className="p-3 bg-[#FAFAF8] rounded border border-stone-ridge">
            <p className="text-[9px] font-medium text-[#6B7280] uppercase tracking-wider mb-0.5">Run</p>
            <p className="font-medium text-abyss-ink text-[10px] truncate">{failure.run_id}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function FailureAtlasPage({ designFilter }) {
  const [failures, setFailures] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [commonFailures, setCommonFailures] = useState(null)
  const [fixEffectiveness, setFixEffectiveness] = useState(null)
  const [qorImprovements, setQorImprovements] = useState(null)
  const [failureTrends, setFailureTrends] = useState(null)
  const [resolutionConfidence, setResolutionConfidence] = useState(null)
  const [coverage, setCoverage] = useState(null)
  const [selectedFailure, setSelectedFailure] = useState(null)
  const [search, setSearch] = useState("")
  const [severityFilter, setSeverityFilter] = useState("")
  const [typeFilter, setTypeFilter] = useState("")
  const [includeHeuristic, setIncludeHeuristic] = useState(false)
  const [includeUnverified, setIncludeUnverified] = useState(false)
  const [loading, setLoading] = useState(true)

  const _severityLevel = (sev) => {
    const map = { INFO: "INFO", LOW: "ADVISORY", WARNING: "WARNING", MEDIUM: "WARNING",
      PERFORMANCE_DEGRADATION: "WARNING", FUNCTIONAL_RISK: "ERROR", HIGH: "ERROR",
      UNDER_REVIEW: "ERROR", TAPEOUT_BLOCKING: "CRITICAL" }
    return map[sev] || "WARNING"
  }
  const _severityOrder = { CRITICAL: 4, ERROR: 3, WARNING: 2, ADVISORY: 1, INFO: 0 }
  const sortedFailures = [...failures]
    .filter(f => !severityFilter || _severityLevel(f.severity) === severityFilter)
    .sort((a, b) => {
      const oa = _severityOrder[_severityLevel(a.severity)] || 0
      const ob = _severityOrder[_severityLevel(b.severity)] || 0
      if (oa !== ob) return ob - oa
      return (b.detected_at || "").localeCompare(a.detected_at || "")
    })

  const fetchAll = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (search) params.set("search", search)
    if (typeFilter) params.set("failure_type", typeFilter)
    if (designFilter) params.set("design", designFilter)
    if (includeHeuristic) params.set("include_heuristic", "true")
    if (includeUnverified) params.set("include_unverified", "true")
    params.set("limit", "200")

    const pStr = params.toString()

    Promise.all([
      fetch(`${API_BASE}/failures?${pStr}`).then(r => r.json()),
      fetch(`${API_BASE}/analytics/summary?${pStr}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/analytics/common-failures?${pStr}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/analytics/fix-effectiveness?${pStr}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/analytics/qor-improvements?${pStr}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/analytics/failure-trends?${pStr}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/analytics/resolution-confidence?${pStr}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/analytics/coverage?${pStr}`).then(r => r.ok ? r.json() : null),
    ])
      .then(([f, a, cf, fe, qi, ft, rc, cov]) => {
        setFailures(Array.isArray(f) ? f : (f.results || []))
        setAnalytics(a)
        setCommonFailures(cf)
        setFixEffectiveness(fe)
        setQorImprovements(qi)
        setFailureTrends(ft)
        setResolutionConfidence(rc)
        setCoverage(cov)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchAll()
    const id = setInterval(fetchAll, 30000)
    return () => clearInterval(id)
  }, [designFilter, includeHeuristic, includeUnverified])

  const handleSearch = (e) => {
    e.preventDefault()
    fetchAll()
  }

  const uniqueTypes = [...new Set(failures.map(f => f.failure_type || f.category).filter(Boolean))]

  if (selectedFailure) {
    return <FailureDetail failure={selectedFailure} onBack={() => setSelectedFailure(null)} />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">Failure Atlas</h2>
        <div className="text-[10px] text-[#6B7280]">{failures.length} total entries</div>
      </div>

      <OverviewCards analytics={analytics} />
      <SeveritySummary failures={failures} />

      <div className="grid grid-cols-2 gap-4">
        <CommonFailures data={commonFailures} />
        <FixEffectiveness data={fixEffectiveness} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <QoRImprovements data={qorImprovements} />
        <ResolutionConfidence data={resolutionConfidence} />
      </div>

      <FailureTrends data={failureTrends} />
      <CoverageIntelligence data={coverage} />

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">All Failures</h3>
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <div className="flex items-center gap-2 mr-2">
              <label className="flex items-center gap-1 text-[10px] text-[#6B7280] cursor-pointer hover:text-abyss-ink transition-colors">
                <input
                  type="checkbox"
                  checked={includeHeuristic}
                  onChange={(e) => setIncludeHeuristic(e.target.checked)}
                  className="rounded border-stone-ridge text-meridian-gold focus:ring-meridian-gold"
                />
                Heuristic
              </label>
              <label className="flex items-center gap-1 text-[10px] text-[#6B7280] cursor-pointer hover:text-abyss-ink transition-colors">
                <input
                  type="checkbox"
                  checked={includeUnverified}
                  onChange={(e) => setIncludeUnverified(e.target.checked)}
                  className="rounded border-stone-ridge text-meridian-gold focus:ring-meridian-gold"
                />
                Unverified
              </label>
            </div>
            <div className="relative">
              <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-[#6B7280]" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search failures..."
                className="pl-6 pr-2 py-1 text-[10px] border border-stone-ridge rounded w-40"
              />
            </div>
            <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)} className="text-[10px] border border-stone-ridge rounded px-2 py-1">
              <option value="">All Levels</option>
              <option value="CRITICAL">Critical</option>
              <option value="ERROR">Error</option>
              <option value="WARNING">Warning</option>
              <option value="ADVISORY">Advisory</option>
              <option value="INFO">Info</option>
            </select>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="text-[10px] border border-stone-ridge rounded px-2 py-1">
              <option value="">All Types</option>
              {uniqueTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <button type="submit" className="text-[10px] bg-meridian-gold text-abyss-ink px-3 py-1 rounded font-medium hover:bg-yellow-500">Filter</button>
          </form>
        </div>
        {loading ? (
          <p className="text-xs text-[#6B7280] py-4">Loading failures...</p>
        ) : (
          <FailureList failures={sortedFailures} onSelect={setSelectedFailure} />
        )}
      </div>
    </div>
  )
}
