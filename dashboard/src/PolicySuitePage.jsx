import { useState, useEffect } from "react"
import { Sliders, CheckCircle, XCircle, FileText } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function PolicySuitePage() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/runs?limit=10000`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setRuns(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading policy data...</div>

  const total = runs.length
  const withQor = runs.filter(r => r.qor_score != null).length
  const passing = runs.filter(r => r.qor_score != null && r.qor_score >= 0.7).length
  const failing = runs.filter(r => r.qor_score != null && r.qor_score < 0.7).length
  const passRate = withQor > 0 ? Math.round(passing / withQor * 100) : 0

  const policies = [
    { name: "QoR Threshold ≥ 0.70", status: passRate >= 80 ? "PASSING" : passRate > 0 ? "WARNING" : "NO_DATA", detail: `${passing}/${withQor} runs pass (${passRate}%)` },
    { name: "Timing Closure (WNS ≥ 0)", status: "MONITORING", detail: "Tracked per-run in timing reports" },
    { name: "DRC Clean", status: "MONITORING", detail: "Verified during run execution" },
    { name: "LVS Clean", status: "MONITORING", detail: "Verified during run execution" },
    { name: "Reliability Score ≥ 50", status: "MONITORING", detail: "Computed via reliability pipeline" },
  ]

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Policy Suite</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Sliders size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Policies Tracked</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{policies.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><CheckCircle size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Passing</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">{policies.filter(p => p.status === "PASSING").length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FFF7ED] flex items-center justify-center mb-3"><FileText size={16} color="#C2410C" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Under Monitoring</p>
          <p className="text-[28px] text-[#C2410C] font-semibold font-[Eczar]">{policies.filter(p => p.status === "MONITORING").length}</p>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Governance Policies</h3>
        <div className="space-y-3">
          {policies.map((p, i) => (
            <div key={i} className="flex items-center justify-between p-3 border border-stone-ridge rounded-lg hover:bg-[#FAFAF8]">
              <div>
                <p className="text-xs font-medium text-abyss-ink">{p.name}</p>
                <p className="text-[10px] text-[#6B7280] mt-0.5">{p.detail}</p>
              </div>
              <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold ${
                p.status === "PASSING" ? "bg-[#F0FDF4] text-[#16A34A]" :
                p.status === "WARNING" ? "bg-[#FFF7ED] text-[#C2410C]" :
                p.status === "MONITORING" ? "bg-[#EFF6FF] text-[#3B82F6]" :
                "bg-[#F3F2ED] text-[#6B7280]"
              }`}>{p.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
