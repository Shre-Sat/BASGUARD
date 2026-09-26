import { useExperimentStore } from '../../store/useExperimentStore';

export const ExperimentStatus = () => {
  const { experiment, protocol } = useExperimentStore();
  const currentIndex = protocol.findIndex((s) => s.id === experiment.currentStepId);
  const currentStep = protocol[currentIndex];
  const nextStep = protocol[currentIndex + 1];

  const statusColor =
    experiment.status === 'ERROR'
      ? 'text-semantic-critical'
      : experiment.status === 'COMPLETED'
        ? 'text-semantic-success'
        : 'text-accent';

  return (
    <div className="flex flex-col h-full">
      {/* Section label */}
      <div className="px-4 py-2 border-b border-border">
        <span className="text-label font-medium text-text-secondary">Experiment State</span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-5">
        {/* Current state — dominant */}
        <div className="flex flex-col gap-1">
          <span className="text-meta text-text-muted uppercase tracking-wider">Current</span>
          <div className="flex items-baseline gap-3">
            <span className="text-2xl font-semibold text-text-primary">
              Step {String(currentIndex + 1).padStart(2, '0')}
            </span>
            <span className={`text-meta font-medium uppercase tracking-wider ${statusColor}`}>
              {experiment.status === 'ERROR' ? 'Violation' : experiment.status.replace('_', ' ')}
            </span>
          </div>
          <span className="text-sm text-text-secondary mt-0.5">
            {currentStep?.name || 'Unknown'}
          </span>
          <div className="flex items-baseline gap-1.5 mt-1">
            <span className="text-telemetry font-mono text-text-primary">
              {experiment.confidence.toFixed(1)}%
            </span>
            <span className="text-meta text-text-muted">confidence</span>
          </div>
        </div>

        {/* Next expected */}
        {nextStep && (
          <div className="flex flex-col gap-1">
            <span className="text-meta text-text-muted uppercase tracking-wider">Next expected</span>
            <span className="text-sm text-text-tertiary">{nextStep.name}</span>
          </div>
        )}

        {/* Divider */}
        <div className="divider-h" />

        {/* Sequence timeline — horizontal */}
        <div className="flex flex-col gap-3">
          <span className="text-meta text-text-muted uppercase tracking-wider">Sequence</span>
          <div className="flex items-start gap-0">
            {protocol.map((step, idx) => {
              const isCompleted = experiment.completedStepIds.includes(step.id);
              const isCurrent = step.id === experiment.currentStepId;
              const isError = isCurrent && experiment.status === 'ERROR';

              return (
                <div key={step.id} className="flex-1 flex flex-col items-center gap-1.5 min-w-0">
                  {/* Indicator */}
                  <div className="flex items-center w-full">
                    {/* Connecting line — left half */}
                    {idx > 0 && (
                      <div className={`flex-1 h-px ${isCompleted || isCurrent ? 'bg-border-light' : 'bg-border'}`} />
                    )}
                    {idx === 0 && <div className="flex-1" />}

                    {/* Node */}
                    <div
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-meta font-mono shrink-0
                        ${isCompleted
                          ? 'bg-semantic-success/20 text-semantic-success'
                          : isError
                            ? 'bg-semantic-critical/20 text-semantic-critical'
                            : isCurrent
                              ? 'bg-accent-dim text-accent border border-accent/40'
                              : 'bg-panel text-text-muted border border-border'
                        }`}
                    >
                      {isCompleted ? '✓' : String(idx + 1).padStart(2, '0')}
                    </div>

                    {/* Connecting line — right half */}
                    {idx < protocol.length - 1 && (
                      <div className={`flex-1 h-px ${isCompleted ? 'bg-border-light' : 'bg-border'}`} />
                    )}
                    {idx === protocol.length - 1 && <div className="flex-1" />}
                  </div>

                  {/* Label */}
                  <span className={`text-meta text-center leading-tight px-0.5 truncate w-full
                    ${isCurrent ? 'text-text-primary font-medium' : 'text-text-muted'}`}
                  >
                    {step.name.split(' ').slice(0, 2).join(' ')}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
