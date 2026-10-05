import { useState } from 'react';
import { Viewer3D } from '../components/viewer3d/Viewer3D';
import { Box, Eye, Grid, Shield, Radio, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export const Scene = () => {
  const [showWireframe, setShowWireframe] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [showBounds, setShowBounds] = useState(true);

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#04070D] font-sans select-none">
      <div className="h-12 border-b border-white/10 bg-[#090D18]/90 px-6 flex items-center justify-between shrink-0 backdrop-blur-md">
        <div className="flex items-center gap-4 font-mono">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-100 uppercase tracking-wider">
            <Box className="w-4 h-4 text-blue-400" /> 3D DIGITAL TWIN & KINEMATIC VIEWPORT
          </div>
          <span className="text-white/20">|</span>
          <span className="text-xs text-slate-400">ISRO RACK-RELATIVE FRAME (mm)</span>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <button
            onClick={() => setShowWireframe(!showWireframe)}
            className={`px-3 py-1.5 rounded border text-xs flex items-center gap-1.5 transition-all ${
              showWireframe ? 'border-blue-500/40 bg-blue-500/20 text-blue-300 font-semibold' : 'border-white/10 bg-slate-900 text-slate-400'
            }`}
          >
            <Eye className="w-3.5 h-3.5" /> BINDING 3D MESH
          </button>

          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`px-3 py-1.5 rounded border text-xs flex items-center gap-1.5 transition-all ${
              showGrid ? 'border-blue-500/40 bg-blue-500/20 text-blue-300 font-semibold' : 'border-white/10 bg-slate-900 text-slate-400'
            }`}
          >
            <Grid className="w-3.5 h-3.5" /> CALIBRATION GRID
          </button>

          <button
            onClick={() => setShowBounds(!showBounds)}
            className={`px-3 py-1.5 rounded border text-xs flex items-center gap-1.5 transition-all ${
              showBounds ? 'border-amber-500/40 bg-amber-500/20 text-amber-300 font-semibold' : 'border-white/10 bg-slate-900 text-slate-400'
            }`}
          >
            <Shield className="w-3.5 h-3.5" /> SAFETY BOUNDARIES
          </button>
        </div>
      </div>

      <div className="flex-1 relative">
        <Viewer3D />

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="absolute top-4 right-4 glass-panel border border-white/10 rounded-xl p-4 w-80 flex flex-col gap-3 text-xs shadow-2xl z-20"
        >
          <div className="flex items-center justify-between pb-2 border-b border-white/10">
            <span className="font-semibold text-slate-200 font-mono uppercase tracking-wider text-xs flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" /> SPATIAL KINEMATICS
            </span>
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between items-center py-1 border-b border-white/5">
              <span className="text-slate-400">Right Glove Wrist:</span>
              <span className="text-blue-400 font-semibold">+142.4, -28.1, +310.8</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-white/5">
              <span className="text-slate-400">Index Tip Vector:</span>
              <span className="text-emerald-400 font-semibold">+148.9, -24.3, +298.2</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-white/5">
              <span className="text-slate-400">Yellow Box Center:</span>
              <span className="text-amber-400 font-semibold">+150.1, -25.0, +295.0</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Grasp Vector Delta:</span>
              <span className="text-emerald-400 font-semibold">0.8 mm (ACTIVE GRASP)</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
