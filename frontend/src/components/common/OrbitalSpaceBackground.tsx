import { motion } from 'framer-motion';

export const OrbitalSpaceBackground = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      {/* 📡 ISRO Payload Satellite Background Floating Shadow Silhouette */}
      <motion.div
        initial={{ opacity: 0, x: 80, y: -40 }}
        animate={{
          opacity: [0.15, 0.25, 0.15],
          x: [0, 25, 0],
          y: [0, -20, 0],
          rotate: [0, 6, -6, 0]
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
        className="absolute top-12 right-12 sm:right-24 w-48 sm:w-72 h-auto text-blue-500/25 dark:text-blue-400/20 filter drop-shadow-[0_0_20px_rgba(59,130,246,0.2)]"
      >
        <svg viewBox="0 0 300 200" fill="currentColor" className="w-full h-full">
          {/* Left Solar Panel Array */}
          <rect x="20" y="80" width="75" height="40" rx="3" fill="currentColor" opacity="0.85" />
          <line x1="45" y1="80" x2="45" y2="120" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />
          <line x1="70" y1="80" x2="70" y2="120" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />
          <line x1="20" y1="100" x2="95" y2="100" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />

          {/* Panel Connector Boom */}
          <rect x="95" y="96" width="30" height="8" fill="currentColor" opacity="0.9" />

          {/* Satellite Main Body Frame */}
          <rect x="125" y="65" width="50" height="70" rx="6" fill="currentColor" />
          <circle cx="150" cy="85" r="8" fill="rgba(255,255,255,0.25)" />
          <rect x="135" y="105" width="30" height="15" rx="2" fill="rgba(255,255,255,0.15)" />

          {/* Right Solar Panel Array */}
          <rect x="175" y="96" width="30" height="8" fill="currentColor" opacity="0.9" />
          <rect x="205" y="80" width="75" height="40" rx="3" fill="currentColor" opacity="0.85" />
          <line x1="230" y1="80" x2="230" y2="120" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />
          <line x1="255" y1="80" x2="255" y2="120" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />
          <line x1="205" y1="100" x2="280" y2="100" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />

          {/* Top Parabolic Dish Antenna */}
          <path d="M 130 65 Q 150 45 170 65 Z" fill="currentColor" opacity="0.9" />
          <line x1="150" y1="45" x2="150" y2="25" stroke="currentColor" strokeWidth="3" />
          <circle cx="150" cy="23" r="4" fill="#60A5FA" />

          {/* Thruster Nozzle */}
          <path d="M 140 135 L 135 150 L 165 150 L 160 135 Z" fill="currentColor" opacity="0.7" />
        </svg>
      </motion.div>

      {/* 🧑‍🚀 Astronaut Spacewalker Silhouette Floating in Space */}
      <motion.div
        initial={{ opacity: 0, x: -60, y: 60 }}
        animate={{
          opacity: [0.12, 0.22, 0.12],
          x: [0, -20, 0],
          y: [0, 25, 0],
          rotate: [0, -10, 10, 0]
        }}
        transition={{
          duration: 22,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
        className="absolute bottom-12 left-8 sm:left-20 w-44 sm:w-64 h-auto text-indigo-500/20 dark:text-blue-300/15 filter drop-shadow-[0_0_25px_rgba(99,102,241,0.2)]"
      >
        <svg viewBox="0 0 240 280" fill="currentColor" className="w-full h-full">
          {/* Safety Tether Cord */}
          <path d="M 120 270 Q 70 230 110 160" stroke="currentColor" strokeWidth="2.5" strokeDasharray="5,5" fill="none" opacity="0.6" />

          {/* Helmet Visor */}
          <circle cx="120" cy="55" r="24" fill="currentColor" />
          <path d="M 108 45 Q 120 38 132 45 Q 136 58 128 65 Q 112 65 108 45 Z" fill="#F59E0B" opacity="0.85" />

          {/* Life Support Backpack Unit */}
          <rect x="85" y="70" width="70" height="75" rx="10" fill="currentColor" opacity="0.9" />

          {/* Torso Suit Frame */}
          <path d="M 95 80 L 70 110 L 78 150 L 98 165 L 142 165 L 162 150 L 170 110 L 145 80 Z" fill="currentColor" />
          <circle cx="120" cy="110" r="10" fill="rgba(255,255,255,0.2)" />
          <rect x="105" y="130" width="30" height="12" rx="3" fill="rgba(255,255,255,0.15)" />

          {/* Left Arm & Spacewalk Glove */}
          <path d="M 75 95 L 40 120 L 25 110" stroke="currentColor" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <circle cx="20" cy="108" r="8" fill="currentColor" />

          {/* Right Arm Extended */}
          <path d="M 165 95 L 200 115 L 215 105" stroke="currentColor" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <circle cx="220" cy="102" r="8" fill="currentColor" />

          {/* Left Leg */}
          <path d="M 105 160 L 90 210 L 75 235" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <ellipse cx="70" cy="242" rx="10" ry="6" fill="currentColor" />

          {/* Right Leg */}
          <path d="M 135 160 L 150 210 L 165 235" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <ellipse cx="170" cy="242" rx="10" ry="6" fill="currentColor" />
        </svg>
      </motion.div>
    </div>
  );
};
