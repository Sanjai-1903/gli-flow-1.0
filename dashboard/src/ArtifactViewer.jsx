import { useState, useEffect, useRef, useCallback } from "react"
import {
  Search, FileText, FileImage, File, Download, Maximize2, Minimize2,
  Copy, Check, X, ChevronUp, ChevronDown, Filter, ZoomIn, ZoomOut,
  ArrowLeft, ArrowRight, ExternalLink, AlertTriangle
} from "lucide-react"

const API_BASE = import.meta.env.VITE_API_URL || ""
const TEXT_PREVIEW_MB = 10

const FILE_ICONS = {
  rpt: { icon: FileText, color: "text-blue-600" },
  log: { icon: FileText, color: "text-amber-600" },
  txt: { icon: FileText, color: "text-gray-600" },
  csv: { icon: FileText, color: "text-green-600" },
  json: { icon: FileText, color: "text-purple-600" },
  yaml: { icon: FileText, color: "text-cyan-600" },
  yml: { icon: FileText, color: "text-cyan-600" },
  md: { icon: FileText, color: "text-blue-600" },
  v: { icon: FileText, color: "text-orange-600" },
  sv: { icon: FileText, color: "text-orange-600" },
  vhdl: { icon: FileText, color: "text-orange-600" },
  tcl: { icon: FileText, color: "text-teal-600" },
  py: { icon: FileText, color: "text-yellow-600" },
  png: { icon: FileImage, color: "text-green-600" },
  jpg: { icon: FileImage, color: "text-green-600" },
  jpeg: { icon: FileImage, color: "text-green-600" },
  webp: { icon: FileImage, color: "text-green-600" },
  svg: { icon: FileImage, color: "text-green-600" },
  pdf: { icon: File, color: "text-red-600" },
  html: { icon: File, color: "text-blue-600" },
  htm: { icon: File, color: "text-blue-600" },
  gds: { icon: File, color: "text-purple-600" },
  def: { icon: File, color: "text-purple-600" },
  lef: { icon: File, color: "text-purple-600" },
}

