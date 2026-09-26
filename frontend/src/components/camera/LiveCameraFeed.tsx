import { useExperimentStore } from '../../store/useExperimentStore';

export const LiveCameraFeed = () => {
  const { experiment, health, demoMode } = useExperimentStore();
  const isOnline = health.streamStatus === 'CONNECTED';

  return (
    <div className="relative w-full h-full flex flex-col bg-base overflow-hidden">
      {/* Section label */}
      <div className="flex items-center justify-between px-4 py-2 shrink-0">
        <div className="flex items-baseline gap-3">
          <span className="text-label font-medium text-text-secondary">Live Perception</span>
          <span className="text-meta font-mono text-text-muted">CAM-01</span>
        </div>
        {isOnline && (
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-semantic-critical animate-pulse" />
            <span className="text-meta font-medium text-semantic-critical">LIVE</span>
          </div>
        )}
      </div>

      {/* Video viewport */}
      <div className="flex-1 relative bg-[#050810] mx-4 mb-2 rounded overflow-hidden">
        {isOnline ? (
          <>
            {/* Subtle reference grid */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:60px_60px] pointer-events-none z-10" />

            {demoMode ? (
              // DEMO MODE: Simulated UI
              <>
                {/* Bounding box: Outer Box */}
                <div className="absolute top-[22%] left-[18%] w-[45%] h-[50%] border border-text-muted/40 z-20">
                  <span className="absolute -top-5 left-0 text-meta font-mono text-text-tertiary">
                    outer_box <span className="text-text-muted">96.4%</span>
                  </span>
                </div>

                {/* Bounding box: Red Box */}
                <div className="absolute top-[35%] left-[22%] w-[14%] h-[22%] border border-semantic-critical/40 z-20">
                  <span className="absolute -top-5 left-0 text-meta font-mono text-text-tertiary">
                    red_box <span className="text-text-muted">94.8%</span>
                  </span>
                </div>

                {/* Bounding box: Yellow Box */}
                {(experiment.currentStepId === 'IDENTIFY_YELLOW' ||
                  experiment.currentStepId === 'PICK_YELLOW' ||
                  experiment.currentStepId === 'PLACE_YELLOW') && (
                  <div className="absolute top-[38%] left-[40%] w-[12%] h-[18%] border border-semantic-warning/40 z-20">
                    <span className="absolute -top-5 left-0 text-meta font-mono text-text-tertiary">
                      yellow_box <span className="text-text-muted">97.1%</span>
                    </span>
                  </div>
                )}

                {/* Hand indicator */}
                {['PICK_YELLOW', 'PLACE_YELLOW', 'OPEN_OUTER'].includes(experiment.currentStepId) && (
                  <div className="absolute top-[48%] left-[46%] z-20">
                    <div className="w-1.5 h-1.5 bg-semantic-success rounded-full" />
                    <span className="absolute top-3 left-0 text-meta font-mono text-semantic-success/70 whitespace-nowrap">
                      hand · {experiment.currentStepId === 'PICK_YELLOW' ? 'holding' : 'approaching'}
                    </span>
                  </div>
                )}
              </>
            ) : (
              // REAL BACKEND MJPEG FEED
              <img 
                src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/video_feed`} 
                alt="Live Camera Feed"
                className="w-full h-full object-contain"
              />
            )}

            {/* Center crosshair — very subtle */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20 pointer-events-none z-10">
              <div className="w-6 h-px bg-white absolute top-1/2 left-1/2 -translate-x-1/2" />
              <div className="h-6 w-px bg-white absolute top-1/2 left-1/2 -translate-y-1/2" />
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <span className="text-sm text-text-muted">No signal</span>
          </div>
        )}
      </div>

      {/* Bottom metadata */}
      <div className="flex items-center gap-6 px-4 py-1.5 text-meta font-mono text-text-muted shrink-0">
        <span>1920 × 1080</span>
        <span>{health.fps.toFixed(1)} fps</span>
        <span>{health.inferenceLatency} ms inference</span>
      </div>
    </div>
  );
};
