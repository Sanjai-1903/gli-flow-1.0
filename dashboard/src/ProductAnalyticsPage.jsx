import { useState, useEffect } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function ProductAnalyticsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/analytics/product`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading...</div>
  if (!data) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">No analytics data available.</div>

  const installData = [
    { name: "Success", value: data.install.success },
    { name: "Failed", value: data.install.failures },
  ]
  const firstRunData = [
    { name: "Success", value: data.first_run.success },
    { name: "Failed", value: data.first_run.failures },
  ]

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Product Analytics</h1>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">Install Success Rate</p>
          <p className="font-[Eczar] text-[28px] text-abyss-ink">{data.install.rate}%</p>
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">{data.install.success} success / {data.install.failures} failed</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">First Run Success</p>
          <p className="font-[Eczar] text-[28px] text-[#16A34A]">{data.first_run.rate}%</p>
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">{data.first_run.success} success / {data.first_run.failures} failed</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">Unique Sessions</p>
          <p className="font-[Eczar] text-[28px] text-[#3B82F6]">{data.unique_sessions}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">Dashboard Views</p>
          <p className="font-[Eczar] text-[28px] text-[#A855F7]">{data.dashboard_usage}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Install Success Rate</h2>
          <div style={{ height: 180 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={installData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" strokeWidth={0}>
                  <Cell fill="#22C55E" /><Cell fill="#F87171" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">First Run Success Rate</h2>
          <div style={{ height: 180 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={firstRunData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" strokeWidth={0}>
                  <Cell fill="#22C55E" /><Cell fill="#F87171" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Most Used Commands</h2>
          {data.most_used_commands?.length > 0 ? (
            <div className="space-y-2">
              {data.most_used_commands.map((c, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="font-[Work_Sans] text-[11px] text-abyss-ink">{c.details}</span>
                  <span className="font-[Work_Sans] text-[11px] font-bold">{c.cnt}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[#6B7280] text-xs font-[Work_Sans]">No command data yet.</p>
          )}
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Most Common Failures</h2>
          {data.most_common_failures?.length > 0 ? (
            <div className="space-y-2">
              {data.most_common_failures.map((f, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="font-[Work_Sans] text-[11px] text-abyss-ink">{f.failure_type}</span>
                  <span className="font-[Work_Sans] text-[11px] font-bold text-[#C2410C]">{f.cnt}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[#6B7280] text-xs font-[Work_Sans]">No failure data yet.</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-4 text-center">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">Atlas Views</p>
          <p className="font-[Eczar] text-[24px] text-[#D4AF37]">{data.atlas_views}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4 text-center">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">AI Investigation Usage</p>
          <p className="font-[Eczar] text-[24px] text-[#A855F7]">{data.ai_investigation_usage}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-4 text-center">
          <p className="font-[Work_Sans] text-[10px] text-[#6B7280]">Most Common Resolutions</p>
          <p className="font-[Eczar] text-[24px] text-[#16A34A]">{data.most_common_resolutions?.length || 0}</p>
        </div>
      </div>
    </div>
  )
}
