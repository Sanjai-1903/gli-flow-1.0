import { useState, useEffect } from "react"
import { Sparkles, XCircle } from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function AIAvailabilityGuard({ children, fallback }) {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    fetch(`${API_BASE}/ai/health`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (!cancelled) {
          setHealth(data)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHealth(null)
          setLoading(false)
        }
      })
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return null
  }

  if (!health || health.status !== "READY") {
    if (fallback) {
      return fallback(health)
    }
    const reason = health?.reason || "AI investigation is not available"
    const fix = health?.fix || "Check your configuration"
    return (
      <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <XCircle size={14} className="text-amber-600" />
          <h4 className="text-xs font-semibold text-amber-800">AI Investigation Unavailable</h4>
        </div>
        <p className="text-[10px] text-amber-700 mb-1">
          <span className="font-medium">Reason:</span> {reason}
        </p>
        <p className="text-[10px] text-amber-700">
          <span className="font-medium">How To Fix:</span> {fix}
        </p>
      </div>
    )
  }

  return children
}
