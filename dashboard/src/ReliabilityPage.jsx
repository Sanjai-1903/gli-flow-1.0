import { useState, useEffect } from "react"
import { Shield, CheckCircle, AlertTriangle, XCircle, Activity, TrendingUp, BarChart3 } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

function HealthBadge({ health }) {
  const styles = {
    HEALTHY: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    WARNING: "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA]",
    FAILED: "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]",
  }
  const cls = styles[health] || "bg-[#F3F2ED] text-[#6B7280] border-[#E5E4E0]"
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[10px] font-bold font-[Work_Sans] ${cls}`}>{health}</span>
}

function ConfidenceBadge({ confidence }) {
  const styles = {
    HIGH: "bg-[#F0FDF4] text-[#16A34A]",
    MEDIUM: "bg-[#FFF7ED] text-[#C2410C]",
    LOW: "bg-[#FEF2F2] text-[#991B1B]",
  }
  const cls = styles[confidence] || "bg-[#F3F2ED] text-[#6B7280]"
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold font-[Work_Sans] ${cls}`}>{confidence}</span>
}

export default function ReliabilityPage() {
  const [summary, setSummary] = useState(null)
  const [healthData, setHealthData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/reliability/summary`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/reliability/health`).then(r => r.ok ? r.json() : []),
    ]).then(([s, h]) => {
      setSummary(s)
      setHealthData(h)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading reliability data...</div>

  const scores = summary?.scores || []
  const avgScore = summary?.avg_score || 0
  const healthDist = summary?.health_distribution || {}
  const healthyCount = healthDist.HEALTHY || 0
  const warningCount = healthDist.WARNING || 0
  const failedCount = healthDist.FAILED || 0
  const total = summary?.total_runs || 0

  const scoreColor = avgScore >= 80 ? "text-[#16A34A]" : avgScore >= 50 ? "text-[#C2410C]" : "text-[#991B1B]"

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Reliability Intelligence</h1>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><Shield size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Average Reliability</p>
          <p className={`text-[28px] font-semibold font-[Eczar] ${scoreColor}`}>{avgScore}/100</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Across {total} runs</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><CheckCircle size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Healthy Runs</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">{healthyCount}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">{total > 0 ? Math.round(healthyCount / total * 100) : 0}% of total</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FFF7ED] flex items-center justify-center mb-3"><AlertTriangle size={16} color="#C2410C" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Warnings</p>
          <p className="text-[28px] text-[#C2410C] font-semibold font-[Eczar]">{warningCount}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Needs investigation</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FEF2F2] flex items-center justify-center mb-3"><XCircle size={16} color="#991B1B" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Failed Runs</p>
          <p className="text-[28px] text-[#991B1B] font-semibold font-[Eczar]">{failedCount}</p>
          <p className="text-[11px] text-[#6B7280] font-[Work_Sans] mt-1">Requires attention</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Health Distribution</h3>
          {total === 0 ? (
            <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No reliability data available</div>
          ) : (
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-[Work_Sans] mb-1">
                  <span className="text-[#16A34A] flex items-center gap-1"><CheckCircle size={12} /> Healthy</span>
                  <span>{healthyCount} ({total > 0 ? Math.round(healthyCount / total * 100) : 0}%)</span>
                </div>
                <div className="h-3 bg-[#F3F2ED] rounded-full overflow-hidden">
                  <div className="h-full bg-[#16A34A] rounded-full" style={{ width: `${total > 0 ? healthyCount / total * 100 : 0}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs font-[Work_Sans] mb-1">
                  <span className="text-[#C2410C] flex items-center gap-1"><AlertTriangle size={12} /> Warning</span>
                  <span>{warningCount} ({total > 0 ? Math.round(warningCount / total * 100) : 0}%)</span>
                </div>
                <div className="h-3 bg-[#F3F2ED] rounded-full overflow-hidden">
                  <div className="h-full bg-[#C2410C] rounded-full" style={{ width: `${total > 0 ? warningCount / total * 100 : 0}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs font-[Work_Sans] mb-1">
                  <span className="text-[#991B1B] flex items-center gap-1"><XCircle size={12} /> Failed</span>
                  <span>{failedCount} ({total > 0 ? Math.round(failedCount / total * 100) : 0}%)</span>
                </div>
                <div className="h-3 bg-[#F3F2ED] rounded-full overflow-hidden">
                  <div className="h-full bg-[#991B1B] rounded-full" style={{ width: `${total > 0 ? failedCount / total * 100 : 0}%` }} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Confidence Distribution</h3>
          {!summary?.confidence_distribution ? (
            <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No confidence data</div>
          ) : (
            <div className="space-y-3">
              {Object.entries(summary.confidence_distribution).map(([level, count]) => {
                const color = level === "HIGH" ? "bg-[#16A34A]" : level === "MEDIUM" ? "bg-[#C2410C]" : "bg-[#991B1B]"
                return (
                  <div key={level}>
                    <div className="flex justify-between text-xs font-[Work_Sans] mb-1">
                      <span>{level}</span>
                      <span>{count} ({total > 0 ? Math.round(count / total * 100) : 0}%)</span>
                    </div>
                    <div className="h-3 bg-[#F3F2ED] rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${color}`} style={{ width: `${total > 0 ? count / total * 100 : 0}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={14} className="text-[#6B7280]" />
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Per-Run Reliability Scores</h3>
        </div>
        {scores.length === 0 ? (
          <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No reliability scores available</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full font-[Work_Sans]">
              <thead>
                <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">Run ID</th>
                  <th className="text-left pb-2 font-medium">Status</th>
                  <th className="text-left pb-2 font-medium">Health</th>
                  <th className="text-left pb-2 font-medium">Score</th>
                  <th className="text-left pb-2 font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {scores.map((s, i) => (
                  <tr key={s.run || i} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""}`}>
                    <td className="py-2 pr-2 font-medium text-abyss-ink">{s.run || s.run_id}</td>
                    <td className="py-2 pr-2">{s.status}</td>
                    <td className="py-2 pr-2"><HealthBadge health={s.health} /></td>
                    <td className="py-2 pr-2">
                      <span className={`font-semibold ${s.reliability_score >= 80 ? "text-[#16A34A]" : s.reliability_score >= 50 ? "text-[#C2410C]" : "text-[#991B1B]"}`}>
                        {s.reliability_score}/100
                      </span>
                    </td>
                    <td className="py-2"><ConfidenceBadge confidence={s.confidence} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
