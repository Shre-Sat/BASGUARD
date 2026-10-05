// Web Speech API synthesized voice alerts matching Piper TTS backend behaviour

let isAudioMuted = false;

export const setAudioMuted = (muted: boolean) => {
  isAudioMuted = muted;
  if (muted && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
};

export const getAudioMuted = () => isAudioMuted;

export const speakAlert = (text: string, pitch = 1.0, rate = 1.05) => {
  if (isAudioMuted || !('speechSynthesis' in window)) return;

  try {
    window.speechSynthesis.cancel(); // Cancel any ongoing speech for immediate alert
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.pitch = pitch;
    utterance.rate = rate;
    
    // Select an English voice if available
    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('David') || v.name.includes('Zira'))) || voices[0];
    
    if (englishVoice) {
      utterance.voice = englishVoice;
    }
    
    window.speechSynthesis.speak(utterance);
  } catch (err) {
    console.error('Audio alert synthesis error:', err);
  }
};

// Play micro-sound effects via Web Audio API for UI feedback
export const playUiBeep = (freq = 880, type: OscillatorType = 'sine', duration = 0.08) => {
  if (isAudioMuted) return;
  try {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.05, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch {
    // Ignore audio context autoplay restrictions gracefully
  }
};
