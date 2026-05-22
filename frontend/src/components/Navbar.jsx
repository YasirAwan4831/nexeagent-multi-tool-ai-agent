import { Menu, Sparkles } from 'lucide-react';

export default function Navbar({ onMenuClick, title, subtitle }) {
  return (
    <header className="sticky top-0 z-30 glass border-b border-slate-700/50 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-slate-800/60 text-slate-300"
          aria-label="Open menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            {title}
          </h2>
          {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
        </div>
      </div>
      <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        Agent Online
      </div>
    </header>
  );
}
