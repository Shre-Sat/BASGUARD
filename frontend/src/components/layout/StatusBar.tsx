import { useExperimentStore } from '../../store/useExperimentStore';

export const StatusBar = () => {
  const { health } = useExperimentStore();

  const items = [
    { label: 'Cameras', value: '2 / 2 Online', ok: health.streamStatus === 'CONNECTED' },
    { label: 'Model', value: 'Running', ok: true },
    { label: 'Calibration', value: 'Valid', ok: true },
    { label: 'Stream', value: health.streamStatus === 'CONNECTED' ? 'Connected' : 'Disconnected', ok: health.streamStatus === 'CONNECTED' },
    { label: 'Recording', value: 'Active', ok: true },
    { label: 'FPS', value: health.fps.toFixed(1), ok: health.fps > 20 },
    { label: 'Latency', value: `${health.inferenceLatency} ms`, ok: health.inferenceLatency < 200 },
  ];

  return (
    <div className="h-7 flex items-center px-5 gap-6 bg-base border-b border-border text-meta shrink-0">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <span className="text-text-muted">{item.label}</span>
          <div className="flex items-center gap-1">
            <div className={`w-1 h-1 rounded-full ${item.ok ? 'bg-semantic-success' : 'bg-semantic-critical'}`} />
            <span className={`font-mono ${item.ok ? 'text-text-secondary' : 'text-semantic-critical'}`}>
              {item.value}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
