import { useState, useEffect } from "react"
import { Folder, FileText, Download, ExternalLink, Search } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function ArtifactsPage() {
  const [runs, setRuns] = useState([])
  const [selectedRun, setSelectedRun] = useState(null)
  const [artifacts, setArtifacts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
      fetch(`${API_BASE}/runs?limit=10000`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setRuns(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedRun) return
    fetch(`${API_BASE}/runs/${selectedRun}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => setArtifacts(data?.artifacts || []))
      .catch(() => setArtifacts([]))
  }, [selectedRun])

  const extensionIcon = (name) => {
    if (name.endsWith(".json")) return "📋"
    if (name.endsWith(".rpt") || name.endsWith(".txt")) return "📄"
    if (name.endsWith(".csv")) return "📊"
    if (name.endsWith(".log")) return "📝"
    if (name.endsWith(".gds")) return "💾"
    if (name.endsWith(".def")) return "🔧"
    if (name.endsWith(".v")) return "🔌"
    if (name.endsWith(".png") || name.endsWith(".webp") || name.endsWith(".jpg")) return "🖼️"
    return "📁"
  }

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading artifacts...</div>

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Artifacts</h1>

      <div className="grid grid-cols-[300px_1fr] gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-4">
          <h3 className="font-[Playfair_Display] text-[13px] text-abyss-ink mb-3">Run Selection</h3>
          <div className="space-y-1 max-h-[400px] overflow-y-auto">
            {runs.map((r, i) => (
              <button
                key={r.run_id}
                onClick={() => setSelectedRun(r.run_id)}
                className={`w-full text-left px-3 py-2 rounded text-[11px] font-[Work_Sans] transition-colors ${
                  selectedRun === r.run_id ? "bg-[#EFF6FF] text-[#2563EB] font-medium" : "text-[#6B7280] hover:bg-[#FAFAF8]"
                }`}
              >
                <span className="truncate block">{r.run_id?.slice(0, 24)}</span>
                <span className="text-[9px] text-[#9CA3AF]">{r.design_name}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">
              {selectedRun ? `Artifacts: ${selectedRun.slice(0, 20)}` : "Select a run"}
            </h3>
            {selectedRun && <span className="text-[10px] text-[#6B7280]">{artifacts.length} files</span>}
          </div>
          {!selectedRun ? (
            <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Select a run from the left to view its artifacts</div>
          ) : artifacts.length === 0 ? (
            <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">No artifacts found for this run</div>
          ) : (
            <div className="space-y-1 max-h-[500px] overflow-y-auto">
              {artifacts.map((a, i) => (
                <div key={i} className="flex items-center gap-2 p-2 rounded text-[11px] font-[Work_Sans] hover:bg-[#FAFAF8]">
                  <span className="text-[14px]">{extensionIcon(a)}</span>
                  <span className="text-abyss-ink truncate flex-1">{a}</span>
                  <a
                    href={`${API_BASE}/runs/${selectedRun}/report/${a}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[10px] text-meridian-gold hover:underline flex items-center gap-1 flex-shrink-0"
                  >
                    <Download size={10} /> View
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
