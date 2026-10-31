import React from 'react';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateProgress: (progress: number) => void;
  onOpenWorkspace: () => void;
  onOpenBenchmark: () => void;
}

export const MobileMenu: React.FC<MobileMenuProps> = ({
  isOpen,
  onClose,
  onNavigateProgress,
  onOpenWorkspace,
  onOpenBenchmark,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 md:hidden bg-[#01030F]/95 backdrop-blur-xl flex flex-col pt-24 px-8 pb-12 animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation Menu"
    >
      {/* Navigation links */}
      <nav className="flex flex-col gap-6 text-lg font-medium tracking-wide">
        <a
          href="#overview"
          onClick={(e) => {
            e.preventDefault();
            onNavigateProgress(0);
            onClose();
          }}
          className="text-white hover:text-[#8FC2FF] border-b border-white/10 pb-4 transition-colors font-mono text-sm tracking-widest"
        >
          01 // OVERVIEW
        </a>

        <a
          href="#method"
          onClick={(e) => {
            e.preventDefault();
            onNavigateProgress(0.34);
            onClose();
          }}
          className="text-white hover:text-[#8FC2FF] border-b border-white/10 pb-4 transition-colors font-mono text-sm tracking-widest"
        >
          02 // THE CIVORA METHOD
        </a>

        <a
          href="#verification"
          onClick={(e) => {
            e.preventDefault();
            onNavigateProgress(0.96);
            onClose();
          }}
          className="text-white hover:text-[#8FC2FF] border-b border-white/10 pb-4 transition-colors font-mono text-sm tracking-widest"
        >
          03 // VERIFICATION ENGINE
        </a>

        <button
          type="button"
          onClick={() => {
            onClose();
            onOpenBenchmark();
          }}
          className="text-left text-white hover:text-[#8FC2FF] border-b border-white/10 pb-4 transition-colors font-mono text-sm tracking-widest"
        >
          04 // GEMMA 4 BENCHMARK
        </button>

        <a
          href="https://github.com/anshgandhi68-sys/CIVORA"
          target="_blank"
          rel="noopener noreferrer"
          className="text-white hover:text-[#8FC2FF] border-b border-white/10 pb-4 transition-colors font-mono text-sm tracking-widest flex items-center justify-between"
        >
          <span>05 // GITHUB REPOSITORY</span>
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 opacity-80">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
          </svg>
        </a>
      </nav>

      {/* Main Workspace & AI Chat CTAs */}
      <div className="mt-auto pt-8 flex flex-col gap-3">
        <button
          type="button"
          onClick={() => {
            onClose();
            if (typeof window !== 'undefined' && (window as any).openCivoraAIChat) {
              (window as any).openCivoraAIChat();
            } else {
              document.getElementById('civora-chat-container')?.classList.add('active');
            }
          }}
          className="w-full py-3.5 px-6 bg-white/[0.04] hover:bg-white/[0.08] border border-white/10 hover:border-white/20 text-white font-mono text-xs font-semibold tracking-widest rounded-lg flex items-center justify-center gap-3 transition-colors"
        >
          <span className="w-2 h-2 rounded-full bg-[#38BDF8] shadow-[0_0_6px_#38BDF8]" />
          <span>CIVORA AI</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-[#38BDF8]">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>

        <button
          type="button"
          onClick={() => {
            onClose();
            onOpenWorkspace();
          }}
          className="w-full py-4 px-6 bg-[#0071FF] text-white font-mono text-xs font-semibold tracking-widest rounded-lg flex items-center justify-center gap-3 shadow-[0_0_20px_rgba(0,113,255,0.4)]"
        >
          <span>OPEN MISSION CONTROL</span>
          <svg viewBox="0 0 13 13" className="w-4 h-4 fill-none stroke-currentColor stroke-[2]">
            <path d="M2 11 11 2M2 2h9v9" />
          </svg>
        </button>
      </div>
    </div>
  );
};
