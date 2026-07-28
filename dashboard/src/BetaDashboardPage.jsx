import { useState, useEffect } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const API_BASE = import.meta.env.VITE_API_URL || ""

function MetricCard({ label, value, sub, color }) {
  return (
    <div className="bg-white border border-stone-ridge rounded-lg p-4">
      <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">{label}</p>
      <p className="font-[Eczar] text-[24px]" style={{ color: color || "#abyss-ink" }}>{value}</p>
      {sub && <p className="font-[Work_Sans] text-[9px] text-[#6B7280] mt-0.5">{sub}</p>}
    </div>
  )
}

export default function BetaDashboardPage() {
  const [data, setData] = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/beta/dashboard`).then(r => r.json()),
      fetch(`${API_BASE}/beta/report`).then(r => r.json()),
      fetch(`${API_BASE}/atlas/metrics`).then(r => r.json()),
      fetch(`${API_BASE}/resolutions/metrics`).then(r => r.json()),
    ])
      .then(([dash, rep, atlas, res]) => {
        setData(dash)
        setReport(rep)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading...</div>
  if (!data) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">No beta data available.</div>

  const trustColors = { HIGH: "#22C55E", MEDIUM: "#F59E0B", LOW: "#F87171" }

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Beta Operations Dashboard</h1>

      <div className="text-[10px] font-[Work_Sans] text-[#6B7280] bg-[#F3F2ED] rounded px-3 py-1.5 inline-block">
        Report period: last 7 days · Generated: {report?.generated_at?.slice(0, 16) || "—"}
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Total Sessions" value={data.users?.total_sessions || 0} sub={`${data.users?.active_today || 0} active today`} color="#3B82F6" />
        <MetricCard label="Open Feedback" value={data.feedback?.open || 0} sub={`${data.feedback?.total || 0} total submissions`} color="#F59E0B" />
        <MetricCard label="Open Issues" value={data.issues?.open || 0} color="#C2410C" />
        <MetricCard label="System Success Rate" value={`${data.system?.success_rate || 0}%`} sub={`${data.system?.total_runs || 0} total runs`} color="#16A34A" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Weekly Report</h2>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 bg-[#F0FDF4] rounded">
              <p className="font-[Eczar] text-[22px] text-[#16A34A]">{report?.new_users || 0}</p>
              <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">New Users</p>
            </div>
            <div className="text-center p-3 bg-[#FEF2F2] rounded">
              <p className="font-[Eczar] text-[22px] text-[#C2410C]">{report?.new_failures || 0}</p>
              <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">New Failures</p>
            </div>
            <div className="text-center p-3 bg-[#EFF6FF] rounded">
              <p className="font-[Eczar] text-[22px] text-[#3B82F6]">{report?.feedback_submitted || 0}</p>
              <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Feedback</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 border border-stone-ridge rounded">
              <p className="font-[Eczar] text-[18px] text-[#D4AF37]">{report?.atlas_growth || 0}</p>
              <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Atlas Entries</p>
            </div>
            <div className="text-center p-3 border border-stone-ridge rounded">
              <p className="font-[Eczar] text-[18px] text-[#A855F7]">{report?.resolution_growth || 0}</p>
              <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Resolutions</p>
            </div>
          </div>

          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mt-4 mb-2">Top Pain Points</h3>
          {report?.top_pain_points?.length > 0 ? (
            <div className="space-y-1.5">
              {report.top_pain_points.map((p, i) => (
                <div key={i} className="flex items-center justify-between text-[11px] font-[Work_Sans]">
                  <span className="text-abyss-ink">{p.failure_type}</span>
                  <span className="font-bold text-[#C2410C]">{p.cnt}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[#6B7280] text-xs font-[Work_Sans]">No data this week.</p>
          )}
        </div>

        <div className="space-y-4">
          <div className="bg-white border border-stone-ridge rounded-lg p-5">
            <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Failure Atlas Coverage</h2>
            <div className="flex items-center gap-6">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-[Work_Sans] text-[11px] text-[#6B7280]">Known</span>
                  <span className="font-[Work_Sans] text-[11px] font-bold text-[#16A34A]">{data.atlas?.known || 0}</span>
                </div>
                <div className="h-2 bg-[#F3F2ED] rounded-full overflow-hidden">
                  <div className="h-full bg-[#16A34A] rounded-full" style={{ width: `${data.atlas?.coverage || 0}%` }} />
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="font-[Work_Sans] text-[11px] text-[#6B7280]">Unknown</span>
                  <span className="font-[Work_Sans] text-[11px] font-bold text-[#F87171]">{data.atlas?.unknown || 0}</span>
                </div>
                <div className="h-2 bg-[#F3F2ED] rounded-full overflow-hidden mt-1">
                  <div className="h-full bg-[#F87171] rounded-full" style={{ width: `${100 - (data.atlas?.coverage || 0)}%` }} />
                </div>
              </div>
              <div className="text-center">
                <p className="font-[Eczar] text-[32px] text-[#D4AF37]">{data.atlas?.coverage || 0}%</p>
                <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Coverage</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-stone-ridge rounded-lg p-5">
            <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Resolution Performance</h2>
            <div className="grid grid-cols-4 gap-3 text-center">
              <div>
                <p className="font-[Eczar] text-[20px] text-[#3B82F6]">{data.resolutions?.suggested || 0}</p>
                <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Suggested</p>
              </div>
              <div>
                <p className="font-[Eczar] text-[20px] text-[#16A34A]">{data.resolutions?.accepted || 0}</p>
                <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Accepted</p>
              </div>
              <div>
                <p className="font-[Eczar] text-[20px] text-[#F87171]">{data.resolutions ? (data.resolutions.suggested - data.resolutions.accepted) : 0}</p>
                <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Rejected</p>
              </div>
              <div>
                <p className="font-[Eczar] text-[20px] text-[#A855F7]">{data.resolutions?.success_rate || 0}%</p>
                <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">Success</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-stone-ridge rounded-lg p-5">
            <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Trust Distribution</h2>
            <div className="flex gap-3">
              {["HIGH", "MEDIUM", "LOW"].map(level => {
                const count = data.resolutions?.trust_distribution?.find(t => t.trust_level === level)?.cnt || 0
                return (
                  <div key={level} className="flex-1 text-center p-3 rounded border border-stone-ridge">
                    <span className={`w-2 h-2 rounded-full inline-block mb-1`} style={{ backgroundColor: trustColors[level] }} />
                    <p className="font-[Work_Sans] text-[9px] text-[#6B7280]">{level}</p>
                    <p className="font-[Eczar] text-[18px]" style={{ color: trustColors[level] }}>{count}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
