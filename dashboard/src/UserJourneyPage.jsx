import { useState, useEffect } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const API_BASE = import.meta.env.VITE_API_URL || ""

const STAGE_ORDER = ["install", "first_run", "failure", "diagnosis", "resolution", "success"]
const STAGE_LABELS = { install: "Install", first_run: "First Run", failure: "Failure", diagnosis: "Diagnosis", resolution: "Resolution", success: "Success" }
const STAGE_COLORS = { install: "#3B82F6", first_run: "#22C55E", failure: "#F87171", diagnosis: "#F59E0B", resolution: "#A855F7", success: "#16A34A" }

export default function UserJourneyPage() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/journey/report`)
      .then(r => r.json())
      .then(d => { setReport(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading...</div>
  if (!report) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">No journey data available.</div>

  const funnelData = STAGE_ORDER.map(s => ({
    stage: STAGE_LABELS[s] || s,
    users: report.funnel?.find(f => f.stage === s)?.cnt || 0,
    fill: STAGE_COLORS[s],
  }))

  const dropOffData = [
    { name: "Install → First Run", rate: report.drop_off?.install_to_first_run?.rate || 0, total: report.drop_off?.install_to_first_run?.total_installers || 0 },
    { name: "First Run → Failure", rate: report.drop_off?.first_run_to_failure?.rate || 0, total: report.drop_off?.first_run_to_failure?.total_first_run || 0 },
    { name: "Failure → Success", rate: report.drop_off?.failure_to_success?.rate || 0, total: report.drop_off?.failure_to_success?.total_failures || 0 },
  ]

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">User Journey</h1>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Journey Funnel</h2>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData} layout="vertical" margin={{ left: 80, right: 20 }}>
                <CartesianGrid stroke="#F3F2ED" strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontFamily: "Work Sans", fontSize: 10, fill: "#6B7280" }} />
                <YAxis type="category" dataKey="stage" tick={{ fontFamily: "Work Sans", fontSize: 11, fill: "#6B7280" }} width={90} />
                <Tooltip />
                <Bar dataKey="users" radius={[0, 4, 4, 0]}>
                  {funnelData.map((entry, i) => (
                    <rect key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Drop-off Points</h2>
          <div className="space-y-4">
            {dropOffData.map((d, i) => (
              <div key={i} className="border border-stone-ridge rounded p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-[Work_Sans] text-[12px] text-abyss-ink font-medium">{d.name}</span>
                  <span className={`font-[Eczar] text-[20px] ${d.rate < 50 ? 'text-[#C2410C]' : d.rate < 80 ? 'text-[#A16207]' : 'text-[#16A34A]'}`}>
                    {d.rate}%
                  </span>
                </div>
                <div className="h-2 bg-[#F3F2ED] rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all" style={{
                    width: `${d.rate}%`,
                    backgroundColor: d.rate < 50 ? "#F87171" : d.rate < 80 ? "#F59E0B" : "#22C55E"
                  }} />
                </div>
                <p className="font-[Work_Sans] text-[10px] text-[#6B7280] mt-1">{d.total} user(s) reached this stage</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Average Time per Stage</h2>
        {report.avg_stage_duration_sec?.length > 0 ? (
          <div className="grid grid-cols-6 gap-3">
            {STAGE_ORDER.map(s => {
              const item = report.avg_stage_duration_sec.find(f => f.stage === s)
              return (
                <div key={s} className="text-center p-3 border border-stone-ridge rounded">
                  <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">{STAGE_LABELS[s] || s}</p>
                  <p className="font-[Eczar] text-[18px]" style={{ color: STAGE_COLORS[s] }}>
                    {item ? `${Math.round(item.avg_sec)}s` : "—"}
                  </p>
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-[#6B7280] text-xs font-[Work_Sans]">No timing data yet.</p>
        )}
      </div>
    </div>
  )
}
