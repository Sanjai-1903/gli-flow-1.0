import { useState, useEffect } from "react"
import { ArrowLeft, MoreVertical } from "lucide-react"
import RunStar from "./components/RunStar"

const API_BASE = import.meta.env.VITE_API_URL || ""

function QorScorePill({ score }) {
  let classes = "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium font-[Work_Sans] "
  if (score >= 0.80) {
    classes += "bg-[#FEF9E7] text-[#92751A]"
  } else if (score >= 0.65) {
    classes += "bg-[#FFF7ED] text-[#C2410C]"
  } else {
    classes += "bg-[#FEF2F2] text-[#C2410C] font-bold"
  }
  return <span className={classes}>{score.toFixed(2)}</span>
}

function StatusBadge({ status }) {
  const styles = {
    SUCCESS: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    COMPLETED: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    FAILED: "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]",
    TIMEOUT: "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA]",
    PARTIAL: "bg-[#FEFCE8] text-[#A16207] border-[#FDE68A]",
    RUNNING: "bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]",
    REGRESSION: "bg-[#FEF2F2] text-[#C2410C] border-[#FECACA]",
  }
  const cls = styles[status] || "bg-[#F3F2ED] text-[#6B7280] border-[#E5E4E0]"
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full border text-[10px] font-bold font-[Work_Sans] ${cls}`}>
      {status}
    </span>
  )
}

export default function RunsPage({ onBack, onSelectRun, importantOnly = false }) {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/runs?limit=10000&important=${importantOnly}`)
      .then(r => { if (!r.ok) throw new Error(`/runs ${r.status}`); return r.json() })
      .then(data => { setRuns(data); setLoading(false) })
      .catch(e => { console.error("Failed to load runs:", e); setLoading(false) })
  }, [importantOnly])

  const handleToggleImportant = (runId, isImportant) => {
    fetch(`${API_BASE}/runs/${runId}/important`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_important: isImportant }),
    })
      .then(r => r.ok ? setRuns(prev => prev.map(r => r.run_id === runId ? { ...r, is_important: isImportant ? 1 : 0 } : r)) : null)
      .catch(e => console.error("Failed to toggle importance:", e))
  }

  const rows = runs.map(r => ({
    runId: r.run_id,
    design: r.design_name,
    flow: "GLI-FLOW",
    status: r.status === "COMPLETED" ? "SUCCESS" : r.status,
    qorScore: r.qor_score ?? 0,
    runtime: r.runtime_sec ? `${Math.floor(r.runtime_sec / 60)}m ${Math.round(r.runtime_sec % 60)}s` : "—",
    date: r.timestamp ? r.timestamp.slice(0, 16).replace("T", " ") : "",
    isImportant: r.is_important === 1
  }))

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="flex items-center gap-1 text-[11px] text-meridian-gold hover:underline font-[Work_Sans] cursor-pointer">
            <ArrowLeft size={14} /> Back to Dashboard
          </button>
          <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">{importantOnly ? "Important Runs" : "All Runs"}</h1>
        </div>
        <span className="text-[11px] text-[#6B7280] font-[Work_Sans]">{runs.length} total runs</span>
      </div>

      {loading ? (
        <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading runs...</div>
      ) : rows.length === 0 ? (
        <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">No runs yet</div>
      ) : (
        <div className="bg-white border border-stone-ridge rounded-lg overflow-hidden">
          <table className="w-full font-[Work_Sans]">
            <thead>
              <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge bg-[#FAFAF8]">
                <th className="px-4 py-3"></th>
                <th className="text-left px-4 py-3 font-medium">Run ID</th>
                <th className="text-left px-4 py-3 font-medium">Design</th>
                <th className="text-left px-4 py-3 font-medium">Flow</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">QoR Score</th>
                <th className="text-left px-4 py-3 font-medium">Runtime</th>
                <th className="text-left px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((run, i) => (
                <tr key={run.runId}
                    className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""} cursor-pointer hover:bg-[#F3F2ED]`}
                    onClick={() => onSelectRun(run.runId)}>
                  <td className="px-4 py-3">
                    <RunStar isImportant={run.isImportant} onClick={(v) => handleToggleImportant(run.runId, v)} />
                  </td>
                  <td className="px-4 py-3 font-medium text-abyss-ink">{run.runId}</td>
                  <td className="px-4 py-3 text-[#6B7280]">{run.design}</td>
                  <td className="px-4 py-3 text-[#6B7280]">{run.flow}</td>
                  <td className="px-4 py-3"><StatusBadge status={run.status} /></td>
                  <td className="px-4 py-3"><QorScorePill score={run.qorScore} /></td>
                  <td className="px-4 py-3 text-[#6B7280]">{run.runtime}</td>
                  <td className="px-4 py-3 text-[#6B7280] whitespace-nowrap">{run.date}</td>
                  <td className="px-4 py-3"><MoreVertical size={14} className="text-[#6B7280]" /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
