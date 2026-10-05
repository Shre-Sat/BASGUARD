export type LanguageCode = 'en' | 'hi' | 'fr' | 'es';

export interface LanguageOption {
  code: LanguageCode;
  name: string;
  nativeName: string;
  flag: string;
  speechLocale: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧', speechLocale: 'en-US' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', flag: '🇮🇳', speechLocale: 'hi-IN' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷', speechLocale: 'fr-FR' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸', speechLocale: 'es-ES' },
];

export const TRANSLATIONS: Record<LanguageCode, Record<string, string>> = {
  en: {
    start_mission: "START MISSION DASHBOARD 🚀",
    start_sub: "Click to launch live ISRO monitor",
    hero_title_1: "Precision Space Safety & ",
    hero_title_2: "Astronaut Verification",
    badge_title: "ISRO SPACE EXPERIMENT AI MONITOR",
    select_language: "Language",
    deep_space: "DEEP SPACE 🌌",
    white_blue: "WHITE & BLUE ☀️",
    mission_control: "Mission Control",
    fsm_protocol: "FSM Protocol",
    spatial_telemetry: "3D Telemetry",
    telemetry_logs: "Telemetry Logs",
    system_health: "System Health",
    settings: "Settings",
    perception_feed: "PERCEPTION FEED",
    verify_step: "VERIFY STEP",
    simulated_edge: "SIMULATED EDGE AI 🤖",
    hardware_online: "HARDWARE ONLINE ⚡",
    stream_disconnected: "STREAM DISCONNECTED 📡",
    orbital_day: "ORBITAL SUNLIGHT (DAY ☀️)",
    orbital_night: "ORBITAL ECLIPSE (NIGHT 🌙)",
    welcome_voice: "Welcome to ISRO BAS Guard. Mission Control system online.",
  },
  hi: {
    start_mission: "मिशन डैशबोर्ड शुरू करें 🚀",
    start_sub: "लाइव इसरो मॉनिटर खोलने के लिए क्लिक करें",
    hero_title_1: "सटीक अंतरिक्ष सुरक्षा एवं ",
    hero_title_2: "अंतरिक्ष यात्री सत्यापन",
    badge_title: "इसरो अंतरिक्ष प्रयोग एआई मॉनिटर",
    select_language: "भाषा (Language)",
    deep_space: "गहरा अंतरिक्ष 🌌",
    white_blue: "श्वेत और नीला ☀️",
    mission_control: "मिशन नियंत्रण",
    fsm_protocol: "एफएसएम प्रोटोकॉल",
    spatial_telemetry: "3D टेलीमेट्री",
    telemetry_logs: "टेलीमेट्री लॉग",
    system_health: "सिस्टम स्वास्थ्य",
    settings: "सेटिंग्स",
    perception_feed: "दृष्टि फीड (Perception Feed)",
    verify_step: "चरण सत्यापित करें",
    simulated_edge: "सिम्युलेटेड एज एआई 🤖",
    hardware_online: "हार्डवेयर ऑनलाइन ⚡",
    stream_disconnected: "स्ट्रीम डिस्कनेक्टेड 📡",
    orbital_day: "कक्षीय सूर्यप्रकाश (दिन ☀️)",
    orbital_night: "कक्षीय ग्रहण (रात 🌙)",
    welcome_voice: "इसरो बास गार्ड में आपका स्वागत है। मिशन नियंत्रण प्रणाली ऑनलाइन है।",
  },
  fr: {
    start_mission: "LANCER LE TABLEAU DE BORD 🚀",
    start_sub: "Cliquer pour lancer le moniteur ISRO",
    hero_title_1: "Sécurité spatiale de précision & ",
    hero_title_2: "Vérification d'astronaute",
    badge_title: "MONITEUR IA D'EXPÉRIENCE SPATIALE ISRO",
    select_language: "Langue",
    deep_space: "ESPACE PROFOND 🌌",
    white_blue: "BLANC & BLEU ☀️",
    mission_control: "Contrôle de Mission",
    fsm_protocol: "Protocole FSM",
    spatial_telemetry: "Télémétrie 3D",
    telemetry_logs: "Journaux Télémétrie",
    system_health: "Santé du Système",
    settings: "Paramètres",
    perception_feed: "FLUX DE PERCEPTION",
    verify_step: "VÉRIFIER L'ÉTAPE",
    simulated_edge: "IA EDGE SIMULÉE 🤖",
    hardware_online: "MATÉRIEL EN LIGNE ⚡",
    stream_disconnected: "FLUX DÉCONNECTÉ 📡",
    orbital_day: "SOLEIL ORBITAL (JOUR ☀️)",
    orbital_night: "ÉCLIPSE ORBITALE (NUIT 🌙)",
    welcome_voice: "Bienvenue sur ISRO BAS Guard. Système de contrôle de mission en ligne.",
  },
  es: {
    start_mission: "INICIAR PANEL DE CONTROL 🚀",
    start_sub: "Haga clic para iniciar el monitor ISRO",
    hero_title_1: "Seguridad espacial de precisión y ",
    hero_title_2: "Verificación de astronautas",
    badge_title: "MONITOR DE IA DE EXPERIMENTOS ESPACIALES ISRO",
    select_language: "Idioma",
    deep_space: "ESPACIO PROFUNDO 🌌",
    white_blue: "BLANCO Y AZUL ☀️",
    mission_control: "Control de Misión",
    fsm_protocol: "Protocolo FSM",
    spatial_telemetry: "Telemetría 3D",
    telemetry_logs: "Registros de Telemetría",
    system_health: "Salud del Sistema",
    settings: "Configuración",
    perception_feed: "CANAL DE PERCEPCIÓN",
    verify_step: "VERIFICAR PASO",
    simulated_edge: "IA EDGE SIMULADA 🤖",
    hardware_online: "HARDWARE EN LÍNEA ⚡",
    stream_disconnected: "TRANSMISIÓN DESCONECTADA 📡",
    orbital_day: "LUZ SOLAR ORBITAL (DÍA ☀️)",
    orbital_night: "ECLIPSE ORBITAL (NOCHE 🌙)",
    welcome_voice: "Bienvenido a ISRO BAS Guard. Sistema de control de misión en línea.",
  },
};

export const getTranslation = (lang: LanguageCode, key: string): string => {
  return TRANSLATIONS[lang]?.[key] || TRANSLATIONS.en[key] || key;
};
