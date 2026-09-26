import React from 'react';
import { useExperimentStore } from '../store/useExperimentStore';
import { SystemHealth } from '../components/telemetry/SystemHealth';
import { Cpu, Zap, Server, Activity, Thermometer, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const System: React.FC = () => {
  const { health } = useExperimentStore();

  const pipelineStages = [
    { name: 'CAM-01 WebRTC Capture', latency: '4.2 ms', share: '10%' },
    { name: 'YOLOv8 Pose & Object Detector', latency: '18.6 ms', share: '44%' },
    { name: 'Hand-Object Contact Graph Engine', latency: '8.1 ms', share: '19%' },
    { name: 'FSM Rule Matrix Validator', latency: '2.4 ms', share: '6%' },
    { name: '3D Point Cloud Projection (R3F)', latency: '5.2 ms', share: '12%' },
    { name: 'Telemetry Broadcast & Log Streamer', latency: '3.5 ms', share: '9%' },
  ];

  const devices = [
    { name: 'ISRO AGX Payload Accelerator (NVIDIA Orin 64GB)', type: 'GPU Node', status: 'NOMINAL', temp: '54°C', load: `${health.gpu}%` },
    { name: 'Host ARM Cortex-A78AE (12 Cores)', type: 'CPU Node', status: 'NOMINAL', temp: '48°C', load: `${health.cpu}%` },
    { name: 'CAM-01 RGB-D High-Speed Optical Payload', type: 'Sensor', status: health.streamStatus === 'CONNECTED' ? 'NOMINAL' : 'FAULT', temp: '36°C', load: `${health.fps.toFixed(1)} FPS` },
    { name: 'CAM-02 Orbital Overview Camera', type: 'Sensor', status: 'NOMINAL', temp: '34°C', load: '30.0 FPS' },
    { name: 'Telemetry Serial Bus (MIL-STD-1553 Interface)', type: 'Comms', status: 'NOMINAL', temp: '38°C', load: '98.4 KB/s' },
  ];

  return (
    <div className="flex h-full w-full overflow-hidden bg-bg-dark">
      {/* Left Sidebar: Standard System Health Summary */}
      <div className="w-[360px] border-r border-border shrink-0 flex flex-col h-full bg-bg-panel/40">
        <SystemHealth />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto p-6 gap-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div>
            <h1 className="text-base font-semibold text-text-primary tracking-tight">System Telemetry & Resource Diagnostics</h1>
            <p className="text-meta text-text-tertiary mt-0.5">
              Deep AI inference profiler, hardware resource allocation, and sensor bus status
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-meta font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> HARDWARE OK
            </span>
          </div>
        </div>

        {/* Top Cards: Hardware Resources */}
        <div className="grid grid-cols-4 gap-4">
          <div className="p-4 rounded border border-border bg-bg-panel flex flex-col justify-between">
            <div className="flex items-center justify-between text-text-tertiary">
              <span className="text-meta font-semibold uppercase">CUDA Tensor Cores</span>
              <Cpu className="w-4 h-4 text-accent" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-text-primary">{health.gpu}%</span>
              <div className="w-full h-1.5 bg-bg-dark rounded-full mt-2 overflow-hidden border border-border/40">
                <div className="h-full bg-accent transition-all duration-300" style={{ width: `${health.gpu}%` }} />
              </div>
            </div>
            <span className="text-[11px] text-text-tertiary mt-2">NVIDIA Orin AGX 64GB</span>
          </div>

          <div className="p-4 rounded border border-border bg-bg-panel flex flex-col justify-between">
            <div className="flex items-center justify-between text-text-tertiary">
              <span className="text-meta font-semibold uppercase">Inference Latency</span>
              <Activity className="w-4 h-4 text-accent" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-text-primary">{health.inferenceLatency} ms</span>
              <div className="w-full h-1.5 bg-bg-dark rounded-full mt-2 overflow-hidden border border-border/40">
                <div
                  className={`h-full transition-all duration-300 ${health.inferenceLatency > 60 ? 'bg-rose-500' : 'bg-emerald-400'}`}
                  style={{ width: `${Math.min(100, (health.inferenceLatency / 100) * 100)}%` }}
                />
              </div>
            </div>
            <span className="text-[11px] text-text-tertiary mt-2">Target &lt; 50ms (30 FPS Target)</span>
          </div>

          <div className="p-4 rounded border border-border bg-bg-panel flex flex-col justify-between">
            <div className="flex items-center justify-between text-text-tertiary">
              <span className="text-meta font-semibold uppercase">Unified VRAM</span>
              <Server className="w-4 h-4 text-accent" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-text-primary">{health.ram.toFixed(1)} GB</span>
              <div className="w-full h-1.5 bg-bg-dark rounded-full mt-2 overflow-hidden border border-border/40">
                <div className="h-full bg-accent transition-all duration-300" style={{ width: `${(health.ram / 64) * 100}%` }} />
              </div>
            </div>
            <span className="text-[11px] text-text-tertiary mt-2">64.0 GB Total Memory</span>
          </div>

          <div className="p-4 rounded border border-border bg-bg-panel flex flex-col justify-between">
            <div className="flex items-center justify-between text-text-tertiary">
              <span className="text-meta font-semibold uppercase">Payload Power</span>
              <Zap className="w-4 h-4 text-accent" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-mono font-bold text-text-primary">{health.power.toFixed(1)} W</span>
              <div className="w-full h-1.5 bg-bg-dark rounded-full mt-2 overflow-hidden border border-border/40">
                <div className="h-full bg-accent transition-all duration-300" style={{ width: `${(health.power / 60) * 100}%` }} />
              </div>
            </div>
            <span className="text-[11px] text-text-tertiary mt-2">Limit: 60.0 Watts MAX</span>
          </div>
        </div>

        {/* Pipeline Execution Profiler */}
        <div className="border border-border rounded bg-bg-panel p-5 flex flex-col gap-4">
          <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider pb-3 border-b border-border/60">
            Pipeline Execution Profile & Latency Budget
          </h2>

          <div className="space-y-3">
            {pipelineStages.map((stage) => (
              <div key={stage.name} className="flex items-center justify-between text-xs py-1 border-b border-border/30">
                <span className="text-text-secondary w-1/3">{stage.name}</span>
                <div className="flex-1 mx-4 h-2 bg-bg-dark rounded overflow-hidden border border-border/30">
                  <div className="h-full bg-accent/70" style={{ width: stage.share }} />
                </div>
                <div className="font-mono text-right w-24">
                  <span className="text-text-primary">{stage.latency}</span>
                  <span className="text-text-tertiary ml-2 text-[10px]">({stage.share})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Device Matrix & Hardware Bus Tree */}
        <div className="border border-border rounded bg-bg-panel p-5 flex flex-col gap-4">
          <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider pb-3 border-b border-border/60">
            Hardware Sensor Bus & Subsystem Tree
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-border text-text-tertiary font-mono">
                  <th className="pb-2 font-normal">SUBSYSTEM DEVICE</th>
                  <th className="pb-2 font-normal">NODE TYPE</th>
                  <th className="pb-2 font-normal">STATUS</th>
                  <th className="pb-2 font-normal">THERMAL</th>
                  <th className="pb-2 font-normal">OPERATIONAL LOAD</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {devices.map((dev) => (
                  <tr key={dev.name} className="hover:bg-bg-dark/40">
                    <td className="py-2.5 text-text-primary font-sans font-medium">{dev.name}</td>
                    <td className="py-2.5 text-text-tertiary">{dev.type}</td>
                    <td className="py-2.5">
                      {dev.status === 'NOMINAL' ? (
                        <span className="text-emerald-400 text-[11px] flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> NOMINAL
                        </span>
                      ) : (
                        <span className="text-rose-400 text-[11px] flex items-center gap-1">
                          <ShieldAlert className="w-3.5 h-3.5" /> FAULT
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 text-text-secondary flex items-center gap-1">
                      <Thermometer className="w-3.5 h-3.5 text-text-tertiary" /> {dev.temp}
                    </td>
                    <td className="py-2.5 text-text-secondary">{dev.load}</td>
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
