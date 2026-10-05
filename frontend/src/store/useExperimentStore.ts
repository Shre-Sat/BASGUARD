import { create } from 'zustand';
import type { 
  ExperimentState, 
  AlertEvent, 
  SystemHealth, 
  ProtocolStep 
} from '../types';
import { speakAlert, playUiBeep } from '../utils/audioAlert';
import type { LanguageCode } from '../utils/i18n';

interface AppState {
  // Mode & Audio & i18n Language Choice
  demoMode: boolean;
  setDemoMode: (enabled: boolean) => void;
  audioMuted: boolean;
  toggleAudioMuted: () => void;
  languageMode: LanguageCode;
  setLanguageMode: (lang: LanguageCode) => void;
  
  // Theme & Orbital Day/Night Telemetry
  themeMode: 'NIGHT' | 'WHITE_BLUE';
  toggleThemeMode: () => void;
  orbitalPhase: 'DAY' | 'NIGHT';
  toggleOrbitalPhase: () => void;

  // HUD Camera controls
  showScanlines: boolean;
  setShowScanlines: (show: boolean) => void;
  showHsvFilter: boolean;
  setShowHsvFilter: (show: boolean) => void;

  // Protocol Definition
  protocol: ProtocolStep[];
  
  // Real-time State
  experiment: ExperimentState;
  alerts: AlertEvent[];
  health: SystemHealth;
  detections: any[];
  
  // Actions for Demo/Backend
  updateExperiment: (update: Partial<ExperimentState>) => void;
  addAlert: (alert: Omit<AlertEvent, 'id' | 'timestamp'>) => void;
  updateHealth: (update: Partial<SystemHealth>) => void;
  acknowledgeAlert: (alertId: string) => void;
  clearAllAlerts: () => void;
  
  // Real backend connection
  connectWebSocket: (url: string) => void;
  
  // Demo Controls
  triggerNormalSequence: () => void;
  triggerOutOfSequence: () => void;
  triggerLowConfidence: () => void;
  simulateCameraLoss: () => void;
  completeExperiment: () => void;
  resetExperiment: () => void;
}

const DEFAULT_PROTOCOL: ProtocolStep[] = [
  { id: 'IDLE', name: 'Wait / Standby (System Ready 🚀)', description: 'Chilling out on orbit. Awaiting astronaut signal.' },
  { id: 'DETECT_OUTER', name: 'Detect Outer Box (Big Space Box 📦)', description: 'Locate the main biological containment unit.' },
  { id: 'OPEN_OUTER', name: 'Open Outer Box (Unlatch Lid 🔓)', description: 'Astronaut carefully opens the main box lid.' },
  { id: 'IDENTIFY_RED', name: 'Identify Red Box (Spicy Bio Sample A 🌶️)', description: 'Hawk-eye AI locks onto the Red Specimen Container.' },
  { id: 'IDENTIFY_YELLOW', name: 'Identify Yellow Box (Banana Mold Sample B 🍌)', description: 'Hawk-eye AI locks onto Yellow Specimen Container.' },
  { id: 'PICK_YELLOW', name: 'Pick Yellow Box (Careful Hold 🧑‍🚀)', description: 'Astronaut glove picks up Yellow Specimen Box.' },
  { id: 'PLACE_YELLOW', name: 'Place Yellow Box (Dock & Lock 🔒)', description: 'Safely dock container onto workbench workstation.' },
  { id: 'COMPLETE', name: 'Protocol Completed (High Five! 🎉)', description: 'All steps done perfectly! Telemetry saved.' },
];

const INITIAL_HEALTH: SystemHealth = {
  fps: 29.8,
  inferenceLatency: 14.2,
  cpu: 34.5,
  gpu: 62.1,
  ram: 4.8,
  power: 45.2,
  storage: 124.5,
  streamStatus: 'CONNECTED',
};

const INITIAL_EXPERIMENT: ExperimentState = {
  currentStepId: 'IDLE',
  completedStepIds: [],
  nextStepId: 'DETECT_OUTER',
  confidence: 98.4,
  status: 'IDLE'
};

