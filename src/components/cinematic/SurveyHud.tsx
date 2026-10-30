import React, { useEffect, useState } from 'react';

interface SurveyHudProps {
  onOpenSurveyNote: () => void;
  opacity: number;
}

export const SurveyHud: React.FC<SurveyHudProps> = ({
  onOpenSurveyNote,
  opacity,
}) => {
  const [line1, setLine1] = useState('STRUCTURE');
  const [line2, setLine2] = useState('& DEPENDENCIES');

  if (opacity <= 0.005) return null;

  // Single-run character decoding animation on initial mount
  useEffect(() => {
    const target1 = 'STRUCTURE';
    const target2 = '& DEPENDENCIES';
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#/_<>';
    let frame = 0;
    const interval = setInterval(() => {
      frame++;
      if (frame <= target1.length) {
        let scrambled1 = target1.slice(0, frame);
        for (let k = 0; k < Math.min(2, target1.length - frame); k++) {
          scrambled1 += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        setLine1(scrambled1);
      } else {
        setLine1(target1);
      }

      if (frame <= target2.length) {
        let scrambled2 = target2.slice(0, frame);
        for (let k = 0; k < Math.min(2, target2.length - frame); k++) {
          scrambled2 += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        setLine2(scrambled2);
      } else {
        setLine2(target2);
      }

      if (frame > target2.length + 3) {
        clearInterval(interval);
        setLine1(target1);
        setLine2(target2);
      }
    }, 60);

    return () => clearInterval(interval);
  }, []);

  return (
    <div 
      className="hudgroup transition-opacity duration-150"
      style={{ opacity, pointerEvents: opacity < 0.05 ? 'none' : 'auto' }}
      aria-label="Repository architecture survey instrument"
    >
      <svg className="hud" viewBox="0 0 1280 720">
        <defs>
          <filter id="node-glow" x="-120%" y="-120%" width="340%" height="340%">
            <feGaussianBlur stdDeviation="3.2" />
          </filter>
        </defs>

        {/* Survey Axes and calibration lines */}
        <g className="axes" aria-hidden="true">
          <path className="dashed" d="M762.5 374V452M731 406.5H857M731 391.5h17M731 396.5h21M731 402.5h17" />
          <path className="solid" d="M731 388.5h15M731 390h12M731 392h15M731 393.5h10M731 395h15" />
        </g>

        {/* Clickable Survey Node */}
        <g 
          className="node-hit group cursor-pointer"
          role="button"
          tabIndex={0}
          onClick={onOpenSurveyNote}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onOpenSurveyNote();
            }
          }}
          aria-label="Inspect repository structure and dependencies"
        >
          <circle className="hit-area" cx="762.5" cy="406.5" r="28" fill="transparent" />
          <circle cx="762.5" cy="406.5" r="14" fill="none" stroke="rgba(77, 163, 255, 0.4)" strokeWidth="1" />
          <g className="node transition-transform duration-300 group-hover:scale-125">
            <circle cx="762.5" cy="406.5" r="9" fill="#0071FF" filter="url(#node-glow)" opacity="0.9" />
            <circle cx="762.5" cy="406.5" r="6" fill="#0071FF" />
            <circle cx="762.5" cy="406.5" r="2.2" fill="#FFFFFF" />
          </g>
        </g>

        {/* Reticle Marks */}
        <g className="marks" aria-hidden="true">
          <circle className="ring" cx="800" cy="418" r="4.5" />
          <circle className="dot" cx="800" cy="418" r="1.5" />
          <path className="plus" d="M830 380v8M826 384h8" />
        </g>
      </svg>

      {/* Blue Pill: REPOSITORY */}
      <button 
        type="button"
        onClick={onOpenSurveyNote}
        className="pill text-white focus-visible:outline-none"
        aria-label="Inspect Repository Specification"
      >
        <span>REPOSITORY</span>
      </button>

      {/* Technical Annotation */}
      <div 
        onClick={onOpenSurveyNote}
        className="annot hover:text-[#8FC2FF] transition-colors"
        role="button"
        tabIndex={0}
      >
        <span>{line1}</span>
        <span>{line2}</span>
      </div>
    </div>
  );
};
