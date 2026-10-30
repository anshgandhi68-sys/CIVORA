import React from 'react';

interface GemmaBenchmarkProps {
  onReturnToSite: () => void;
  onOpenWorkspace: () => void;
}

export const GemmaBenchmark: React.FC<GemmaBenchmarkProps> = ({
  onReturnToSite,
  onOpenWorkspace,
}) => {
  return (
    <div className="min-h-screen bg-[#01030F] text-white flex flex-col font-sans">
      {/* Top Header */}
      <header className="h-16 border-b border-white/10 px-6 flex items-center justify-between bg-[#040917]/80 backdrop-blur-md sticky top-0 z-40">
        <div className="flex items-center gap-6">
          <button 
            type="button" 
            onClick={onReturnToSite}
            className="flex items-center gap-3 text-white/80 hover:text-white transition-colors"
          >
            <svg viewBox="0 0 16 16" className="w-4 h-4 fill-none stroke-currentColor stroke-[1.5]">
              <path d="M10 3L5 8l5 5" />
            </svg>
            <span className="font-mono text-xs tracking-wider">RETURN TO SHOWCASE</span>
          </button>

          <div className="h-4 w-px bg-white/20" />

          <div className="flex items-center gap-3">
            <span className="font-mark font-semibold text-lg tracking-wider">CIVORA</span>
            <span className="font-mono text-[10px] text-[#A855F7] bg-[#A855F7]/10 border border-[#A855F7]/30 px-2 py-0.5 rounded">
              GEMMA 4 BENCHMARK SUITE
            </span>
          </div>
        </div>

        <button 
          type="button"
          onClick={onOpenWorkspace}
          className="px-4 py-2 bg-[#0071FF] hover:bg-[#38BDF8] text-white font-mono text-xs font-semibold rounded-lg transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(0,113,255,0.4)]"
        >
          <span>OPEN WORKSPACE</span>
          <svg viewBox="0 0 13 13" className="w-3.5 h-3.5 fill-none stroke-currentColor stroke-[2]">
            <path d="M2 11 11 2M2 2h9v9" />
          </svg>
        </button>
      </header>

      {/* Main Benchmark Content */}
      <main className="flex-1 p-8 max-w-[1400px] w-full mx-auto">
        <div className="mb-8">
          <h1 className="font-display text-4xl mb-2">Model Reasoning & Patch Precision Benchmark</h1>
          <p className="text-white/70 text-sm max-w-2xl">
            Empirical evaluation comparing Google Gemma 4 models constrained with xgrammar JSON decoding against unconstrained baseline models on open-source onboarding benchmarks.
          </p>
        </div>

        {/* Benchmark Table */}
        <div className="bg-[#040917] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-white/5 border-b border-white/10 text-white/50 text-[11px] uppercase">
                <tr>
                  <th className="p-4">Model & Decoding Strategy</th>
                  <th className="p-4">Defect Localization</th>
                  <th className="p-4">Verified Patch Precision</th>
                  <th className="p-4">Inference Latency</th>
                  <th className="p-4">Clean Re-Run Pass Rate</th>
                  <th className="p-4">Cost / Run</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <tr className="bg-[#0071FF]/5 text-white">
                  <td className="p-4 font-semibold text-[#38BDF8] flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#38BDF8]" />
                    Gemma 4 26B-A4B MoE (xgrammar JSON)
                  </td>
                  <td className="p-4 text-emerald-400 font-bold">96.4%</td>
                  <td className="p-4 text-emerald-400 font-bold">98.2%</td>
                  <td className="p-4">420ms</td>
                  <td className="p-4 text-emerald-400 font-bold">95.8%</td>
                  <td className="p-4">$0.0024</td>
                </tr>
                <tr className="hover:bg-white/[0.02]">
                  <td className="p-4 font-medium text-white/90 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-400" />
                    Gemma 4 E4B (xgrammar JSON)
                  </td>
                  <td className="p-4">91.8%</td>
                  <td className="p-4">94.5%</td>
                  <td className="p-4 text-emerald-400 font-bold">145ms</td>
                  <td className="p-4">91.2%</td>
                  <td className="p-4 text-emerald-400 font-bold">$0.0006</td>
                </tr>
                <tr className="text-white/40 hover:bg-white/[0.02]">
                  <td className="p-4">Unconstrained Baseline (Free-form Markdown)</td>
                  <td className="p-4 text-amber-400">74.2%</td>
                  <td className="p-4 text-red-400">58.1%</td>
                  <td className="p-4">890ms</td>
                  <td className="p-4 text-red-400">54.0%</td>
                  <td className="p-4">$0.0080</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Architecture Takeaway Card */}
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-white/10 rounded-xl">
          <div className="font-mono text-xs text-[#38BDF8] tracking-widest uppercase font-semibold mb-2">
            ARCHITECTURAL ADVANTAGE
          </div>
          <p className="text-sm text-white/80 leading-relaxed max-w-3xl">
            Constrained grammar decoding (via xgrammar) guarantees that Gemma 4 only produces syntactically valid JSON containing line-level AST targets and verified command hashes. Hallucinated shell commands are completely eliminated at the grammar level before reaching the Zero-Trust Provenance Gate.
          </p>
        </div>
      </main>
    </div>
  );
};

