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
        <a
          href="https://github.com/anshgandhi68-sys/CIVORA"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none text-[12px] font-semibold tracking-[0.085em] flex items-center gap-[6px]"
          aria-label="CIVORA Project on GitHub"
        >
          <span>PROJECT</span>
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5 opacity-80">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
          </svg>
        </a>
        <button
          type="button"
          onClick={onOpenWorkspace}
          className="hover:text-[#8FC2FF] focus-visible:text-[#8FC2FF] focus-visible:outline-none text-[12px] font-semibold tracking-[0.085em] flex items-center gap-[6px] text-[#38BDF8]"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] shadow-[0_0_6px_#38BDF8]" />
          TRUEFOUNDRY AGENT
        </button>
      </nav>

      {/* Top-Right CTAs: AI Chat Bot & Open Workspace */}
      <div className="hidden md:flex items-center gap-3">
        <button
          type="button"
          onClick={() => {
            if ((window as any).openCivoraAIChat) {
              (window as any).openCivoraAIChat();
            } else {
              document.getElementById('civora-widget-trigger')?.click();
            }
          }}
          className="navcta open-ai-chat group focus-visible:outline-none !static hover:text-[#8FC2FF] transition-colors"
          aria-label="Open TrueFoundry AI Chatbot"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] shadow-[0_0_6px_#38BDF8]" />
          <span className="text-[12px] font-semibold tracking-[0.085em]">
            AI CHAT BOT
          </span>
          <span className="square">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </span>
        </button>

        <button
          type="button"
          onClick={onOpenWorkspace}
          className="navcta group focus-visible:outline-none !static"
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
