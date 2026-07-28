import { useState, useEffect } from "react"
import { Server, Database, Wrench, CheckCircle, XCircle } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function InfrastructurePage() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { setHealth(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading infrastructure data...</div>

  const tools = health?.tools || {}

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Infrastructure</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Server size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">API Status</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">
            {health?.status === "ok" ? "Online" : "Offline"}
          </p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><Database size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Database</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{health?.database ? "Connected" : "Disconnected"}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FDF4FF] flex items-center justify-center mb-3"><Wrench size={16} color="#A855F7" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Tools Available</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{Object.values(tools).filter(Boolean).length}/{Object.keys(tools).length}</p>
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Pipeline Tools</h3>
        <div className="space-y-2">
          {Object.entries(tools).map(([name, available]) => (
            <div key={name} className="flex items-center justify-between p-3 border border-stone-ridge rounded-lg">
              <div className="flex items-center gap-2">
                {available ? <CheckCircle size={14} className="text-[#16A34A]" /> : <XCircle size={14} className="text-[#991B1B]" />}
                <span className="text-xs font-medium text-abyss-ink capitalize">{name}</span>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                available ? "bg-[#F0FDF4] text-[#16A34A]" : "bg-[#FEF2F2] text-[#991B1B]"
              }`}>{available ? "Available" : "Not Found"}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
