import { useState, useEffect } from "react"
import { Activity, Play, CheckCircle, AlertTriangle, XCircle } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function RunMonitorPage() {
  const [runs, setRuns] = useState([])
  const [liveRuns, setLiveRuns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/runs?limit=10000`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/live_runs`).then(r => r.ok ? r.json() : []),
    ]).then(([r, l]) => {
      setRuns(r)
      setLiveRuns(l)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading monitor data...</div>

  const running = liveRuns.length
  const completed = runs.filter(r => r.status === "SUCCESS" || r.status === "COMPLETED").length
  const failed = runs.filter(r => r.status === "FAILED").length

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Run Monitor</h1>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Activity size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Running</p>
          <p className="text-[28px] text-[#2563EB] font-semibold font-[Eczar]">{running}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{running > 0 ? "Active" : "Idle"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><CheckCircle size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Completed</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">{completed}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FEF2F2] flex items-center justify-center mb-3"><XCircle size={16} color="#991B1B" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Failed</p>
          <p className="text-[28px] text-[#991B1B] font-semibold font-[Eczar]">{failed}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FDF4FF] flex items-center justify-center mb-3"><AlertTriangle size={16} color="#A855F7" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{runs.length}</p>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Active Runs</h3>
        {liveRuns.length === 0 ? (
          <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No runs currently active</div>
        ) : (
          <div className="space-y-2">
            {liveRuns.map((r, i) => (
              <div key={r.run_id || i} className="flex items-center gap-3 p-3 border border-stone-ridge rounded-lg">
                <div className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
                <span className="text-xs font-medium text-abyss-ink">{r.run_id}</span>
                <span className="text-[10px] text-[#6B7280]">{r.current_stage || "—"}</span>
                <div className="ml-auto flex items-center gap-2">
                  <div className="w-24 h-2 bg-[#F3F2ED] rounded-full overflow-hidden">
                    <div className="h-full bg-[#2563EB] rounded-full" style={{ width: `${r.progress || 0}%` }} />
                  </div>
                  <span className="text-[10px] text-[#6B7280]">{r.progress || 0}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Recent Activity</h3>
        <div className="space-y-1">
          {runs.slice(0, 20).map((r, i) => (
            <div key={r.run_id || i} className="flex items-center gap-2 text-xs py-1.5 border-b border-stone-ridge/50 last:border-0">
              {r.status === "RUNNING" ? <Play size={10} className="text-[#2563EB]" /> :
               r.status === "SUCCESS" || r.status === "COMPLETED" ? <CheckCircle size={10} className="text-[#16A34A]" /> :
               r.status === "FAILED" ? <XCircle size={10} className="text-[#991B1B]" /> :
               <AlertTriangle size={10} className="text-[#C2410C]" />}
              <span className="font-medium text-abyss-ink">{r.run_id?.slice(0, 20)}</span>
              <span className="text-[#6B7280]">{r.design_name}</span>
              <span className="ml-auto text-[#6B7280] text-[10px]">{r.timestamp ? r.timestamp.slice(0, 16).replace("T", " ") : ""}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
