import { useState } from 'react';
import { Viewer3D } from '../components/viewer3d/Viewer3D';
import { Box, Eye, Grid, Shield, Radio, Activity } from 'lucide-react';

export const Scene = () => {
  const [showWireframe, setShowWireframe] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [showBounds, setShowBounds] = useState(true);
  const [cameraPreset, setCameraPreset] = useState<'ISOMETRIC' | 'PAYLOAD_TOP' | 'ASTRONAUT_POV'>('ISOMETRIC');

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-bg-dark">
      {/* Control Bar */}
      <div className="h-12 border-b border-border bg-bg-panel px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-text-primary uppercase tracking-wider">
            <Box className="w-4 h-4 text-accent" /> 3D Digital Twin & Spatial Perception Viewport
          </div>
          <span className="text-border">|</span>
          <span className="text-meta text-text-tertiary font-mono">FRAME: 14,892 // TIME: 00:14:32</span>
        </div>

        {/* Viewport controls */}
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1 bg-bg-dark border border-border rounded p-0.5">
            <button
              onClick={() => setCameraPreset('ISOMETRIC')}
              className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                cameraPreset === 'ISOMETRIC' ? 'bg-accent/20 text-accent font-semibold' : 'text-text-tertiary hover:text-text-primary'
              }`}
            >
              Isometric
            </button>
            <button
              onClick={() => setCameraPreset('PAYLOAD_TOP')}
              className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                cameraPreset === 'PAYLOAD_TOP' ? 'bg-accent/20 text-accent font-semibold' : 'text-text-tertiary hover:text-text-primary'
              }`}
            >
              Payload Top
            </button>
            <button
              onClick={() => setCameraPreset('ASTRONAUT_POV')}
              className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                cameraPreset === 'ASTRONAUT_POV' ? 'bg-accent/20 text-accent font-semibold' : 'text-text-tertiary hover:text-text-primary'
              }`}
            >
              Chest POV
            </button>
          </div>

          <button
            onClick={() => setShowWireframe(!showWireframe)}
            className={`px-2.5 py-1.5 rounded border text-[11px] font-mono flex items-center gap-1.5 transition-colors ${
              showWireframe ? 'border-accent/40 bg-accent/10 text-accent' : 'border-border text-text-tertiary hover:text-text-primary'
            }`}
          >
            <Eye className="w-3.5 h-3.5" /> Bounding 3D
          </button>

          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`px-2.5 py-1.5 rounded border text-[11px] font-mono flex items-center gap-1.5 transition-colors ${
              showGrid ? 'border-accent/40 bg-accent/10 text-accent' : 'border-border text-text-tertiary hover:text-text-primary'
            }`}
          >
            <Grid className="w-3.5 h-3.5" /> Calib Grid
          </button>

          <button
            onClick={() => setShowBounds(!showBounds)}
            className={`px-2.5 py-1.5 rounded border text-[11px] font-mono flex items-center gap-1.5 transition-colors ${
              showBounds ? 'border-accent/40 bg-accent/10 text-accent' : 'border-border text-text-tertiary hover:text-text-primary'
            }`}
          >
            <Shield className="w-3.5 h-3.5" /> Safety Zone
          </button>
        </div>
      </div>

      {/* Main 3D Canvas Area */}
      <div className="flex-1 relative">
        <Viewer3D />

        {/* Floating Spatial Joint Coordinate Telemetry Drawer */}
        <div className="absolute top-4 right-4 border border-border/80 rounded bg-bg-panel/90 backdrop-blur p-4 w-72 flex flex-col gap-3 text-xs shadow-xl">
          <div className="flex items-center justify-between pb-2 border-b border-border">
            <span className="font-semibold text-text-primary uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-accent" /> Spatial Kinematics (mm)
            </span>
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          </div>

          <div className="space-y-2 font-mono text-[11px]">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Right Wrist X,Y,Z:</span>
              <span className="text-accent">+142.4, -28.1, +310.8</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Right Index Tip:</span>
              <span className="text-text-primary">+148.9, -24.3, +298.2</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Yellow Box Center:</span>
              <span className="text-yellow-400">+150.1, -25.0, +295.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Contact Vector:</span>
              <span className="text-emerald-400">0.8 mm (GRASPED)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
