import { useEffect, useState } from 'react';
import { Mail, Send } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function Email() {
  const [status, setStatus] = useState(null);
  const [form, setForm] = useState({ to: '', subject: '', body: '' });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    api.emailStatus().then(setStatus).catch(() => {});
  }, []);

  const send = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      const res = await api.sendEmail({
        to: form.to,
        subject: form.subject,
        body: form.body,
      });
      if (res.success) toast.success(res.message);
      else toast.error(res.message);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="p-4 md:p-6 max-w-xl mx-auto">
      <div
        className={`rounded-2xl p-4 mb-6 text-sm border ${
          status?.configured
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
        }`}
      >
        {status?.message ||
          'Configure SMTP_USER and SMTP_PASSWORD in backend/.env to enable email.'}
      </div>

      <form onSubmit={send} className="glass rounded-2xl p-6 space-y-4">
        <h3 className="font-semibold text-slate-200 flex items-center gap-2">
          <Mail className="w-5 h-5 text-cyan-400" />
          Send Email
        </h3>
        <input
          type="email"
          value={form.to}
          onChange={(e) => setForm({ ...form, to: e.target.value })}
          placeholder="Recipient email"
          required
          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm"
        />
        <input
          value={form.subject}
          onChange={(e) => setForm({ ...form, subject: e.target.value })}
          placeholder="Subject"
          required
          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm"
        />
        <textarea
          value={form.body}
          onChange={(e) => setForm({ ...form, body: e.target.value })}
          placeholder="Body — job links, summaries, notifications..."
          required
          rows={8}
          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm resize-none"
        />
        <button
          type="submit"
          disabled={sending}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          {sending ? 'Sending...' : 'Send Email'}
        </button>
      </form>
    </div>
  );
}
