import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

const QUICK_PROMPTS = [
  'Search remote AI developer jobs',
  'Find Python Flask full stack jobs',
  'What time is it?',
  'Summarize: AI automation helps developers ship faster',
];

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const bottomRef = useRef(null);

  useEffect(() => {
    api
      .getChatHistory(sessionId)
      .then((res) => {
        const hist = (res.history || [])
          .filter((m) => m?.content)
          .map((m) => ({
            role: m.role === 'user' ? 'user' : 'assistant',
            content: m.content,
            tools: Array.isArray(m.tools) ? m.tools : undefined,
          }));
        if (hist.length) setMessages(hist);
      })
      .catch(() => {});
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: msg }]);
    setLoading(true);
    try {
      const res = await api.sendMessage(msg, sessionId);
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: res.response,
          tools: res.tool_results,
        },
      ]);
    } catch (err) {
      toast.error(err.message);
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    toast.success('Chat cleared locally');
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <p className="text-2xl font-bold gradient-text mb-2">Welcome to NEXEAGENT</p>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              Your multi-tool AI assistant for job search, notes, email, and automation.
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-6">
              {QUICK_PROMPTS.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => send(p)}
                  className="text-xs px-3 py-2 rounded-full border border-slate-600 text-slate-300 hover:border-cyan-500/50 hover:text-cyan-400 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-cyan-600 to-indigo-600 text-white'
                  : 'glass text-slate-200'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.tools?.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-600/50 text-xs text-cyan-400/80">
                  Tools:{' '}
                  {msg.tools
                    .map((t) => (typeof t === 'string' ? t : t?.tool))
                    .filter(Boolean)
                    .join(', ')}
                </div>
              )}
            </div>
          </motion.div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="glass rounded-2xl px-4 py-3 flex gap-1.5">
              <span className="loading-dot w-2 h-2 rounded-full bg-cyan-400" />
              <span className="loading-dot w-2 h-2 rounded-full bg-cyan-400" />
              <span className="loading-dot w-2 h-2 rounded-full bg-cyan-400" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-slate-700/50 glass">
        <div className="flex gap-2 items-end">
          <button
            type="button"
            onClick={clearChat}
            className="p-3 rounded-xl text-slate-400 hover:bg-slate-800/60 hover:text-red-400 transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Ask about jobs, notes, email, or utilities..."
            rows={1}
            className="flex-1 resize-none rounded-xl bg-slate-900/60 border border-slate-600/50 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 min-h-[48px] max-h-32"
          />
          <button
            type="button"
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="p-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white disabled:opacity-40 hover:opacity-90 transition-opacity"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
