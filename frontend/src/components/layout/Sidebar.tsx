import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  Box,
  Terminal,
  Cpu,
  Settings,
  Radio
} from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/mission-control', icon: LayoutDashboard, label: 'Mission Control' },
  { path: '/experiment', icon: Activity, label: 'FSM Protocol' },
  { path: '/scene', icon: Box, label: '3D Telemetry' },
  { path: '/logs', icon: Terminal, label: 'Telemetry Logs' },
  { path: '/system', icon: Cpu, label: 'System Health' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const Sidebar = () => {
  return (
    <aside className="w-16 h-full bg-[#070B14] border-r border-white/10 flex flex-col items-center py-4 justify-between shrink-0 z-20 select-none">
      <div className="flex flex-col items-center gap-6 w-full">
        {/* Brand Crest */}
        <NavLink to="/" className="relative group flex items-center justify-center cursor-pointer">
          <div className="w-9 h-9 rounded-lg bg-[#0B101D] flex items-center justify-center shadow-glow-accent border border-blue-400/30 p-1">
            <img src="/basguard-logo.png" alt="BASGUARD Logo" className="w-full h-full object-contain" />
          </div>
          <div className="absolute left-14 px-2.5 py-1 rounded bg-slate-900 border border-white/10 text-xs font-mono text-white whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-all shadow-xl z-50">
            Launch Page &amp; Mission Overview 🚀
          </div>
        </NavLink>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-2 w-full px-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `relative w-full h-11 flex items-center justify-center rounded-lg transition-all group ${
                  isActive
                    ? 'text-blue-400 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {/* Framer Motion Active Indicator Pill */}
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-active-pill"
                      className="absolute inset-0 bg-blue-500/15 border border-blue-500/30 rounded-lg shadow-glow-accent"
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    />
                  )}

                  <item.icon className="w-5 h-5 z-10" strokeWidth={isActive ? 2 : 1.5} />

                  {/* Tooltip on Hover */}
                  <div className="absolute left-14 px-2.5 py-1 rounded bg-slate-900 border border-white/10 text-xs font-mono text-slate-100 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-all shadow-xl z-50">
                    {item.label}
                  </div>
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom Mission Beacon */}
      <div className="flex flex-col items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-slate-900 border border-white/10 flex items-center justify-center text-slate-400 hover:text-amber-400 transition-colors cursor-pointer" title="Telemetry Relay Active">
          <Radio className="w-4 h-4 animate-pulse text-amber-400" />
        </div>
      </div>
    </aside>
  );
};
