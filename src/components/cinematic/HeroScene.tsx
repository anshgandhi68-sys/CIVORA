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

      {/* Explore CTA Button */}
      <button 
        type="button"
        onClick={onExplore}
        className="cta group"
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
