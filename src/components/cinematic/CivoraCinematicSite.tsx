import React, { useEffect, useRef, useState } from 'react';
import { BrandHeader } from './BrandHeader';
import { HeroScene } from './HeroScene';
import { VisionScene } from './VisionScene';
import { VerificationScene } from './VerificationScene';
import { SurveyHud } from './SurveyHud';
import { SystemNoteDialog } from './SystemNoteDialog';
import { MobileMenu } from './MobileMenu';

interface CivoraCinematicSiteProps {
  onOpenWorkspace: () => void;
  onOpenBenchmark: () => void;
}

const FILM_MAP = [
  [0, 0],
  [0.12, 0.25],
  [0.47, 0.52],
  [0.72, 0.78],
  [0.92, 1],
  [1, 1],
];

const STILLS = [
  '/assets/civora-hero-plate.webp',
  '/assets/civora-vision-fallback.webp',
  '/assets/civora-city-fallback.webp',
];

function clamp01(v: number): number {
  return Math.max(0, Math.min(1, v));
}

function ramp(p: number, a: number, b: number): number {
  return clamp01((p - a) / (b - a));
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

function mapProgressToTime(points: number[][], p: number): number {
  for (let i = 1; i < points.length; i++) {
    if (p <= points[i][0]) {
      const segStart = points[i - 1][0];
      const segEnd = points[i][0];
      const t = ramp(p, segStart, segEnd);
      return points[i - 1][1] + (points[i][1] - points[i - 1][1]) * t;
    }
  }
  return points[points.length - 1][1];
}

export const CivoraCinematicSite: React.FC<CivoraCinematicSiteProps> = ({
  onOpenWorkspace,
  onOpenBenchmark,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const posterRef = useRef<HTMLImageElement>(null);

  const [displayedProgress, setDisplayedProgress] = useState<number>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const p = params.get('progress');
      if (p) {
        const val = parseFloat(p);
        if (!isNaN(val)) return val;
      }
    }
    return 0;
  });

  const [isVideoReady, setIsVideoReady] = useState(false);
  const [stillIndex, setStillIndex] = useState<number>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const p = params.get('progress');
      if (p) {
        const val = parseFloat(p);
        if (!isNaN(val)) return val < 0.15 ? 0 : val < 0.72 ? 1 : 2;
      }
    }
    return 0;
  });

  // Dialog & menu state
  const [activeNoteIndex, setActiveNoteIndex] = useState<number | null>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const n = params.get('note');
      if (n) {
        const val = parseInt(n, 10);
        if (!isNaN(val)) return val;
      }
    }
    return null;
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Scroll targets for smoothing
  const targetProgressRef = useRef(displayedProgress);
  const displayedProgressRef = useRef(displayedProgress);
  const lastTimeRef = useRef(0);
  const rafIdRef = useRef<number | null>(null);

  // Preload and initialize video
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const p = params.get('progress');
    if (p) {
      const progressVal = parseFloat(p);
      if (!isNaN(progressVal)) {
        targetProgressRef.current = progressVal;
        displayedProgressRef.current = progressVal;
        setDisplayedProgress(progressVal);
      }
    }

    const n = params.get('note');
    if (n) {
      const noteVal = parseInt(n, 10);
      if (!isNaN(noteVal)) {
        setActiveNoteIndex(noteVal);
      }
    }

    const video = videoRef.current;
    if (!video) return;

    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;

    const handleLoadedData = () => {
      video.pause();
      setIsVideoReady(true);
    };

    video.addEventListener('loadeddata', handleLoadedData);
    video.src = '/assets/civora-city-fabric-scrub.mp4';
    video.load();

    return () => {
      video.removeEventListener('loadeddata', handleLoadedData);
    };
  }, []);

  // Frame-rate independent scroll scrub loop
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
      const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      targetProgressRef.current = clamp01(scrollY / maxScroll);

      if (!rafIdRef.current) {
        rafIdRef.current = requestAnimationFrame(tick);
      }
    };

    const tick = (now: number) => {
      rafIdRef.current = null;
      const dt = lastTimeRef.current ? Math.min(64, now - lastTimeRef.current) : 16.667;
      lastTimeRef.current = now;

      // Exponential smoothing (1 - (1 - 0.11)^(dt / 16.667))
      const smoothing = 1 - Math.pow(1 - 0.11, dt / 16.667);
      displayedProgressRef.current += (targetProgressRef.current - displayedProgressRef.current) * smoothing;

      if (Math.abs(targetProgressRef.current - displayedProgressRef.current) < 0.0001) {
        displayedProgressRef.current = targetProgressRef.current;
      }

      const p = displayedProgressRef.current;
      setDisplayedProgress(p);

      // Video scrub seek
      const video = videoRef.current;
      if (video && isVideoReady && isFinite(video.duration) && !video.seeking) {
        const desiredRatio = mapProgressToTime(FILM_MAP, p);
        const desiredTime = desiredRatio * Math.max(0, video.duration - 0.05);
        if (Math.abs(video.currentTime - desiredTime) > 0.005) {
          video.currentTime = desiredTime;
        }
      }

      // Update still fallback image if video isn't ready
      const nextStill = p < 0.15 ? 0 : p < 0.72 ? 1 : 2;
      setStillIndex(nextStill);

      if (Math.abs(targetProgressRef.current - displayedProgressRef.current) > 0.0001) {
        rafIdRef.current = requestAnimationFrame(tick);
      } else {
        lastTimeRef.current = 0;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
    };
  }, [isVideoReady]);

  // Smooth programmatic scroll navigation
  const navigateToProgress = (p: number) => {
    setMobileMenuOpen(false);
    const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    window.scrollTo({
      top: maxScroll * p,
      behavior: 'smooth',
    });
  };

  // Transition calculation formulas matching reference
  const heroFade = easeOutCubic(ramp(displayedProgress, 0, 0.11));
  const heroOpacity = 1 - heroFade;
  const heroTranslateY = `${-56 * heroFade}px`;

  // Bar opacity: fades out 0.12–0.20, reappears 0.76–0.84
  const barOpacity = clamp01(1 - ramp(displayedProgress, 0.12, 0.20) + ramp(displayedProgress, 0.76, 0.84));

  // Scene 02 Vision progress: enters 0.15–0.31, leaves 0.47–0.57
  const visionEnter = easeOutCubic(ramp(displayedProgress, 0.15, 0.31));
  const visionLeave = easeOutCubic(ramp(displayedProgress, 0.47, 0.57));

  return (
    <>
      {/* 700vh Scroll Track */}
      <div className="track" aria-hidden="true" />

      {/* Fixed Full-Screen Visual Frame */}
      <div className="frame">
        {/* Background Video (Scrubbed) */}
        <video
          ref={videoRef}
          className={`plate film ${isVideoReady ? 'on' : ''}`}
          playsInline
          muted
          aria-hidden="true"
        />

        {/* Fallback Still Plate */}
        <img
          ref={posterRef}
          src={STILLS[stillIndex]}
          alt="CIVORA Architecture Model"
          className="plate"
          style={{
            opacity: isVideoReady ? 0 : 1,
            transition: 'opacity 0.4s ease',
          }}
          aria-hidden="true"
        />

        {/* Contrast Veils */}
        <div 
          className="veil veil-v" 
          style={{ opacity: Math.min(visionEnter, 1 - visionLeave) }}
          aria-hidden="true"
        />
        <div 
          className="veil veil-e" 
          style={{ opacity: ramp(displayedProgress, 0.80, 0.95) }}
          aria-hidden="true"
        />

        {/* Fixed Header directly inside frame for perfect responsive anchoring */}
        <BrandHeader
          onNavigateProgress={navigateToProgress}
          onOpenWorkspace={onOpenWorkspace}
          onOpenBenchmark={onOpenBenchmark}
          onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
          mobileMenuOpen={mobileMenuOpen}
          opacity={barOpacity}
        />

        {/* 1280x720 Logical Responsive Stage */}
        <div className="stage">
          {/* Scene 01: Hero Content */}
          <HeroScene
            onExplore={() => navigateToProgress(0.34)}
            opacity={heroOpacity}
            translateY={heroTranslateY}
          />

          {/* Surveying Annotations HUD */}
          <SurveyHud
            onOpenSurveyNote={() => setActiveNoteIndex(4)}
            opacity={heroOpacity}
          />

          {/* Scene 02: The CIVORA Method */}
          <VisionScene
            enterProgress={visionEnter}
            leaveProgress={visionLeave}
          />

          {/* Scene 03: Verified Contributor Experience */}
          <VerificationScene
            progress={displayedProgress}
            onSelectMarker={(idx) => setActiveNoteIndex(idx)}
            activeMarkerIndex={activeNoteIndex}
          />
        </div>

        {/* Detail Note Panel Dialog */}
        <SystemNoteDialog
          isOpen={activeNoteIndex !== null}
          activeNoteIndex={activeNoteIndex ?? 0}
          onClose={() => setActiveNoteIndex(null)}
          onSelectNote={(idx) => setActiveNoteIndex(idx)}
          onOpenWorkspace={onOpenWorkspace}
        />

        {/* Mobile Navigation Drawer */}
        <MobileMenu
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
          onNavigateProgress={navigateToProgress}
          onOpenWorkspace={onOpenWorkspace}
          onOpenBenchmark={onOpenBenchmark}
        />
      </div>
    </>
  );
};
