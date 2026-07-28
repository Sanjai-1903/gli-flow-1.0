import { useState, useEffect } from "react"
import { ArrowLeft, Clock, AlertTriangle, CheckCircle, XCircle, Download, ChevronDown, ChevronRight, ExternalLink, FolderOpen } from "lucide-react"
import ArtifactViewer from "./ArtifactViewer"
import AIAvailabilityGuard from "./components/AIAvailabilityGuard"

const API_BASE = import.meta.env.VITE_API_URL || ""

function TabButton({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 text-xs font-[Work_Sans] rounded-t border-b-2 transition-colors ${
        active ? "border-meridian-gold text-abyss-ink font-semibold" : "border-transparent text-[#6B7280] hover:text-abyss-ink"
      }`}
    >
      {label}
    </button>
  )
}

function SummaryTab({ run }) {
  const implColor = run.implementation_status === "SUCCESS" ? "text-green-600" : "text-red-600"
  const _signoffColor = (s) => s === "PASS" ? "text-green-600" : s === "CONDITIONAL_PASS" ? "text-amber-600" : s === "INCOMPLETE" ? "text-orange-600" : s === "FAIL" ? "text-red-600" : "text-[#6B7280]"
  const signoffColor = _signoffColor(run.signoff_status)
  const tapeoutColor = run.tapeout_ready ? "text-green-600" : "text-red-600"
  const [trustScore, setTrustScore] = useState(null)

  useEffect(() => {
    if (!run.run_id) return
    fetch(`${API_BASE}/runs/${run.run_id}/trust-score`)
      .then(r => r.ok ? r.json() : null)
      .then(setTrustScore)
  }, [run.run_id])

  return (
    <div>
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Status</p>
          <p className="text-sm font-semibold mt-1">{run.status || "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Trust Score</p>
          <p className="text-sm font-semibold mt-1">
            {trustScore ? `${(trustScore.trust_ratio * 100).toFixed(0)}%` : "—"}
          </p>
          <p className="text-[9px] text-[#6B7280] mt-0.5">
            {trustScore ? `${trustScore.verified_count} V / ${trustScore.heuristic_count} H / ${trustScore.unverified_count} U` : "—"}
          </p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">QoR Score</p>
          <p className="text-sm font-semibold mt-1">{run.qor_score?.toFixed(2) ?? "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Current Stage</p>
          <p className="text-sm font-semibold mt-1">{run.current_stage || "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Implementation</p>
          <p className={`text-sm font-semibold mt-1 ${implColor}`}>{run.implementation_status || "—"}</p>
          <p className="text-[10px] text-[#6B7280] mt-0.5">{run.implementation_score?.toFixed(3) ?? "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Signoff</p>
          <p className={`text-sm font-semibold mt-1 ${signoffColor}`}>{run.signoff_status || "—"}</p>
          <p className="text-[10px] text-[#6B7280] mt-0.5">{run.signoff_score != null ? run.signoff_status : "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Tapeout Ready</p>
          <p className={`text-sm font-semibold mt-1 ${tapeoutColor}`}>{run.tapeout_ready ? "YES" : "NO"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">WNS</p>
          <p className={`text-sm font-semibold mt-1 ${(run.wns ?? 0) < 0 ? "text-red-600" : "text-green-600"}`}>{run.wns?.toFixed(3) ?? "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">TNS</p>
          <p className={`text-sm font-semibold mt-1 ${(run.tns ?? 0) < 0 ? "text-red-600" : "text-green-600"}`}>{run.tns?.toFixed(3) ?? "—"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Runtime</p>
          <p className="text-sm font-semibold mt-1">{run.runtime_sec ? `${run.runtime_sec}s` : "—"}</p>
        </div>
      </div>
      {run.root_cause_summary && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <p className="text-[10px] font-semibold text-amber-800 mb-1">Root Cause Summary</p>
          <p className="text-[10px] text-amber-700">{run.root_cause_summary}</p>
        </div>
      )}
    </div>
  )
}

function TimingTab({ run }) {
  const telemetry = run.telemetry || {}
  const metrics = telemetry.metrics || {}
  return (
    <div className="space-y-3">
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h4 className="text-xs font-semibold mb-3">Setup Timing</h4>
        <div className="grid grid-cols-3 gap-4">
          <div><p className="text-[10px] text-[#6B7280]">WNS</p><p className="text-sm font-semibold">{(run.wns ?? metrics.wns)?.toFixed(3) ?? "—"}</p></div>
          <div><p className="text-[10px] text-[#6B7280]">TNS</p><p className="text-sm font-semibold">{(run.tns ?? metrics.tns)?.toFixed(3) ?? "—"}</p></div>
          <div><p className="text-[10px] text-[#6B7280]">Fmax</p><p className="text-sm font-semibold">{metrics.fmax_mhz ? `${metrics.fmax_mhz} MHz` : "—"}</p></div>
        </div>
      </div>
      {run.sta_corners && run.sta_corners.length > 0 && (
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <h4 className="text-xs font-semibold mb-3">Multi-Corner STA</h4>
          <div className="space-y-2">
            {run.sta_corners.map((c, i) => (
              <div key={i} className="flex items-center gap-4 text-xs">
                <span className="font-medium w-20">{c.corner?.name || "corner"}</span>
                <span className={c.success ? "text-green-600" : "text-red-600"}>{c.success ? "PASS" : "FAIL"}</span>
                <span>Setup WNS: {c.setup_wns?.toFixed(3)}</span>
                <span>Setup TNS: {c.setup_tns?.toFixed(3)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function AreaPowerTab({ run }) {
  const telemetry = run.telemetry || {}
  const metrics = telemetry.metrics || {}
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h4 className="text-xs font-semibold mb-3">Area</h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-[#6B7280]">Utilization</span><span>{run.utilization ?? metrics.utilization ?? "—"}%</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Cell Count</span><span>{run.cell_count ?? metrics.cell_count ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Die Area</span><span>{metrics.die_area_um2 ? `${metrics.die_area_um2.toFixed(2)} µm²` : "—"}</span></div>
        </div>
      </div>
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h4 className="text-xs font-semibold mb-3">Power</h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-[#6B7280]">Total Power</span><span>{metrics.total_power_mw ? `${metrics.total_power_mw.toFixed(2)} mW` : "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Internal</span><span>{metrics.internal_power_mw ? `${metrics.internal_power_mw.toFixed(2)} mW` : "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Switching</span><span>{metrics.switching_power_mw ? `${metrics.switching_power_mw.toFixed(2)} mW` : "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Leakage</span><span>{metrics.leakage_power_mw ? `${metrics.leakage_power_mw.toFixed(4)} mW` : "—"}</span></div>
        </div>
      </div>
    </div>
  )
}

function ToolAgreementBadge({ agreement }) {
  if (!agreement || agreement === "NO_ANALYSIS") return null
  const colors = {
    CONSISTENT_PASS: "bg-green-100 text-green-700 border-green-200",
    CONSISTENT_FAIL: "bg-red-100 text-red-700 border-red-200",
    TOOL_DISAGREEMENT: "bg-orange-100 text-orange-700 border-orange-200",
  }
  const cls = colors[agreement] || "bg-gray-100 text-gray-700 border-gray-200"
  return <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${cls}`}>{agreement.replace("_", " ")}</span>
}

