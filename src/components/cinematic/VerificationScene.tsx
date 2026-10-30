import React from 'react';

interface VerificationSceneProps {
  progress: number;
  onSelectMarker: (index: number) => void;
  activeMarkerIndex: number | null;
}

const MARKERS = [
  {
    index: 0,
    title: 'SANDBOX',
    subtitle: 'EXECUTES REAL SETUP STEPS',
    x: '22.8%',
    y: '53.5%',
    mx: '18%',
    my: '58%',
  },
  {
    index: 1,
    title: 'DRIFT RADAR',
    subtitle: 'FINDS DOCS VS CI MISMATCH',
    x: '76.45%',
    y: '50.5%',
    mx: '54%',
    my: '65%',
  },
  {
    index: 2,
    title: 'PROOF ENGINE',
    subtitle: 'TESTS FIXES BEFORE PATCHING',
    x: '6.5%',
    y: '73.3%',
    mx: '12%',
    my: '76%',
  },
  {
    index: 3,
    title: 'ZERO-TRUST',
    subtitle: 'BLOCKS UNVERIFIED COMMANDS',
    x: '61.65%',
    y: '80.1%',
    mx: '50%',
    my: '87%',
  },
];

export const VerificationScene: React.FC<VerificationSceneProps> = ({
  progress,
  onSelectMarker,
  activeMarkerIndex,
}) => {
  const isVisible = progress > 0.75;
  const opacity = Math.max(0, Math.min(1, (progress - 0.78) / 0.15));

  if (!isVisible) return null;

  return (
    <div 
      className="eco"
      style={{ opacity, pointerEvents: opacity > 0.4 ? 'auto' : 'none' }}
      aria-label="Scene 03: Verified Contributor Onboarding"
    >
      {/* Top Editorial Statement */}
      <div 
        className="eco-top"
        style={{
          transform: `translateY(${22 * (1 - opacity)}px)`,
          opacity,
        }}
      >
        <div className="eco-label">
          EXECUTION-BACKED<br />
          DOCUMENTATION REPAIR<br />
          SECURITY-VERIFIED
        </div>
        <h2>
          CIVORA connects repository instructions, CI evidence and isolated execution—so every documentation repair is proven before it reaches a contributor.
        </h2>
      </div>

      {/* Four Interactive Blue Markers */}
      <div id="spots" aria-label="Interactive architecture verification markers">
        {MARKERS.map((m, idx) => {
          const markerProgress = Math.max(0, Math.min(1, (progress - (0.80 + idx * 0.035)) / 0.1));
          const markerOpacity = markerProgress;
          const markerScale = 0.7 + 0.3 * markerProgress;
          const isActive = activeMarkerIndex === m.index;

          return (
            <button
              key={m.index}
              type="button"
              className="spot group focus-visible:outline-none"
              style={{
                '--x': m.x,
                '--y': m.y,
                opacity: markerOpacity,
                transform: `scale(${markerScale})`,
                pointerEvents: markerProgress > 0.5 ? 'auto' : 'none',
              } as React.CSSProperties}
              onClick={() => onSelectMarker(m.index)}
              aria-label={`Explore ${m.title}: ${m.subtitle}`}
              aria-expanded={isActive}
            >
              <span className="pin">
                {/* 5-dot SVG inside the pin */}
                <svg viewBox="0 0 16 16" aria-hidden="true">
                  <circle cx="8" cy="8" r="1.5" />
                  <circle cx="8" cy="3" r="1.5" />
                  <circle cx="3" cy="8" r="1.5" />
                  <circle cx="13" cy="8" r="1.5" />
                  <circle cx="8" cy="13" r="1.5" />
                </svg>
              </span>
              <span className="cap">
                {m.title}<br />
                {m.subtitle}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

