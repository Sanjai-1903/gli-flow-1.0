import { useState, useEffect } from "react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, Area, AreaChart, PieChart, Pie, Cell,
  ResponsiveContainer, Legend
} from "recharts"
import {
  LayoutDashboard, Play, Grid, Activity, Folder, BarChart2, Zap, TrendingUp,
  Map, GitBranch, Shield, Sliders, Server, Settings, HelpCircle,
  Bell, ChevronDown, MoreVertical, CheckCircle, AlertTriangle,
  Star, Menu, ExternalLink, Eye, Upload, MessageSquare, Target, Users,
  BarChart3, Award
} from "lucide-react"
import RunDetail from "./RunDetail"
import FailureAtlasPage from "./FailureAtlasPage"
import EngineeringDashboardPage from "./EngineeringDashboardPage"
import QoRAnalyticsPage from "./QoRAnalyticsPage"
import RegressionDetectorPage from "./RegressionDetectorPage"
import TrendsReportsPage from "./TrendsReportsPage"
import RunsPage from "./RunsPage"
import ReliabilityPage from "./ReliabilityPage"
import ProvenancePage from "./ProvenancePage"
import ReleaseValidationPage from "./ReleaseValidationPage"
import PolicySuitePage from "./PolicySuitePage"
import RunDesignPage from "./RunDesignPage"
import RunMatrixPage from "./RunMatrixPage"
import RunMonitorPage from "./RunMonitorPage"
import ArtifactsPage from "./ArtifactsPage"
import InfrastructurePage from "./InfrastructurePage"
import SettingsPage from "./SettingsPage"
import HelpPage from "./HelpPage"
import TelemetryPage from "./TelemetryPage"
import TelemetryHealthPage from "./TelemetryHealthPage"
import TelemetryReplayPage from "./TelemetryReplayPage"
import FeedbackCenterPage from "./FeedbackCenterPage"
import ProductAnalyticsPage from "./ProductAnalyticsPage"
import UserJourneyPage from "./UserJourneyPage"
import BetaDashboardPage from "./BetaDashboardPage"
import RunStar from "./components/RunStar"
import { trackEvent } from "./lib/telemetry"

const API_BASE = import.meta.env.VITE_API_URL || ""
const POLL_MS = parseInt(import.meta.env.VITE_POLL_INTERVAL || "2000", 10)

const navGroups = [
  {
    group: "EXECUTION",
    items: [
      { id: "Run Design", icon: Play, label: "Run Design" },
      { id: "Run Matrix", icon: Grid, label: "Run Matrix" },
      { id: "Run Monitor", icon: Activity, label: "Run Monitor" },
      { id: "Important Runs", icon: Star, label: "Important Runs" },
      { id: "Artifacts", icon: Folder, label: "Artifacts" },
    ],
  },
  {
    group: "INTELLIGENCE",
    items: [
      { id: "QoR Analytics", icon: BarChart2, label: "QoR Analytics" },
      { id: "Regression Detector", icon: Zap, label: "Regression Detector" },
      { id: "Trends & Reports", icon: TrendingUp, label: "Trends & Reports" },
      { id: "Failure Atlas", icon: Map, label: "Failure Atlas" },
      { id: "Engineering Dashboard", icon: Shield, label: "Engineering" },
    ],
  },
  {
    group: "GOVERNANCE",
    items: [
      { id: "Provenance", icon: GitBranch, label: "Provenance" },
      { id: "Release Validation", icon: Shield, label: "Release Validation" },
      { id: "Policy Suite", icon: Sliders, label: "Policy Suite" },
    ],
  },
  {
    group: "BETA",
    items: [
      { id: "Beta Dashboard", icon: Award, label: "Beta Ops" },
      { id: "Feedback Center", icon: MessageSquare, label: "Feedback Center" },
      { id: "Product Analytics", icon: BarChart3, label: "Product Analytics" },
      { id: "User Journey", icon: Users, label: "User Journey" },
    ],
  },
  {
    group: "SYSTEM",
    items: [
      { id: "Infrastructure", icon: Server, label: "Infrastructure" },
      { id: "Telemetry", icon: Eye, label: "Telemetry" },
      { id: "Telemetry Health", icon: Activity, label: "Telemetry Health" },
      { id: "Telemetry Replay", icon: Upload, label: "Telemetry Replay" },
      { id: "Settings", icon: Settings, label: "Settings" },
      { id: "Help", icon: HelpCircle, label: "Help" },
    ],
  },
]

function QorScorePill({ score }) {
  let classes = "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium font-[Work_Sans] "
  if (score >= 0.80) {
    classes += "bg-[#FEF9E7] text-[#92751A]"
  } else if (score >= 0.65) {
    classes += "bg-[#FFF7ED] text-[#C2410C]"
  } else {
    classes += "bg-[#FEF2F2] text-[#C2410C] font-bold"
  }
  return <span className={classes}>{score.toFixed(2)}</span>
}

