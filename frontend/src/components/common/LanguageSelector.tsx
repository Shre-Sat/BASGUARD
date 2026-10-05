import { useState, useRef, useEffect } from 'react';
import { useExperimentStore } from '../../store/useExperimentStore';
import { SUPPORTED_LANGUAGES, type LanguageCode } from '../../utils/i18n';
import { Globe, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const LanguageSelector = () => {
  const { languageMode, setLanguageMode } = useExperimentStore();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === languageMode) || SUPPORTED_LANGUAGES[0];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (code: LanguageCode) => {
    setLanguageMode(code);
    setIsOpen(false);
  };

  return (
    <div className="relative z-50 font-mono" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold bg-slate-900/80 text-slate-200 border-white/15 hover:border-blue-400/50 hover:bg-slate-800 transition-all shadow-sm active:scale-95"
        title="Select Language / भाषा चुनें"
      >
        <Globe className="w-3.5 h-3.5 text-blue-400" />
        <span className="text-base leading-none">{currentLang.flag}</span>
        <span className="hidden sm:inline font-sans">{currentLang.nativeName}</span>
        <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-1.5 w-44 p-1.5 rounded-xl glass-panel border border-white/15 shadow-2xl z-50 flex flex-col gap-1 backdrop-blur-xl"
          >
            <div className="px-2 py-1 text-[10px] text-slate-400 border-b border-white/10 font-bold uppercase tracking-wider">
              SELECT LANGUAGE / भाषा
            </div>

            {SUPPORTED_LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleSelect(lang.code)}
                className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-sans transition-colors ${
                  languageMode === lang.code
                    ? 'bg-blue-600/30 text-blue-300 font-bold border border-blue-500/40'
                    : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-base">{lang.flag}</span>
                  <span>{lang.nativeName}</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono uppercase">{lang.code}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
