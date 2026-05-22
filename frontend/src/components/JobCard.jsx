import { motion } from 'framer-motion';
import { Building2, ExternalLink, MapPin, Tag } from 'lucide-react';

export default function JobCard({ job, index = 0, onSave }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="glass rounded-2xl p-5 hover:border-cyan-500/30 border border-transparent transition-all group"
    >
      <div className="flex justify-between items-start gap-3">
        <div>
          <h3 className="font-semibold text-slate-100 group-hover:text-cyan-400 transition-colors line-clamp-2">
            {job.title}
          </h3>
          <p className="flex items-center gap-1.5 text-sm text-slate-400 mt-1">
            <Building2 className="w-3.5 h-3.5" />
            {job.company}
          </p>
        </div>
        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 p-2 rounded-lg bg-slate-800/60 text-cyan-400 hover:bg-cyan-500/20 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>

      <div className="flex flex-wrap gap-2 mt-3 text-xs text-slate-500">
        {job.location && (
          <span className="flex items-center gap-1 px-2 py-1 rounded-md bg-slate-800/50">
            <MapPin className="w-3 h-3" />
            {job.location}
          </span>
        )}
        {job.category && (
          <span className="flex items-center gap-1 px-2 py-1 rounded-md bg-slate-800/50">
            <Tag className="w-3 h-3" />
            {job.category}
          </span>
        )}
      </div>

      {job.description && (
        <p className="text-xs text-slate-400 mt-3 line-clamp-3">{job.description.replace(/<[^>]+>/g, '')}</p>
      )}

      {onSave && (
        <button
          type="button"
          onClick={() => onSave(job)}
          className="mt-4 text-xs text-cyan-400 hover:text-cyan-300 font-medium"
        >
          Save to notes →
        </button>
      )}
    </motion.article>
  );
}
