import React from 'react';

interface VisionSceneProps {
  enterProgress: number;
  leaveProgress: number;
}

export const VisionScene: React.FC<VisionSceneProps> = ({
  enterProgress,
  leaveProgress,
}) => {
  const isVisible = enterProgress > 0 && leaveProgress < 1;
  const opacity = Math.max(0, Math.min(1, enterProgress * (1 - leaveProgress)));
  const translateY = -18 * leaveProgress;
  const scale = 1 + 0.14 * leaveProgress;

  if (!isVisible) return null;

  return (
    <div 
      className="vision transition-transform duration-100"
      style={{
        opacity,
        transform: `translateY(${translateY}px) scale(${scale})`,
        pointerEvents: opacity > 0.3 ? 'auto' : 'none',
      }}
      aria-label="Scene 02: The CIVORA Method"
    >
      {/* Eyebrow */}
      <span 
        className="tag"
        style={{
          opacity: enterProgress,
          transform: `translateY(${10 * (1 - enterProgress)}px)`,
        }}
      >
        THE CIVORA METHOD
      </span>

      {/* Main Headline */}
      <h2>
        <i>
          <span style={{ transform: `translate3d(0, ${110 * (1 - Math.min(1, enterProgress * 1.3))}%, 0)` }}>
            From Broken Setup
          </span>
        </i>
        <i>
          <span style={{ transform: `translate3d(0, ${110 * (1 - Math.min(1, enterProgress * 1.15))}%, 0)` }}>
            Instructions to
          </span>
        </i>
        <i>
          <span style={{ transform: `translate3d(0, ${110 * (1 - Math.min(1, enterProgress))}%, 0)` }}>
            Verified Contribution
          </span>
        </i>
      </h2>

      {/* Supporting Paragraph */}
      <p 
        style={{
          opacity: Math.max(0, (enterProgress - 0.4) / 0.6),
          transform: `translateY(${12 * (1 - enterProgress)}px)`,
        }}
      >
        CIVORA follows the exact setup path a new developer would. It compares repository documentation against CI configuration, tests possible interventions, applies minimal verified edits and executes the repaired instructions again from a clean environment.
      </p>
    </div>
  );
};

