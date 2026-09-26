import { useExperimentStore } from '../store/useExperimentStore';

export const Settings = () => {
  const {
    demoMode, setDemoMode,
    triggerNormalSequence, triggerOutOfSequence, triggerLowConfidence,
    simulateCameraLoss, completeExperiment, resetExperiment,
  } = useExperimentStore();

  const demoActions = [
    { label: 'Normal Sequence', desc: 'Advance to next step', fn: triggerNormalSequence },
    { label: 'Out-of-Sequence', desc: 'Trigger sequence violation', fn: triggerOutOfSequence },
    { label: 'Low Confidence', desc: 'Simulate uncertain detection', fn: triggerLowConfidence },
    { label: 'Camera Failure', desc: 'Disconnect primary camera', fn: simulateCameraLoss },
    { label: 'Complete Experiment', desc: 'Mark all steps complete', fn: completeExperiment },
    { label: 'Reset', desc: 'Reset to initial state', fn: resetExperiment },
  ];

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="max-w-2xl w-full mx-auto px-6 py-6 flex flex-col gap-8">

        {/* Demo mode toggle */}
        <div>
          <h2 className="text-sm font-semibold text-text-primary mb-1">Operator Tools</h2>
          <p className="text-meta text-text-tertiary mb-4">
            Enable demo mode to simulate experiment events for evaluation and testing.
          </p>

          <div className="flex items-center justify-between py-3 border-t border-border">
            <div>
              <span className="text-sm text-text-primary">Demo Mode</span>
              <p className="text-meta text-text-muted mt-0.5">Enables simulation controls below.</p>
            </div>
            <button
              onClick={() => setDemoMode(!demoMode)}
              className={`w-10 h-5 rounded-full flex items-center transition-colors p-0.5 ${demoMode ? 'bg-accent' : 'bg-border-light'}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full transition-transform ${demoMode ? 'translate-x-5' : 'translate-x-0'}`} />
            </button>
          </div>
        </div>

        {/* Demo actions */}
        {demoMode && (
          <div>
            <h3 className="text-sm font-semibold text-text-primary mb-3">Simulation Actions</h3>
            <div className="flex flex-col gap-0 border-t border-border">
              {demoActions.map((action) => (
                <div key={action.label} className="flex items-center justify-between py-3 border-b border-border/50">
                  <div>
                    <span className="text-sm text-text-primary">{action.label}</span>
                    <p className="text-meta text-text-muted mt-0.5">{action.desc}</p>
                  </div>
                  <button
                    onClick={action.fn}
                    className="text-meta font-medium text-accent hover:text-accent-muted transition-colors px-3 py-1.5 rounded hover:bg-accent-dim"
                  >
                    Run
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
