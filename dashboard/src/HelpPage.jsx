import { HelpCircle, BookOpen, Code2, Mail, Terminal, FileText } from "lucide-react"

export default function HelpPage() {
  const resources = [
    { icon: BookOpen, label: "User Manual", desc: "Complete GLI-FLOW user guide", href: "/docs/user_guide/user_manual.md" },
    { icon: Terminal, label: "CLI Reference", desc: "Command-line interface documentation", href: "#" },
    { icon: FileText, label: "Architecture Docs", desc: "System architecture and design", href: "/docs/architecture/" },
    { icon: Code2, label: "GitHub Repository", desc: "Source code and issue tracker", href: "https://github.com/anomalyco/gli-flow" },
    { icon: Mail, label: "Contact Team", desc: "team@gatelevel.io", href: "mailto:team@gatelevel.io" },
  ]

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Help & Documentation</h1>

      <div className="bg-white border border-stone-ridge rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-[#EFF6FF] flex items-center justify-center">
            <HelpCircle size={20} color="#3B82F6" />
          </div>
          <div>
            <h2 className="font-[Playfair_Display] text-[18px] text-abyss-ink">GLI-FLOW Resources</h2>
            <p className="text-xs text-[#6B7280] font-[Work_Sans]">Get help and explore documentation</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {resources.map((r, i) => {
            const Icon = r.icon
            return (
              <a
                key={i}
                href={r.href}
                target={r.href.startsWith("http") || r.href.startsWith("mailto") ? "_blank" : undefined}
                rel={r.href.startsWith("http") ? "noreferrer" : undefined}
                className="flex items-start gap-3 p-4 border border-stone-ridge rounded-lg hover:bg-[#FAFAF8] transition-colors"
              >
                <div className="w-8 h-8 rounded bg-[#F3F2ED] flex items-center justify-center flex-shrink-0">
                  <Icon size={14} className="text-[#6B7280]" />
                </div>
                <div>
                  <p className="text-xs font-medium text-abyss-ink">{r.label}</p>
                  <p className="text-[10px] text-[#6B7280] mt-0.5">{r.desc}</p>
                </div>
              </a>
            )
          })}
        </div>

        <div className="mt-6 p-4 bg-[#FAFAF8] border border-stone-ridge rounded-lg">
          <p className="text-xs font-medium text-abyss-ink mb-2">Quick Commands</p>
          <div className="space-y-1 text-[10px] font-mono">
            <p className="text-[#6B7280]"><span className="text-abyss-ink">$</span> gli-flow --help</p>
            <p className="text-[#6B7280]"><span className="text-abyss-ink">$</span> gli-flow doctor</p>
            <p className="text-[#6B7280]"><span className="text-abyss-ink">$</span> gli-flow diagnose</p>
          </div>
        </div>
      </div>
    </div>
  )
}
