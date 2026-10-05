import React from 'react';
import { useExperimentStore } from '../store/useExperimentStore';
import { SystemHealth } from '../components/telemetry/SystemHealth';
import { Cpu, Zap, Activity, Thermometer, CheckCircle2, Gauge, HardDrive } from 'lucide-react';
import { motion } from 'framer-motion';

export const System: React.FC = () => {
  const { health } = useExperimentStore();

  const pipelineStages = [
    { name: 'CAM-01 WebRTC / GStreamer Capture', latency: '4.2 ms', share: '10%' },
    { name: 'YOLOv8 Pose & Object Bounding Box Engine', latency: '18.6 ms', share: '44%' },
    { name: 'MediaPipe 3D Hand Vector Graph', latency: '8.1 ms', share: '19%' },
    { name: 'Petri-Net State Machine Validator', latency: '2.4 ms', share: '6%' },
    { name: '3D Spatial Viewport Projection', latency: '5.2 ms', share: '12%' },
    { name: 'WebSocket & JSONL Telemetry Streamer', latency: '3.5 ms', share: '9%' },
  ];

  const devices = [
    { name: 'ISRO AGX Payload Accelerator (NVIDIA Orin 64GB)', type: 'GPU Node', status: 'NOMINAL', temp: '54°C', load: `${health.gpu}%` },
    { name: 'Host ARM Cortex-A78AE (12 Cores)', type: 'CPU Node', status: 'NOMINAL', temp: '48°C', load: `${health.cpu}%` },
    { name: 'CAM-01 RGB-D High-Speed Optical Sensor', type: 'Sensor', status: health.streamStatus === 'CONNECTED' ? 'NOMINAL' : 'FAULT', temp: '36°C', load: `${health.fps.toFixed(1)} FPS` },
    { name: 'CAM-02 Orbital Overview Camera', type: 'Sensor', status: 'NOMINAL', temp: '34°C', load: '30.0 FPS' },
    { name: 'Telemetry Serial Bus (MIL-STD-1553 Interface)', type: 'Comms', status: 'NOMINAL', temp: '38°C', load: '98.4 KB/s' },
  ];

  return (
    <div className="flex h-full w-full overflow-hidden bg-[#04070D] font-sans select-none">
      <div className="w-[380px] border-r border-white/10 shrink-0 flex flex-col h-full bg-[#050810]">
        <SystemHealth />
      </div>

      <div className="flex-1 flex flex-col h-full overflow-y-auto p-6 gap-6">
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Gauge className="w-5 h-5 text-blue-400" /> SYSTEM DIAGNOSTICS & TELEMETRY PROFILER
            </h1>
            <p className="text-xs font-mono text-slate-400 mt-1">
              Deep GPU inference profiling, pipeline latency budgets, and hardware subsystem health
            </p>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded border border-emerald-500/20 flex items-center gap-1.5 shadow-glow-success">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" /> ALL HARDWARE NOMINAL
          </span>
        </div>

        <div className="grid grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl border border-white/10 flex flex-col justify-between shadow-xl">
            <div className="flex items-center justify-between text-slate-400 font-mono text-xs">
              <span className="uppercase font-bold">CUDA Tensor Cores</span>
              <Cpu className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-white">{health.gpu}%</span>
              <div className="w-full h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden">
                <motion.div className="h-full bg-emerald-400" animate={{ width: `${health.gpu}%` }} />
              </div>
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-2">NVIDIA Orin AGX 64GB</span>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-white/10 flex flex-col justify-between shadow-xl">
            <div className="flex items-center justify-between text-slate-400 font-mono text-xs">
              <span className="uppercase font-bold">Inference Latency</span>
              <Activity className="w-4 h-4 text-blue-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-white">{health.inferenceLatency} ms</span>
              <div className="w-full h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden">
                <motion.div className="h-full bg-blue-400" animate={{ width: `${Math.min(100, (health.inferenceLatency / 100) * 100)}%` }} />
              </div>
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-2">Target &lt; 50ms (30 FPS Target)</span>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-white/10 flex flex-col justify-between shadow-xl">
            <div className="flex items-center justify-between text-slate-400 font-mono text-xs">
              <span className="uppercase font-bold">Unified VRAM</span>
              <HardDrive className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-white">{health.ram.toFixed(1)} GB</span>
              <div className="w-full h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden">
                <motion.div className="h-full bg-amber-400" animate={{ width: `${(health.ram / 64) * 100}%` }} />
              </div>
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-2">64.0 GB Memory Pool</span>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-white/10 flex flex-col justify-between shadow-xl">
            <div className="flex items-center justify-between text-slate-400 font-mono text-xs">
              <span className="uppercase font-bold">Payload Power</span>
              <Zap className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-white">{health.power.toFixed(1)} W</span>
              <div className="w-full h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden">
                <motion.div className="h-full bg-indigo-400" animate={{ width: `${(health.power / 60) * 100}%` }} />
              </div>
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-2">Limit: 60.0 Watts MAX</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/10 flex flex-col gap-4 shadow-xl">
          <h2 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider pb-3 border-b border-white/10">
            PIPELINE EXECUTION PROFILE & LATENCY BUDGET
          </h2>

          <div className="space-y-3 font-mono text-xs">
            {pipelineStages.map((stage) => (
              <div key={stage.name} className="flex items-center justify-between py-1 border-b border-white/5">
                <span className="text-slate-300 w-1/3">{stage.name}</span>
                <div className="flex-1 mx-4 h-2 bg-slate-900 rounded overflow-hidden">
                  <div className="h-full bg-blue-500/80 rounded" style={{ width: stage.share }} />
                </div>
                <div className="text-right w-28">
                  <span className="text-slate-100 font-bold">{stage.latency}</span>
                  <span className="text-slate-500 ml-2 text-[10px]">({stage.share})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/10 flex flex-col gap-4 shadow-xl">
          <h2 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider pb-3 border-b border-white/10">
            HARDWARE SUBSYSTEM BUS & SENSOR MATRIX
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left font-mono">
              <thead>
                <tr className="border-b border-white/10 text-slate-400">
                  <th className="pb-2 font-semibold">DEVICE NAME</th>
                  <th className="pb-2 font-semibold">TYPE</th>
                  <th className="pb-2 font-semibold">STATUS</th>
                  <th className="pb-2 font-semibold">THERMAL</th>
                  <th className="pb-2 font-semibold">OPERATIONAL LOAD</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {devices.map((dev) => (
                  <tr key={dev.name} className="hover:bg-slate-900/40">
                    <td className="py-2.5 text-slate-200 font-sans font-medium">{dev.name}</td>
                    <td className="py-2.5 text-slate-400">{dev.type}</td>
                    <td className="py-2.5">
                      <span className="text-emerald-400 text-[11px] flex items-center gap-1 font-bold">
                        <CheckCircle2 className="w-3.5 h-3.5" /> NOMINAL
                      </span>
                    </td>
                    <td className="py-2.5 text-slate-300 flex items-center gap-1">
                      <Thermometer className="w-3.5 h-3.5 text-slate-500" /> {dev.temp}
                    </td>
                    <td className="py-2.5 text-slate-300 font-semibold">{dev.load}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
