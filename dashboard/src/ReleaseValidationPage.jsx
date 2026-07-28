import { useState, useEffect } from "react"
import { Shield, CheckCircle, XCircle, Clock, ExternalLink } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function ReleaseValidationPage({ onSelectRun }) {
  const [releases, setReleases] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/releases`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setReleases(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading release data...</div>

  const validated = releases.filter(r => r.status === "SUCCESS" || r.status === "COMPLETED")
  const pending = releases.filter(r => r.status !== "SUCCESS" && r.status !== "COMPLETED")

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Release Validation</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><CheckCircle size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Validated</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">{validated.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FFF7ED] flex items-center justify-center mb-3"><Clock size={16} color="#C2410C" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Pending</p>
          <p className="text-[28px] text-[#C2410C] font-semibold font-[Eczar]">{pending.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Shield size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total Runs</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{releases.length}</p>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Release Candidates</h3>
        {releases.length === 0 ? (
          <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No release candidates yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full font-[Work_Sans]">
              <thead>
                <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                  <th className="text-left pb-2 font-medium">Run ID</th>
                  <th className="text-left pb-2 font-medium">Design</th>
                  <th className="text-left pb-2 font-medium">QoR Score</th>
                  <th className="text-left pb-2 font-medium">Status</th>
                  <th className="text-left pb-2 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {releases.map((r, i) => (
                  <tr key={r.run_id} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""} cursor-pointer hover:bg-[#F3F2ED]`} onClick={() => onSelectRun?.(r.run_id)}>
                    <td className="py-2 pr-2 font-medium text-abyss-ink">{r.run_id}</td>
                    <td className="py-2 pr-2 text-[#6B7280]">{r.design_name}</td>
                    <td className="py-2 pr-2">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${(r.qor_score || 0) >= 0.8 ? "bg-[#FEF9E7] text-[#92751A]" : (r.qor_score || 0) >= 0.65 ? "bg-[#FFF7ED] text-[#C2410C]" : "bg-[#FEF2F2] text-[#C2410C]"}`}>
                        {r.qor_score?.toFixed(2) ?? "—"}
                      </span>
                    </td>
                    <td className="py-2 pr-2">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[9px] font-bold ${
                        r.status === "SUCCESS" || r.status === "COMPLETED" ? "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]" : "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]"
                      }`}>{r.status}</span>
                    </td>
                    <td className="py-2 text-[#6B7280] whitespace-nowrap">{r.timestamp ? r.timestamp.slice(0, 10) : "—"}</td>
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
