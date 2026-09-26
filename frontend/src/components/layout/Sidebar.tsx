import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  Box,
  Terminal,
  Cpu,
  Settings,
} from 'lucide-react';

const navItems = [
  { path: '/mission-control', icon: LayoutDashboard, label: 'Mission Control' },
  { path: '/experiment', icon: Activity, label: 'Experiment' },
  { path: '/scene', icon: Box, label: 'Scene' },
  { path: '/logs', icon: Terminal, label: 'Event Log' },
  { path: '/system', icon: Cpu, label: 'System' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const Sidebar = () => {
  return (
    <aside className="w-16 h-full bg-base-50 flex flex-col items-center py-5 gap-1 shrink-0">
      {/* Brand mark */}
      <div className="w-8 h-8 flex items-center justify-center mb-6">
        <span className="text-sm font-bold text-text-primary tracking-tight">BG</span>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 w-full px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            title={item.label}
            className={({ isActive }) =>
              `w-full h-10 flex items-center justify-center rounded transition-colors relative
              ${isActive
                ? 'text-accent bg-accent-dim'
                : 'text-text-muted hover:text-text-secondary'
              }`
            }
          >
            <item.icon className="w-[18px] h-[18px]" strokeWidth={1.5} />
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
