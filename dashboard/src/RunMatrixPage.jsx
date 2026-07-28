import { useState, useEffect } from "react"
import { Grid } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function RunMatrixPage() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/runs?limit=10000`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setRuns(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading matrix data...</div>

  const designs = [...new Set(runs.map(r => r.design_name).filter(Boolean))]
  const stages = [...new Set(runs.map(r => r.current_stage).filter(Boolean))]

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Run Matrix</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Grid size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total Designs</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{designs.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Unique Stages</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{stages.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total Runs</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{runs.length}</p>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Design × Stage Matrix</h3>
        {designs.length === 0 || stages.length === 0 ? (
          <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No run data available for matrix view</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full font-[Work_Sans]">
              <thead>
                <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">Design / Stage</th>
                  {stages.map(s => <th key={s} className="text-center pb-2 font-medium px-2">{s}</th>)}
                  <th className="text-center pb-2 font-medium px-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {designs.map((design, i) => {
                  const designRuns = runs.filter(r => r.design_name === design)
                  const latestRun = designRuns[0]
                  return (
                    <tr key={design} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""}`}>
                      <td className="py-2 pr-2 font-medium text-abyss-ink">{design}</td>
                      {stages.map(stage => {
                        const inStage = designRuns.some(r => r.current_stage === stage)
                        return (
                          <td key={stage} className="text-center py-2 px-2">
                            {inStage ? <span className="w-2 h-2 inline-block rounded-full bg-[#16A34A]" /> : <span className="w-2 h-2 inline-block rounded-full bg-[#E5E4E0]" />}
                          </td>
                        )
                      })}
                      <td className="text-center py-2 px-2">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${
                          latestRun?.status === "SUCCESS" || latestRun?.status === "COMPLETED" ? "bg-[#F0FDF4] text-[#16A34A]" :
                          latestRun?.status === "FAILED" ? "bg-[#FEF2F2] text-[#991B1B]" : "bg-[#F3F2ED] text-[#6B7280]"
                        }`}>{latestRun?.status || "—"}</span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
