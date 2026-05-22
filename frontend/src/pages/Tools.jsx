import { useState } from 'react';
import { Calculator, Clock, Link2, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

const TOOLS = [
  { id: 'calculator', label: 'Calculator', icon: Calculator, placeholder: '2 + 2 * 10' },
  { id: 'datetime_tool', label: 'Date & Time', icon: Clock, placeholder: '' },
  { id: 'url_extractor', label: 'URL Extractor', icon: Link2, placeholder: 'Paste text with https:// links' },
  { id: 'text_summarizer', label: 'Summarizer', icon: Sparkles, placeholder: 'Long text to summarize...' },
  { id: 'keyword_extractor', label: 'Keywords', icon: Sparkles, placeholder: 'Text for keyword extraction' },
  { id: 'json_formatter', label: 'JSON Formatter', icon: Sparkles, placeholder: '{"key": "value"}' },
  { id: 'text_cleaner', label: 'Text Cleaner', icon: Sparkles, placeholder: '  messy   text  ' },
  { id: 'search_optimizer', label: 'Search Optimizer', icon: Sparkles, placeholder: 'AI developer jobs' },
];

export default function Tools() {
  const [active, setActive] = useState(TOOLS[0].id);
  const [input, setInput] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    setResult(null);
    try {
      const tool = TOOLS.find((t) => t.id === active);
      const needsInput = active !== 'datetime_tool';
      if (needsInput && !input.trim()) {
        toast.error('Please enter input for this tool');
        setLoading(false);
        return;
      }
      let payload = {};
      if (active === 'calculator') payload = { expression: input.trim() };
      else if (active === 'datetime_tool') payload = {};
      else if (active === 'search_optimizer') payload = { query: input.trim() };
      else payload = { text: input.trim() };

      const res = await api.runTool(active, payload);
      if (res.result?.error) {
        toast.error(res.result.error);
      } else {
        toast.success(`${tool.label} completed`);
      }
      setResult(res.result);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const current = TOOLS.find((t) => t.id === active);

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-6">
        {TOOLS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => {
              setActive(id);
              setResult(null);
            }}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl text-xs font-medium transition-all ${
              active === id
                ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                : 'glass text-slate-400 hover:text-slate-200'
            }`}
          >
            <Icon className="w-5 h-5" />
            {label}
          </button>
        ))}
      </div>

      <div className="glass rounded-2xl p-5 space-y-4">
        <h3 className="font-semibold text-slate-200">{current?.label}</h3>
        {active === 'datetime_tool' ? (
          <p className="text-sm text-slate-400">Returns current UTC date and time. No input required.</p>
        ) : (
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={current?.placeholder || 'Enter input...'}
            rows={4}
            className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm"
          />
        )}
        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="px-6 py-2.5 rounded-xl bg-cyan-600 text-white text-sm disabled:opacity-50"
        >
          {loading ? 'Running...' : 'Run Tool'}
        </button>
        {result && (
          <pre className="text-xs bg-slate-900/80 p-4 rounded-xl overflow-auto text-slate-300 max-h-64">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
