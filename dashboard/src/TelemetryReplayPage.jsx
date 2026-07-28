import { useState } from "react"
import { Upload, Play, CheckCircle, AlertTriangle, ChevronDown, ChevronRight, Download } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function TelemetryReplayPage() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [fileContent, setFileContent] = useState(null)
  const [fileName, setFileName] = useState("")
  const [expandedTimeline, setExpandedTimeline] = useState(false)
  const [expandedEvents, setExpandedEvents] = useState(false)
  const [expandedFailures, setExpandedFailures] = useState(false)
  const [expandedResolutions, setExpandedResolutions] = useState(false)

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = (evt) => {
      try {
        const json = JSON.parse(evt.target.result)
        setFileContent(json)
      } catch {
        alert("Invalid JSON file")
      }
    }
    reader.readAsText(file)
  }

  const runReplay = () => {
    if (!fileContent) return
    setLoading(true)
    fetch(`${API_BASE}/telemetry/replay`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: fileContent, dry_run: true }),
    })
      .then(r => r.json())
      .then(data => {
        setResults(data)
        setLoading(false)
      })
      .catch(() => {
        alert("Replay failed")
        setLoading(false)
      })
  }

  const meta = results?.replay_metadata || {}

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-[Playfair_Display] text-lg text-abyss-ink">Telemetry Replay</h2>
        <p className="text-[10px] text-[#6B7280] mt-0.5">
          Upload a telemetry export file to simulate or replay events. Never modifies original data.
        </p>
      </div>

      {/* Upload Section */}
      <div className="bg-white border border-stone-ridge rounded-lg p-6">
        <div className="flex items-center justify-center">
          <label className="flex flex-col items-center gap-2 cursor-pointer">
            <Upload size={24} className="text-[#6B7280]" />
            <span className="text-xs text-[#6B7280]">
              {fileName ? `Selected: ${fileName}` : "Click to upload telemetry_export.json"}
            </span>
            <input
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
        {fileContent && (
          <div className="mt-4 flex justify-center">
            <button
              onClick={runReplay}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-meridian-gold text-white rounded-lg text-xs font-medium hover:bg-amber-600 disabled:opacity-50"
            >
              <Play size={14} />
              {loading ? "Replaying..." : "Run Replay"}
            </button>
          </div>
        )}
      </div>

      {!results && !loading && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white border border-stone-ridge rounded-lg p-4">
            <h3 className="text-[10px] font-semibold text-abyss-ink mb-2">How it works</h3>
            <ul className="text-[10px] text-[#6B7280] space-y-2 list-disc pl-4">
              <li>Upload a JSON file exported from another GLI-FLOW instance.</li>
              <li>The system parses telemetry, unknown failures, and resolution patterns.</li>
              <li>Replay runs in <strong>dry-run</strong> mode by default (simulated).</li>
              <li>A timeline and detailed event list will be generated below.</li>
            </ul>
          </div>
          <div className="bg-white border border-stone-ridge rounded-lg p-4">
            <h3 className="text-[10px] font-semibold text-abyss-ink mb-2">Sample Format</h3>
            <pre className="text-[9px] bg-gray-50 p-2 rounded border border-stone-ridge overflow-x-auto font-mono text-abyss-ink">
{`{
  "telemetry_events": [
    { "event": "ai_investigation_run", ... }
  ],
  "unknown_failures": [
    { "failure_type": "DRC_VIOLATION", ... }
  ]
}`}
            </pre>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <>
          {/* Summary */}
          <div className="bg-white border border-stone-ridge rounded-lg p-4">
            <h3 className="text-xs font-semibold text-abyss-ink mb-3">Replay Summary</h3>
            <div className="grid grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-blue-700 font-semibold">{meta.total_events}</p>
                <p className="text-[10px] text-blue-600">Total Events</p>
              </div>
              <div className="p-3 bg-emerald-50 rounded border border-emerald-200">
                <p className="text-emerald-700 font-semibold">{meta.successful}</p>
                <p className="text-[10px] text-emerald-600">Successful</p>
              </div>
              <div className="p-3 bg-red-50 rounded border border-red-200">
                <p className="text-red-700 font-semibold">{meta.failed}</p>
                <p className="text-[10px] text-red-600">Failed</p>
              </div>
              <div className="p-3 bg-gray-50 rounded border border-stone-ridge">
                <p className="text-gray-700 font-semibold">{meta.source_file?.split("/").pop() || "—"}</p>
                <p className="text-[10px] text-gray-600">Source File</p>
              </div>
            </div>
            <div className="mt-3 text-[10px] text-[#6B7280]">
              Started: {meta.started_at?.slice(0, 19) || "—"} &middot;
              Completed: {meta.completed_at?.slice(0, 19) || "—"}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white border border-stone-ridge rounded-lg">
            <button
              onClick={() => setExpandedTimeline(!expandedTimeline)}
              className="w-full flex items-center justify-between px-4 py-3 text-xs font-medium text-abyss-ink hover:bg-gray-50"
            >
              <span>Timeline ({results.timeline?.length || 0} entries)</span>
              {expandedTimeline ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            {expandedTimeline && (
              <div className="px-4 pb-3 max-h-64 overflow-y-auto">
                {(results.timeline || []).map((t, i) => (
                  <div key={i} className="flex items-center gap-3 py-1 text-[10px] border-b border-stone-ridge/50 last:border-0">
                    <span className="w-24 font-mono text-[#6B7280]">{t.timestamp?.slice(0, 10) || "—"}</span>
                    <span className={`px-1.5 py-0.5 rounded font-medium ${
                      t.status === "recorded" ? "bg-emerald-100 text-emerald-700" : "bg-blue-100 text-blue-700"
                    }`}>{t.status}</span>
                    <span className="w-28 text-[#6B7280]">{t.type}</span>
                    <span className="font-mono text-abyss-ink truncate">{t.name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Events */}
          <div className="bg-white border border-stone-ridge rounded-lg">
            <button
              onClick={() => setExpandedEvents(!expandedEvents)}
              className="w-full flex items-center justify-between px-4 py-3 text-xs font-medium text-abyss-ink hover:bg-gray-50"
            >
              <span>Events ({results.events?.length || 0})</span>
              {expandedEvents ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            {expandedEvents && (
              <div className="px-4 pb-3 max-h-64 overflow-y-auto">
                {(results.events || []).map((e, i) => (
                  <div key={i} className="flex items-center gap-2 py-1 text-[10px] border-b border-stone-ridge/50 last:border-0">
                    <CheckCircle size={10} className="text-emerald-500" />
                    <span className="font-medium">{e.event}</span>
                    <span className="text-[#6B7280]">{e.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Failures */}
          <div className="bg-white border border-stone-ridge rounded-lg">
            <button
              onClick={() => setExpandedFailures(!expandedFailures)}
              className="w-full flex items-center justify-between px-4 py-3 text-xs font-medium text-abyss-ink hover:bg-gray-50"
            >
              <span>Failures ({results.failures?.length || 0})</span>
              {expandedFailures ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            {expandedFailures && (
              <div className="px-4 pb-3 max-h-64 overflow-y-auto">
                {(results.failures || []).map((f, i) => (
                  <div key={i} className="flex items-center gap-2 py-1 text-[10px] border-b border-stone-ridge/50 last:border-0">
                    <AlertTriangle size={10} className="text-amber-500" />
                    <span className="font-medium">{f.tool}:{f.failure_type}</span>
                    <span className="text-[#6B7280] font-mono">{f.signature || "—"}</span>
                    <span className="text-[#6B7280]">x{f.frequency}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Resolutions */}
          <div className="bg-white border border-stone-ridge rounded-lg">
            <button
              onClick={() => setExpandedResolutions(!expandedResolutions)}
              className="w-full flex items-center justify-between px-4 py-3 text-xs font-medium text-abyss-ink hover:bg-gray-50"
            >
              <span>Resolutions ({results.resolutions?.length || 0})</span>
              {expandedResolutions ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            {expandedResolutions && (
              <div className="px-4 pb-3 max-h-64 overflow-y-auto">
                {(results.resolutions || []).map((r, i) => (
                  <div key={i} className="flex items-center gap-2 py-1 text-[10px] border-b border-stone-ridge/50 last:border-0">
                    <CheckCircle size={10} className="text-emerald-500" />
                    <span className="font-mono text-[#6B7280]">{r.fingerprint?.slice(0, 24) || r.id || "—"}</span>
                    <span className="text-abyss-ink">{r.resolution?.slice(0, 60)}{(r.resolution?.length || 0) > 60 ? "..." : ""}</span>
                    <span className="text-[#6B7280]">{(r.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
