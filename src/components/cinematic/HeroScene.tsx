import React from 'react';

interface HeroSceneProps {
  onExplore: () => void;
  opacity: number;
  translateY: string;
}

export const HeroScene: React.FC<HeroSceneProps> = ({
  onExplore,
  opacity,
  translateY,
}) => {
  if (opacity <= 0.005) return null;

  return (
    <div
      className="body transition-opacity duration-150"
      style={{
        opacity,
        transform: `translateY(${translateY})`,
        pointerEvents: opacity < 0.05 ? 'none' : 'auto'
      }}
    >
      {/* Eyebrow */}
      <div className="hero-eyebrow flex items-center justify-center gap-2">
        <span>AUTONOMOUS OPEN-SOURCE ENGINEERING</span>
        <span className="opacity-40">•</span>
        <span className="text-[#38BDF8]">POWERED BY TRUEFOUNDRY AGENT & MCP</span>
      </div>

      {/* Main Headline */}
      <h1 className="headline" aria-label="Every Repository Deserves a Working First Run">
        <i><span>Every Repository</span></i>
        <i><span>Deserves a</span></i>
        <i><span>Working First Run</span></i>
      </h1>

      {/* Primary Actions Group */}
      <div
        className="flex items-center gap-4 pointer-events-auto"
        style={{
          position: 'absolute',
          left: '40.5px',
          top: 'calc(379.5px + (100% - 720px) * .22)',
          zIndex: 4,
        }}
      >
        <button
          type="button"
          onClick={onExplore}
          className="cta group !relative !left-auto !top-auto !translate-y-0"
          aria-label="Explore the CIVORA engine"
        >
          <span className="cta-label text-white group-hover:text-[#8FC2FF] transition-colors">
            EXPLORE THE ENGINE
          </span>
          <span className="square">
            <svg viewBox="0 0 13 13" aria-hidden="true">
              <path d="M2 11 11 2M2 2h9v9" />
            </svg>
          </span>
        </button>

        <button
          type="button"
          onClick={() => {
            if (typeof window !== 'undefined' && (window as any).openCivoraAIChat) {
              (window as any).openCivoraAIChat();
            } else {
              document.getElementById('civora-widget-trigger')?.click();
            }
          }}
          className="open-ai-chat group !relative !left-auto !top-auto !translate-y-0 w-[218px] h-[56px] px-4 rounded-lg bg-[#0071FF]/15 hover:bg-[#0071FF]/30 border border-[#38BDF8]/40 hover:border-[#38BDF8] shadow-[0_0_20px_rgba(0,113,255,0.25)] hover:shadow-[0_0_28px_rgba(56,189,248,0.5)] flex items-center justify-between backdrop-blur-md transition-all cursor-pointer"
          aria-label="Chat with CIVORA AI Agent"
        >
          <span className="text-white flex items-center gap-2 font-['Manrope'] font-bold text-xs tracking-[0.085em]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] shadow-[0_0_8px_#38BDF8] shrink-0" />
            CIVORA AI
          </span>
          <span className="w-6 h-6 rounded-md bg-[#0071FF] shadow-[0_0_12px_rgba(0,113,255,0.7)] group-hover:shadow-[0_0_20px_rgba(0,113,255,0.95)] flex items-center justify-center shrink-0 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </span>
        </button>
      </div>

      {/* Supporting Copy */}
      <div className="sub">
        <b>Make every repository ready for its next contributor.</b>
        <span>
          CIVORA executes setup instructions, discovers hidden blockers, proves the correct fixes, and repairs documentation before a new developer hits a dead end.
        </span>
      </div>

      {/* Scroll Hint */}
      <div className="scroll" aria-hidden="true">
        <svg className="scroll-mark" viewBox="0 0 32 38">
          <path
            d="M16 1 31 9.5v18.8L16 37 1 28.3V9.5ZM1 9.5 16 18l15-8.5M16 18v19M8.5 5.3 23.5 14v18.5M23.5 5.3 8.5 14v18.5M1 19l15 8.5L31 19M1 28.3 23.5 14M31 28.3 8.5 14"
            stroke="rgba(255,255,255,0.8)"
            strokeWidth="1.5"
            fill="none"
          />
          <ellipse cx="16" cy="28" rx="9" ry="5.1" stroke="rgba(255,255,255,0.8)" strokeWidth="1.5" fill="none" />
          <ellipse cx="16" cy="28" rx="6" ry="3.4" stroke="rgba(255,255,255,0.8)" strokeWidth="1.5" fill="none" />
        </svg>
        <span>Scroll to explore</span>
      </div>
    </div>
  );
};
