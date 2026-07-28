import { useState, useEffect } from "react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function TrendsReportsPage({ onSelectRun }) {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/runs?limit=10000`)
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        setRuns(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading trends...</div>

  const scored = runs.filter(r => r.qor_score != null)
  const completed = runs.filter(r => r.status === "SUCCESS" || r.status === "COMPLETED")
  const failed = runs.filter(r => r.status === "FAILED")

  const designs = [...new Set(runs.map(r => r.design_name).filter(Boolean))]

  const timeline = [...scored]
    .sort((a, b) => (a.timestamp || "").localeCompare(b.timestamp || ""))
    .map(r => ({
      label: r.timestamp ? r.timestamp.slice(5, 16).replace("T", " ") : r.run_id.slice(0, 14),
      qor: r.qor_score ?? 0,
      wns: r.wns,
      tns: r.tns,
      util: r.utilization,
      run_id: r.run_id,
    }))

  const successRate = runs.length > 0 ? ((completed.length / runs.length) * 100).toFixed(1) : "0.0"

  const topN = [...scored].sort((a, b) => (b.qor_score ?? 0) - (a.qor_score ?? 0)).slice(0, 5)

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Trends & Reports</h1>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Success Rate</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">{successRate}%</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{completed.length} of {runs.length} runs</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total Runs</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{runs.length}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{failed.length} failed</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Designs Tracked</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{designs.length}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{designs.join(", ") || "N/A"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Avg QoR</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{scored.length > 0 ? (scored.reduce((s, r) => s + (r.qor_score ?? 0), 0) / scored.length).toFixed(2) : "—"}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Across {scored.length} scored runs</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">QoR Timeline</h3>
          {timeline.length < 2 ? (
            <div className="h-48 flex items-center justify-center text-[#6B7280] text-xs font-[Work_Sans]">Not enough data</div>
          ) : (
            <div className="space-y-1">
              {timeline.map((d, i) => (
                <div key={i} className="flex items-center gap-3 text-[11px] font-[Work_Sans] cursor-pointer hover:bg-[#FAFAF8]" onClick={() => onSelectRun?.(d.run_id)}>
                  <span className="text-[#6B7280] w-24 truncate">{d.label}</span>
                  <div className="flex-1 h-5 bg-[#F3F2ED] rounded-full overflow-hidden flex">
                    <div className="h-full bg-meridian-gold rounded-l-full" style={{ width: `${d.qor * 100}%`, minWidth: d.qor > 0 ? "4px" : "0" }} />
                    <div className="h-full bg-[#FBBF24]/30" style={{ width: `${Math.max(0, d.qor > 0.7 ? 0 : (0.7 - d.qor) * 100)}%` }} />
                  </div>
                  <span className="w-12 text-right font-medium">{d.qor.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Top 5 Runs</h3>
          {topN.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-[#6B7280] text-xs font-[Work_Sans]">No scored runs</div>
          ) : (
            <table className="w-full font-[Work_Sans]">
              <thead>
                <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">#</th>
                  <th className="text-left pb-2 font-medium">Run ID</th>
                  <th className="text-left pb-2 font-medium">Design</th>
                  <th className="text-left pb-2 font-medium">QoR</th>
                  <th className="text-left pb-2 font-medium">WNS</th>
                  <th className="text-left pb-2 font-medium">TNS</th>
                </tr>
              </thead>
              <tbody>
                {topN.map((r, i) => (
                  <tr key={r.run_id} className="text-xs border-b border-stone-ridge/50 cursor-pointer hover:bg-[#FAFAF8]" onClick={() => onSelectRun?.(r.run_id)}>
                    <td className="py-2 pr-2 text-[#6B7280]">{i + 1}</td>
                    <td className="py-2 pr-2 font-medium text-abyss-ink">{r.run_id.slice(0, 14)}</td>
                    <td className="py-2 pr-2 text-[#6B7280]">{r.design_name}</td>
                    <td className="py-2 pr-2 font-medium">{(r.qor_score ?? 0).toFixed(3)}</td>
                    <td className="py-2 pr-2 text-[#6B7280]">{r.wns != null ? r.wns.toFixed(3) : "—"}</td>
                    <td className="py-2 text-[#6B7280]">{r.tns != null ? r.tns.toFixed(1) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">WNS / TNS / Utilization Trends</h3>
        <div className="overflow-x-auto">
          <table className="w-full font-[Work_Sans]">
            <thead>
              <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                <th className="text-left pb-2 font-medium">Date</th>
                <th className="text-left pb-2 font-medium">Run ID</th>
                <th className="text-left pb-2 font-medium">Design</th>
                <th className="text-left pb-2 font-medium">Status</th>
                <th className="text-left pb-2 font-medium">QoR</th>
                <th className="text-left pb-2 font-medium">WNS (ns)</th>
                <th className="text-left pb-2 font-medium">TNS (ns)</th>
                <th className="text-left pb-2 font-medium">Utilization</th>
                <th className="text-left pb-2 font-medium">Runtime</th>
              </tr>
            </thead>
            <tbody>
              {[...runs].sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || "")).slice(0, 30).map((r, i) => (
                <tr key={r.run_id} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""} cursor-pointer hover:bg-[#F3F2ED]`} onClick={() => onSelectRun?.(r.run_id)}>
                  <td className="py-2 pr-2 text-[#6B7280] whitespace-nowrap">{r.timestamp ? r.timestamp.slice(0, 16).replace("T", " ") : ""}</td>
                  <td className="py-2 pr-2 font-medium text-abyss-ink">{r.run_id.slice(0, 14)}</td>
                  <td className="py-2 pr-2 text-[#6B7280]">{r.design_name}</td>
                  <td className="py-2 pr-2">
                    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold border ${
                      r.status === "SUCCESS" || r.status === "COMPLETED" ? "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]" :
                      r.status === "FAILED" ? "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]" :
                      "bg-[#F3F2ED] text-[#6B7280] border-[#E5E4E0]"
                    }`}>{r.status}</span>
                  </td>
                  <td className="py-2 pr-2 font-medium">{(r.qor_score ?? 0).toFixed(2)}</td>
                  <td className={`py-2 pr-2 ${r.wns != null && r.wns < 0 ? "text-[#C2410C]" : "text-[#6B7280]"}`}>{r.wns != null ? r.wns.toFixed(3) : "—"}</td>
                  <td className={`py-2 pr-2 ${r.tns != null && r.tns < 0 ? "text-[#C2410C]" : "text-[#6B7280]"}`}>{r.tns != null ? r.tns.toFixed(1) : "—"}</td>
                  <td className={`py-2 pr-2 ${r.utilization != null && r.utilization > 80 ? "text-[#C2410C]" : "text-[#6B7280]"}`}>{r.utilization != null ? `${r.utilization}%` : "—"}</td>
                  <td className="py-2 text-[#6B7280]">{r.runtime_sec ? `${Math.floor(r.runtime_sec / 60)}m ${Math.round(r.runtime_sec % 60)}s` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
