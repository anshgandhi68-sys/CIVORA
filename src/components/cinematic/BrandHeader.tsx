import React from 'react';

interface BrandHeaderProps {
  onNavigateProgress: (progress: number) => void;
  onOpenWorkspace: () => void;
  onOpenBenchmark: () => void;
  onToggleMobileMenu: () => void;
  mobileMenuOpen: boolean;
  opacity: number;
}

export const BrandHeader: React.FC<BrandHeaderProps> = ({
  onNavigateProgress,
  onOpenWorkspace,
  onOpenBenchmark,
  onToggleMobileMenu,
  mobileMenuOpen,
  opacity,
}) => {
  return (
    <header 
      className="bar transition-opacity duration-200"
      style={{ opacity, pointerEvents: opacity < 0.05 ? 'none' : 'auto' }}
      aria-label="Site header"
    >
      {/* Brand logo & wordmark */}
      <a 
        href="#top" 
        className="brand group flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4DA3FF] rounded-lg"
        onClick={(e) => {
          e.preventDefault();
          onNavigateProgress(0);
        }}
        aria-label="CIVORA Homepage"
      >
        <svg 
          className="mark transition-transform duration-300 group-hover:scale-105" 
          viewBox="0 0 32 38" 
          aria-hidden="true"
        >
          <path 
            d="M16 1 31 9.5v18.8L16 37 1 28.3V9.5ZM1 9.5 16 18l15-8.5M16 18v19M8.5 5.3 23.5 14v18.5M23.5 5.3 8.5 14v18.5M1 19l15 8.5L31 19M1 28.3 23.5 14M31 28.3 8.5 14" 
            stroke="rgba(255,255,255,0.9)" 
            strokeWidth="1.15" 
            fill="none" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
          />
          <ellipse cx="16" cy="28" rx="9" ry="5.1" stroke="rgba(255,255,255,0.9)" strokeWidth="1.15" fill="none" />
          <ellipse cx="16" cy="28" rx="6" ry="3.4" stroke="rgba(255,255,255,0.9)" strokeWidth="1.15" fill="none" />
          <ellipse cx="16" cy="28" rx="3" ry="1.7" stroke="rgba(255,255,255,0.9)" strokeWidth="1.15" fill="none" />
        </svg>
        <span className="wordmark">CIVORA</span>
      </a>

      {/* Centered Desktop Navigation */}
      <nav className="nav hidden md:flex items-center" aria-label="Main Navigation">
        <a 
          href="#overview" 
          onClick={(e) => { e.preventDefault(); onNavigateProgress(0); }}
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none"
        >
          OVERVIEW
        </a>
        <a 
          href="#method" 
          onClick={(e) => { e.preventDefault(); onNavigateProgress(0.34); }}
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none"
        >
          HOW IT WORKS
          <svg className="chev" viewBox="0 0 10 6" aria-hidden="true">
            <path d="M1 1 5 5 9 1" />
          </svg>
        </a>
        <a 
          href="#verification" 
          onClick={(e) => { e.preventDefault(); onNavigateProgress(0.96); }}
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none"
        >
          VERIFICATION
          <svg className="chev" viewBox="0 0 10 6" aria-hidden="true">
            <path d="M1 1 5 5 9 1" />
          </svg>
        </a>
        <button
          type="button"
          onClick={onOpenBenchmark}
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none text-[12px] font-semibold tracking-[0.085em] flex items-center gap-[9px]"
        >
          BENCHMARK
        </button>
        <button
          type="button"
          onClick={onOpenWorkspace}
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none text-[12px] font-semibold tracking-[0.085em] flex items-center gap-[6px] text-[#38BDF8]"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          TRUEFOUNDRY AGENT
        </button>
      </nav>

      {/* Top-Right CTA: Open Workspace */}
      <div className="hidden md:flex">
        <button
          type="button"
          onClick={onOpenWorkspace}
          className="navcta group focus-visible:outline-none"
          aria-label="Open Mission Control Workspace"
        >
          <span className="text-[12px] font-semibold tracking-[0.085em] group-hover:text-[#8FC2FF] transition-colors">
            OPEN WORKSPACE
          </span>
          <span className="square">
            <svg viewBox="0 0 13 13" aria-hidden="true">
              <path d="M2 11 11 2M2 2h9v9" />
            </svg>
          </span>
        </button>
      </div>

      {/* Mobile Hamburger Button */}
      <button 
        type="button"
        id="burger"
        className="lg:hidden absolute right-5 top-4 w-10 h-10 border border-white/20 rounded-lg flex items-center justify-center bg-white/5 backdrop-blur-md text-white hover:border-white/40 focus-visible:outline-none z-50 pointer-events-auto cursor-pointer"
        onClick={onToggleMobileMenu}
        aria-expanded={mobileMenuOpen}
        aria-label={mobileMenuOpen ? 'Close navigation' : 'Open navigation'}
      >
        {mobileMenuOpen ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        )}
      </button>
    </header>
  );
};
