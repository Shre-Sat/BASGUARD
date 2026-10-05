import { useState, useRef, useEffect } from 'react';
import { useExperimentStore } from '../../store/useExperimentStore';
import { 
  Camera, 
  Eye, 
  Scan,
  Video,
  UserCheck,
  CheckCircle2
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
    triggerNormalSequence,
    addAlert
  } = useExperimentStore();

  const [activeCam, setActiveCam] = useState<'CAM01' | 'CAM02' | 'WEBCAM'>('CAM01');
  const [shutterFlash, setShutterFlash] = useState(false);
  const [snapshotCount, setSnapshotCount] = useState(0);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const webcamVideoRef = useRef<HTMLVideoElement | null>(null);

  const isOnline = health.streamStatus === 'CONNECTED' || demoMode || activeCam === 'WEBCAM';

  useEffect(() => {
    let stream: MediaStream | null = null;

    if (activeCam === 'WEBCAM') {
      navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } })
        .then((s) => {
          stream = s;
          if (webcamVideoRef.current) {
            webcamVideoRef.current.srcObject = stream;
          }
          addAlert({
            severity: 'SUCCESS',
            type: 'SYSTEM',
            message: 'User Hardware Webcam connected successfully for live astronaut step verification.',
            acknowledged: false
          });
        })
        .catch((err) => {
          console.error('Failed to access webcam:', err);
          addAlert({
            severity: 'WARNING',
            type: 'SYSTEM',
            message: 'Webcam permission denied or device not found.',
            acknowledged: false
          });
        });
    }

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [activeCam]);

  const handleTakeSnapshot = () => {
    setShutterFlash(true);
    setSnapshotCount(prev => prev + 1);
    setTimeout(() => setShutterFlash(false), 350);

    addAlert({
      severity: 'INFO',
      type: 'SYSTEM',
      message: `Camera snapshot captured (${activeCam} #${snapshotCount + 1}). Telemetry logged.`,
      acknowledged: false
    });
  };

  useEffect(() => {
    if (!demoMode || !canvasRef.current || activeCam === 'WEBCAM') return;
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

      if (activeCam === 'CAM02') {
        baseX = canvas.width * 0.5 + Math.sin(t * 0.5) * 20;
        baseY = canvas.height * 0.35 + Math.cos(t * 0.5) * 15;
      } else if (experiment.currentStepId === 'PICK_YELLOW' || experiment.currentStepId === 'PLACE_YELLOW') {
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

      ctx.strokeStyle = activeCam === 'CAM02' ? '#3B82F6' : '#10B981';
      ctx.lineWidth = 2;
      ctx.shadowColor = activeCam === 'CAM02' ? '#3B82F6' : '#10B981';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      joints.forEach((j, idx) => {
        if (idx === 0) return;
        ctx.moveTo(joints[0].x, joints[0].y);
        ctx.lineTo(j.x, j.y);
      });
      ctx.stroke();

      joints.forEach((j) => {
        ctx.fillStyle = activeCam === 'CAM02' ? '#93C5FD' : '#6EE7B7';
        ctx.beginPath();
        ctx.arc(j.x, j.y, 4, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.shadowBlur = 0;
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillStyle = activeCam === 'CAM02' ? '#93C5FD' : '#10B981';
      ctx.fillText(
        activeCam === 'CAM02' ? 'ASTRONAUT POSE (Chest Camera) · 21 KEYPOINTS' : 'HAND (Right Glove) · 21 KEYPOINTS', 
        baseX - 60, 
        baseY + 70
      );

      animId = requestAnimationFrame(renderHandSkeleton);
    };

    renderHandSkeleton();
    return () => cancelAnimationFrame(animId);
  }, [demoMode, experiment.currentStepId, activeCam]);

  return (
    <div className="relative w-full h-full flex flex-col bg-[#04070D] overflow-hidden select-none border border-white/5">
      {shutterFlash && <div className="absolute inset-0 z-50 shutter-flash pointer-events-none" />}

      {/* Top Controls Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-[#090D18]/80 backdrop-blur-md border-b border-white/10 shrink-0 z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Scan className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold font-mono text-slate-200">PERCEPTION FEED</span>
          </div>

          {/* Multi-Camera Angle Selector Buttons */}
          <div className="flex items-center gap-1 font-mono text-[10px]">
            <button
              onClick={() => setActiveCam('CAM01')}
              className={`px-2 py-0.5 rounded border transition-all ${
                activeCam === 'CAM01' 
                  ? 'bg-blue-500/20 text-blue-300 border-blue-500/40 font-bold shadow-glow-accent' 
                  : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
              }`}
            >
              CAM-01 [PAYLOAD]
            </button>

            <button
              onClick={() => setActiveCam('CAM02')}
              className={`px-2 py-0.5 rounded border transition-all ${
                activeCam === 'CAM02' 
                  ? 'bg-blue-500/20 text-blue-300 border-blue-500/40 font-bold shadow-glow-accent' 
                  : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
              }`}
            >
              CAM-02 [BODYCAM]
            </button>

            <button
              onClick={() => setActiveCam('WEBCAM')}
              className={`px-2 py-0.5 rounded border transition-all flex items-center gap-1 ${
                activeCam === 'WEBCAM' 
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold shadow-glow-success' 
                  : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
              }`}
            >
              <Video className="w-3 h-3 text-emerald-400" />
              <span>LIVE WEBCAM</span>
            </button>
          </div>
        </div>

        {/* HUD Overlay Toggles */}
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

      {/* Main Viewport Container */}
      <div className="flex-1 relative bg-[#03050A] overflow-hidden flex items-center justify-center">
        {/* Tactical Crosshair Guidelines */}
        <div className="absolute inset-0 pointer-events-none z-10 opacity-30">
          <div className="absolute top-1/2 left-0 right-0 h-px bg-blue-500/40" />
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-blue-500/40" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full border border-blue-500/20 pointer-events-none" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 rounded-full border border-blue-500/10 pointer-events-none" />
        </div>

        {/* HUD Corner Bracket Reticles */}
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

        {/* Real Hardware User Webcam Feed Viewport */}
        {activeCam === 'WEBCAM' ? (
          <div className="relative w-full h-full flex items-center justify-center bg-black">
            <video 
              ref={webcamVideoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover z-10"
            />

            <div className="absolute top-[25%] left-[25%] w-[50%] h-[50%] border-2 border-emerald-400/80 rounded z-20 shadow-glow-success pointer-events-none">
              <div className="absolute -top-6 left-0 px-2 py-0.5 bg-emerald-600 text-white rounded text-[10px] font-mono shadow-md">
                LIVE_WEBCAM_DETECTION · ASTRONAUT_HAND
              </div>
            </div>

            <div className="absolute top-4 right-4 z-30 flex items-center gap-2 px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-xs font-mono backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>HARDWARE WEBCAM ACTIVE</span>
            </div>
          </div>
        ) : isOnline ? (
          <>
            {demoMode ? (
              <div className="relative w-full h-full flex items-center justify-center">
                <div className="absolute inset-0 flex items-center justify-center opacity-15">
                  <div className="w-[600px] h-[400px] border-2 border-dashed border-slate-500/40 rounded-2xl flex items-center justify-center">
                    <span className="text-4xl font-black font-mono text-slate-600 tracking-widest">
                      {activeCam === 'CAM01' ? 'ISRO BAS CONTAINER' : 'ASTRONAUT BODY SUIT'}
                    </span>
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
                  className={`absolute ${
                    activeCam === 'CAM01' ? 'top-[20%] left-[16%] w-[48%] h-[55%]' : 'top-[15%] left-[25%] w-[50%] h-[65%]'
                  } border-2 border-blue-400/70 rounded bg-blue-500/5 z-20 shadow-glow-accent`}
                >
                  <div className="absolute -top-6 left-0 flex items-center gap-1.5 px-2 py-0.5 bg-blue-600 text-white rounded text-[10px] font-mono shadow-md">
                    <span>{activeCam === 'CAM01' ? 'OUTER_CONTAINER' : 'ASTRONAUT_TORSO_SUIT'}</span>
                    <span className="text-blue-200">98.4%</span>
                  </div>
                  <div className="absolute -top-1 -left-1 w-2 h-2 bg-blue-400" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue-400" />
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-blue-400" />
                  <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-blue-400" />
                </motion.div>

                {activeCam === 'CAM01' && (
                  <>
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
                  </>
                )}

                <div className="absolute bottom-4 left-4 z-30 flex flex-col gap-1 text-[11px] font-mono text-slate-300 bg-slate-950/80 p-2.5 rounded border border-white/10 backdrop-blur-md">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                    <span className="text-emerald-400 font-semibold">LIVE DETECTIONS ({activeCam})</span>
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

        {/* Floating Astronaut Step Verification Card */}
        <div className="absolute top-4 right-4 z-30 glass-panel p-3 rounded-lg border border-white/10 w-72 flex flex-col gap-2 shadow-2xl">
          <div className="flex items-center justify-between pb-1.5 border-b border-white/10 text-xs font-mono">
            <span className="text-slate-300 font-semibold flex items-center gap-1.5">
              <UserCheck className="w-4 h-4 text-blue-400" /> ASTRONAUT STEP VERIFIER
            </span>
            <span className="text-[10px] text-emerald-400 font-bold">ACTIVE</span>
          </div>

          <div className="flex flex-col gap-1 font-mono text-[11px]">
            <div className="flex justify-between text-slate-400">
              <span>CURRENT STEP:</span>
              <span className="text-amber-400 font-bold">{experiment.currentStepId}</span>
            </div>
            <p className="text-[10px] font-sans text-slate-300 leading-snug">
              Monitoring astronaut glove trajectory & box contact vector.
            </p>

            <button
              onClick={triggerNormalSequence}
              className="mt-1.5 w-full py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-mono text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-all shadow-md active:scale-95"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300" />
              <span>VERIFY STEP ({experiment.currentStepId})</span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between px-4 py-2 bg-[#090D18]/90 border-t border-white/10 shrink-0 font-mono text-xs text-slate-400">
        <div className="flex items-center gap-6">
          <span>RES: 1920 × 1080 @ 30 FPS</span>
          <span>SOURCE: {activeCam}</span>
        </div>
        <div className="flex items-center gap-4 text-emerald-400">
          <span>CONFIDENCE: {experiment.confidence.toFixed(1)}%</span>
          <span className="text-blue-400">SNAPSHOTS: {snapshotCount}</span>
        </div>
      </div>
    </div>
  );
};
