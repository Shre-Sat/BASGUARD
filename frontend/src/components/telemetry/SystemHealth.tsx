import { useExperimentStore } from '../../store/useExperimentStore';

export const SystemHealth = () => {
  const { health } = useExperimentStore();

  const metrics = [
    { label: 'GPU', value: `${health.gpu}%`, warn: health.gpu > 85 },
    { label: 'CPU', value: `${health.cpu}%`, warn: health.cpu > 85 },
    { label: 'Memory', value: `${health.ram.toFixed(1)} / 8 GB`, warn: health.ram > 7 },
    { label: 'Inference', value: `${health.inferenceLatency} ms`, warn: health.inferenceLatency > 100 },
    { label: 'FPS', value: health.fps.toFixed(1), warn: health.fps < 20 },
    { label: 'Power', value: `${health.power.toFixed(1)} W`, warn: false },
    { label: 'Storage', value: `${health.storage} GB`, warn: false },
    { label: 'Stream', value: health.streamStatus === 'CONNECTED' ? 'Connected' : 'Offline', warn: health.streamStatus !== 'CONNECTED' },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Section label */}
      <div className="px-4 py-2 border-b border-border">
        <span className="text-label font-medium text-text-secondary">System Health</span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3">
        <div className="grid grid-cols-2 gap-x-6 gap-y-3">
          {metrics.map((m) => (
            <div key={m.label} className="flex items-baseline justify-between gap-2">
              <span className="text-meta text-text-muted">{m.label}</span>
              <span className={`text-label font-mono ${m.warn ? 'text-semantic-warning' : 'text-text-primary'}`}>
                {m.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