function DrcLvsTab({ run }) {
  const drcLvs = run.drc_lvs || {}
  const drc = drcLvs.drc || {}
  const lvs = drcLvs.lvs || {}
  const analysis = run.drc_analysis || {}
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h4 className="text-xs font-semibold mb-3 flex items-center gap-2">
          DRC {drc.is_clean ? <CheckCircle size={14} className="text-green-600" /> : <XCircle size={14} className="text-red-600" />}
          {analysis.tool_agreement && <ToolAgreementBadge agreement={analysis.tool_agreement} />}
        </h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-[#6B7280]">Total Violations</span><span>{drc.total_violations ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Clean</span><span>{drc.is_clean ? "Yes" : "No"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Magic Violations</span><span>{analysis.magic_violations ?? drc.magic_violations ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">KLayout Violations</span><span>{analysis.klayout_violations ?? drc.klayout_violations ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Runtime</span><span>{drc.runtime_seconds ? `${drc.runtime_seconds.toFixed(1)}s` : "—"}</span></div>
        </div>
        {analysis.tool_agreement === "TOOL_DISAGREEMENT" && (
          <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded">
            <p className="text-[10px] font-medium text-orange-700">Tool Disagreement Detected</p>
            <p className="text-[10px] text-orange-600">Magic and KLayout report different violation counts. Cross-tool DRC incident recorded in Failure Atlas.</p>
            {analysis.incident_id && (
              <p className="text-[10px] text-[#6B7280] mt-1">Incident: <span className="font-mono">{analysis.incident_id}</span></p>
            )}
          </div>
        )}
        {drc.by_rule && Object.keys(drc.by_rule).length > 0 && (
          <div className="mt-3">
            <p className="text-[10px] text-[#6B7280] mb-1">By Rule:</p>
            {Object.entries(drc.by_rule).map(([rule, count]) => (
              <div key={rule} className="flex justify-between text-xs"><span>{rule}</span><span>{count}</span></div>
            ))}
          </div>
        )}
      </div>
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h4 className="text-xs font-semibold mb-3 flex items-center gap-2">
          LVS {lvs.is_clean ? <CheckCircle size={14} className="text-green-600" /> : <XCircle size={14} className="text-red-600" />}
        </h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-[#6B7280]">Result</span><span>{lvs.result || "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Unmatched Devices</span><span>{lvs.unmatched_devices ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Unmatched Nets</span><span>{lvs.unmatched_nets ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Shorts</span><span>{lvs.short_count ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Opens</span><span>{lvs.open_count ?? "—"}</span></div>
          <div className="flex justify-between"><span className="text-[#6B7280]">Runtime</span><span>{lvs.runtime_seconds ? `${lvs.runtime_seconds.toFixed(1)}s` : "—"}</span></div>
        </div>
      </div>
    </div>
  )
}

function LayoutImagesTab({ run }) {
  const images = ["final_all", "final_placement", "final_routing", "final_clocks", "final_ir_drop"]
  return (
    <div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 text-[10px] text-blue-700 flex items-center gap-2">
        <FolderOpen size={14} />
        For full artifact browsing (including all images), use the <strong>Artifacts</strong> tab above.
      </div>
      <div className="grid grid-cols-2 gap-4">
        {images.map((name) => (
          <div key={name} className="bg-white border border-stone-ridge rounded-lg p-3">
            <p className="text-[10px] font-[Work_Sans] text-[#6B7280] mb-2">{name}</p>
            <img
              src={`${API_BASE}/runs/${run.run_id}/image/${name}`}
              alt={name}
              className="w-full rounded border border-stone-ridge"
              onError={(e) => {
                console.warn(`Layout image not found: ${name} for run ${run.run_id}`)
                e.target.style.display = "none"
              }}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

function ReportsTab({ run }) {
  const reportTypes = ["6_finish", "metrics", "synth_stat"]
  return (
    <div className="space-y-3">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-[10px] text-blue-700 flex items-center gap-2">
        <FolderOpen size={14} />
        Browse all reports, logs, and artifacts in the <strong>Artifacts</strong> tab above.
      </div>
      {reportTypes.map((name) => (
        <div key={name} className="bg-white border border-stone-ridge rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-semibold">{name}</h4>
            <a
              href={`${API_BASE}/runs/${run.run_id}/report/${name}`}
              target="_blank"
              rel="noreferrer"
              className="text-[10px] text-meridian-gold flex items-center gap-1"
            >
              <Download size={12} /> View
            </a>
          </div>
        </div>
      ))}
    </div>
  )
}

function FailureAtlasTab({ run, onNavigateToArtifact }) {
  const [failures, setFailures] = useState(null)
  const [expanded, setExpanded] = useState({})
  const [resolutionForm, setResolutionForm] = useState(null)
  const [includeHeuristic, setIncludeHeuristic] = useState(false)
  const [includeUnverified, setIncludeUnverified] = useState(false)

  useEffect(() => {
    if (!run?.run_id) return
    const doFetch = () => {
      const params = new URLSearchParams()
      if (includeHeuristic) params.set("include_heuristic", "true")
      if (includeUnverified) params.set("include_unverified", "true")
      fetch(`${API_BASE}/runs/${run.run_id}/failures?${params}`)
        .then(r => r.ok ? r.json() : { results: [] })
        .then(data => Array.isArray(data) ? data : (data.results || []))
        .then(setFailures)
        .catch(() => setFailures([]))
    }
    doFetch()
    const id = setInterval(doFetch, 15000)
    return () => clearInterval(id)
  }, [run?.run_id, includeHeuristic, includeUnverified])

  const toggleExpand = (id) => setExpanded(p => ({ ...p, [id]: !p[id] }))

  const _severityLevel = (sev) => {
    const map = { INFO: "INFO", LOW: "ADVISORY", WARNING: "WARNING", MEDIUM: "WARNING",
      PERFORMANCE_DEGRADATION: "WARNING", FUNCTIONAL_RISK: "ERROR", HIGH: "ERROR",
      UNDER_REVIEW: "ERROR", TAPEOUT_BLOCKING: "CRITICAL" }
    return map[sev] || "WARNING"
  }
  const _severityOrder = { CRITICAL: 4, ERROR: 3, WARNING: 2, ADVISORY: 1, INFO: 0 }
  const _countByLevel = (entries) => {
    const counts = { CRITICAL: 0, ERROR: 0, WARNING: 0, ADVISORY: 0, INFO: 0 }
    entries.forEach(e => { const l = _severityLevel(e.severity); if (counts[l] != null) counts[l]++ })
    return counts
  }
  const severityColor = (sev) => {
    const level = _severityLevel(sev)
    if (level === "CRITICAL") return "text-red-600 bg-red-50"
    if (level === "ERROR") return "text-orange-600 bg-orange-50"
    if (level === "WARNING") return "text-yellow-600 bg-yellow-50"
    if (level === "ADVISORY") return "text-slate-600 bg-slate-50"
    if (level === "INFO") return "text-blue-600 bg-blue-50"
    return "text-gray-600 bg-gray-50"
  }

  const handleResolve = async (failureId) => {
    const payload = resolutionForm[failureId]
    if (!payload?.fix_type) return
    try {
      const resp = await fetch(`${API_BASE}/failures/${failureId}/resolution`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      if (resp.ok) {
        setFailures(f => f.map(fa => fa.id === failureId || fa.failure_id === failureId ? { ...fa, fix_applied: true, fix_type: payload.fix_type, fix_description: payload.fix_description } : fa))
        setResolutionForm(p => ({ ...p, [failureId]: null }))
      }
    } catch (e) {
      console.error("Resolution failed", e)
    }
  }

  if (failures === null) {
    return <div className="text-xs text-[#6B7280]">Loading failure detections...</div>
  }

  if (failures.length === 0) {
    return (
      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <h4 className="text-xs font-semibold mb-3 text-green-700 flex items-center gap-2"><CheckCircle size={14} /> No Failures Detected</h4>
        <p className="text-xs text-[#6B7280]">This run completed without any Failure Atlas detections.</p>
      </div>
    )
  }

  const backfilled = failures.every(f => f.domain === "PIPELINE" && f.category === "PIPELINE_FAILURE")

  const sorted = [...failures].sort((a, b) => {
    const oa = _severityOrder[_severityLevel(a.severity)] || 0
    const ob = _severityOrder[_severityLevel(b.severity)] || 0
    if (oa !== ob) return ob - oa
    return (b.detected_at || "").localeCompare(a.detected_at || "")
  })

  const counts = _countByLevel(failures)

  const signoffOk = run.implementation_status === "SUCCESS" && (run.signoff_status === "PASS" || run.signoff_status === "CONDITIONAL_PASS") && run.tapeout_ready
  const blockedBySignoff = run.implementation_status === "SUCCESS" && run.signoff_status === "FAIL"

  return (
    <div className="space-y-3">
      {signoffOk && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-[10px] text-green-800">
          Run passed signoff. Failure Atlas contains engineering observations and historical learning signals.
        </div>
      )}
      {blockedBySignoff && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-[10px] text-red-800">
          Run completed but signoff blockers remain.
        </div>
      )}
      {!signoffOk && !blockedBySignoff && run.implementation_status === "FAILED" && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-[10px] text-red-800">
          Run terminated before successful completion.
        </div>
      )}
      {backfilled && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-[10px] text-amber-800">
          This run completed before Failure Atlas was fully active. Entries shown below were backfilled from run metadata.
        </div>
      )}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h4 className="text-xs font-semibold flex items-center gap-2">
            <AlertTriangle size={14} className="text-orange-500" />
            Failure Atlas
          </h4>
          <div className="flex items-center gap-2 text-[10px]">
            {["CRITICAL", "ERROR", "WARNING", "ADVISORY", "INFO"].map(level => {
              const c = counts[level]
              if (!c) return null
              const colorMap = { CRITICAL: "text-red-600 bg-red-50", ERROR: "text-orange-600 bg-orange-50",
                WARNING: "text-yellow-600 bg-yellow-50", ADVISORY: "text-slate-600 bg-slate-50",
                INFO: "text-blue-600 bg-blue-50" }
              return <span key={level} className={`px-1.5 py-0.5 rounded font-medium ${colorMap[level]}`}>{level}: {c}</span>
            })}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1 text-[9px] text-[#6B7280] cursor-pointer hover:text-abyss-ink transition-colors">
            <input
              type="checkbox"
              checked={includeHeuristic}
              onChange={(e) => setIncludeHeuristic(e.target.checked)}
              className="rounded border-stone-ridge text-meridian-gold focus:ring-meridian-gold w-3 h-3"
            />
            Heuristic
          </label>
          <label className="flex items-center gap-1 text-[9px] text-[#6B7280] cursor-pointer hover:text-abyss-ink transition-colors">
            <input
              type="checkbox"
              checked={includeUnverified}
              onChange={(e) => setIncludeUnverified(e.target.checked)}
              className="rounded border-stone-ridge text-meridian-gold focus:ring-meridian-gold w-3 h-3"
            />
            Unverified
          </label>
        </div>
      </div>
      {sorted.map((fa) => {
        let ev = {}
        try { if (typeof fa.evidence === "string") { ev = JSON.parse(fa.evidence) } else if (fa.evidence) { ev = fa.evidence } } catch {}
        const stage = ev.stage || fa.detection_stage || "—"
        const isGeneric = !fa.title || fa.title === `Pipeline failed at stage ${stage}` || fa.title.startsWith("Run run_")
        const fid = fa.id || fa.failure_id
        return (
        <div key={fid} className={`bg-white border rounded-lg overflow-hidden ${fa.fix_applied ? "border-green-300" : "border-stone-ridge"}`}>
          <div className="flex items-start justify-between p-4 cursor-pointer hover:bg-[#FAFAF8]" onClick={() => toggleExpand(fid)}>
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {expanded[fid] ? <ChevronDown size={14} className="text-[#6B7280] flex-shrink-0" /> : <ChevronRight size={14} className="text-[#6B7280] flex-shrink-0" />}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${severityColor(fa.severity)}`}>{_severityLevel(fa.severity)}</span>
                  {ev.classification === "VALIDATED_TOOL_DISAGREEMENT" && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-purple-100 text-purple-700 border border-purple-200">Known Tool Disagreement</span>
                  )}
                  {stage !== "—" && <span className="text-[10px] text-[#6B7280]">· {stage}</span>}
                  {fa.fix_applied && <span className="text-[10px] text-green-600 font-medium flex items-center gap-1"><CheckCircle size={10} /> Fixed</span>}
                </div>
                {isGeneric ? (
                  <p className="text-xs text-[#6B7280] italic mt-0.5">{fa.title || "Pipeline execution failed"}</p>
                ) : (
                  <p className="text-xs font-medium text-[#991B1B] mt-0.5 leading-relaxed">{fa.title}</p>
                )}
              </div>
            </div>
            {fa.confidence != null && (
              <span className="text-[10px] text-[#6B7280] flex-shrink-0 ml-2">{(fa.confidence * 100).toFixed(0)}% confidence</span>
            )}
          </div>
          {!isGeneric && fa.description && fa.description !== fa.title && (
            <div className="px-4 pb-2 ml-5">
              <p className="text-[10px] text-[#6B7280] leading-relaxed">{fa.description}</p>
            </div>
          )}
          {expanded[fid] && (
            <div className="ml-5 mr-4 mb-4 space-y-3 border-t border-stone-ridge pt-3">
              {ev.error && !isGeneric && (
                <div className="p-2 bg-[#FFF7ED] border border-[#FED7AA] rounded">
                  <p className="text-[10px] font-semibold text-[#C2410C] mb-1">Diagnostic Details</p>
                  {ev.exit_code != null && <p className="text-[10px]"><span className="text-[#6B7280]">Exit Code:</span> <span className={`font-medium ${ev.exit_code === 0 ? "text-[#16A34A]" : "text-[#C2410C]"}`}>{ev.exit_code}</span></p>}
                  {ev.log_file && (
                    <p className="text-[10px]">
                      <span className="text-[#6B7280]">Log:</span>{" "}
                      <button
                        onClick={() => onNavigateToArtifact && onNavigateToArtifact(ev.log_file)}
                        className="font-mono text-meridian-gold hover:underline cursor-pointer"
                      >
                        {ev.log_file}
                      </button>
                    </p>
                  )}
                  {ev.command && <p className="text-[10px]"><span className="text-[#6B7280]">Command:</span> <span className="font-mono">{ev.command}</span></p>}
                  {ev.stderr && (
                    <details className="mt-1">
                      <summary className="text-[10px] text-[#C2410C] cursor-pointer font-medium">stderr</summary>
                      <pre className="text-[9px] text-[#6B7280] bg-[#FAFAF8] p-2 rounded mt-1 max-h-20 overflow-auto">{ev.stderr}</pre>
                    </details>
                  )}
                </div>
              )}
              {fa.recommended_fix && (() => {
                let fixItems = []
                if (Array.isArray(fa.recommended_fix)) {
                  fixItems = fa.recommended_fix
                } else if (fa.recommended_fix && typeof fa.recommended_fix === "object") {
                  fixItems = fa.recommended_fix.description ? [fa.recommended_fix.description] : []
                  if (Array.isArray(fa.recommended_fix.steps)) {
                    fixItems = [...fixItems, ...fa.recommended_fix.steps]
                  }
                }
                return fixItems.length > 0 ? (
                <div>
                  <p className="text-[10px] font-semibold text-abyss-ink mb-1">Industry Knowledge Base:</p>
                  <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
                    {fixItems.map((fix, i) => <li key={i}>{fix}</li>)}
                  </ul>
                </div>
                ) : null
              })()}
              {ev && typeof ev === "object" && Object.keys(ev).length > 0 && (
                <div>
                  <p className="text-[10px] font-semibold text-abyss-ink mb-1">
                    Evidence <span className="font-normal text-[#6B7280]">({Object.keys(ev).length} fields)</span>
                  </p>
                  {(ev.log_file || ev.file) && (
                    <div className="flex gap-1 mb-2">
                      {ev.log_file && (
                        <button
                          onClick={() => onNavigateToArtifact && onNavigateToArtifact(ev.log_file)}
                          className="text-[9px] bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-medium hover:bg-blue-100"
                        >
                          View {ev.log_file}
                        </button>
                      )}
                      {ev.file && ev.file !== ev.log_file && (
                        <button
                          onClick={() => onNavigateToArtifact && onNavigateToArtifact(ev.file)}
                          className="text-[9px] bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-medium hover:bg-blue-100"
                        >
                          View {ev.file}
                        </button>
                      )}
                    </div>
                  )}
                  <pre className="text-[9px] text-[#6B7280] bg-[#FAFAF8] p-2 rounded mt-1 overflow-auto max-h-24 border border-stone-ridge">
                    {JSON.stringify(ev, null, 2)}
                  </pre>
                </div>
              )}
              {fa.fix_type && (
                <div className="p-2 bg-green-50 rounded">
                  <p className="text-[10px] font-semibold text-green-700">Fix Applied:</p>
                  <p className="text-[10px] text-green-600">{fa.fix_type}{fa.fix_description ? ` - ${fa.fix_description}` : ""}</p>
                  {fa.fix_run_id && <p className="text-[10px] text-green-600">Run: {fa.fix_run_id}</p>}
                </div>
              )}
              {!fa.fix_applied && (
                <div>
                  <button
                    onClick={(e) => { e.stopPropagation(); setResolutionForm(p => ({ ...p, [fid]: p?.[fid] || { fix_type: "", fix_description: "", fix_run_id: "" } })) }}
                    className="text-[10px] text-meridian-gold hover:underline flex items-center gap-1"
                  >
                    <ExternalLink size={10} /> Link Resolution
                  </button>
                  {resolutionForm?.[fid] && (
                    <div className="mt-2 p-2 bg-[#FAFAF8] rounded space-y-2" onClick={(e) => e.stopPropagation()}>
                      <select
                        value={resolutionForm[fid].fix_type}
                        onChange={(e) => setResolutionForm(p => ({ ...p, [fid]: { ...p[fid], fix_type: e.target.value } }))}
                        className="w-full text-[10px] border border-stone-ridge rounded px-2 py-1"
                      >
                        <option value="">Select Resolution Type...</option>
                        <option value="pipeline_insertion">Pipeline Insertion</option>
                        <option value="retiming">Retiming</option>
                        <option value="floorplan_change">Floorplan Change</option>
                        <option value="macro_relocation">Macro Relocation</option>
                        <option value="clock_restructuring">Clock Restructuring</option>
                        <option value="buffer_insertion">Buffer Insertion</option>
                        <option value="constraint_update">Constraint Update</option>
                        <option value="utilization_reduction">Utilization Reduction</option>
                        <option value="placement_density_change">Placement Density Change</option>
                        <option value="routing_strategy_change">Routing Strategy Change</option>
                        <option value="cdc_fix">CDC Fix</option>
                        <option value="rtl_bug_fix">RTL Bug Fix</option>
                        <option value="sram_integration_fix">SRAM Integration Fix</option>
                        <option value="other">Other</option>
                      </select>
                      <input
                        type="text"
                        placeholder="Fix description"
                        value={resolutionForm[fid].fix_description}
                        onChange={(e) => setResolutionForm(p => ({ ...p, [fid]: { ...p[fid], fix_description: e.target.value } }))}
                        className="w-full text-[10px] border border-stone-ridge rounded px-2 py-1"
                      />
                      <input
                        type="text"
                        placeholder="Fix run ID"
                        value={resolutionForm[fid].fix_run_id}
                        onChange={(e) => setResolutionForm(p => ({ ...p, [fid]: { ...p[fid], fix_run_id: e.target.value } }))}
                        className="w-full text-[10px] border border-stone-ridge rounded px-2 py-1"
                      />
                      <button
                        onClick={(e) => { e.stopPropagation(); handleResolve(fid) }}
                        className="text-[10px] bg-meridian-gold text-abyss-ink px-3 py-1 rounded font-medium hover:bg-yellow-500"
                      >
                        Record Resolution
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )})}
    </div>
  )
}

function AiInvestigationTab({ run, onNavigateToArtifact }) {
  const [investigation, setInvestigation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchInvestigation = () => {
    if (!run?.run_id) return
    fetch(`${API_BASE}/runs/${run.run_id}/investigation`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        setInvestigation(data)
        setLoading(false)
      })
      .catch(() => { setLoading(false); setError("Failed to load") })
  }

  useEffect(() => {
    if (!run?.run_id) return
    setLoading(true)
    fetchInvestigation()
  }, [run?.run_id])

  const runInvestigation = () => {
    setLoading(true)
    setError(null)
    fetch(`${API_BASE}/runs/${run.run_id}/investigation`, { method: "POST" })
      .then(r => r.ok ? r.json() : r.json().then(e => { throw new Error(e.detail || "Investigation failed") }))
      .then(data => {
        setInvestigation(data)
        setLoading(false)
      })
      .catch(e => { setLoading(false); setError(e.message) })
  }

  if (loading && !investigation) {
    return <div className="text-xs text-[#6B7280]">Loading AI investigation...</div>
  }

  const hasResult = investigation && (investigation.investigation || investigation.status)
  const hasSuccessful = investigation?.investigation
  const failedAttempts = investigation?.failed_attempts || []
  const history = investigation?.history || []
  const hasBackup = investigation?.has_backup
  const wasPreserved = investigation?.preserved_existing

  return (
    <AIAvailabilityGuard>
      <div className="space-y-3">
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
        <p className="text-[10px] font-semibold text-amber-800 flex items-center gap-2">
          <AlertTriangle size={12} />
          AI Investigation — Experimental
        </p>
        <p className="text-[10px] text-amber-700 mt-1">
          AI-generated hypotheses. Not verified. Does not override signoff results.
          Root Cause Analysis remains the primary source of truth.
        </p>
      </div>

      {hasBackup && hasSuccessful && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
          <p className="text-[10px] text-blue-700 flex items-center gap-1">
            <CheckCircle size={10} /> Backup available — investigation can be recovered if overwritten.
          </p>
        </div>
      )}

      {wasPreserved && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-2">
          <p className="text-[10px] text-green-700 flex items-center gap-1">
            <CheckCircle size={10} /> Previous successful investigation preserved. Failed attempt recorded separately.
          </p>
        </div>
      )}

      {!hasResult && !loading && (
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="text-xs text-[#6B7280] mb-3">No investigation has been run for this run.</p>
          <button
            onClick={runInvestigation}
            disabled={loading}
            className="text-[10px] bg-yellow-500 text-abyss-ink px-3 py-1.5 rounded font-medium hover:bg-yellow-400 disabled:opacity-50"
          >
            {loading ? "Running investigation..." : "Run AI Investigation"}
          </button>
        </div>
      )}

      {loading && hasResult && (
        <div className="text-xs text-[#6B7280]">Running investigation...</div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-[10px] text-red-700">{error}</p>
        </div>
      )}

      {hasResult && !loading && (
        <div>
          {hasSuccessful && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={14} className="text-green-600" />
                <span className="text-[10px] font-semibold text-green-700 uppercase tracking-wider">Last Successful Investigation</span>
                {investigation.timestamp && (
                  <span className="text-[10px] text-[#6B7280]">{new Date(investigation.timestamp).toLocaleString()}</span>
                )}
              </div>

              <div className="space-y-3">
                <div className="bg-white border border-stone-ridge rounded-lg p-4">
                  <p className="text-[10px] font-[Work_Sans] text-[#6B7280] uppercase tracking-wider">Summary</p>
                  <p className="text-sm font-semibold mt-1">{investigation.investigation.summary || "—"}</p>
                </div>

                {investigation.investigation.facts && investigation.investigation.facts.length > 0 && (
                  <div className="bg-white border border-stone-ridge rounded-lg p-4">
                    <p className="text-[10px] font-semibold mb-2">Facts ({investigation.investigation.facts.length})</p>
                    <div className="space-y-2">
                      {investigation.investigation.facts.map((f, i) => (
                        <div key={i} className="text-xs">
                          <span className="text-[#6B7280]">•</span> {f.observation}
                          <span className="text-[10px] text-[#6B7280] ml-1">({f.source})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {investigation.investigation.possible_causes && investigation.investigation.possible_causes.length > 0 && (
                  <div className="bg-white border border-stone-ridge rounded-lg p-4">
                    <p className="text-[10px] font-semibold mb-2">Possible Causes ({investigation.investigation.possible_causes.length})</p>
                    <div className="space-y-2">
                      {investigation.investigation.possible_causes.map((c, i) => (
                        <div key={i} className="border border-stone-ridge rounded p-2 text-xs">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                              c.confidence === "HIGH" ? "bg-red-100 text-red-700" :
                              c.confidence === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
                              "bg-gray-100 text-gray-600"
                            }`}>{c.confidence}</span>
                            <span className="font-medium">{c.cause}</span>
                          </div>
                          <p className="text-[#6B7280]">{c.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {investigation.investigation.recommended_next_steps && investigation.investigation.recommended_next_steps.length > 0 && (
                  <div className="bg-white border border-stone-ridge rounded-lg p-4">
                    <p className="text-[10px] font-semibold mb-2">Recommended Next Steps</p>
                    <ul className="list-disc list-inside text-xs text-[#6B7280] space-y-1">
                      {investigation.investigation.recommended_next_steps.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {investigation.investigation.missing_information && investigation.investigation.missing_information.length > 0 && (
                  <div className="bg-white border border-stone-ridge rounded-lg p-4">
                    <p className="text-[10px] font-semibold mb-1">Missing Information</p>
                    <ul className="list-disc list-inside text-[10px] text-[#6B7280] space-y-0.5">
                      {investigation.investigation.missing_information.map((m, i) => (
                        <li key={i}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {investigation.investigation.disclaimer && (
                  <p className="text-[10px] text-[#6B7280] italic">{investigation.investigation.disclaimer}</p>
                )}
              </div>
            </div>
          )}

          {investigation.status && !hasSuccessful && (
            <div className="bg-white border border-stone-ridge rounded-lg p-4">
              <p className="text-xs">
                <span className="font-medium">Status:</span> {investigation.status}
              </p>
              {investigation.error && (
                <p className="text-xs text-red-600 mt-1">{investigation.error}</p>
              )}
              {!investigation.error && (
                <button
                  onClick={runInvestigation}
                  disabled={loading}
                  className="mt-3 text-[10px] bg-yellow-500 text-abyss-ink px-3 py-1.5 rounded font-medium hover:bg-yellow-400 disabled:opacity-50"
                >
                  {loading ? "Running..." : "Run AI Investigation"}
                </button>
              )}
            </div>
          )}

          {failedAttempts.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-3">
              <div className="flex items-center gap-2 mb-2">
                <XCircle size={14} className="text-red-600" />
                <span className="text-[10px] font-semibold text-red-700 uppercase tracking-wider">
                  Recent Failed Attempts ({failedAttempts.length})
                </span>
              </div>
              <div className="space-y-2">
                {failedAttempts.slice().reverse().map((attempt, i) => (
                  <div key={i} className="bg-white border border-red-100 rounded p-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-red-700">{attempt.status}</span>
                      <span className="text-[10px] text-[#6B7280]">
                        {attempt.timestamp ? new Date(attempt.timestamp).toLocaleString() : ""}
                      </span>
                    </div>
                    <p className="text-red-600 mt-1">{attempt.error}</p>
                    {attempt.latency_sec > 0 && (
                      <p className="text-[10px] text-[#6B7280] mt-1">Latency: {attempt.latency_sec}s</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {history.length > 1 && (
            <details className="mt-3">
              <summary className="text-[10px] text-[#6B7280] cursor-pointer hover:text-abyss-ink">
                Investigation History ({history.length} entries)
              </summary>
              <div className="mt-2 space-y-1">
                {history.slice().reverse().map((entry, i) => (
                  <div key={i} className="bg-white border border-stone-ridge rounded p-2 text-[10px] flex items-center justify-between">
                    <span className={entry.status === "EXPERIMENTAL" ? "text-green-700 font-medium" : "text-red-600"}>
                      {entry.status}
                    </span>
                    <span className="text-[#6B7280]">
                      {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : ""}
                    </span>
                  </div>
                ))}
              </div>
            </details>
          )}

          <div className="mt-3">
            <button
              onClick={runInvestigation}
              disabled={loading}
              className="text-[10px] bg-yellow-500 text-abyss-ink px-3 py-1.5 rounded font-medium hover:bg-yellow-400 disabled:opacity-50"
            >
              {loading ? "Running investigation..." : "Run AI Investigation"}
            </button>
          </div>
        </div>
      )}
      </div>
    </AIAvailabilityGuard>
  )
}

function RunComparisonTab({ run }) {
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [targetRunId, setTargetRunId] = useState("")
  const [runList, setRunList] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/runs?limit=50`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setRunList(data.filter(r => r.run_id !== run.run_id))
      })
      .catch(() => {})
  }, [run.run_id])

  const runComparison = () => {
    if (!targetRunId) return
    setLoading(true)
    setError(null)
    fetch(`${API_BASE}/runs/${run.run_id}/compare/${targetRunId}`)
      .then(r => r.ok ? r.json() : r.json().then(e => { throw new Error(e.detail || "Comparison failed") }))
      .then(data => {
        setComparison(data)
        setLoading(false)
      })
      .catch(e => { setLoading(false); setError(e.message) })
  }

  return (
    <div className="space-y-3">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-[10px] font-semibold text-blue-800 flex items-center gap-2">
          <CheckCircle size={12} />
          Run Comparison
        </p>
        <p className="text-[10px] text-blue-700 mt-1">
          Compare this run with another to identify what changed and why recovery succeeded.
        </p>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-4">
        <p className="text-[10px] font-semibold mb-2">Compare with another run</p>
        <div className="flex items-center gap-2">
          <select
            value={targetRunId}
            onChange={(e) => setTargetRunId(e.target.value)}
            className="text-[10px] border border-stone-ridge rounded px-2 py-1.5 flex-1"
          >
            <option value="">Select a run...</option>
            {runList.map(r => (
              <option key={r.run_id} value={r.run_id}>
                {r.run_id.slice(0, 16)}... ({r.status}) {r.design_name ? `- ${r.design_name}` : ""}
              </option>
            ))}
          </select>
          <button
            onClick={runComparison}
            disabled={!targetRunId || loading}
            className="text-[10px] bg-blue-600 text-white px-3 py-1.5 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Comparing..." : "Compare"}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-[10px] text-red-700">{error}</p>
        </div>
      )}

      {comparison && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-stone-ridge rounded-lg p-4">
              <p className="text-[10px] font-semibold text-[#6B7280] uppercase mb-2">{comparison.run_a.run_id.slice(0, 16)} ({comparison.run_a.status})</p>
              <p className="text-[10px] text-[#6B7280]">Before / Failed</p>
            </div>
            <div className="bg-white border border-stone-ridge rounded-lg p-4">
              <p className="text-[10px] font-semibold text-[#6B7280] uppercase mb-2">{comparison.run_b.run_id.slice(0, 16)} ({comparison.run_b.status})</p>
              <p className="text-[10px] text-[#6B7280]">After / Successful</p>
            </div>
          </div>

          {comparison.fields && Object.keys(comparison.fields).length > 0 && (
            <div className="bg-white border border-stone-ridge rounded-lg p-4">
              <p className="text-[10px] font-semibold mb-3">Field Changes</p>
              <table className="w-full text-[10px] text-left">
                <thead>
                  <tr className="text-[#6B7280] border-b border-stone-ridge">
                    <th className="pb-1.5">Field</th>
                    <th className="pb-1.5">Before</th>
                    <th className="pb-1.5">After</th>
                    <th className="pb-1.5">Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(comparison.fields).map(([field, data]) => (
                    <tr key={field} className="border-b border-stone-ridge/50">
                      <td className="py-1.5 font-medium">{field}</td>
                      <td className="py-1.5">{data.before}</td>
                      <td className="py-1.5">{data.after}</td>
                      <td className={`py-1.5 font-medium ${
                        data.delta > 0 ? "text-green-600" : data.delta < 0 ? "text-red-600" : ""
                      }`}>
                        {data.delta != null ? (data.delta > 0 ? "+" : "") + data.delta.toFixed(2) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {comparison.failure_diffs && comparison.failure_diffs.length > 0 && (
            <div className="bg-white border border-stone-ridge rounded-lg p-4">
              <p className="text-[10px] font-semibold mb-3">Failure Differences</p>
              <div className="space-y-2">
                {comparison.failure_diffs.map((diff, i) => (
                  <div key={i} className={`p-2 rounded text-[10px] ${
                    diff.type === "resolved" ? "bg-green-50 border border-green-200" :
                    diff.type === "new" ? "bg-red-50 border border-red-200" :
                    "bg-amber-50 border border-amber-200"
                  }`}>
                    <p className="font-medium mb-1">
                      {diff.type === "resolved" ? "✓ Resolved" : diff.type === "new" ? "✗ New" : "⟳ Persistent"}
                      {diff.failures.length > 0 && ` (${diff.failures.length})`}
                    </p>
                    {diff.failures.map((f, j) => (
                      <span key={j} className="inline-block mr-1 mb-0.5 text-[9px] bg-white/50 px-1 rounded">{f}</span>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}

          {comparison.qor_changes && Object.keys(comparison.qor_changes).length > 0 && (
            <div className="bg-white border border-stone-ridge rounded-lg p-4">
              <p className="text-[10px] font-semibold mb-3">QoR Changes</p>
              <table className="w-full text-[10px] text-left">
                <thead>
                  <tr className="text-[#6B7280] border-b border-stone-ridge">
                    <th className="pb-1.5">Metric</th>
                    <th className="pb-1.5">Before</th>
                    <th className="pb-1.5">After</th>
                    <th className="pb-1.5">Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(comparison.qor_changes).map(([field, data]) => (
                    <tr key={field} className="border-b border-stone-ridge/50">
                      <td className="py-1 font-medium">{field}</td>
                      <td className="py-1">{data.before}</td>
                      <td className="py-1">{data.after}</td>
                      <td className={`py-1 font-medium ${
                        data.delta > 0 ? "text-green-600" : data.delta < 0 ? "text-red-600" : ""
                      }`}>
                        {data.delta != null ? (data.delta > 0 ? "+" : "") + data.delta.toFixed(2) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function ReproducibilityTab({ run }) {
  const [manifest, setManifest] = useState(null)
  useEffect(() => {
    fetch(`${API_BASE}/runs/${run.run_id}/report/reproducibility.json`)
      .then(r => r.ok ? r.json() : null)
      .then(setManifest)
      .catch(() => setManifest(null))
  }, [run.run_id])

  if (!manifest) {
    return <div className="text-xs text-[#6B7280]">Reproducibility manifest not available.</div>
  }
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-4">
      <h4 className="text-xs font-semibold mb-3">Reproducibility Manifest</h4>
      <pre className="text-[10px] text-[#6B7280] overflow-auto max-h-80 whitespace-pre-wrap">{JSON.stringify(manifest, null, 2)}</pre>
    </div>
  )
}

function ArtifactsTab({ run, artifactViewerPath }) {
  const [viewerPath, setViewerPath] = useState(artifactViewerPath || null)
  useEffect(() => {
    if (artifactViewerPath) setViewerPath(artifactViewerPath)
  }, [artifactViewerPath])
  return (
    <ArtifactViewer
      runId={run.run_id}
      initialPath={viewerPath}
      onArtifactSelect={(path) => setViewerPath(path)}
    />
  )
}

const TABS = [
  { key: "summary", label: "Summary", component: SummaryTab },
  { key: "timing", label: "Timing", component: TimingTab },
  { key: "area_power", label: "Area & Power", component: AreaPowerTab },
  { key: "drc_lvs", label: "DRC/LVS", component: DrcLvsTab },
  { key: "images", label: "Layout Images", component: LayoutImagesTab },
  { key: "artifacts", label: "Artifacts", component: ArtifactsTab },
  { key: "failure_atlas", label: "Failure Atlas", component: FailureAtlasTab },
  { key: "reproducibility", label: "Reproducibility", component: ReproducibilityTab },
  { key: "ai_investigation", label: "AI Investigation", component: AiInvestigationTab },
  { key: "comparison", label: "Compare", component: RunComparisonTab },
]

export default function RunDetail({ runId, onBack, onNavigateToArtifact }) {
  const [run, setRun] = useState(null)
  const [activeTab, setActiveTab] = useState("summary")
  const [error, setError] = useState(null)
  const [artifactPath, setArtifactPath] = useState(null)

  const handleNavigateToArtifact = (path) => {
    setArtifactPath(path)
    setActiveTab("artifacts")
    if (onNavigateToArtifact) onNavigateToArtifact(path)
  }

  useEffect(() => {
    if (!runId) return
    fetch(`${API_BASE}/runs/${runId}`)
      .then(r => { if (!r.ok) throw new Error(`/${runId} ${r.status}`); return r.json() })
      .then(setRun)
      .catch(e => { console.error(e); setError(e.message) })
  }, [runId])

  if (error) {
    return (
      <div className="bg-white border border-stone-ridge rounded-lg p-6">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-meridian-gold mb-4"><ArrowLeft size={14} /> Back</button>
        <p className="text-sm text-red-600">Error loading run: {error}</p>
      </div>
    )
  }

  if (!run) {
    return (
      <div className="bg-white border border-stone-ridge rounded-lg p-6">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-meridian-gold mb-4"><ArrowLeft size={14} /> Back</button>
        <p className="text-xs text-[#6B7280]">Loading run details...</p>
      </div>
    )
  }

  const ActiveComponent = TABS.find(t => t.key === activeTab)?.component || SummaryTab
  const tabProps = { run, onNavigateToArtifact: handleNavigateToArtifact, artifactViewerPath: artifactPath }

  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="flex items-center gap-1 text-xs text-meridian-gold hover:underline"><ArrowLeft size={14} /> Back</button>
          <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">{run.run_id}</h2>
          {run.implementation_status && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${run.implementation_status === "SUCCESS" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>Execution: {run.implementation_status}</span>
          )}
          {run.signoff_status && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ml-1 ${run.signoff_status === "PASS" ? "bg-green-100 text-green-700" : run.signoff_status === "CONDITIONAL_PASS" ? "bg-amber-100 text-amber-700" : run.signoff_status === "INCOMPLETE" ? "bg-orange-100 text-orange-700" : run.signoff_status === "NOT_RUN" ? "bg-gray-100 text-gray-500" : "bg-red-100 text-red-700"}`}>Signoff: {run.signoff_status}</span>
          )}
          {run.tapeout_ready != null && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ml-1 ${run.tapeout_ready ? (run.signoff_status === "CONDITIONAL_PASS" ? "bg-amber-100 text-amber-700" : "bg-green-100 text-green-700") : "bg-red-100 text-red-700"}`}>Tapeout: {run.tapeout_ready ? "YES" : "NO"}</span>
          )}
        </div>
        <span className="text-[10px] text-[#6B7280]">{run.design_name}</span>
      </div>

      <div className="flex border-b border-stone-ridge mb-4">
        {TABS.map(tab => (
          <TabButton key={tab.key} label={tab.label} active={activeTab === tab.key} onClick={() => setActiveTab(tab.key)} />
        ))}
      </div>

      <ActiveComponent {...tabProps} />
    </div>
  )
}
