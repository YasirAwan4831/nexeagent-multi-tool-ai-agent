import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import JobCard from '../components/JobCard';
import { api } from '../services/api';

const FILTERS = [
  'AI',
  'automation',
  'Python',
  'Flask',
  'React',
  'full stack',
  'remote',
  'web development',
];

export default function Jobs() {
  const [query, setQuery] = useState('AI automation developer remote');
  const [jobs, setJobs] = useState([]);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [companyFilter, setCompanyFilter] = useState('');

  const search = async (q = query) => {
    setLoading(true);
    try {
      const res = await api.searchJobs(q);
      setJobs(res.jobs || []);
      setSummary(res.summary || '');
      toast.success(`Found ${res.count || 0} jobs`);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveJobNote = async (job) => {
    try {
      await api.createNote({
        title: `${job.title} @ ${job.company}`,
        content: `${job.url}\n\n${(job.description || '').slice(0, 500)}`,
        tags: ['job', job.category || 'dev'].filter(Boolean),
        type: 'job',
      });
      toast.success('Job saved to notes');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const filtered = companyFilter
    ? jobs.filter((j) =>
        j.company?.toLowerCase().includes(companyFilter.toLowerCase())
      )
    : jobs;

  return (
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      <div className="glass rounded-2xl p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && search()}
              placeholder="Search AI, Python, React, remote jobs..."
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600/50 text-sm focus:outline-none focus:border-cyan-500/50"
            />
          </div>
          <button
            type="button"
            onClick={() => search()}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white text-sm font-medium disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search Jobs'}
          </button>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {FILTERS.map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => {
                setQuery(f);
                search(f);
              }}
              className="text-xs px-3 py-1.5 rounded-full border border-slate-600 text-slate-400 hover:border-cyan-500/50 hover:text-cyan-400"
            >
              {f}
            </button>
          ))}
        </div>
        <div className="mt-3 flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <input
            value={companyFilter}
            onChange={(e) => setCompanyFilter(e.target.value)}
            placeholder="Filter by company..."
            className="flex-1 max-w-xs px-3 py-2 rounded-lg bg-slate-900/50 border border-slate-600/50 text-xs"
          />
        </div>
      </div>

      {summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass rounded-2xl p-4 mb-6 text-sm text-slate-300 border-l-4 border-cyan-500"
        >
          <p className="font-medium text-cyan-400 mb-1">AI Summary</p>
          <p className="whitespace-pre-wrap">{summary}</p>
        </motion.div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map((job, i) => (
          <JobCard key={job.id || i} job={job} index={i} onSave={saveJobNote} />
        ))}
      </div>

      {!loading && filtered.length === 0 && (
        <p className="text-center text-slate-500 py-16">
          Search for remote developer jobs to get started.
        </p>
      )}
    </div>
  );
}
