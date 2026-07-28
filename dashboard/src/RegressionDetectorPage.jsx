import { useState, useEffect } from "react"
import { AlertTriangle, ArrowUp, ArrowDown, Minus, Zap, Search, ChevronDown } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function RegressionDetectorPage({ onSelectRun }) {
  const [runs, setRuns] = useState([])
  const [regressions, setRegressions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/runs?limit=10000`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/regressions`).then(r => r.ok ? r.json() : []),
    ]).then(([runsData, regsData]) => {
      setRuns(runsData)
      setRegressions(regsData)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading regression data...</div>

  const completedRuns = runs.filter(r => r.status === "SUCCESS" || r.status === "COMPLETED" || r.status === "FAILED")
  const sortedRuns = [...completedRuns].sort((a, b) => {
    const da = a.timestamp || ""
    const db = b.timestamp || ""
    return db.localeCompare(da)
  })

  function computeDiff(after, before) {
    if (!after || !before) return null
    return {
      wns: { before: before.wns, after: after.wns, delta: (after.wns ?? 0) - (before.wns ?? 0) },
      tns: { before: before.tns, after: after.tns, delta: (after.tns ?? 0) - (before.tns ?? 0) },
      qor_score: { before: before.qor_score, after: after.qor_score, delta: (after.qor_score ?? 0) - (before.qor_score ?? 0) },
      utilization: { before: before.utilization, after: after.utilization, delta: (after.utilization ?? 0) - (before.utilization ?? 0) },
      runtime_sec: { before: before.runtime_sec, after: after.runtime_sec, delta: (after.runtime_sec ?? 0) - (before.runtime_sec ?? 0) },
    }
  }

  function isRegression(diff) {
    if (!diff) return false
    return (diff.qor_score.delta < -0.05) ||
           (diff.wns.delta < -0.05) ||
           (diff.utilization.delta > 5)
  }

  function DeltaBadge({ delta, unit, higherIsBetter }) {
    if (delta == null || delta === 0) return <span className="text-[#6B7280] flex items-center gap-0.5"><Minus size={10} />0{unit}</span>
    const isGood = higherIsBetter ? delta > 0 : delta < 0
    if (isGood) return <span className="text-[#16A34A] flex items-center gap-0.5"><ArrowUp size={10} />{delta > 0 ? "+" : ""}{delta.toFixed(3)}{unit}</span>
    return <span className="text-[#C2410C] flex items-center gap-0.5"><ArrowDown size={10} />{delta > 0 ? "+" : ""}{delta.toFixed(3)}{unit}</span>
  }

  const adjacentDiffs = []
  for (let i = 0; i < sortedRuns.length - 1; i++) {
    const diff = computeDiff(sortedRuns[i], sortedRuns[i + 1])
    if (diff) {
      adjacentDiffs.push({
        after: sortedRuns[i],
        before: sortedRuns[i + 1],
        diff,
        isRegression: isRegression(diff),
      })
    }
  }

  const detected = adjacentDiffs.filter(d => d.isRegression)

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Regression Detector</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FEF2F2] flex items-center justify-center mb-3"><AlertTriangle size={16} color="#C2410C" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Regressions Detected</p>
          <p className="text-[28px] text-topography-rust font-semibold font-[Eczar]">{detected.length}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Across {adjacentDiffs.length} comparisons</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Zap size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total comparisons</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{adjacentDiffs.length}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Adjacent run pairs</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FDF4FF] flex items-center justify-center mb-3"><Search size={16} color="#A855F7" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Failure Atlas Events</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{regressions.length}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">First-occurrence regressions</p>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Run-to-Run Regression Diffs</h3>
        {adjacentDiffs.length === 0 ? (
          <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">Not enough completed runs for comparison</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full font-[Work_Sans]">
              <thead>
                <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">Regression</th>
                  <th className="text-left pb-2 font-medium">After</th>
                  <th className="text-left pb-2 font-medium">Before</th>
                  <th className="text-left pb-2 font-medium">QoR</th>
                  <th className="text-left pb-2 font-medium">WNS</th>
                  <th className="text-left pb-2 font-medium">TNS</th>
                  <th className="text-left pb-2 font-medium">Util</th>
                  <th className="text-left pb-2 font-medium">Runtime</th>
                </tr>
              </thead>
              <tbody>
                {adjacentDiffs.slice(0, 30).map((d, i) => (
                  <tr key={i} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""} ${d.isRegression ? "bg-[#FEF2F2]/30" : ""}`}>
                    <td className="py-2 pr-2">
                      {d.isRegression
                        ? <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#FEF2F2] text-[#C2410C]">REGRESSION</span>
                        : <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#F0FDF4] text-[#16A34A]">OK</span>
                      }
                    </td>
                    <td className="py-2 pr-2 cursor-pointer hover:text-meridian-gold" onClick={() => onSelectRun?.(d.after.run_id)}>
                      <span className="font-medium text-abyss-ink">{d.after.run_id.slice(0, 14)}</span>
                      <span className="text-[#6B7280] ml-1">{d.after.design_name}</span>
                    </td>
                    <td className="py-2 pr-2 cursor-pointer hover:text-meridian-gold" onClick={() => onSelectRun?.(d.before.run_id)}>
                      <span className="text-[#6B7280]">{d.before.run_id.slice(0, 14)}</span>
                    </td>
                    <td className="py-2 pr-2"><DeltaBadge delta={d.diff.qor_score.delta} unit="" higherIsBetter={true} /></td>
                    <td className="py-2 pr-2"><DeltaBadge delta={d.diff.wns.delta} unit="ns" higherIsBetter={true} /></td>
                    <td className="py-2 pr-2"><DeltaBadge delta={d.diff.tns.delta} unit="ns" higherIsBetter={true} /></td>
                    <td className="py-2 pr-2"><DeltaBadge delta={d.diff.utilization.delta} unit="%" higherIsBetter={false} /></td>
                    <td className="py-2"><DeltaBadge delta={d.diff.runtime_sec.delta} unit="s" higherIsBetter={false} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Failure Atlas Regressions</h3>
        {regressions.length === 0 ? (
          <div className="py-4 text-center text-[#6B7280] text-xs font-[Work_Sans]">No regression events recorded</div>
        ) : (
          <div className="space-y-2">
            {regressions.map((r, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded border border-stone-ridge hover:bg-[#FAFAF8] cursor-pointer" onClick={() => onSelectRun?.(r.run_id)}>
                <AlertTriangle size={14} className="text-topography-rust flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-abyss-ink truncate">{r.title || r.failure_type}</p>
                  <p className="text-[10px] text-[#6B7280]">{r.run_id?.slice(0, 20)} · {r.detected_at}</p>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#FEF2F2] text-[#C2410C] font-medium">{r.severity}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
