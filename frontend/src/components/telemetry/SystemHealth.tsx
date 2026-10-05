import { useExperimentStore } from '../../store/useExperimentStore';
import { Cpu, Activity, HardDrive, Zap, Gauge } from 'lucide-react';
import { motion } from 'framer-motion';

export const SystemHealth = () => {
  const { health } = useExperimentStore();

  const metrics = [
    { label: 'GPU (YOLOv8x)', val: health.gpu, max: 100, unit: '%', icon: Activity, color: 'text-emerald-400', bar: 'bg-emerald-400' },
    { label: 'CPU (MediaPipe)', val: health.cpu, max: 100, unit: '%', icon: Cpu, color: 'text-blue-400', bar: 'bg-blue-400' },
    { label: 'VRAM Usage', val: health.ram, max: 8, unit: 'GB', icon: HardDrive, color: 'text-amber-400', bar: 'bg-amber-400' },
    { label: 'Power Draw', val: health.power, max: 100, unit: 'W', icon: Zap, color: 'text-indigo-400', bar: 'bg-indigo-400' },
  ];

  return (
    <div className="flex flex-col h-full bg-[#05080F] border border-white/5 select-none overflow-hidden">
      {/* Header bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-[#090D18]/90 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold font-mono text-slate-200">SYSTEM TELEMETRY HEALTH</span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          NOMINAL 30FPS
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 grid grid-cols-2 gap-2.5">
        {metrics.map((m) => {
          const Icon = m.icon;
          const percent = Math.min(100, Math.round((m.val / m.max) * 100));

          return (
            <div key={m.label} className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5 flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-mono">
                  <Icon className={`w-3.5 h-3.5 ${m.color}`} />
                  <span className="truncate">{m.label}</span>
                </div>
                <span className={`text-xs font-mono font-bold ${m.color}`}>
                  {m.val.toFixed(1)}{m.unit}
                </span>
              </div>

              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full rounded-full ${m.bar}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${percent}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
