import { useExperimentStore } from '../../store/useExperimentStore';
import { ArrowRight, Layers } from 'lucide-react';
import { motion } from 'framer-motion';

export const ExperimentStatus = () => {
  const { experiment, protocol, triggerNormalSequence } = useExperimentStore();
  
  const currentIndex = protocol.findIndex((s) => s.id === experiment.currentStepId);
  const currentStep = protocol[currentIndex] || protocol[0];

  const isCompleted = experiment.status === 'COMPLETED';
  const isError = experiment.status === 'ERROR';

  const progressPercent = Math.round(((currentIndex + (isCompleted ? 1 : 0)) / protocol.length) * 100);

  return (
    <div className="flex flex-col h-full bg-[#05080F] border border-white/5 select-none overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 bg-[#090D18]/90 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold font-mono text-slate-200">PETRI-NET STATE MACHINE</span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
          FSM SEQUENCE
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        <div className={`p-4 rounded-xl relative overflow-hidden transition-all ${
          isError 
            ? 'bg-rose-950/40 border border-rose-500/50 shadow-glow-critical' 
            : isCompleted
            ? 'bg-emerald-950/40 border border-emerald-500/50 shadow-glow-success'
            : 'bg-slate-900/80 border border-blue-500/30 shadow-glow-accent'
        }`}>
          <div className="flex items-start justify-between">
            <div className="flex flex-col">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                CURRENT ACTIVE STEP {String(currentIndex + 1).padStart(2, '0')} / {protocol.length}
              </span>
              <h2 className="text-lg font-bold font-sans text-white mt-0.5">
                {currentStep?.name || 'Idle'}
              </h2>
            </div>

            <div className={`px-2.5 py-1 rounded text-xs font-mono font-bold tracking-wider uppercase ${
              isError 
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                : isCompleted
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                : 'bg-blue-500/20 text-blue-400 border border-blue-500/40'
            }`}>
              {isError ? 'PROTOCOL VIOLATION' : experiment.status}
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Perception Confidence:</span>
            <span className={`font-semibold ${
              experiment.confidence > 80 ? 'text-emerald-400' : experiment.confidence > 50 ? 'text-amber-400' : 'text-rose-400'
            }`}>
              {experiment.confidence.toFixed(1)}%
            </span>
          </div>

          <div className="w-full h-1.5 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
            <motion.div 
              className={`h-full rounded-full ${
                experiment.confidence > 80 ? 'bg-emerald-400' : experiment.confidence > 50 ? 'bg-amber-400' : 'bg-rose-400'
              }`}
              initial={{ width: 0 }}
              animate={{ width: `${experiment.confidence}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>

          {!isCompleted && !isError && (
            <button
              onClick={triggerNormalSequence}
              className="w-full mt-3 py-1.5 px-3 rounded bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs flex items-center justify-center gap-2 transition-all shadow-md active:scale-98"
            >
              <span>VERIFY & ADVANCE STEP</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>SEQUENCE PROGRESS</span>
            <span className="text-blue-400 font-semibold">{progressPercent}%</span>
          </div>

          <div className="flex flex-col gap-1.5">
            {protocol.map((step, idx) => {
              const stepCompleted = experiment.completedStepIds.includes(step.id);
              const stepCurrent = step.id === experiment.currentStepId;
              const stepError = stepCurrent && isError;

              return (
                <div
                  key={step.id}
                  className={`flex items-center gap-3 p-2.5 rounded-lg border text-xs transition-all ${
                    stepCompleted
                      ? 'bg-emerald-500/5 border-emerald-500/20 text-slate-300'
                      : stepError
                      ? 'bg-rose-500/10 border-rose-500/40 text-rose-300'
                      : stepCurrent
                      ? 'bg-blue-500/10 border-blue-500/40 text-white font-medium shadow-glow-accent'
                      : 'bg-slate-900/40 border-white/5 text-slate-500'
                  }`}
                >
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] shrink-0 ${
                    stepCompleted
                      ? 'bg-emerald-500 text-slate-950 font-bold'
                      : stepError
                      ? 'bg-rose-500 text-white font-bold'
                      : stepCurrent
                      ? 'bg-blue-500 text-white font-bold'
                      : 'bg-slate-800 text-slate-500'
                  }`}>
                    {stepCompleted ? '✓' : idx + 1}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold truncate">{step.name}</span>
                      <span className="text-[10px] font-mono text-slate-500">P-{idx + 1}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 truncate">{step.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
