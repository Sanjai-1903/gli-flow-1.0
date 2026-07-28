import { Play, Terminal, BookOpen } from "lucide-react"

export default function RunDesignPage() {
  const commands = [
    { label: "Run with mock mode", cmd: "gli-flow run examples/tiny_or --mock", desc: "Quick test run using mock mode" },
    { label: "Run full flow", cmd: "gli-flow run examples/gcd", desc: "Full RTL-to-GDS run" },
    { label: "Run with config", cmd: "gli-flow run examples/counter --config my_config.yaml", desc: "Run with custom configuration" },
    { label: "Batch run", cmd: "gli-flow batch examples/batch_config.yaml", desc: "Execute multiple designs" },
  ]

  return (
    <div className="space-y-6">
      <h1 className="font-[Playfair_Display] text-[20px] text-abyss-ink">Run Design</h1>

      <div className="bg-white border border-stone-ridge rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-meridian-gold flex items-center justify-center">
            <Play size={20} className="text-abyss-ink ml-0.5" />
          </div>
          <div>
            <h2 className="font-[Playfair_Display] text-[18px] text-abyss-ink">Execute an ASIC Design</h2>
            <p className="text-xs text-[#6B7280] font-[Work_Sans]">Run the GLI-FLOW RTL-to-GDS pipeline</p>
          </div>
        </div>

        <p className="text-xs text-[#6B7280] font-[Work_Sans] mb-5 leading-relaxed">
          Use the GLI-FLOW CLI to execute designs through the 29-stage RTL-to-GDS implementation pipeline.
          The pipeline uses OpenROAD, Yosys, KLayout, Magic, and Netgen for a complete ASIC implementation flow.
        </p>

        <div className="space-y-3">
          {commands.map((c, i) => (
            <div key={i} className="border border-stone-ridge rounded-lg p-4 hover:bg-[#FAFAF8] transition-colors">
              <div className="flex items-center gap-2 mb-1">
                <Terminal size={14} className="text-[#6B7280]" />
                <span className="text-xs font-semibold text-abyss-ink">{c.label}</span>
              </div>
              <code className="block text-[11px] bg-[#F3F2ED] text-abyss-ink px-3 py-2 rounded font-mono mt-1">{c.cmd}</code>
              <p className="text-[10px] text-[#6B7280] mt-1">{c.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 p-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg">
          <div className="flex items-center gap-2">
            <BookOpen size={14} color="#3B82F6" />
            <span className="text-xs text-[#2563EB] font-medium">Tip: Use <code className="bg-white px-1 rounded text-[10px]">--mock</code> flag for quick testing without EDA tools</span>
          </div>
        </div>
      </div>
    </div>
  )
}
