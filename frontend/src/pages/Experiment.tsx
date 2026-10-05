import { useState } from 'react';
import { useExperimentStore } from '../store/useExperimentStore';
import { ExperimentStatus } from '../components/experiment/ExperimentStatus';
import { 
  CheckCircle2, 
  Circle, 
  AlertTriangle, 
  ShieldCheck, 
  Clock, 
  Eye, 
  Layers,
  GitCommit
} from 'lucide-react';
import { motion } from 'framer-motion';

export const Experiment = () => {
  const { protocol, experiment } = useExperimentStore();
  const [selectedStepId, setSelectedStepId] = useState<string>(experiment.currentStepId);

  const selectedStep = protocol.find((p) => p.id === selectedStepId) || protocol[0];

  const stepDetails: Record<string, { duration: string; objects: string[]; criteria: string; safety: string }> = {
    IDLE: {
      duration: '0s (Standby)',
      objects: ['Payload Camera FOV', 'Space Station Rack Frame'],
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
    <div className="flex h-full w-full overflow-hidden bg-[#04070D] font-sans select-none">
      <div className="w-[380px] border-r border-white/10 shrink-0 flex flex-col h-full bg-[#050810]">
        <ExperimentStatus />
      </div>

      <div className="flex-1 flex flex-col h-full overflow-y-auto p-6 gap-6">
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Layers className="w-5 h-5 text-blue-400" />
              PETRI-NET FINITE STATE MACHINE REASONER
            </h1>
            <p className="text-xs font-mono text-slate-400 mt-1">
              ISRO Biological Activity Space Protocol · Sequential Vector Verification Engine
            </p>
          </div>

          <div className="flex items-center gap-3 font-mono text-xs">
            <span className="px-3 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold shadow-glow-accent">
              MODEL: PETRI-FSM v2.4.1
            </span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-white/10 flex flex-col gap-4 shadow-2xl">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <GitCommit className="w-4 h-4 text-emerald-400" /> TRANSITION PIPELINE DIAGRAM
            </h2>
            <span className="text-[11px] font-mono text-slate-400">Click any state node to inspect parameters</span>
          </div>

          <div className="grid grid-cols-4 gap-4 relative">
            {protocol.map((step, idx) => {
              const isCompleted = experiment.completedStepIds.includes(step.id);
              const isActive = experiment.currentStepId === step.id;
              const isSelected = selectedStepId === step.id;
              const isNext = experiment.nextStepId === step.id;

              return (
                <motion.div
                  key={step.id}
                  onClick={() => setSelectedStepId(step.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`relative p-4 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-blue-400 bg-blue-500/15 shadow-glow-accent'
                      : isActive
                      ? 'border-amber-400 bg-amber-500/15 shadow-glow-isro'
                      : isCompleted
                      ? 'border-emerald-500/30 bg-emerald-500/5'
                      : isNext
                      ? 'border-blue-500/30 bg-slate-900/60'
                      : 'border-white/5 bg-slate-900/30 opacity-60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono text-slate-400 font-bold">STATE P-0{idx + 1}</span>
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : isActive ? (
                      <span className="w-3 h-3 rounded-full bg-amber-400 animate-ping" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-600" />
                    )}
                  </div>

                  <h3 className="text-xs font-bold text-white mb-1 truncate">{step.name}</h3>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">{step.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="glass-panel p-5 rounded-xl border border-white/10 flex flex-col gap-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Eye className="w-4 h-4 text-blue-400" /> STATE INSPECTOR: {selectedStep.name}
              </h3>
              <span className="text-xs font-mono text-blue-400 font-bold">{selectedStep.id}</span>
            </div>

            <div className="flex flex-col gap-3 font-mono text-xs">
              <div className="flex justify-between py-1.5 border-b border-white/5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-400" /> Nominal Step Duration:
                </span>
                <span className="text-slate-100 font-semibold">{details.duration}</span>
              </div>

              <div className="flex flex-col gap-1 py-1.5 border-b border-white/5">
                <span className="text-slate-400">Target Perception Objects:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {details.objects.map((obj) => (
                    <span key={obj} className="px-2 py-0.5 rounded bg-slate-900 border border-white/10 text-[10px] text-blue-300">
                      {obj}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1 py-1.5 border-b border-white/5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> AI Perception Criteria:
                </span>
                <p className="text-slate-200 font-sans text-xs leading-relaxed mt-0.5">{details.criteria}</p>
              </div>

              <div className="flex flex-col gap-1 py-1.5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Safety & Containment Guard:
                </span>
                <p className="text-slate-200 font-sans text-xs leading-relaxed mt-0.5">{details.safety}</p>
              </div>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-xl border border-white/10 flex flex-col gap-4 shadow-xl">
            <h3 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider pb-3 border-b border-white/10">
              PETRI-NET TRANSITION RULES & GUARDS
            </h3>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-blue-400 font-bold text-[11px]">GUARD 01 // DETERMINISTIC SEQUENCING</span>
                <p className="text-slate-300 font-sans text-xs mt-1 leading-relaxed">
                  Tokens cannot jump out-of-order states. Any skipped transition generates immediate <span className="text-rose-400 font-mono">OUT_OF_SEQUENCE</span> neural voice alert.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-blue-400 font-bold text-[11px]">GUARD 02 // GRASP VECTOR CONFIRMATION</span>
                <p className="text-slate-300 font-sans text-xs mt-1 leading-relaxed">
                  Manipulation step transition requires 12 continuous frames of MediaPipe hand-box vector contact.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-blue-400 font-bold text-[11px]">GUARD 03 // ANOMALY DURATION TIMEOUT</span>
                <p className="text-slate-300 font-sans text-xs mt-1 leading-relaxed">
                  If step duration exceeds 1.5x nominal limit, Piper TTS triggers prompt warning to astronaut.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
