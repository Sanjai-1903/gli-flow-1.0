import { useState, useEffect } from "react"
import { BarChart2, TrendingUp, Clock, Activity } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

function QorScorePill({ score }) {
  let c = "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium font-[Work_Sans] "
  if (score >= 0.8) c += "bg-[#FEF9E7] text-[#92751A]"
  else if (score >= 0.65) c += "bg-[#FFF7ED] text-[#C2410C]"
  else c += "bg-[#FEF2F2] text-[#C2410C] font-bold"
  return <span className={c}>{score.toFixed(2)}</span>
}

function StatusBadge({ status }) {
  const s = {
    SUCCESS: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    COMPLETED: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    FAILED: "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]",
    RUNNING: "bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]",
  }
  const cls = s[status] || "bg-[#F3F2ED] text-[#6B7280] border-[#E5E4E0]"
  return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full border text-[10px] font-bold font-[Work_Sans] ${cls}`}>{status}</span>
}

export default function QoRAnalyticsPage({ onSelectRun }) {
  const [runs, setRuns] = useState([])
  const [releases, setReleases] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/runs?limit=10000`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/releases`).then(r => r.ok ? r.json() : []),
    ]).then(([runsData, releasesData]) => {
      setRuns(runsData)
      setReleases(releasesData)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading QoR analytics...</div>

  const totalRuns = runs.length
  const scored = runs.filter(r => r.qor_score != null)
  const avgQor = scored.length > 0 ? scored.reduce((s, r) => s + (r.qor_score ?? 0), 0) / scored.length : 0
  const best = scored.length > 0 ? scored.reduce((a, b) => ((a.qor_score ?? 0) > (b.qor_score ?? 0) ? a : b), scored[0]) : null
  const worst = scored.length > 0 ? scored.reduce((a, b) => ((a.qor_score ?? 0) < (b.qor_score ?? 0) ? a : b), scored[0]) : null

  const trendData = [...runs].reverse().map(r => ({
    date: r.timestamp ? r.timestamp.slice(5, 16).replace("T", " ") : "",
    score: r.qor_score ?? 0,
    wns: r.wns ?? 0,
    tns: r.tns ?? 0,
    util: r.utilization ?? 0,
  }))

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">QoR Analytics</h1>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><BarChart2 size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Average QoR</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{avgQor.toFixed(2)}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Across {scored.length} runs</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><TrendingUp size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Best Run</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{best ? best.qor_score?.toFixed(2) : "—"}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{best ? best.run_id.slice(0, 20) : "N/A"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FEF2F2] flex items-center justify-center mb-3"><Clock size={16} color="#C2410C" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Worst Run</p>
          <p className="text-[28px] text-topography-rust font-semibold font-[Eczar]">{worst ? worst.qor_score?.toFixed(2) : "—"}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{worst ? worst.run_id.slice(0, 20) : "N/A"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FDF4FF] flex items-center justify-center mb-3"><Activity size={16} color="#A855F7" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total Runs</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{totalRuns}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{scored.length} with QoR scores</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">QoR Score Trend</h3>
          {trendData.length < 2 ? (
            <div className="h-48 flex items-center justify-center text-[#6B7280] text-xs font-[Work_Sans]">Not enough data for trend</div>
          ) : (
            <div className="space-y-0.5">
              {trendData.map((d, i) => (
                <div key={i} className="flex items-center gap-3 text-[11px] font-[Work_Sans]">
                  <span className="text-[#6B7280] w-28 truncate">{d.date}</span>
                  <div className="flex-1 h-4 bg-[#F3F2ED] rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-meridian-gold" style={{ width: `${d.score * 100}%` }} />
                  </div>
                  <span className="w-12 text-right font-medium">{d.score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Top Runs by QoR</h3>
          {releases.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-[#6B7280] text-xs font-[Work_Sans]">No runs with QoR scores</div>
          ) : (
            <table className="w-full font-[Work_Sans]">
              <thead>
                <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">Run ID</th>
                  <th className="text-left pb-2 font-medium">Design</th>
                  <th className="text-left pb-2 font-medium">Score</th>
                  <th className="text-left pb-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {releases.slice(0, 10).map((r, i) => (
                  <tr key={r.run_id} className="text-xs border-b border-stone-ridge/50 cursor-pointer hover:bg-[#F3F2ED]" onClick={() => onSelectRun?.(r.run_id)}>
                    <td className="py-2 pr-2 font-medium text-abyss-ink">{r.run_id.slice(0, 16)}</td>
                    <td className="py-2 pr-2 text-[#6B7280]">{r.design_name}</td>
                    <td className="py-2 pr-2"><QorScorePill score={r.qor_score ?? 0} /></td>
                    <td className="py-2"><StatusBadge status={r.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">All Runs</h3>
        <div className="overflow-x-auto">
          <table className="w-full font-[Work_Sans]">
            <thead>
              <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                <th className="text-left pb-2 font-medium">Run ID</th>
                <th className="text-left pb-2 font-medium">Design</th>
                <th className="text-left pb-2 font-medium">Status</th>
                <th className="text-left pb-2 font-medium">QoR</th>
                <th className="text-left pb-2 font-medium">WNS</th>
                <th className="text-left pb-2 font-medium">TNS</th>
                <th className="text-left pb-2 font-medium">Util</th>
                <th className="text-left pb-2 font-medium">Runtime</th>
                <th className="text-left pb-2 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {runs.slice(0, 50).map((r, i) => (
                <tr key={r.run_id} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""} cursor-pointer hover:bg-[#F3F2ED]`} onClick={() => onSelectRun?.(r.run_id)}>
                  <td className="py-2 pr-2 font-medium text-abyss-ink">{r.run_id.slice(0, 16)}</td>
                  <td className="py-2 pr-2 text-[#6B7280]">{r.design_name}</td>
                  <td className="py-2 pr-2"><StatusBadge status={r.status} /></td>
                  <td className="py-2 pr-2"><QorScorePill score={r.qor_score ?? 0} /></td>
                  <td className="py-2 pr-2 text-[#6B7280]">{r.wns != null ? r.wns.toFixed(3) : "—"}</td>
                  <td className="py-2 pr-2 text-[#6B7280]">{r.tns != null ? r.tns.toFixed(1) : "—"}</td>
                  <td className="py-2 pr-2 text-[#6B7280]">{r.utilization != null ? `${r.utilization}%` : "—"}</td>
                  <td className="py-2 pr-2 text-[#6B7280]">{r.runtime_sec ? `${Math.floor(r.runtime_sec / 60)}m ${Math.round(r.runtime_sec % 60)}s` : "—"}</td>
                  <td className="py-2 text-[#6B7280] whitespace-nowrap">{r.timestamp ? r.timestamp.slice(0, 16).replace("T", " ") : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
