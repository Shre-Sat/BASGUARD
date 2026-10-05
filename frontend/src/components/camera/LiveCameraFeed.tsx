import { useState, useRef, useEffect } from 'react';
import { useExperimentStore } from '../../store/useExperimentStore';
import { 
  Camera, 
  Eye, 
  Scan
} from 'lucide-react';
import { motion } from 'framer-motion';

export const LiveCameraFeed = () => {
  const { 
    experiment, 
    health, 
    demoMode, 
    showScanlines, 
    setShowScanlines,
    showHsvFilter,
    setShowHsvFilter,
    addAlert
  } = useExperimentStore();

  const [shutterFlash, setShutterFlash] = useState(false);
  const [snapshotCount, setSnapshotCount] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const isOnline = health.streamStatus === 'CONNECTED' || demoMode;

  const handleTakeSnapshot = () => {
    setShutterFlash(true);
    setSnapshotCount(prev => prev + 1);
    setTimeout(() => setShutterFlash(false), 350);

    addAlert({
      severity: 'INFO',
      type: 'SYSTEM',
      message: `Camera snapshot captured (#${snapshotCount + 1}). Telemetry frame logged.`,
      acknowledged: false
    });
  };

  useEffect(() => {
    if (!demoMode || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let t = 0;

    const renderHandSkeleton = () => {
      t += 0.03;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      let baseX = canvas.width * 0.45 + Math.sin(t * 0.8) * 15;
      let baseY = canvas.height * 0.48 + Math.cos(t * 0.6) * 10;

      if (experiment.currentStepId === 'PICK_YELLOW' || experiment.currentStepId === 'PLACE_YELLOW') {
        baseX = canvas.width * 0.42 + Math.sin(t * 1.2) * 8;
        baseY = canvas.height * 0.42 + Math.cos(t * 1.2) * 6;
      }

      const joints = [
        { x: baseX, y: baseY + 50 },
        { x: baseX - 15, y: baseY + 35 },
        { x: baseX - 25, y: baseY + 20 },
        { x: baseX - 35, y: baseY + 10 },
        { x: baseX - 10, y: baseY + 15 },
        { x: baseX - 12, y: baseY - 10 },
        { x: baseX - 14, y: baseY - 30 },
        { x: baseX, y: baseY + 10 },
        { x: baseX, y: baseY - 20 },
        { x: baseX, y: baseY - 40 },
        { x: baseX + 10, y: baseY + 15 },
        { x: baseX + 12, y: baseY - 10 },
        { x: baseX + 14, y: baseY - 30 },
        { x: baseX + 20, y: baseY + 25 },
        { x: baseX + 25, y: baseY + 5 },
        { x: baseX + 28, y: baseY - 15 },
      ];

      ctx.strokeStyle = '#10B981';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#10B981';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      joints.forEach((j, idx) => {
        if (idx === 0) return;
        ctx.moveTo(joints[0].x, joints[0].y);
        ctx.lineTo(j.x, j.y);
      });
      ctx.stroke();

      joints.forEach((j) => {
        ctx.fillStyle = '#6EE7B7';
        ctx.beginPath();
        ctx.arc(j.x, j.y, 4, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.shadowBlur = 0;
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillStyle = '#10B981';
      ctx.fillText('HAND (Right Glove) · 21 KEYPOINTS', baseX - 40, baseY + 70);

      animId = requestAnimationFrame(renderHandSkeleton);
    };

    renderHandSkeleton();
    return () => cancelAnimationFrame(animId);
  }, [demoMode, experiment.currentStepId]);

  return (
    <div className="relative w-full h-full flex flex-col bg-[#04070D] overflow-hidden select-none border border-white/5">
      {shutterFlash && <div className="absolute inset-0 z-50 shutter-flash pointer-events-none" />}

      <div className="flex items-center justify-between px-3 py-2 bg-[#090D18]/80 backdrop-blur-md border-b border-white/10 shrink-0 z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Scan className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold font-mono text-slate-200">LIVE PERCEPTION</span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
            CAM-01 [YOLOv8x + HSV]
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowScanlines(!showScanlines)}
            className={`px-2 py-1 text-[10px] font-mono rounded border transition-colors ${
              showScanlines 
                ? 'bg-blue-500/20 text-blue-300 border-blue-500/40' 
                : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
            }`}
          >
            SCANLINES {showScanlines ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={() => setShowHsvFilter(!showHsvFilter)}
            className={`px-2 py-1 text-[10px] font-mono rounded border transition-colors ${
              showHsvFilter 
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' 
                : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
            }`}
          >
            HSV FILTER {showHsvFilter ? 'ACTIVE' : 'RAW'}
          </button>

          <button
            onClick={handleTakeSnapshot}
            className="flex items-center gap-1 px-2.5 py-1 text-[10px] font-mono rounded bg-slate-800 text-slate-200 border border-white/15 hover:bg-slate-700 active:scale-95 transition-all"
            title="Take High-Res Telemetry Snapshot"
          >
            <Camera className="w-3.5 h-3.5 text-emerald-400" />
            <span>SNAPSHOT</span>
          </button>
        </div>
      </div>

      <div className="flex-1 relative bg-[#03050A] overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 pointer-events-none z-10 opacity-30">
          <div className="absolute top-1/2 left-0 right-0 h-px bg-blue-500/40" />
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-blue-500/40" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full border border-blue-500/20 pointer-events-none" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 rounded-full border border-blue-500/10 pointer-events-none" />
        </div>

        <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-blue-400/60 pointer-events-none z-20" />
        <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-blue-400/60 pointer-events-none z-20" />
        <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-blue-400/60 pointer-events-none z-20" />
        <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-blue-400/60 pointer-events-none z-20" />

        {showScanlines && (
          <div className="absolute inset-0 scanline-overlay pointer-events-none z-10" />
        )}
        {showScanlines && (
          <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400/50 to-transparent scan-beam pointer-events-none z-20 shadow-glow-accent" />
        )}

        {showHsvFilter && (
          <div className="absolute inset-0 bg-amber-500/10 mix-blend-color-dodge pointer-events-none z-10" />
        )}

        {isOnline ? (
          <>
            {demoMode ? (
              <div className="relative w-full h-full flex items-center justify-center">
                <div className="absolute inset-0 flex items-center justify-center opacity-15">
                  <div className="w-[600px] h-[400px] border-2 border-dashed border-slate-500/40 rounded-2xl flex items-center justify-center">
                    <span className="text-4xl font-black font-mono text-slate-600 tracking-widest">ISRO BAS CONTAINER</span>
                  </div>
                </div>

                <canvas 
                  ref={canvasRef} 
                  width={800} 
                  height={500} 
                  className="absolute inset-0 w-full h-full object-cover z-20 pointer-events-none" 
                />

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="absolute top-[20%] left-[16%] w-[48%] h-[55%] border-2 border-blue-400/70 rounded bg-blue-500/5 z-20 shadow-glow-accent"
                >
                  <div className="absolute -top-6 left-0 flex items-center gap-1.5 px-2 py-0.5 bg-blue-600 text-white rounded text-[10px] font-mono shadow-md">
                    <span>OUTER_CONTAINER</span>
                    <span className="text-blue-200">98.4%</span>
                  </div>
                  <div className="absolute -top-1 -left-1 w-2 h-2 bg-blue-400" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue-400" />
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-blue-400" />
                  <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-blue-400" />
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="absolute top-[32%] left-[20%] w-[15%] h-[26%] border-2 border-rose-500/80 rounded bg-rose-500/10 z-20 shadow-glow-critical"
                >
                  <div className="absolute -top-6 left-0 flex items-center gap-1 px-2 py-0.5 bg-rose-600 text-white rounded text-[10px] font-mono shadow-md">
                    <span>RED_BOX</span>
                    <span className="text-rose-200">96.2%</span>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="absolute top-[34%] left-[42%] w-[14%] h-[24%] border-2 border-amber-400/90 rounded bg-amber-500/10 z-20 shadow-glow-isro"
                >
                  <div className="absolute -top-6 left-0 flex items-center gap-1 px-2 py-0.5 bg-amber-600 text-white rounded text-[10px] font-mono shadow-md">
                    <span>YELLOW_BOX</span>
                    <span className="text-amber-100">97.8%</span>
                  </div>
                </motion.div>

                <div className="absolute bottom-4 left-4 z-30 flex flex-col gap-1 text-[11px] font-mono text-slate-300 bg-slate-950/80 p-2.5 rounded border border-white/10 backdrop-blur-md">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                    <span className="text-emerald-400 font-semibold">LIVE DETECTIONS (3 OBJECTS)</span>
                  </div>
                  <div className="text-slate-400">YOLO: 14.2ms | MEDIAPIPE 3D: 8.6ms</div>
                  <div className="text-slate-400">PETRI-NET: STATE VALID</div>
                </div>
              </div>
            ) : (
              <img 
                src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/video_feed`} 
                alt="ISRO BAS Live Camera Stream"
                className="w-full h-full object-contain z-10"
              />
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 z-30">
            <Eye className="w-10 h-10 text-slate-600 animate-pulse" />
            <span className="text-sm font-mono text-slate-400">CAMERA STREAM OFFLINE</span>
            <span className="text-xs font-mono text-slate-600">Connecting to GStreamer pipeline...</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between px-4 py-2 bg-[#090D18]/90 border-t border-white/10 shrink-0 font-mono text-xs text-slate-400">
        <div className="flex items-center gap-6">
          <span>RES: 1920 × 1080 @ 30 FPS</span>
          <span>CODEC: H.264 / RTSP</span>
        </div>
        <div className="flex items-center gap-4 text-emerald-400">
          <span>CONFIDENCE: {experiment.confidence.toFixed(1)}%</span>
          <span className="text-blue-400">SNAPSHOTS: {snapshotCount}</span>
        </div>
      </div>
    </div>
  );
};
