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
      </nav>

      {/* Main Workspace CTA */}
      <div className="mt-auto pt-8">
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

