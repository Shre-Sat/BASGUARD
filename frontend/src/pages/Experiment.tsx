import { useState } from 'react';
import { useExperimentStore } from '../store/useExperimentStore';
import { ExperimentStatus } from '../components/experiment/ExperimentStatus';
import { CheckCircle2, Circle, AlertTriangle, ArrowRight, ShieldCheck, Clock, Eye, Layers } from 'lucide-react';

export const Experiment = () => {
  const { protocol, experiment, updateExperiment } = useExperimentStore();
  const [selectedStepId, setSelectedStepId] = useState<string>(experiment.currentStepId);

  const selectedStep = protocol.find((p) => p.id === selectedStepId) || protocol[0];

  const stepDetails: Record<string, { duration: string; objects: string[]; criteria: string; safety: string }> = {
    IDLE: {
      duration: '0s (Standby)',
      objects: ['Baseline Camera Field'],
      criteria: 'Awaiting astronaut initiation signal.',
      safety: 'Payload doors closed and latched.'
    },
    DETECT_OUTER: {
      duration: '3.2s',
      objects: ['Outer Biological Containment Box'],
      criteria: 'YOLOv8 bounding box confidence > 0.85 on outer container.',
      safety: 'No obstruction in payload camera line of sight.'
    },
    OPEN_OUTER: {
      duration: '8.4s',
      objects: ['Outer Container Lid', 'Astronaut Hand/Glove'],
      criteria: 'Hand-object overlap vector detected, lid angle > 45 deg.',
      safety: 'Glove clearance within safety zone B.'
    },
    IDENTIFY_RED: {
      duration: '4.1s',
      objects: ['Red Sample Box (Bio Specimen A)'],
      criteria: 'Color histogram + 3D spatial bound alignment.',
      safety: 'Specimen temp maintained at 4°C.'
    },
    IDENTIFY_YELLOW: {
      duration: '3.8s',
      objects: ['Yellow Sample Box (Bio Specimen B)'],
      criteria: 'Color histogram + 3D spatial bound alignment.',
      safety: 'Specimen temp maintained at 4°C.'
    },
    PICK_YELLOW: {
      duration: '6.5s',
      objects: ['Yellow Sample Box', 'Astronaut Glove Right'],
      criteria: 'Grasp pose detection, lift displacement vector > 5cm.',
      safety: 'Controlled velocity < 0.15 m/s to protect microgravity sample.'
    },
    PLACE_YELLOW: {
      duration: '7.2s',
      objects: ['Yellow Sample Box', 'Analysis Workbench Dock'],
      criteria: 'Contact sensor pulse + zero relative velocity.',
      safety: 'Docking mechanism confirmed locked.'
    },
    COMPLETE: {
      duration: 'Finalized',
      objects: ['All Biological Containers'],
      criteria: 'All protocol sequence steps validated by AI FSM.',
      safety: 'Payload sealed, post-run telemetry archived.'
    }
  };

  const details = stepDetails[selectedStep.id] || stepDetails['IDLE'];

  return (
    <div className="flex h-full w-full overflow-hidden bg-bg-dark">
      {/* Left Sidebar: Standard Step List */}
      <div className="w-[360px] border-r border-border shrink-0 flex flex-col h-full bg-bg-panel/40">
        <ExperimentStatus />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto p-6 gap-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div>
            <h1 className="text-base font-semibold text-text-primary tracking-tight">FSM Protocol State Machine</h1>
            <p className="text-meta text-text-tertiary mt-0.5">
              Finite State Machine sequence verification graph for ISRO BAS Biological Payload Experiment
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-meta px-2.5 py-1 rounded bg-accent-dim text-accent border border-accent/20 font-mono">
              FSM v2.4.1 [ACTIVE]
            </span>
          </div>
        </div>

        {/* FSM Visual Graph Diagram */}
        <div className="border border-border rounded bg-bg-panel p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-text-secondary uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-accent" /> Sequential Transition Pipeline
            </h2>
            <span className="text-meta text-text-tertiary">Click node to inspect criteria</span>
          </div>

          <div className="grid grid-cols-4 gap-4 relative">
            {protocol.map((step, idx) => {
              const isCompleted = experiment.completedStepIds.includes(step.id);
              const isActive = experiment.currentStepId === step.id;
              const isSelected = selectedStepId === step.id;
              const isNext = experiment.nextStepId === step.id;

              return (
                <div
                  key={step.id}
                  onClick={() => setSelectedStepId(step.id)}
                  className={`relative p-4 rounded border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-accent bg-accent/10'
                      : isActive
                      ? 'border-accent/60 bg-accent/5'
                      : isCompleted
                      ? 'border-border-light bg-bg-dark/80 hover:border-text-tertiary'
                      : isNext
                      ? 'border-yellow-500/40 bg-yellow-500/5'
                      : 'border-border/50 bg-bg-dark/40 opacity-70 hover:opacity-100'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-meta font-mono text-text-tertiary">STEP 0{idx}</span>
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : isActive ? (
                      <span className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse" />
                    ) : isNext ? (
                      <span className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
                    ) : (
                      <Circle className="w-4 h-4 text-text-tertiary/40" />
                    )}
                  </div>
                  <h3 className="text-xs font-medium text-text-primary mb-1 truncate">{step.name}</h3>
                  <p className="text-[11px] text-text-tertiary line-clamp-2 leading-relaxed">{step.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Node Inspection Panel & Verification Matrix */}
        <div className="grid grid-cols-2 gap-6">
          {/* Node Details */}
          <div className="border border-border rounded bg-bg-panel p-5 flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-border/60">
              <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider flex items-center gap-2">
                <Eye className="w-4 h-4 text-accent" /> Step Inspector: {selectedStep.name}
              </h3>
              <span className="text-meta font-mono text-accent">{selectedStep.id}</span>
            </div>

            <div className="flex flex-col gap-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-border/40">
                <span className="text-text-tertiary flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" /> Target Duration
                </span>
                <span className="font-mono text-text-primary">{details.duration}</span>
              </div>

              <div className="flex flex-col gap-1 py-1.5 border-b border-border/40">
                <span className="text-text-tertiary">Target Perception Objects</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {details.objects.map((obj) => (
                    <span key={obj} className="px-2 py-0.5 rounded bg-bg-dark border border-border text-[11px] font-mono text-text-secondary">
                      {obj}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1 py-1.5 border-b border-border/40">
                <span className="text-text-tertiary flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> AI Detection Criteria
                </span>
                <p className="text-text-secondary leading-relaxed mt-0.5">{details.criteria}</p>
              </div>

              <div className="flex flex-col gap-1 py-1.5">
                <span className="text-text-tertiary flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" /> Safety & Containment Constraint
                </span>
                <p className="text-text-secondary leading-relaxed mt-0.5">{details.safety}</p>
              </div>
            </div>

            {experiment.currentStepId !== selectedStep.id && (
              <button
                onClick={() => updateExperiment({ currentStepId: selectedStep.id })}
                className="mt-2 text-xs font-mono py-2 px-3 rounded bg-accent/20 text-accent border border-accent/40 hover:bg-accent/30 transition-colors flex items-center justify-center gap-2"
              >
                Set Active State to {selectedStep.id} <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Compliance & Transition Log Matrix */}
          <div className="border border-border rounded bg-bg-panel p-5 flex flex-col gap-4">
            <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider pb-3 border-b border-border/60">
              State Machine Rules & Vector Guards
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded bg-bg-dark border border-border/60">
                <span className="font-mono text-accent text-[11px]">RULE 01 // STRICT SEQUENCING</span>
                <p className="text-text-tertiary mt-1 leading-relaxed">
                  Skipping steps triggers immediate <span className="text-rose-400 font-mono">OUT_OF_SEQUENCE</span> alert to ground control.
                </p>
              </div>

              <div className="p-3 rounded bg-bg-dark border border-border/60">
                <span className="font-mono text-accent text-[11px]">RULE 02 // HAND-OBJECT CONTACT GRAPH</span>
                <p className="text-text-tertiary mt-1 leading-relaxed">
                  Manipulation state change requires minimum 12 continuous frames of contact vector validation before advancing step.
                </p>
              </div>

              <div className="p-3 rounded bg-bg-dark border border-border/60">
                <span className="font-mono text-accent text-[11px]">RULE 03 // LOW CONFIDENCE TIMEOUT</span>
                <p className="text-text-tertiary mt-1 leading-relaxed">
                  If confidence drops below 60% for &gt;5 seconds, astronaut voice prompt is dispatched automatically.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