function getFileIcon(name) {
  const ext = name.split(".").pop().toLowerCase()
  const info = FILE_ICONS[ext]
  if (info) {
    const Icon = info.icon
    return <Icon size={14} className={info.color} />
  }
  return <File size={14} className="text-gray-400" />
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function SearchBar({ value, onChange, placeholder }) {
  return (
    <div className="relative">
      <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-[#6B7280]" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Search..."}
        className="w-full pl-6 pr-2 py-1.5 text-[11px] border border-stone-ridge rounded bg-white focus:outline-none focus:border-meridian-gold"
      />
    </div>
  )
}

function TextViewer({ content, truncated, fileName, onClose, onDownload }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchMatches, setSearchMatches] = useState([])
  const [currentMatch, setCurrentMatch] = useState(-1)
  const [copied, setCopied] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  const [lineCount, setLineCount] = useState(0)
  const searchRef = useRef(null)
  const contentRef = useRef(null)

  const lines = content ? content.split("\n") : []
  useEffect(() => { setLineCount(lines.length) }, [content])

  const handleSearch = useCallback((query) => {
    setSearchQuery(query)
    if (!query) { setSearchMatches([]); setCurrentMatch(-1); return }
    const matches = []
    lines.forEach((line, i) => {
      let idx = 0
      const lower = line.toLowerCase()
      const lowerQ = query.toLowerCase()
      while (idx < line.length) {
        const pos = lower.indexOf(lowerQ, idx)
        if (pos === -1) break
        matches.push({ line: i, col: pos })
        idx = pos + 1
      }
    })
    setSearchMatches(matches)
    setCurrentMatch(matches.length > 0 ? 0 : -1)
  }, [lines])

  const goToMatch = (dir) => {
    if (searchMatches.length === 0) return
    let next = currentMatch + dir
    if (next < 0) next = searchMatches.length - 1
    if (next >= searchMatches.length) next = 0
    setCurrentMatch(next)
    const m = searchMatches[next]
    if (contentRef.current) {
      const target = contentRef.current.querySelector(`[data-line="${m.line}"]`)
      if (target) target.scrollIntoView({ behavior: "smooth", block: "center" })
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(content).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000) })
  }

  const highlightLine = (lineIdx) => {
    if (!searchQuery) return null
    const match = searchMatches.find(m => m.line === lineIdx && currentMatch >= 0 && searchMatches[currentMatch]?.line === lineIdx && searchMatches[currentMatch]?.col === searchMatches.find(m2 => m2.line === lineIdx && m2.col === m.col)?.col)
    if (match && searchMatches.indexOf(match) === currentMatch)
      return "bg-yellow-300"
    if (searchMatches.some(m => m.line === lineIdx))
      return "bg-yellow-100"
    return null
  }

  const containerClass = fullscreen
    ? "fixed inset-0 z-50 bg-white flex flex-col"
    : "flex flex-col h-full"

  return (
    <div className={containerClass}>
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-stone-ridge bg-[#FAFAF8] text-[11px]">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="font-medium text-abyss-ink truncate">{fileName}</span>
          <span className="text-[#6B7280]">{lineCount} lines{truncated ? " (truncated)" : ""}</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="relative flex items-center">
            <input
              ref={searchRef}
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Find..."
              className="w-28 pl-2 pr-1 py-0.5 text-[10px] border border-stone-ridge rounded focus:outline-none focus:border-meridian-gold"
            />
            {searchQuery && (
              <div className="flex items-center ml-1">
                <span className="text-[9px] text-[#6B7280] min-w-[3rem]">
                  {currentMatch >= 0 ? `${currentMatch + 1}/${searchMatches.length}` : "0/0"}
                </span>
                <button onClick={() => goToMatch(-1)} className="p-0.5 hover:bg-gray-200 rounded"><ChevronUp size={12} /></button>
                <button onClick={() => goToMatch(1)} className="p-0.5 hover:bg-gray-200 rounded"><ChevronDown size={12} /></button>
              </div>
            )}
          </div>
          <div className="w-px h-4 bg-stone-ridge mx-1" />
          <button onClick={handleCopy} className="p-1 hover:bg-gray-200 rounded" title="Copy content">
            {copied ? <Check size={12} className="text-green-600" /> : <Copy size={12} />}
          </button>
          <button onClick={onDownload} className="p-1 hover:bg-gray-200 rounded" title="Download">
            <Download size={12} />
          </button>
          <button onClick={() => setFullscreen(!fullscreen)} className="p-1 hover:bg-gray-200 rounded" title={fullscreen ? "Exit fullscreen" : "Fullscreen"}>
            {fullscreen ? <Minimize2 size={12} /> : <Maximize2 size={12} />}
          </button>
          {onClose && (
            <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded" title="Close">
              <X size={12} />
            </button>
          )}
        </div>
      </div>
      <div ref={contentRef} className="flex-1 overflow-auto bg-white font-mono text-[10px] leading-relaxed">
        {truncated && (
          <div className="sticky top-0 z-10 bg-amber-50 border-b border-amber-200 px-3 py-1.5 text-[10px] text-amber-700 flex items-center gap-1">
            <AlertTriangle size={10} /> Preview truncated. Download the full file for complete content.
          </div>
        )}
        <table className="w-full border-collapse">
          <tbody>
            {lines.map((line, i) => {
              const hl = highlightLine(i)
              return (
                <tr key={i} data-line={i} className={hl || (i % 2 === 0 ? "bg-[#FAFAF8]" : "")}>
                  <td className="select-none text-right text-[#6B7280] px-2 py-0 w-12 border-r border-stone-ridge align-top text-[9px]">
                    {i + 1}
                  </td>
                  <td className={`px-3 py-0 whitespace-pre-wrap break-all ${hl || ""}`}>
                    {line || " "}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ImageViewer({ src, fileName, onClose }) {
  const [zoom, setZoom] = useState(1)
  const [fitWidth, setFitWidth] = useState(true)
  const imgRef = useRef(null)

  const handleWheel = (e) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault()
      setZoom(z => Math.max(0.1, Math.min(10, z - e.deltaY * 0.001)))
      setFitWidth(false)
    }
  }

  useEffect(() => {
    const handleKey = (e) => {
      if (e.ctrlKey && e.key === "0") { setZoom(1); setFitWidth(true) }
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [])

  const handleFitWidth = () => {
    setFitWidth(true)
    setZoom(1)
  }

  const imgStyle = fitWidth
    ? { maxWidth: "100%", height: "auto" }
    : { transform: `scale(${zoom})`, transformOrigin: "top left" }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-stone-ridge bg-[#FAFAF8] text-[11px]">
        <span className="font-medium text-abyss-ink truncate">{fileName}</span>
        <div className="flex items-center gap-1">
          <button onClick={() => { setZoom(z => Math.max(0.1, z - 0.25)); setFitWidth(false) }} className="p-1 hover:bg-gray-200 rounded" title="Zoom out"><ZoomOut size={12} /></button>
          <span className="text-[10px] text-[#6B7280] min-w-[3rem] text-center">{Math.round(zoom * 100)}%</span>
          <button onClick={() => { setZoom(z => Math.min(10, z + 0.25)); setFitWidth(false) }} className="p-1 hover:bg-gray-200 rounded" title="Zoom in"><ZoomIn size={12} /></button>
          <button onClick={handleFitWidth} className={`p-1 rounded ${fitWidth ? "bg-meridian-gold text-abyss-ink" : "hover:bg-gray-200"}`} title="Fit width"><Maximize2 size={12} /></button>
          <div className="w-px h-4 bg-stone-ridge mx-1" />
          <a href={src} download={fileName} className="p-1 hover:bg-gray-200 rounded" title="Download"><Download size={12} /></a>
          <a href={src} target="_blank" rel="noreferrer" className="p-1 hover:bg-gray-200 rounded" title="Open original"><ExternalLink size={12} /></a>
          {onClose && (
            <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded" title="Close"><X size={12} /></button>
          )}
        </div>
      </div>
      <div
        className="flex-1 overflow-auto bg-[#F3F4F6] flex items-start justify-center p-4"
        onWheel={handleWheel}
      >
        <img ref={imgRef} src={src} alt={fileName} style={imgStyle} className="shadow-lg rounded" />
      </div>
    </div>
  )
}

function HtmlViewer({ src, fileName, onClose }) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-stone-ridge bg-[#FAFAF8] text-[11px]">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="font-medium text-abyss-ink truncate">{fileName}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-amber-100 text-amber-700 border border-amber-200">SANDBOXED</span>
        </div>
        <div className="flex items-center gap-1">
          <a href={src} download={fileName} className="p-1 hover:bg-gray-200 rounded" title="Download"><Download size={12} /></a>
          {onClose && (
            <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded" title="Close"><X size={12} /></button>
          )}
        </div>
      </div>
      <div className="flex-1 bg-white">
        <iframe
          src={src}
          title={fileName}
          className="w-full h-full border-0"
          sandbox="allow-same-origin"
          referrerPolicy="no-referrer"
        />
      </div>
    </div>
  )
}

function PdfViewer({ src, fileName, onClose }) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-stone-ridge bg-[#FAFAF8] text-[11px]">
        <span className="font-medium text-abyss-ink truncate">{fileName}</span>
        <div className="flex items-center gap-1">
          <a href={src} download={fileName} className="p-1 hover:bg-gray-200 rounded" title="Download"><Download size={12} /></a>
          <a href={src} target="_blank" rel="noreferrer" className="p-1 hover:bg-gray-200 rounded" title="Open in new tab"><ExternalLink size={12} /></a>
          {onClose && (
            <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded" title="Close"><X size={12} /></button>
          )}
        </div>
      </div>
      <div className="flex-1 bg-[#F3F4F6]">
        <iframe src={src} title={fileName} className="w-full h-full border-0" />
      </div>
    </div>
  )
}

function UnknownViewer({ artifact, onClose, onDownload }) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-stone-ridge bg-[#FAFAF8] text-[11px]">
        <span className="font-medium text-abyss-ink truncate">{artifact.name}</span>
        <div className="flex items-center gap-1">
          <button onClick={onDownload} className="p-1 hover:bg-gray-200 rounded" title="Download"><Download size={12} /></button>
          {onClose && (
            <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded" title="Close"><X size={12} /></button>
          )}
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center bg-[#FAFAF8]">
        <div className="text-center max-w-md">
          <File size={32} className="mx-auto text-[#6B7280] mb-3" />
          <p className="text-sm text-[#6B7280] mb-4">Preview unavailable for this file type.</p>
          <table className="mx-auto text-left text-[11px] text-[#6B7280]">
            <tbody>
              <tr><td className="pr-4 py-1 font-medium text-abyss-ink">Name</td><td>{artifact.name}</td></tr>
              <tr><td className="pr-4 py-1 font-medium text-abyss-ink">Size</td><td>{formatBytes(artifact.size_bytes)}</td></tr>
              <tr><td className="pr-4 py-1 font-medium text-abyss-ink">Type</td><td>{artifact.extension?.toUpperCase() || "Unknown"}</td></tr>
              <tr><td className="pr-4 py-1 font-medium text-abyss-ink">Modified</td><td>{new Date(artifact.modified).toLocaleString()}</td></tr>
              <tr><td className="pr-4 py-1 font-medium text-abyss-ink">Path</td><td className="max-w-[200px] truncate font-mono">{artifact.path}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

const FILTER_OPTIONS = [
  { key: "all", label: "All" },
  { key: "reports", label: "Reports" },
  { key: "logs", label: "Logs" },
  { key: "images", label: "Images" },
  { key: "pdfs", label: "PDFs" },
  { key: "json", label: "JSON" },
  { key: "html", label: "HTML" },
  { key: "code", label: "Code" },
  { key: "config", label: "Config" },
]

export default function ArtifactViewer({ runId, initialPath, onArtifactSelect, highlightLine: initialHighlightLine }) {
  const [artifacts, setArtifacts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedPath, setSelectedPath] = useState(initialPath || null)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterCategory, setFilterCategory] = useState("all")
  const [preview, setPreview] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState(null)
  const listRef = useRef(null)

  const artifactFileUrl = (path) => `${API_BASE}/runs/${runId}/artifact?path=${encodeURIComponent(path)}`

  const fetchArtifacts = useCallback(async (signal) => {
    if (!runId) return []
    let res = await fetch(`${API_BASE}/runs/${runId}/artifacts`, { signal })
    if (res.ok) {
      const data = await res.json()
      if (data.length > 0) return data
    }
    res = await fetch(`${API_BASE}/runs/${runId}`, { signal })
    if (!res.ok) return []
    const runData = await res.json()
    return (runData.artifacts || []).map(name => ({
      path: name,
      name: name.split("/").pop(),
      extension: name.includes(".") ? name.split(".").pop() : "",
      size_bytes: 0,
      modified: "",
      is_text: true,
      is_image: false,
      is_pdf: false,
      is_html: false,
      category: "reports",
    }))
  }, [runId])

  useEffect(() => {
    if (!runId) return
    const controller = new AbortController()
    setLoading(true)
    setError(null)
    fetchArtifacts(controller.signal)
      .then(data => {
        data = data || []
        setArtifacts(data)
        setLoading(false)
        if (initialPath && data.some(a => a.path === initialPath)) {
          setSelectedPath(initialPath)
        } else if (data.length > 0 && !selectedPath) {
          setSelectedPath(data[0].path)
        }
      })
      .catch(e => {
        if (e.name === "AbortError") return
        setLoading(false)
        setArtifacts([])
        setError(e.message)
      })
    return () => controller.abort()
  }, [runId])

  useEffect(() => {
    if (!runId || !selectedPath) {
      setPreview(null)
      setPreviewLoading(false)
      setPreviewError(null)
      return
    }
    const artifact = artifacts.find(a => a.path === selectedPath)
    if (!artifact) {
      setPreview(null)
      setPreviewLoading(false)
      setPreviewError(null)
      return
    }
    if (artifact.is_image || artifact.is_pdf || artifact.is_html) {
      setPreview({ type: "raw", path: selectedPath })
      setPreviewError(null)
      return
    }
    if (artifact.is_text) {
      setPreviewLoading(true)
      setPreviewError(null)
      fetch(`${API_BASE}/runs/${runId}/artifact/preview?path=${encodeURIComponent(selectedPath)}&max_preview_mb=${TEXT_PREVIEW_MB}`)
        .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
        .then(data => { setPreview({ type: "text", ...data, path: selectedPath }); setPreviewLoading(false) })
        .catch(e => { setPreviewError(e.message); setPreviewLoading(false) })
      return
    }
    setPreview({ type: "unknown", path: selectedPath })
  }, [runId, selectedPath, artifacts])

  useEffect(() => {
    if (initialPath && initialPath !== selectedPath) {
      setSelectedPath(initialPath)
    }
  }, [initialPath])

  useEffect(() => {
    if (selectedPath && onArtifactSelect) {
      onArtifactSelect(selectedPath)
    }
  }, [selectedPath])

  const filtered = artifacts.filter(a => {
    if (filterCategory !== "all" && a.category !== filterCategory) return false
    if (searchQuery && !a.path.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const selectedIndex = filtered.findIndex(a => a.path === selectedPath)
  const selectedArtifact = artifacts.find(a => a.path === selectedPath)

  const handleDownload = () => {
    if (!selectedPath) return
    const a = document.createElement("a")
    a.href = artifactFileUrl(selectedPath)
    a.download = selectedPath.split("/").pop()
    a.click()
  }

  const handlePrev = () => {
    if (selectedIndex > 0) setSelectedPath(filtered[selectedIndex - 1].path)
  }
  const handleNext = () => {
    if (selectedIndex < filtered.length - 1) setSelectedPath(filtered[selectedIndex + 1].path)
  }

  const handleKeyDown = useCallback((e) => {
    if (e.ctrlKey && e.key === "f") {
      e.preventDefault()
      const searchInput = document.querySelector("[data-artifact-search]")
      if (searchInput) searchInput.focus()
    }
    if (e.key === "ArrowDown" && (e.altKey || e.ctrlKey)) {
      e.preventDefault(); handleNext()
    }
    if (e.key === "ArrowUp" && (e.altKey || e.ctrlKey)) {
      e.preventDefault(); handlePrev()
    }
  }, [selectedIndex, filtered])

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  const renderViewer = () => {
    if (!selectedPath) {
      return (
        <div className="flex-1 flex items-center justify-center bg-[#FAFAF8] text-[#6B7280] text-xs">
          Select an artifact from the list to preview
        </div>
      )
    }
    if (previewLoading) {
      return (
        <div className="flex-1 flex items-center justify-center bg-[#FAFAF8] text-[#6B7280] text-xs">
          Loading preview...
        </div>
      )
    }
    if (previewError) {
      return (
        <div className="flex-1 flex items-center justify-center bg-[#FAFAF8]">
          <div className="text-center">
            <AlertTriangle size={24} className="mx-auto text-red-400 mb-2" />
            <p className="text-xs text-red-600">{previewError}</p>
          </div>
        </div>
      )
    }
    if (!preview) {
      return (
        <div className="flex-1 flex items-center justify-center bg-[#FAFAF8] text-[#6B7280] text-xs">
          Loading...
        </div>
      )
    }

    const url = artifactFileUrl(selectedPath)

    if (selectedArtifact?.is_image) {
      return <ImageViewer src={url} fileName={selectedArtifact.name} />
    }
    if (selectedArtifact?.is_pdf) {
      return <PdfViewer src={url} fileName={selectedArtifact.name} />
    }
    if (selectedArtifact?.is_html) {
      return <HtmlViewer src={url} fileName={selectedArtifact.name} />
    }
    if (preview.type === "text") {
      return (
        <TextViewer
          content={preview.content}
          truncated={preview.truncated}
          fileName={selectedArtifact.name}
          onDownload={handleDownload}
        />
      )
    }
    return (
      <UnknownViewer artifact={selectedArtifact} onDownload={handleDownload} />
    )
  }

  if (loading) {
    return <div className="text-xs text-[#6B7280] p-4">Loading artifacts...</div>
  }
  if (error) {
    return <div className="text-xs text-red-600 p-4">Error loading artifacts: {error}</div>
  }
  if (artifacts.length === 0) {
    return (
      <div className="bg-white border border-stone-ridge rounded-lg p-8 text-center">
        <File size={24} className="mx-auto text-[#6B7280] mb-2" />
        <p className="text-xs text-[#6B7280]">No artifacts found for this run.</p>
      </div>
    )
  }

  return (
    <div className="flex border border-stone-ridge rounded-lg overflow-hidden bg-white" style={{ height: "calc(100vh - 280px)", minHeight: "400px" }}>
      {/* Left sidebar — artifact list */}
      <div className="w-60 flex-shrink-0 border-r border-stone-ridge flex flex-col bg-[#FAFAF8]">
        <div className="p-2 border-b border-stone-ridge space-y-1.5">
          <SearchBar value={searchQuery} onChange={setSearchQuery} placeholder="Search files..." />
          <div data-artifact-search className="flex flex-wrap gap-1">
            {FILTER_OPTIONS.map(opt => (
              <button
                key={opt.key}
                onClick={() => setFilterCategory(opt.key)}
                className={`text-[9px] px-1.5 py-0.5 rounded font-medium transition-colors ${
                  filterCategory === opt.key
                    ? "bg-meridian-gold text-abyss-ink"
                    : "bg-white text-[#6B7280] border border-stone-ridge hover:bg-gray-100"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        <div ref={listRef} className="flex-1 overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="p-4 text-[10px] text-[#6B7280] text-center">No matching files</div>
          ) : (
            filtered.map((a) => (
              <button
                key={a.path}
                onClick={() => setSelectedPath(a.path)}
                className={`w-full text-left px-2.5 py-1.5 flex items-center gap-2 text-[10px] border-b border-stone-ridge transition-colors ${
                  selectedPath === a.path
                    ? "bg-meridian-gold/10 text-abyss-ink font-medium"
                    : "text-[#6B7280] hover:bg-white"
                }`}
              >
                <span className="flex-shrink-0">{getFileIcon(a.name)}</span>
                <span className="truncate flex-1">{a.path}</span>
                <span className="text-[8px] text-[#9CA3AF] flex-shrink-0">{formatBytes(a.size_bytes)}</span>
              </button>
            ))
          )}
        </div>
        <div className="p-1.5 border-t border-stone-ridge text-[9px] text-[#6B7280] flex justify-between">
          <span>{filtered.length} / {artifacts.length} files</span>
          {selectedIndex >= 0 && (
            <span className="flex items-center gap-1">
              <button onClick={handlePrev} disabled={selectedIndex <= 0} className="p-0.5 hover:bg-gray-200 rounded disabled:opacity-30" title="Previous (Alt+Up)"><ChevronUp size={10} /></button>
              <span>{selectedIndex + 1}/{filtered.length}</span>
              <button onClick={handleNext} disabled={selectedIndex >= filtered.length - 1} className="p-0.5 hover:bg-gray-200 rounded disabled:opacity-30" title="Next (Alt+Down)"><ChevronDown size={10} /></button>
            </span>
          )}
        </div>
      </div>
      {/* Right panel — artifact viewer */}
      {renderViewer()}
    </div>
  )
}
