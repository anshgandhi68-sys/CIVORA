import React from 'react';

interface DriftRadarProps {
  onReturnToSite: () => void;
  onOpenWorkspace: () => void;
}

export const DriftRadar: React.FC<DriftRadarProps> = ({
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
            <span className="font-mono text-[10px] text-[#38BDF8] bg-[#38BDF8]/10 border border-[#38BDF8]/30 px-2 py-0.5 rounded">
              CI-VS-DOCS DRIFT RADAR
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

      {/* Main Drift Comparison */}
      <main className="flex-1 p-8 max-w-[1400px] w-full mx-auto">
        <div className="mb-8">
          <h1 className="font-display text-4xl mb-2">CI Drift Intelligence Matrix</h1>
          <p className="text-white/70 text-sm max-w-2xl">
            CIVORA systematically extracts and diffs machine-executable CI workflows against human-facing documentation instructions to detect onboarding friction before execution begins.
          </p>
        </div>

        {/* Comparison Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Card 1: README Instructions */}
          <div className="bg-[#040917] border border-white/10 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
              <span className="font-mono text-xs text-white/50 uppercase">01 // DOCUMENTED SETUP</span>
              <span className="font-mono text-xs px-2 py-0.5 bg-white/5 rounded text-white/80">README.md</span>
            </div>
            <div className="font-mono text-xs text-white/80 leading-relaxed bg-black/40 p-4 rounded-lg flex-1">
              <div className="text-white/40 mb-2"># Documented steps</div>
              <div className="text-red-400 line-through">$ nvm use 18</div>
              <div className="text-white/60">$ npm install</div>
              <div className="text-red-400 line-through">$ npm run dev</div>
              <div className="text-amber-400/80 mt-3 text-[11px]">
                ⚠ Missing .env copy step<br />
                ⚠ Node 18 runtime deprecated
              </div>
            </div>
          </div>

          {/* Card 2: GitHub Actions CI */}
          <div className="bg-[#040917] border border-white/10 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
              <span className="font-mono text-xs text-[#10B981] uppercase">02 // MACHINE CI WORKFLOW</span>
              <span className="font-mono text-xs px-2 py-0.5 bg-green-500/10 text-green-400 rounded">ci.yml (Green)</span>
            </div>
            <div className="font-mono text-xs text-white/80 leading-relaxed bg-black/40 p-4 rounded-lg flex-1">
              <div className="text-white/40 mb-2"># GitHub Actions runner</div>
              <div className="text-green-400">- uses: actions/setup-node@v4</div>
              <div className="text-green-400">&nbsp;&nbsp;with: node-version: 20</div>
              <div className="text-white/60">- run: npm ci</div>
              <div className="text-green-400">- run: cp .env.example .env</div>
              <div className="text-white/60">- run: npm test</div>
              <div className="text-green-400/80 mt-3 text-[11px]">
                ✓ Pre-baked runner env passes CI
              </div>
            </div>
          </div>

          {/* Card 3: CIVORA Verified Repair */}
          <div className="bg-[#040917] border border-white/10 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
              <span className="font-mono text-xs text-[#0071FF] uppercase">03 // PROVEN REMEDIATION</span>
              <span className="font-mono text-xs px-2 py-0.5 bg-[#0071FF]/20 text-[#38BDF8] rounded">CIVORA PR Patch</span>
            </div>
            <div className="font-mono text-xs text-white/80 leading-relaxed bg-black/40 p-4 rounded-lg flex-1">
              <div className="text-white/40 mb-2"># Verified surgical patch</div>
              <div className="text-emerald-400">+ $ nvm use 20</div>
              <div className="text-white/60">&nbsp;&nbsp;$ npm install</div>
              <div className="text-emerald-400">+ $ cp .env.example .env</div>
              <div className="text-white/60">&nbsp;&nbsp;$ npm run dev</div>
              <div className="text-[#38BDF8] mt-3 text-[11px]">
                ✓ Proven in sandbox exit code 0<br />
                ✓ Synthesized .devcontainer.json
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