function StatusBadge({ status }) {
  const styles = {
    SUCCESS: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    COMPLETED: "bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]",
    FAILED: "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]",
    TIMEOUT: "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA]",
    PARTIAL: "bg-[#FEFCE8] text-[#A16207] border-[#FDE68A]",
    RUNNING: "bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]",
    REGRESSION: "bg-[#FEF2F2] text-[#C2410C] border-[#FECACA]",
  }
  const cls = styles[status] || "bg-[#F3F2ED] text-[#6B7280] border-[#E5E4E0]"
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full border text-[10px] font-bold font-[Work_Sans] ${cls}`}>
      {status}
    </span>
  )
}

function ReleaseStatusBadge({ status }) {
  if (status === "VALIDATED") {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-abyss-ink text-white text-[10px] font-bold font-[Work_Sans]">
        VALIDATED
      </span>
    )
  }
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-meridian-gold text-abyss-ink text-[10px] font-bold font-[Work_Sans]">
      PENDING
    </span>
  )
}

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-abyss-ink text-white px-3 py-2 rounded shadow-lg" style={{ fontFamily: "Work Sans, sans-serif", fontSize: 11 }}>
        <p className="font-medium">{label}</p>
        <p>Score: {payload[0].value.toFixed(2)}</p>
      </div>
    )
  }
  return null
}

function DonutCenter({ value, label }) {
  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
      <span className="text-[24px] font-bold font-[Eczar] text-abyss-ink leading-none">{value}</span>
      <span className="text-[10px] font-[Work_Sans] text-[#6B7280] mt-0.5">{label}</span>
    </div>
  )
}

function PieDonut({ data, centerValue, centerLabel, size, innerRatio }) {
  const total = data.reduce((s, d) => s + d.value, 0)
  const pieData = total > 0 ? data.map((d) => ({ ...d, value: d.value / total * 100 })) : data.map((d) => ({ ...d, value: 100 / data.length }))
  return (
    <div className="relative inline-flex" style={{ width: size, height: size }}>
      {size > 0 ? (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%" cy="50%"
              innerRadius={innerRatio * size / 2}
              outerRadius={size / 2 - 2}
              dataKey="value"
              strokeWidth={0}
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={data[i]?.color || "#D1D5DB"} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      ) : null}
      <DonutCenter value={centerValue} label={centerLabel} />
    </div>
  )
}

function normalizeTiming(wns) {
  if (wns == null) return 0.5
  const v = Math.min(1, Math.max(0, (wns + 1) / 2))
  return Math.round(v * 100) / 100
}

function App() {
  const [activeNav, setActiveNav] = useState("Dashboard")
  const [runs, setRuns] = useState([])
  const [liveRuns, setLiveRuns] = useState([])
  const [trends, setTrends] = useState(null)
  const [error, setError] = useState(null)
  const [selectedRun, setSelectedRun] = useState(null)
  const [releases, setReleases] = useState([])
  const [health, setHealth] = useState(null)
  const [viewingRuns, setViewingRuns] = useState(false)
  const [totalRunsCount, setTotalRunsCount] = useState(0)
  const [selectedDesign, setSelectedDesign] = useState("")

  const fetchData = () => {
    Promise.all([
      fetch(`${API_BASE}/runs?limit=10`).then(r => { if (!r.ok) throw new Error(`/runs ${r.status}`); return r.json() }),
      fetch(`${API_BASE}/runs/count`).then(r => r.ok ? r.json() : { total: 0 }),
      fetch(`${API_BASE}/live_runs`).then(r => { if (!r.ok) throw new Error(`/live_runs ${r.status}`); return r.json() }),
      fetch(`${API_BASE}/trends`).then(r => { if (!r.ok) throw new Error(`/trends ${r.status}`); return r.json() }),
      fetch(`${API_BASE}/releases`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/health`).then(r => r.ok ? r.json() : null),
    ])
      .then(([runsData, countData, liveData, trendsData, releasesData, healthData]) => {
        setRuns(runsData)
        setTotalRunsCount(countData.total ?? 0)
        setLiveRuns(liveData)
        setTrends(trendsData)
        setReleases(releasesData)
        setHealth(healthData)
        setError(null)
      })
      .catch((e) => {
        console.error("API fetch failed:", e)
        setError(e.message)
      })
  }

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, POLL_MS)
    return () => clearInterval(id)
  }, [])

  const totalRuns = runs.length
  const successfulRuns = runs.filter(r => r.status === "COMPLETED" || r.status === "SUCCESS").length
  const avgQor = totalRuns > 0 ? runs.reduce((s, r) => s + (r.qor_score ?? 0), 0) / totalRuns : 0
  const regressionsDetected = trends ? trends.regressions : runs.filter(r => (r.qor_score ?? 0) < 0.7).length
  const successRate = totalRuns > 0 ? Math.round(successfulRuns / totalRuns * 100) : 0
  const qorDiff = totalRuns > 1 ? (avgQor - (runs.at(-1)?.qor_score ?? 0)) : 0

  const latestRun = runs[0]

  const qorBreakdown = latestRun ? [
    { name: "Timing", value: normalizeTiming(latestRun.wns), color: "#22C55E" },
    { name: "Utilization", value: Math.min(1, (latestRun.utilization ?? 0) / 100), color: "#3B82F6" },
    { name: "Cell Count", value: Math.min(1, (latestRun.cell_count ?? 0) / 200), color: "#A855F7" },
    { name: "QoR Score", value: latestRun.qor_score ?? 0, color: "#D4AF37" },
    { name: "Runtime", value: Math.min(1, 60 / (latestRun.runtime_sec || 60)), color: "#F59E0B" },
  ] : [
    { name: "Timing", value: 0, color: "#22C55E" },
    { name: "Utilization", value: 0, color: "#3B82F6" },
    { name: "Cell Count", value: 0, color: "#A855F7" },
    { name: "QoR Score", value: 0, color: "#D4AF37" },
    { name: "Runtime", value: 0, color: "#F59E0B" },
  ]
  const overallQor = latestRun ? latestRun.qor_score?.toFixed(2) : "—"

  const healthStatuses = [
    { label: "Success Rate", status: totalRuns > 0 ? `${successRate}%` : "No data" },
    { label: "Total Runs", status: totalRuns > 0 ? `${totalRuns} runs` : "No data" },
    { label: "Live Runs", status: liveRuns.length > 0 ? `${liveRuns.length} active` : "Idle" },
    { label: "Regressions", status: regressionsDetected > 0 ? `${regressionsDetected} found` : "None" },
  ]

  const releaseVersions = (releases.length > 0 ? releases : [...runs]
    .filter(r => r.qor_score != null)
    .sort((a, b) => (b.qor_score ?? 0) - (a.qor_score ?? 0))
    .slice(0, 3))
    .map(r => ({
      name: r.run_id,
      score: r.qor_score?.toFixed(2) || "—",
      status: r.status === "SUCCESS" || r.status === "COMPLETED" ? "VALIDATED" : r.status || "PENDING",
    }))

  const stageColors = [
    { bg: "#EFF6FF", iconColor: "#3B82F6" },
    { bg: "#F0FDF4", iconColor: "#16A34A" },
    { bg: "#FDF4FF", iconColor: "#A855F7" },
    { bg: "#FEF2F2", iconColor: "#C2410C" },
    { bg: "#FFF7ED", iconColor: "#F59E0B" },
    { bg: "#EFF6FF", iconColor: "#3B82F6" },
    { bg: "#F0FDF4", iconColor: "#16A34A" },
    { bg: "#FDF4FF", iconColor: "#A855F7" },
  ]
  const toolList = ["openroad", "yosys", "klayout", "magic", "netgen"]
  const capabilities = toolList.map((name, i) => ({
    ...stageColors[i % stageColors.length],
    label: name.charAt(0).toUpperCase() + name.slice(1),
    available: health?.tools?.[name] ?? null,
  }))

  const notificationCount = regressionsDetected || (error ? 1 : 0)
  const uniqueSuccessfulDesigns = [...new Set(runs.filter(r => r.status === "SUCCESS" || r.status === "COMPLETED").map(r => r.design_name))]
  const releasesValidated = uniqueSuccessfulDesigns.length
  const readyForRelease = runs.filter(r => r.qor_score != null && r.qor_score >= 0.7).length
  const designNames = [...new Set(runs.map(r => r.design_name).filter(Boolean))].sort()

  const qorTrendData = [...runs]
    .filter(r => !selectedDesign || r.design_name === selectedDesign)
    .reverse()
    .map(r => ({
      date: r.timestamp ? r.timestamp.slice(5, 10) : "",
      score: r.qor_score ?? 0
    }))

  const handleToggleImportant = (runId, isImportant) => {
    fetch(`${API_BASE}/runs/${runId}/important`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_important: isImportant }),
    })
      .then(r => r.ok ? setRuns(prev => prev.map(r => r.run_id === runId ? { ...r, is_important: isImportant ? 1 : 0 } : r)) : null)
      .catch(e => console.error("Failed to toggle importance:", e))
  }

  const recentRuns = runs.map(r => ({
    runId: r.run_id,
    design: r.design_name,
    flow: "GLI-FLOW",
    status: r.status === "COMPLETED" ? "SUCCESS" : r.status,
    qorScore: r.qor_score ?? 0,
    runtime: r.runtime_sec ? `${Math.floor(r.runtime_sec / 60)}m ${Math.round(r.runtime_sec % 60)}s` : "—",
    date: r.timestamp ? r.timestamp.slice(0, 16).replace("T", " ") : "",
    failureCount: r.failure_count ?? 0,
    maxSeverity: r.max_severity || "",
    isImportant: r.is_important === 1
  }))

  const isConnected = error === null

  if (selectedRun) {
    return (
      <div className="flex h-screen w-full overflow-hidden bg-canvas-bone" style={{ fontFamily: "Work Sans, sans-serif" }}>
        <aside className="w-[220px] min-w-[220px] h-full bg-abyss-ink flex flex-col flex-shrink-0">
          <div className="px-5 pt-6 pb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-meridian-gold flex items-center justify-center text-abyss-ink font-bold font-[Eczar] text-sm">G</div>
              <span className="text-white font-[Eczar] text-lg font-semibold tracking-tight">tapeitout</span>
            </div>
            <p className="text-[9px] font-[Work_Sans] text-stone-ridge mt-1 ml-10">Execution Intelligence</p>
          </div>
        </aside>
        <div className="flex-1 flex flex-col min-w-0 h-full">
          <main className="flex-1 overflow-y-auto px-6 py-5">
            <RunDetail runId={selectedRun} onBack={() => setSelectedRun(null)} />
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-canvas-bone" style={{ fontFamily: "Work Sans, sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Eczar:wght@400;600;700&family=Playfair+Display:wght@400;600;700&family=Work+Sans:wght@300;400;500;600&family=Cascadia+Code:wght@400&display=swap');
      `}</style>

      {/* === SIDEBAR === */}
      <aside className="w-[220px] min-w-[220px] h-full bg-abyss-ink flex flex-col flex-shrink-0">
        <div className="px-5 pt-6 pb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-meridian-gold flex items-center justify-center text-abyss-ink font-bold font-[Eczar] text-sm">G</div>
            <span className="text-white font-[Eczar] text-lg font-semibold tracking-tight">tapeitout</span>
          </div>
          <p className="text-[9px] font-[Work_Sans] text-stone-ridge mt-1 ml-10">Execution Intelligence</p>
        </div>
        <div className="h-px bg-[#1E293B] mx-5" />

        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
          <div className="mb-3">
            <button
              onClick={() => setActiveNav("Dashboard")}
              className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded text-xs font-[Work_Sans] transition-colors ${
                activeNav === "Dashboard"
                  ? "bg-surface-dark text-white border-l-[3px] border-meridian-gold rounded-l-none"
                  : "text-[#94A3B8] hover:bg-surface-dark"
              }`}
            >
              <LayoutDashboard size={14} strokeWidth={1.5} />
              <span className="text-[11px]">Dashboard</span>
            </button>
          </div>
          {navGroups.map((group) => (
            <div key={group.group}>
              <p className="text-[8px] font-[Work_Sans] uppercase tracking-widest text-stone-ridge px-2 mb-1.5">{group.group}</p>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const isActive = activeNav === item.id
                  const Icon = item.icon
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveNav(item.id)}
                      className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded text-xs font-[Work_Sans] transition-colors ${
                        isActive
                          ? "bg-surface-dark text-white border-l-[3px] border-meridian-gold rounded-l-none"
                          : "text-[#94A3B8] hover:bg-surface-dark"
                      }`}
                    >
                      <Icon size={14} strokeWidth={1.5} />
                      <span className="text-[11px]">{item.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-[#1E293B] px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-surface-mid flex items-center justify-center text-white text-xs font-bold font-[Work_Sans]">
              {totalRuns > 0 ? totalRuns : "0"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-xs font-[Work_Sans] truncate">Operator</p>
              {liveRuns.length > 0 && (
                <span className="inline-block mt-0.5 px-1.5 py-0.5 rounded text-[8px] font-bold font-[Work_Sans] uppercase tracking-wider bg-[#2563EB] text-white">
                  {liveRuns.length} active
                </span>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* === MAIN CONTENT === */}
      <div className="flex-1 flex flex-col min-w-0 h-full">

        {/* === TOPBAR === */}
        <header className="sticky top-0 z-10 bg-canvas-bone border-b border-stone-ridge px-6 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-4">
            <Menu size={20} className="text-abyss-ink cursor-pointer" />
            <div>
              <h1 className="font-[Eczar] text-[20px] text-abyss-ink leading-tight">GLI-FLOW Dashboard</h1>
              <p className="font-[Work_Sans] text-[11px] text-[#6B7280]">Execution Intelligence for ASIC Infrastructure</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 border border-stone-ridge bg-white rounded-md px-3 py-1.5 text-xs font-[Work_Sans] text-abyss-ink cursor-pointer">
              <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-[#22C55E]" : "bg-topography-rust"}`} />
              <span>{isConnected ? "Connected" : "Offline"}</span>
              <ChevronDown size={14} />
            </div>
            <div className="relative cursor-pointer">
              <Bell size={20} className="text-[#6B7280]" />
              {notificationCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-topography-rust text-white text-[8px] font-bold flex items-center justify-center">
                  {notificationCount > 9 ? "9+" : notificationCount}
                </span>
              )}
            </div>
            <Settings size={20} className="text-[#6B7280] cursor-pointer" />
            <div className="flex items-center gap-2 border border-stone-ridge bg-white rounded-full px-3 py-1">
              <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-[#22C55E]" : "bg-topography-rust animate-pulse"} ${liveRuns.length > 0 ? "pulse-dot" : ""}`} />
              <span className="text-[11px] font-[Work_Sans] text-abyss-ink whitespace-nowrap">
                {error ? "Connection Error" : liveRuns.length > 0 ? `${liveRuns.length} run(s) active` : "All Systems Operational"}
              </span>
            </div>
          </div>
        </header>

        {/* === SCROLLABLE CONTENT === */}
        <main className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
          {activeNav === "Important Runs" ? (
            <RunsPage importantOnly={true} onBack={() => setActiveNav("Dashboard")} onSelectRun={setSelectedRun} />
          ) : viewingRuns ? (
            <RunsPage onBack={() => setViewingRuns(false)} onSelectRun={setSelectedRun} />
          ) : activeNav === "Run Design" ? (
            <RunDesignPage />
          ) : activeNav === "Run Matrix" ? (
            <RunMatrixPage />
          ) : activeNav === "Run Monitor" ? (
            <RunMonitorPage />
          ) : activeNav === "Artifacts" ? (
            <ArtifactsPage />
          ) : activeNav === "Engineering Dashboard" ? (
            <EngineeringDashboardPage />
          ) : activeNav === "Failure Atlas" ? (
            <FailureAtlasPage designFilter={selectedDesign} />
          ) : activeNav === "QoR Analytics" ? (
            <QoRAnalyticsPage onSelectRun={setSelectedRun} />
          ) : activeNav === "Regression Detector" ? (
            <RegressionDetectorPage onSelectRun={setSelectedRun} />
          ) : activeNav === "Trends & Reports" ? (
            <TrendsReportsPage onSelectRun={setSelectedRun} />
          ) : activeNav === "Provenance" ? (
            <ProvenancePage />
          ) : activeNav === "Release Validation" ? (
            <ReleaseValidationPage onSelectRun={setSelectedRun} />
          ) : activeNav === "Policy Suite" ? (
            <PolicySuitePage />
          ) : activeNav === "Infrastructure" ? (
            <InfrastructurePage />
          ) : activeNav === "Telemetry" ? (
            <TelemetryPage />
          ) : activeNav === "Telemetry Health" ? (
            <TelemetryHealthPage />
          ) : activeNav === "Telemetry Replay" ? (
            <TelemetryReplayPage />
          ) : activeNav === "Settings" ? (
            <SettingsPage />
          ) : activeNav === "Beta Dashboard" ? (
            <BetaDashboardPage />
          ) : activeNav === "Feedback Center" ? (
            <FeedbackCenterPage />
          ) : activeNav === "Product Analytics" ? (
            <ProductAnalyticsPage />
          ) : activeNav === "User Journey" ? (
            <UserJourneyPage />
          ) : activeNav === "Help" ? (
            <HelpPage />
          ) : (
          <>

          {/* === METRIC CARDS ROW === */}
          <div className="grid grid-cols-5 gap-4">
            <div className="bg-white border border-stone-ridge rounded-lg shadow-sm p-5">
              <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><BarChart2 size={16} color="#3B82F6" /></div>
              <p className="font-[Work_Sans] text-[12px] text-[#6B7280]">Total Runs</p>
              <p className="font-[Eczar] text-[28px] text-abyss-ink font-semibold leading-tight mt-1">{totalRunsCount}</p>
              <p className="font-[Work_Sans] text-[11px] text-[#6B7280] mt-1">{totalRunsCount} total in database</p>
            </div>
            <div className="bg-white border border-stone-ridge rounded-lg shadow-sm p-5">
              <div className="w-8 h-8 rounded bg-[#F0FDF4] flex items-center justify-center mb-3"><CheckCircle size={16} color="#22C55E" /></div>
              <p className="font-[Work_Sans] text-[12px] text-[#6B7280]">Successful Runs</p>
              <p className="font-[Eczar] text-[28px] text-abyss-ink font-semibold leading-tight mt-1">{successfulRuns}</p>
              <p className="font-[Work_Sans] text-[11px] text-[#22C55E] mt-1">{successRate}% success rate</p>
            </div>
            <div className="bg-white border border-stone-ridge rounded-lg shadow-sm p-5">
              <div className="w-8 h-8 rounded bg-[#FDF4FF] flex items-center justify-center mb-3"><Star size={16} color="#A855F7" /></div>
              <p className="font-[Work_Sans] text-[12px] text-[#6B7280]">Avg QoR Score</p>
              <p className="font-[Eczar] text-[28px] text-abyss-ink font-semibold leading-tight mt-1">{avgQor.toFixed(2)}</p>
              <p className="font-[Work_Sans] text-[11px] text-[#22C55E] mt-1">{qorDiff > 0 ? "↑" : qorDiff < 0 ? "↓" : "="} {Math.abs(qorDiff).toFixed(2)} vs earliest</p>
            </div>
            <div className="bg-white border border-stone-ridge rounded-lg shadow-sm p-5">
              <div className="w-8 h-8 rounded bg-[#FFF7ED] flex items-center justify-center mb-3"><AlertTriangle size={16} color="#F59E0B" /></div>
              <p className="font-[Work_Sans] text-[12px] text-[#6B7280]">Regressions Detected</p>
              <p className="font-[Eczar] text-[28px] text-topography-rust font-semibold leading-tight mt-1">{regressionsDetected}</p>
              <p className="font-[Work_Sans] text-[11px] text-topography-rust mt-1">Needs investigation</p>
            </div>
            <div className="bg-white border border-stone-ridge rounded-lg shadow-sm p-5">
              <div className="w-8 h-8 rounded bg-[#EFF6FF] flex items-center justify-center mb-3"><Shield size={16} color="#3B82F6" /></div>
              <p className="font-[Work_Sans] text-[12px] text-[#6B7280]">Unique Designs</p>
              <p className="font-[Eczar] text-[28px] text-abyss-ink font-semibold leading-tight mt-1">{releasesValidated}</p>
              <p className="font-[Work_Sans] text-[11px] text-[#22C55E] mt-1">{readyForRelease} with QoR ≥ 0.70</p>
            </div>
          </div>

          {/* === MIDDLE ROW: QoR Trend + Breakdown/Health === */}
          <div className="grid grid-cols-[60%_40%] gap-4">

            {/* QoR Score Trend */}
            <div className="bg-white border border-stone-ridge rounded-lg p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink">QoR Score Trend</h2>
                <div className="relative">
                  <select
                    value={selectedDesign}
                    onChange={(e) => {
                      const design = e.target.value
                      setSelectedDesign(design)
                      const filtered = runs.filter(r => !design || r.design_name === design)
                      trackEvent("dashboard_design_filter_changed", {
                        design: design || "All Designs",
                        source: "qor_trend",
                        run_count_visible: filtered.length
                      })
                    }}
                    className="border border-stone-ridge bg-white rounded-md px-3 py-1 text-xs font-[Work_Sans] text-abyss-ink cursor-pointer appearance-none pr-7"
                  >
                    <option value="">All Designs</option>
                    {designNames.map(name => (
                      <option key={name} value={name}>{name}</option>
                    ))}
                  </select>
                  <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#6B7280] pointer-events-none" />
                </div>
              </div>
              <div style={{ height: 200 }}>
                {qorTrendData.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-[#6B7280] text-xs font-[Work_Sans]">
                    {selectedDesign ? "No QoR data available for this design" : "No run data yet — run a design to see QoR trends"}
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={qorTrendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="qorGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#D4AF37" stopOpacity={0.2} />
                          <stop offset="100%" stopColor="#D4AF37" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#F3F2ED" strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontFamily: "Work Sans, sans-serif", fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 1]} tick={{ fontFamily: "Work Sans, sans-serif", fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} tickFormatter={(v) => v.toFixed(1)} />
                      <Tooltip content={<CustomTooltip />} />
                      <ReferenceLine y={0.70} stroke="#C2410C" strokeDasharray="4 4" strokeWidth={1} label={{ value: "Threshold: 0.70", position: "insideTopRight", fill: "#C2410C", fontFamily: "Work Sans, sans-serif", fontSize: 9 }} />
                      <Area type="monotone" dataKey="score" stroke="#D4AF37" strokeWidth={2} fill="url(#qorGrad)" dot={{ fill: "#D4AF37", strokeWidth: 0, r: 3 }} />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Right stack: Breakdown + Health */}
            <div className="flex flex-col gap-4">

              {/* QoR Score Breakdown */}
              <div className="bg-white border border-stone-ridge rounded-lg p-5">
                <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">QoR Score Breakdown</h3>
                <div className="flex items-center">
                  <div style={{ width: 140, height: 140 }}>
                    <PieDonut data={qorBreakdown} centerValue={overallQor} centerLabel="Latest Run" size={140} innerRatio={0.65} />
                  </div>
                  <div className="ml-3 space-y-2">
                    {qorBreakdown.map((item) => (
                      <div key={item.name} className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                        <span className="font-[Work_Sans] text-[11px] text-abyss-ink">{item.name}</span>
                        <span className="font-[Work_Sans] text-[11px] text-[#6B7280] ml-auto">{item.value.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {latestRun && (
                  <div className="mt-3 text-[10px] font-[Work_Sans] text-[#6B7280]">
                    Run: {latestRun.run_id} · Stage: {latestRun.current_stage} · Progress: {latestRun.progress}%
                  </div>
                )}
              </div>

              {/* Execution Health */}
              <div className="bg-white border border-stone-ridge rounded-lg p-5">
                <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Execution Health</h3>
                <div className="flex items-center">
                  <div className="relative" style={{ width: 120, height: 120 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[{ value: successRate }, { value: 100 - successRate }]}
                          cx="50%" cy="50%"
                          innerRadius={38}
                          outerRadius={58}
                          dataKey="value"
                          startAngle={90}
                          endAngle={-270}
                          strokeWidth={0}
                        >
                          <Cell fill="#22C55E" />
                          <Cell fill="#F3F2ED" />
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                    <DonutCenter value={`${successRate}%`} label="" />
                  </div>
                  <div className="ml-4 space-y-2.5">
                    {healthStatuses.map((h) => (
                      <div key={h.label} className="flex items-center justify-between gap-4">
                        <span className="font-[Work_Sans] text-[11px] text-abyss-ink">{h.label}</span>
                        <span className="font-[Work_Sans] text-[11px] text-[#22C55E] flex items-center gap-1">
                          {h.status} <span className="text-[8px]">●</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                {liveRuns.length > 0 && (
                  <div className="mt-3 text-[10px] font-[Work_Sans] text-[#2563EB]">
                    {liveRuns.length} run(s) in progress
                  </div>
                )}
              </div>

            </div>
          </div>

          {/* === BOTTOM ROW: Recent Runs + Release/Infra === */}
          <div className="grid grid-cols-[60%_40%] gap-4">

            {/* Recent Runs */}
            <div className="bg-white border border-stone-ridge rounded-lg p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-[Playfair_Display] text-[16px] text-abyss-ink">Recent Runs</h2>
                <button onClick={() => setViewingRuns(true)} className="font-[Work_Sans] text-[11px] text-meridian-gold hover:underline cursor-pointer">View All Runs →</button>
              </div>
              <div className="overflow-x-auto">
                {recentRuns.length === 0 ? (
                  <div className="py-8 text-center text-[#6B7280] text-xs font-[Work_Sans]">
                    No runs yet — execute <code className="bg-[#F3F2ED] px-1 rounded">gli-flow run examples/tiny_or --mock</code> to get started
                  </div>
                ) : (
                  <table className="w-full font-[Work_Sans]">
                    <thead>
                      <tr className="text-[11px] text-[#6B7280] border-b border-stone-ridge">
                        <th className="px-4 py-3"></th>
                        <th className="text-left pb-2 font-medium">Run ID</th>
                        <th className="text-left pb-2 font-medium">Design</th>
                        <th className="text-left pb-2 font-medium">Flow</th>
                        <th className="text-left pb-2 font-medium">Status</th>
                        <th className="text-left pb-2 font-medium">QoR Score</th>
                        <th className="text-left pb-2 font-medium">Failures</th>
                        <th className="text-left pb-2 font-medium">Runtime</th>
                        <th className="text-left pb-2 font-medium">Date</th>
                        <th className="pb-2"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentRuns.map((run, i) => (
                        <tr key={run.runId} className={`text-xs border-b border-stone-ridge/50 ${i % 2 === 1 ? "bg-[#FAFAF8]" : ""} cursor-pointer hover:bg-[#F3F2ED]`} onClick={() => setSelectedRun(run.runId)}>
                          <td className="px-4 py-3">
                            <RunStar isImportant={run.isImportant} onClick={(v) => handleToggleImportant(run.runId, v)} />
                          </td>
                          <td className="py-2.5 pr-2 font-medium text-abyss-ink">{run.runId}</td>
                          <td className="py-2.5 pr-2 text-[#6B7280]">{run.design}</td>
                          <td className="py-2.5 pr-2 text-[#6B7280]">{run.flow}</td>
                          <td className="py-2.5 pr-2"><StatusBadge status={run.status} /></td>
                          <td className="py-2.5 pr-2"><QorScorePill score={run.qorScore} /></td>
                          <td className="py-2.5 pr-2">
                            {run.failureCount > 0 ? (
                              <span className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                                run.maxSeverity === "TAPEOUT_BLOCKING" ? "bg-red-100 text-red-700" : run.maxSeverity === "UNDER_REVIEW" ? "bg-purple-100 text-purple-700" : "bg-orange-100 text-orange-700"
                              }`}>
                                <AlertTriangle size={10} />
                                {run.failureCount}
                              </span>
                            ) : (
                              <span className="text-[10px] text-[#6B7280]">—</span>
                            )}
                          </td>
                          <td className="py-2.5 pr-2 text-[#6B7280]">{run.runtime}</td>
                          <td className="py-2.5 pr-2 text-[#6B7280] whitespace-nowrap">{run.date}</td>
                          <td className="py-2.5"><MoreVertical size={14} className="text-[#6B7280] cursor-pointer" /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                )}
              </div>
              <div className="flex items-center gap-4 mt-4 font-[Work_Sans] text-[10px] text-[#6B7280]">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#22C55E]" /> Success</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-topography-rust" /> Regression</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#991B1B]" /> Failed</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#3B82F6]" /> Running</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#9CA3AF]" /> Pending</span>
              </div>
            </div>

            {/* Right stack: Release Validation + Infrastructure */}
            <div className="flex flex-col gap-4">

              {/* Release Validation */}
              <div className="bg-white border border-stone-ridge rounded-lg p-5">
                <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Top Runs</h3>
                {releaseVersions.length === 0 ? (
                  <div className="py-4 text-center text-[#6B7280] text-xs font-[Work_Sans]">
                    No runs with QoR scores yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {releaseVersions.map((v) => (
                      <div key={v.name} className="flex items-center justify-between">
                        <div className="min-w-0">
                          <p className="font-[Work_Sans] text-[12px] text-abyss-ink truncate max-w-[160px]" title={v.name}>{v.name}</p>
                          <p className="font-[Work_Sans] text-[11px] text-[#6B7280]">Score: {v.score}</p>
                        </div>
                        <ReleaseStatusBadge status={v.status} />
                      </div>
                    ))}
                  </div>
                )}
                <div className="mt-4">
                  <a href="#" className="font-[Work_Sans] text-[11px] text-meridian-gold hover:underline flex items-center gap-1">
                    View all releases <ExternalLink size={11} />
                  </a>
                </div>
              </div>

              {/* Infrastructure Capabilities */}
              <div className="bg-white border border-stone-ridge rounded-lg p-5">
                <h3 className="font-[Playfair_Display] text-[14px] text-abyss-ink mb-4">Pipeline Capabilities</h3>
                <div className="grid grid-cols-2 gap-2">
                  {capabilities.map((cap) => (
                    <div key={cap.label} className="flex items-center gap-2 p-2 rounded-md hover:bg-[#FAFAF8] transition-colors">
                      <div className="w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0" style={{ backgroundColor: cap.bg }}>
                        <div className="w-5 h-5 rounded flex items-center justify-center" style={{ backgroundColor: cap.iconColor, opacity: 0.2 }} />
                      </div>
                      <span className="font-[Work_Sans] text-[10px] text-abyss-ink leading-tight">{cap.label}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-3">
                  <a href="#" className="font-[Work_Sans] text-[11px] text-meridian-gold hover:underline flex items-center gap-1">
                    View all capabilities <ExternalLink size={11} />
                  </a>
                </div>
              </div>

            </div>
          </div>

          <div className="h-14" />
          </>
          )}
        </main>
      </div>

      {/* === BOTTOM FOOTER BAR === */}
      <footer className="fixed bottom-0 left-[220px] right-0 bg-white border-t border-stone-ridge px-6 py-2.5 flex items-center justify-between z-20">
        <span className="font-[Work_Sans] text-[11px] text-[#6B7280]">GLI-FLOW v1.0.0 MVP</span>
        <span className="font-[Work_Sans] text-[11px] text-[#6B7280]">Execution Intelligence for ASIC Infrastructure</span>
        <div className="flex items-center gap-4">
          <a href="#" className="font-[Work_Sans] text-[11px] text-abyss-ink hover:underline flex items-center gap-1">Documentation <ExternalLink size={10} /></a>
          <a href="#" className="font-[Work_Sans] text-[11px] text-abyss-ink hover:underline flex items-center gap-1">GitHub <ExternalLink size={10} /></a>
          <span className={`flex items-center gap-1.5 font-[Work_Sans] text-[11px] ${isConnected ? "text-[#16A34A]" : "text-topography-rust"}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-[#16A34A]" : "bg-topography-rust"}`} />
            {isConnected ? "Connected" : "Offline"}
          </span>
        </div>
      </footer>
    </div>
  )
}

export default App
