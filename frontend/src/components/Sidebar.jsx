import { NavLink } from 'react-router-dom';
import {
  Bot,
  Briefcase,
  Home,
  Mail,
  Moon,
  StickyNote,
  Sun,
  Wrench,
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const links = [
  { to: '/', icon: Home, label: 'Chat' },
  { to: '/jobs', icon: Briefcase, label: 'Jobs' },
  { to: '/notes', icon: StickyNote, label: 'Notes' },
  { to: '/email', icon: Mail, label: 'Email' },
  { to: '/tools', icon: Wrench, label: 'Tools' },
];

export default function Sidebar({ mobileOpen, onClose }) {
  const { dark, toggle } = useTheme();

  return (
    <>
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 flex flex-col glass border-r border-slate-700/50 transition-transform duration-300 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-5 border-b border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="text-left">
              <h1 className="font-bold text-sm gradient-text">NEXEAGENT</h1>
              <p className="text-xs text-slate-400">Multi-Tool AI Agent</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {links.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-700/50">
          <button
            type="button"
            onClick={toggle}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/60 text-slate-300 hover:bg-slate-700/60 text-sm transition-colors"
          >
            {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            {dark ? 'Light mode' : 'Dark mode'}
          </button>
          <p className="text-center text-[10px] text-slate-500 mt-3">NEXE.AGENT Internship</p>
        </div>
      </aside>
    </>
  );
}
