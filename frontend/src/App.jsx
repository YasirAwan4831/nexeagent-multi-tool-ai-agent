import { useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import { ThemeProvider } from './context/ThemeContext';
import Home from './pages/Home';
import Jobs from './pages/Jobs';
import Notes from './pages/Notes';
import Email from './pages/Email';
import Tools from './pages/Tools';

const PAGE_META = {
  '/': { title: 'AI Chat', subtitle: 'Talk to NEXEAGENT — jobs, notes, email & tools' },
  '/jobs': { title: 'Job Search', subtitle: 'AI, Python, React, remote & web dev roles' },
  '/notes': { title: 'Notes', subtitle: 'Save job links, summaries & reminders' },
  '/email': { title: 'Email', subtitle: 'Send job links and automation updates' },
  '/tools': { title: 'Utility Tools', subtitle: 'Calculator, summarizer, keywords & more' },
};

function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { pathname } = useLocation();
  const meta = PAGE_META[pathname] || PAGE_META['/'];

  return (
    <div className="flex min-h-screen bg-[var(--color-surface)]">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0 lg:ml-0">
        <Navbar
          onMenuClick={() => setMobileOpen(true)}
          title={meta.title}
          subtitle={meta.subtitle}
        />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/notes" element={<Notes />} />
            <Route path="/email" element={<Email />} />
            <Route path="/tools" element={<Tools />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#1a2332',
            color: '#e2e8f0',
            border: '1px solid rgba(148,163,184,0.2)',
          },
        }}
      />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    </ThemeProvider>
  );
}
