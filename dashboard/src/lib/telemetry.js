const enabled = true

export function trackEvent(event, fields = {}) {
  if (!enabled || !event) return
  if (import.meta.env.DEV) {
    console.log(`[telemetry] ${event}`, fields)
  }
}
