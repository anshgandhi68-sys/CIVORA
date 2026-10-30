import React, { useState, useEffect } from 'react';
import { CivoraCinematicSite } from './components/cinematic/CivoraCinematicSite';
import { MissionControl } from './components/mission-control/MissionControl';
import { DriftRadar } from './components/radar/DriftRadar';
import { GemmaBenchmark } from './components/benchmark/GemmaBenchmark';

export type AppView = 'cinematic' | 'mission-control' | 'radar' | 'benchmark';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>('cinematic');

  // Sync state with browser location path
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/mission-control') {
        setCurrentView('mission-control');
      } else if (path === '/radar') {
        setCurrentView('radar');
      } else if (path === '/benchmark') {
        setCurrentView('benchmark');
      } else {
        setCurrentView('cinematic');
      }
    };

    handlePopState();
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigateToView = (view: AppView) => {
    setCurrentView(view);
    const path = view === 'cinematic' ? '/' : `/${view}`;
    window.history.pushState({}, '', path);
    window.scrollTo(0, 0);
  };

  return (
    <div className="w-full min-h-screen bg-[#01030F] text-white">
      {currentView === 'cinematic' && (
        <CivoraCinematicSite 
          onOpenWorkspace={() => navigateToView('mission-control')}
          onOpenBenchmark={() => navigateToView('benchmark')}
        />
      )}

      {currentView === 'mission-control' && (
        <MissionControl 
          onReturnToSite={() => navigateToView('cinematic')}
          onOpenRadar={() => navigateToView('radar')}
          onOpenBenchmark={() => navigateToView('benchmark')}
        />
      )}

      {currentView === 'radar' && (
        <DriftRadar 
          onReturnToSite={() => navigateToView('cinematic')}
          onOpenWorkspace={() => navigateToView('mission-control')}
        />
      )}

      {currentView === 'benchmark' && (
        <GemmaBenchmark 
          onReturnToSite={() => navigateToView('cinematic')}
          onOpenWorkspace={() => navigateToView('mission-control')}
        />
      )}
    </div>
  );
};

export default App;