export const useExperimentStore = create<AppState>((set, get) => ({
  demoMode: true,
  setDemoMode: (enabled) => set({ demoMode: enabled }),

  audioMuted: false,
  toggleAudioMuted: () => set((state) => {
    const nextMuted = !state.audioMuted;
    if (nextMuted && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    return { audioMuted: nextMuted };
  }),

  languageMode: 'en',
  setLanguageMode: (lang) => set({ languageMode: lang }),

  themeMode: 'NIGHT',
  toggleThemeMode: () => set((state) => {
    const nextTheme = state.themeMode === 'NIGHT' ? 'WHITE_BLUE' : 'NIGHT';
    if (nextTheme === 'WHITE_BLUE') {
      document.documentElement.classList.add('theme-white-blue');
    } else {
      document.documentElement.classList.remove('theme-white-blue');
    }
    return { themeMode: nextTheme };
  }),

  orbitalPhase: 'DAY',
  toggleOrbitalPhase: () => set((state) => {
    const nextPhase = state.orbitalPhase === 'DAY' ? 'NIGHT' : 'DAY';
    get().addAlert({
      severity: 'INFO',
      type: 'SYSTEM',
      message: `Orbital cycle transition: Station entered ORBITAL ${nextPhase === 'DAY' ? 'SUNLIGHT (DAY ☀️)' : 'ECLIPSE (NIGHT 🌙)'}.`,
      acknowledged: false
    });
    return { orbitalPhase: nextPhase };
  }),

  showScanlines: true,
  setShowScanlines: (show) => set({ showScanlines: show }),
  showHsvFilter: false,
  setShowHsvFilter: (show) => set({ showHsvFilter: show }),
  
  protocol: DEFAULT_PROTOCOL,
  experiment: { ...INITIAL_EXPERIMENT },
  alerts: [
    {
      id: 'init-1',
      severity: 'INFO',
      type: 'SYSTEM',
      message: 'ISRO BASGuard perception pipeline initialized. FPS: 30.0 (Smooth as butter! 🧈🚀).',
      timestamp: Date.now() - 120000,
      acknowledged: true
    },
    {
      id: 'init-2',
      severity: 'SUCCESS',
      type: 'STEP_COMPLETED',
      message: 'Space Rules Brain loaded [Petri-FSM v2.4.1]. Astronauts get ready! 🧑‍🚀✨',
      timestamp: Date.now() - 60000,
      acknowledged: true
    }
  ],
  health: { ...INITIAL_HEALTH },
  detections: [],
  
  updateExperiment: (update) => set((state) => ({ 
    experiment: { ...state.experiment, ...update } 
  })),
  
  addAlert: (alert) => {
    const newId = Math.random().toString(36).substring(7);
    const newAlert = { ...alert, id: newId, timestamp: Date.now(), acknowledged: false };
    
    if (!get().audioMuted) {
      if (alert.severity === 'CRITICAL') {
        speakAlert(`Warning: Anomaly detected. ${alert.message}`);
      } else if (alert.severity === 'WARNING') {
        speakAlert(`Alert: ${alert.message}`);
      } else if (alert.severity === 'SUCCESS') {
        playUiBeep(1046, 'sine', 0.1);
      } else {
        playUiBeep(523, 'sine', 0.05);
      }
    }

    set((state) => ({
      alerts: [newAlert, ...state.alerts].slice(0, 50)
    }));
  },

  acknowledgeAlert: (alertId) => set((state) => ({
    alerts: state.alerts.map((a) => a.id === alertId ? { ...a, acknowledged: true } : a)
  })),

  clearAllAlerts: () => set({ alerts: [] }),
  
  updateHealth: (update) => set((state) => ({
    health: { ...state.health, ...update }
  })),

  connectWebSocket: (url: string) => {
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(url);
    } catch {
      console.log('Backend websocket offline. Operating in edge mode.');
      return;
    }
    
    ws.onopen = () => {
      console.log('Connected to BASGuard Backend WebSocket');
      set((state) => ({
        health: { ...state.health, streamStatus: 'CONNECTED' }
      }));
    };
    
    ws.onmessage = (event) => {
      if (get().demoMode) return;
      try {
        const data = JSON.parse(event.data);
        
        set((state) => {
          const newState = { ...state };
          
          if (data.health) {
            newState.health = { ...state.health, ...data.health, streamStatus: 'CONNECTED' };
          }
          if (data.experiment) {
            newState.experiment = { ...state.experiment, ...data.experiment };
          }
          if (data.alerts && Array.isArray(data.alerts)) {
            const newAlerts = data.alerts.filter((a: any) => 
              !state.alerts.some(existing => existing.timestamp === a.timestamp && existing.message === a.message)
            ).map((a: any) => ({
              id: Math.random().toString(36).substring(7),
              severity: a.severity,
              type: 'SYSTEM',
              message: a.message,
              timestamp: a.timestamp * 1000,
              acknowledged: false
            }));
            
            if (newAlerts.length > 0) {
              newState.alerts = [...newAlerts.reverse(), ...state.alerts].slice(0, 50);
            }
          }
          if (data.detections && Array.isArray(data.detections)) {
            newState.detections = data.detections;
          }
          
          return newState;
        });
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };
    
    ws.onclose = () => {
      set((state) => ({
        health: { ...state.health, streamStatus: 'DISCONNECTED' }
      }));
    };
  },
  
  // --- DEMO ACTIONS ---
  triggerNormalSequence: () => {
    const { experiment, protocol, addAlert } = get();
    const currentIndex = protocol.findIndex(s => s.id === experiment.currentStepId);
    
    if (currentIndex < protocol.length - 1) {
      const nextStep = protocol[currentIndex + 1];
      const futureStep = protocol[currentIndex + 2];
      
      addAlert({
        severity: 'SUCCESS',
        type: 'STEP_COMPLETED',
        message: `Step ${currentIndex + 1} (${protocol[currentIndex].name}) verified successfully! Great job Space Cadet! 🎉`,
        acknowledged: false
      });
      
      set((state) => ({
        experiment: {
          ...state.experiment,
          status: nextStep.id === 'COMPLETE' ? 'COMPLETED' : 'IN_PROGRESS',
          completedStepIds: [...state.experiment.completedStepIds, state.experiment.currentStepId],
          currentStepId: nextStep.id,
          nextStepId: futureStep ? futureStep.id : null,
          confidence: Number((95 + Math.random() * 4.8).toFixed(1))
        }
      }));
    }
  },
  
  triggerOutOfSequence: () => {
    const { addAlert, experiment } = get();
    addAlert({
      severity: 'CRITICAL',
      type: 'OUT_OF_SEQUENCE',
      message: `Space Rule Violation! Expected: ${experiment.nextStepId || 'NEXT_STEP'}. Grabbed wrong item! 🚨`,
      acknowledged: false
    });
    set((state) => ({
      experiment: { ...state.experiment, status: 'ERROR', confidence: 41.3 }
    }));
  },
  
  triggerLowConfidence: () => {
    get().addAlert({
      severity: 'WARNING',
      type: 'LOW_CONFIDENCE',
      message: 'AI is squinting! 🧐 Low detection confidence (34.8%). Please clear camera view.',
      acknowledged: false
    });
    set((state) => ({
      experiment: { ...state.experiment, confidence: 34.8 }
    }));
  },
  
  simulateCameraLoss: () => {
    get().addAlert({
      severity: 'CRITICAL',
      type: 'STREAM_LOST',
      message: 'Whoops! Camera signal lost in space. Retrying connection... 📡',
      acknowledged: false
    });
    set((state) => ({
      health: { ...state.health, streamStatus: 'DISCONNECTED', fps: 0 }
    }));
  },
  
  completeExperiment: () => {
    const { protocol, addAlert } = get();
    const allIds = protocol.map(p => p.id);
    addAlert({
      severity: 'SUCCESS',
      type: 'SYSTEM',
      message: 'All ISRO BAS experiment steps complete! Mission Accomplished! 🏆🚀',
      acknowledged: false
    });
    set({
      experiment: {
        currentStepId: 'COMPLETE',
        completedStepIds: allIds.slice(0, -1),
        nextStepId: null,
        confidence: 99.8,
        status: 'COMPLETED'
      }
    });
  },
  
  resetExperiment: () => {
    get().addAlert({
      severity: 'INFO',
      type: 'SYSTEM',
      message: 'Telemetry reset to Standby. Ready for another run! 🚀',
      acknowledged: false
    });
    set({
      experiment: { ...INITIAL_EXPERIMENT },
      health: { ...INITIAL_HEALTH }
    });
  }
}));
