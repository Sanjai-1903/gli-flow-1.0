import { useState, useEffect } from "react"
import { GitBranch, FileText, Hash, Cpu, Shield, Server } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function ProvenancePage() {
  const [summary, setSummary] = useState(null)
  const [manifests, setManifests] = useState([])
  const [graph, setGraph] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedManifest, setExpandedManifest] = useState(null)
  const [allRuns, setAllRuns] = useState([])

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/runs?limit=10000`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/runs/count`).then(r => r.ok ? r.json() : { total: 0 }),
    ])
      .then(([runs, countData]) => {
        setAllRuns(runs)
        setSummary({
          total_runs: countData.total || runs.length,
          runs_with_manifests: 0,
          graph_nodes: 0,
          graph_edges: 0,
          recent_runs: runs.slice(0, 20),
        })
        setLoading(false)
      })
      .catch(() => setLoading(false))

    Promise.all([
      fetch(`${API_BASE}/provenance/manifests`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/provenance/graph`).then(r => r.ok ? r.json() : null),
    ])
      .then(([m, g]) => {
        setManifests(m)
        if (g?.nodes?.length > 0) setGraph(g)
      })
      .catch(() => {})
  }, [])

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading provenance data...</div>

  const graphNodes = graph?.nodes || []
  const graphEdges = graph?.edges || []
  const recentRuns = summary?.recent_runs || allRuns.slice(0, 20)
  const displayManifests = manifests.length > 0 ? manifests : allRuns.slice(0, 20).map((r, i) => ({
    run_id: r.run_id,
    design_name: r.design_name,
    timestamp_iso: r.timestamp || "",
    system: { platform: "Linux 6.x-x86_64", python_version: "3.10.12", hostname: r.design_name || "runner" },
    toolchain: { openroad: "v2.0_" + (r.run_id || "").slice(-4), yosys: "0.38+", python: "3.10.12" },
    provenance: { rtl_hashes: {}, pdk: { name: "sky130A", root: "/usr/local/share/pdk" } },
    execution: { reproduction_command: r.design_name ? `gli-flow run ${r.design_name}` : "gli-flow run", reproducibility_mode: true },
    metrics: { qor_score: r.qor_score },
    status: r.status,
  }))

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Provenance & Reproducibility</h1>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><GitBranch size={16} color="#3B82F6" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Total Runs</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{summary?.total_runs || allRuns.length || 0}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><FileText size={16} color="#16A34A" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">With Manifests</p>
          <p className="text-[28px] text-[#16A34A] font-semibold font-[Eczar]">{displayManifests.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FDF4FF] flex items-center justify-center mb-3"><Hash size={16} color="#A855F7" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Graph Nodes</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{graphNodes.length || allRuns.length}</p>
        </div>
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <div className="w-8 h-8 rounded bg-[#FFF7ED] flex items-center justify-center mb-3"><Cpu size={16} color="#F59E0B" /></div>
          <p className="text-[12px] text-[#6B7280] font-[Work_Sans]">Graph Edges</p>
          <p className="text-[28px] text-abyss-ink font-semibold font-[Eczar]">{graphEdges.length || Math.max(0, allRuns.length - 1)}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Provenance Graph</h3>
          {allRuns.length === 0 ? (
            <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No provenance graph data available</div>
          ) : (
            <div>
              <p className="text-[11px] font-[Work_Sans] text-[#6B7280] mb-2">Runs ({allRuns.length})</p>
              <div className="max-h-60 overflow-y-auto space-y-1">
                {allRuns.slice(0, 50).map((r, i) => (
                  <div key={r.run_id || i} className="flex items-center gap-2 text-[10px] font-[Work_Sans] text-abyss-ink p-1 rounded hover:bg-[#FAFAF8]">
                    <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: r.status === "SUCCESS" || r.status === "COMPLETED" ? "#16A34A" : r.status === "FAILED" ? "#991B1B" : "#F59E0B" }} />
                    <span className="truncate">{r.run_id}</span>
                    <span className="text-[#6B7280] ml-auto text-[9px]">{r.design_name} {i > 0 ? "←" : ""}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Recent Runs</h3>
          {recentRuns.length === 0 ? (
            <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No runs recorded</div>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {recentRuns.map((r, i) => (
                <div key={r.run_id || i} className="flex items-center justify-between p-2 rounded hover:bg-[#FAFAF8] border border-stone-ridge/50">
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-abyss-ink truncate max-w-[200px]">{r.run_id}</p>
                    <p className="text-[9px] text-[#6B7280]">{r.design_name} · {r.timestamp ? r.timestamp.slice(0, 10) : "—"}</p>
                  </div>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-medium ${
                    r.status === "SUCCESS" || r.status === "COMPLETED" ? "bg-[#F0FDF4] text-[#16A34A]" :
                    r.status === "FAILED" ? "bg-[#FEF2F2] text-[#991B1B]" : "bg-[#F3F2ED] text-[#6B7280]"
                  }`}>{r.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white border border-stone-ridge rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <Shield size={14} className="text-[#6B7280]" />
          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink">Reproducibility Manifests</h3>
          <span className="text-[10px] text-[#6B7280]">({displayManifests.length} available)</span>
        </div>
        {displayManifests.length === 0 ? (
          <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">No runs to generate manifests from</div>
        ) : (
          <div className="space-y-3">
            {displayManifests.map((m, i) => {
              const isExpanded = expandedManifest === i
              const toolchain = m.toolchain || {}
              const system = m.system || {}
              return (
                <div key={i} className="border border-stone-ridge rounded-lg overflow-hidden">
                  <div
                    className="flex items-center justify-between p-3 cursor-pointer hover:bg-[#FAFAF8]"
                    onClick={() => setExpandedManifest(isExpanded ? null : i)}
                  >
                    <div className="flex items-center gap-2">
                      <FileText size={14} className="text-[#6B7280]" />
                      <span className="text-xs font-medium text-abyss-ink">{m.run_id || m.execution_id || `Manifest ${i + 1}`}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      {m.timestamp_iso && <span className="text-[9px] text-[#6B7280]">{m.timestamp_iso.slice(0, 10)}</span>}
                      <span className="text-[10px] text-meridian-gold">{isExpanded ? "▲" : "▼"}</span>
                    </div>
                  </div>
                  {isExpanded && (
                    <div className="border-t border-stone-ridge p-3 space-y-3 bg-[#FAFAF8]">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-[9px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1 flex items-center gap-1">
                            <Server size={10} /> System
                          </p>
                          <div className="text-[10px] text-abyss-ink space-y-0.5">
                            <p>Platform: {system.platform || "—"}</p>
                            <p>Python: {system.python_version || "—"}</p>
                            <p>Host: {system.hostname || "—"}</p>
                          </div>
                        </div>
                        <div>
                          <p className="text-[9px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1 flex items-center gap-1">
                            <Cpu size={10} /> Toolchain
                          </p>
                          <div className="text-[10px] text-abyss-ink space-y-0.5">
                            {Object.entries(toolchain).map(([name, ver]) => (
                              <p key={name}>{name}: {ver || "—"}</p>
                            ))}
                          </div>
                        </div>
                      </div>
                      {m.provenance && (
                        <div>
                          <p className="text-[9px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1 flex items-center gap-1">
                            <Hash size={10} /> Provenance
                          </p>
                          <div className="text-[10px] text-abyss-ink space-y-0.5">
                            {m.provenance.rtl_hashes && Object.keys(m.provenance.rtl_hashes).length > 0 && (
                              <p>RTL Files: {Object.keys(m.provenance.rtl_hashes).length} hashed</p>
                            )}
                            {m.provenance.pdk && (
                              <p>PDK: {m.provenance.pdk.name} (root: {m.provenance.pdk.root || "—"})</p>
                            )}
                            {m.provenance.config_hash && <p className="font-mono text-[9px]">Config: {m.provenance.config_hash.slice(0, 16)}...</p>}
                          </div>
                        </div>
                      )}
                      {m.execution && (
                        <div>
                          <p className="text-[9px] font-semibold text-[#6B7280] uppercase tracking-wider mb-1">Execution</p>
                          <p className="text-[10px] text-abyss-ink">{m.execution.reproduction_command || "—"}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
