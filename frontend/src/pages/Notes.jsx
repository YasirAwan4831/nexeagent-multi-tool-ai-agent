import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Edit2, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function Notes() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ title: '', content: '', tags: '' });
  const [editingId, setEditingId] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.getNotes();
      setNotes(res.notes || []);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      title: form.title,
      content: form.content,
      tags: form.tags ? form.tags.split(',').map((t) => t.trim()) : [],
    };
    try {
      if (editingId) {
        await api.updateNote(editingId, payload);
        toast.success('Note updated');
      } else {
        await api.createNote(payload);
        toast.success('Note created');
      }
      setForm({ title: '', content: '', tags: '' });
      setEditingId(null);
      load();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const remove = async (id) => {
    if (!confirm('Delete this note?')) return;
    try {
      await api.deleteNote(id);
      toast.success('Note deleted');
      load();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const startEdit = (note) => {
    setEditingId(note.id);
    setForm({
      title: note.title,
      content: note.content,
      tags: (note.tags || []).join(', '),
    });
  };

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto">
      <form onSubmit={submit} className="glass rounded-2xl p-5 mb-6 space-y-3">
        <h3 className="font-semibold text-slate-200 flex items-center gap-2">
          <Plus className="w-4 h-4 text-cyan-400" />
          {editingId ? 'Edit Note' : 'New Note'}
        </h3>
        <input
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          placeholder="Title"
          required
          className="w-full px-4 py-2.5 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm"
        />
        <textarea
          value={form.content}
          onChange={(e) => setForm({ ...form, content: e.target.value })}
          placeholder="Content (job links, summaries, reminders...)"
          required
          rows={4}
          className="w-full px-4 py-2.5 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm resize-none"
        />
        <input
          value={form.tags}
          onChange={(e) => setForm({ ...form, tags: e.target.value })}
          placeholder="Tags (comma-separated)"
          className="w-full px-4 py-2.5 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm"
        />
        <div className="flex gap-2">
          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-cyan-600 text-white text-sm font-medium hover:bg-cyan-500"
          >
            {editingId ? 'Update' : 'Save Note'}
          </button>
          {editingId && (
            <button
              type="button"
              onClick={() => {
                setEditingId(null);
                setForm({ title: '', content: '', tags: '' });
              }}
              className="px-5 py-2.5 rounded-xl border border-slate-600 text-slate-400 text-sm"
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p className="text-center text-slate-500">Loading notes...</p>
      ) : (
        <div className="space-y-3">
          {notes.map((note, i) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              className="glass rounded-2xl p-5"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-slate-100">{note.title}</h4>
                  <p className="text-xs text-slate-500 mt-1">
                    {new Date(note.updated_at || note.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex gap-1">
                  <button
                    type="button"
                    onClick={() => startEdit(note)}
                    className="p-2 text-slate-400 hover:text-cyan-400"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => remove(note.id)}
                    className="p-2 text-slate-400 hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-sm text-slate-300 mt-3 whitespace-pre-wrap">{note.content}</p>
              {note.tags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {note.tags.map((t) => (
                    <span
                      key={t}
                      className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
          {notes.length === 0 && (
            <p className="text-center text-slate-500 py-12">No notes yet. Create your first note above.</p>
          )}
        </div>
      )}
    </div>
  );
}
