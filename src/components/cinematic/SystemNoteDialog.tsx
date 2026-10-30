import React, { useEffect, useRef } from 'react';
import { SYSTEM_NOTES } from '../../data/civoraContent';

interface SystemNoteDialogProps {
  isOpen: boolean;
  activeNoteIndex: number;
  onClose: () => void;
  onSelectNote: (index: number) => void;
  onOpenWorkspace: () => void;
}

export const SystemNoteDialog: React.FC<SystemNoteDialogProps> = ({
  isOpen,
  activeNoteIndex,
  onClose,
  onSelectNote,
  onOpenWorkspace,
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const totalNotes = 4; // 4 primary verification markers (indices 0, 1, 2, 3)

  // Keyboard navigation: Left/Right/Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const prev = (activeNoteIndex - 1 + totalNotes) % totalNotes;
        onSelectNote(prev);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const next = (activeNoteIndex + 1) % totalNotes;
        onSelectNote(next);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, activeNoteIndex, onClose, onSelectNote, totalNotes]);

  if (!isOpen) return null;

  const note = SYSTEM_NOTES[activeNoteIndex] || SYSTEM_NOTES[0];
  const isSpecialRepoNote = activeNoteIndex === 4;

  const handlePrev = () => {
    const prev = (activeNoteIndex - 1 + totalNotes) % totalNotes;
    onSelectNote(prev);
  };

  const handleNext = () => {
    const next = (activeNoteIndex + 1) % totalNotes;
    onSelectNote(next);
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-[#01030F]/60 backdrop-blur-[3px] z-[90] transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Detail Panel */}
      <div 
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="note-title"
        className="note-dialog"
      >
        {/* Top Bar */}
        <div className="note-top">
          <div className="note-eyebrow">
            <span>CIVORA / SYSTEM NOTES</span>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="note-close"
            aria-label="Close system note"
          >
            <svg viewBox="0 0 16 16" className="w-4 h-4 fill-none stroke-currentColor stroke-[1.5]">
              <path d="M3 3l10 10M13 3L3 13" />
            </svg>
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="note-body">
          <span className="note-kind">{note.code}</span>
          <h2 id="note-title" className="note-title">{note.title}</h2>
          <p className="note-deck">{note.deck}</p>

          <div className="note-section-label">EXPLANATION</div>
          <p className="note-history">{note.description}</p>

          <div className="note-section-label">ENGINEERING CAPABILITIES</div>
          <ul className="note-features">
            {note.features.map((feat, idx) => (
              <li key={idx}>{feat}</li>
            ))}
          </ul>

          <div className="note-section-label">VERIFIED OUTCOME</div>
          <p className="text-[13px] leading-relaxed text-white/90 bg-white/5 border border-white/10 rounded-lg p-3">
            {note.result}
          </p>

          {/* Launch in Mission Control CTA */}
          <div className="mt-6 pt-4 border-t border-white/10">
            <button
              type="button"
              onClick={() => {
                onClose();
                onOpenWorkspace();
              }}
              className="w-full py-3 px-4 bg-[#0071FF] hover:bg-[#38BDF8] text-white font-mono text-[12px] font-semibold tracking-[0.06em] rounded-lg flex items-center justify-center gap-2 transition-colors shadow-[0_0_15px_rgba(0,113,255,0.4)]"
            >
              <span>RUN IN MISSION CONTROL</span>
              <svg viewBox="0 0 13 13" className="w-3.5 h-3.5 fill-none stroke-currentColor stroke-[2]">
                <path d="M2 11 11 2M2 2h9v9" />
              </svg>
            </button>
          </div>
        </div>

        {/* Bottom Bar with Step Navigation */}
        {!isSpecialRepoNote && (
          <div className="note-bottom">
            <nav className="note-navigation" aria-label="Explore notes">
              <button 
                type="button" 
                onClick={handlePrev}
                className="note-step"
                aria-label="Previous system note"
              >
                <svg viewBox="0 0 12 12" className="w-3 h-3 fill-none stroke-currentColor stroke-[1.5]">
                  <path d="M10 6H2m4-4L2 6l4 4" />
                </svg>
                <span>PREV</span>
              </button>

              <span className="font-mono text-[10px] text-white/40 tracking-wider">
                0{activeNoteIndex + 1} / 04
              </span>

              <button 
                type="button" 
                onClick={handleNext}
                className="note-step"
                aria-label="Next system note"
              >
                <span>NEXT</span>
                <svg viewBox="0 0 12 12" className="w-3 h-3 fill-none stroke-currentColor stroke-[1.5]">
                  <path d="M2 6h8M6 2l4 4-4 4" />
                </svg>
              </button>
            </nav>
          </div>
        )}
      </div>
    </>
  );
};

