import { useState, useEffect } from "react"

const API_BASE = import.meta.env.VITE_API_URL || ""

const TYPES = ["issue", "feature", "general", "success_story"]
const TYPE_LABELS = { issue: "Report Issue", feature: "Request Feature", general: "General Feedback", success_story: "Success Story" }
const TYPE_COLORS = { issue: "#C2410C", feature: "#3B82F6", general: "#6B7280", success_story: "#16A34A" }

export default function FeedbackCenterPage() {
  const [feedback, setFeedback] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [formType, setFormType] = useState("general")
  const [formTitle, setFormTitle] = useState("")
  const [formDesc, setFormDesc] = useState("")
  const [formRunId, setFormRunId] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [filterType, setFilterType] = useState("")
  const [filterStatus, setFilterStatus] = useState("")

  const fetchData = () => {
    const params = new URLSearchParams()
    if (filterType) params.set("feedback_type", filterType)
    if (filterStatus) params.set("status", filterStatus)
    Promise.all([
      fetch(`${API_BASE}/feedback?${params}`).then(r => r.json()),
      fetch(`${API_BASE}/feedback/stats`).then(r => r.json()),
    ])
      .then(([data, statsData]) => {
        setFeedback(data.results || [])
        setStats(statsData)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [filterType, filterStatus])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const resp = await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          feedback_type: formType,
          title: formTitle,
          description: formDesc,
          recent_run_id: formRunId,
          os: navigator.platform || "",
        }),
      })
      if (resp.ok) {
        setSubmitted(true)
        setFormTitle("")
        setFormDesc("")
        setFormRunId("")
        fetchData()
        setTimeout(() => setSubmitted(false), 3000)
      }
    } catch (e) {
      console.error("Submit failed:", e)
    }
    setSubmitting(false)
  }

  if (loading) return <div className="py-12 text-center text-[#6B7280] text-xs font-[Work_Sans]">Loading...</div>

  const getStatusStyle = (s) => {
    const styles = { open: "bg-[#FEF2F2] text-[#991B1B]", acknowledged: "bg-[#FFF7ED] text-[#C2410C]", triaged: "bg-[#EFF6FF] text-[#2563EB]", resolved: "bg-[#F0FDF4] text-[#16A34A]", closed: "bg-[#F3F2ED] text-[#6B7280]" }
    return styles[s] || styles.open
  }

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Feedback Center</h1>

      <div className="grid grid-cols-4 gap-4">
        {TYPES.map(t => (
          <div key={t} className="bg-white border border-stone-ridge rounded-lg p-4 text-center">
            <p className="font-[Eczar] text-[24px]" style={{ color: TYPE_COLORS[t] }}>{stats?.by_type?.[t] || 0}</p>
            <p className="font-[Work_Sans] text-[11px] text-[#6B7280]">{TYPE_LABELS[t]}s</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-[1fr_1fr] gap-6">
        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Submit Feedback</h2>
          {submitted ? (
            <div className="bg-[#F0FDF4] border border-[#BBF7D0] rounded-lg p-4 text-center">
              <p className="font-[Work_Sans] text-[13px] text-[#16A34A] font-medium">Thank you! Your feedback has been submitted.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="font-[Work_Sans] text-[11px] text-[#6B7280] block mb-1">Type</label>
                <div className="flex gap-2 flex-wrap">
                  {TYPES.map(t => (
                    <button key={t} type="button" onClick={() => setFormType(t)}
                      className={`px-3 py-1.5 rounded text-[11px] font-[Work_Sans] border transition-colors ${
                        formType === t ? "bg-abyss-ink text-white border-abyss-ink" : "bg-white text-[#6B7280] border-stone-ridge hover:bg-[#FAFAF8]"
                      }`}
                    >{TYPE_LABELS[t]}</button>
                  ))}
                </div>
              </div>
              <div>
                <label className="font-[Work_Sans] text-[11px] text-[#6B7280] block mb-1">Title</label>
                <input value={formTitle} onChange={e => setFormTitle(e.target.value)} required
                  className="w-full border border-stone-ridge rounded px-3 py-2 text-xs font-[Work_Sans]" placeholder="Brief summary of your feedback" />
              </div>
              <div>
                <label className="font-[Work_Sans] text-[11px] text-[#6B7280] block mb-1">Description</label>
                <textarea value={formDesc} onChange={e => setFormDesc(e.target.value)} required rows={4}
                  className="w-full border border-stone-ridge rounded px-3 py-2 text-xs font-[Work_Sans]" placeholder="Detailed description..." />
              </div>
              <div>
                <label className="font-[Work_Sans] text-[11px] text-[#6B7280] block mb-1">Related Run ID (optional)</label>
                <input value={formRunId} onChange={e => setFormRunId(e.target.value)}
                  className="w-full border border-stone-ridge rounded px-3 py-2 text-xs font-[Work_Sans]" placeholder="e.g. run_20260615_143022" />
              </div>
              <button type="submit" disabled={submitting}
                className="bg-abyss-ink text-white px-4 py-2 rounded text-xs font-[Work_Sans] hover:opacity-90 disabled:opacity-50"
              >{submitting ? "Submitting..." : "Submit Feedback"}</button>
            </form>
          )}
        </div>

        <div className="bg-white border border-stone-ridge rounded-lg p-5">
          <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink mb-4">Filters</h2>
          <div className="flex gap-3 mb-4">
            <select value={filterType} onChange={e => setFilterType(e.target.value)}
              className="border border-stone-ridge rounded px-3 py-1.5 text-xs font-[Work_Sans]"
            >
              <option value="">All Types</option>
              {TYPES.map(t => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
            </select>
            <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
              className="border border-stone-ridge rounded px-3 py-1.5 text-xs font-[Work_Sans]"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="triaged">Triaged</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-3">Recent Feedback</h3>
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {feedback.length === 0 ? (
              <p className="text-[#6B7280] text-xs font-[Work_Sans]">No feedback yet.</p>
            ) : feedback.map(f => (
              <div key={f.id} className="border border-stone-ridge rounded p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold font-[Work_Sans] ${getStatusStyle(f.status)}`}>{f.status}</span>
                  <span className="text-[10px] font-[Work_Sans] px-1.5 py-0.5 rounded bg-[#F3F2ED]" style={{ color: TYPE_COLORS[f.feedback_type] }}>{TYPE_LABELS[f.feedback_type]}</span>
                  {f.priority_level && (
                    <span className={`text-[9px] font-bold font-[Work_Sans] ${f.priority_level === 'HIGH' ? 'text-[#C2410C]' : f.priority_level === 'MEDIUM' ? 'text-[#A16207]' : 'text-[#6B7280]'}`}>
                      {f.priority_level} PRIORITY
                    </span>
                  )}
                </div>
                <p className="font-[Work_Sans] text-[12px] text-abyss-ink font-medium">{f.title || "(no title)"}</p>
                <p className="font-[Work_Sans] text-[10px] text-[#6B7280] mt-0.5 line-clamp-2">{f.description}</p>
                <p className="font-[Work_Sans] text-[9px] text-[#6B7280] mt-1">{f.created_at?.slice(0, 16)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
