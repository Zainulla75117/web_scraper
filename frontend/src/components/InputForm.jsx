import { useState } from 'react';
import { Link, Spinner, CheckCircle, WarningCircle } from '@phosphor-icons/react';
import { motion, AnimatePresence } from 'motion/react';

const InputForm = ({ onScrapeSuccess }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const response = await fetch('http://localhost:8000/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to scrape URL');
      }

      setSuccessMsg('Successfully scraped and saved.');
      setUrl('');
      onScrapeSuccess(); 
      
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <form onSubmit={handleSubmit} className="relative flex items-center w-full max-w-2xl">
        <div className="absolute left-4 text-zinc-500">
          <Link size={20} />
        </div>
        <input 
          type="url" 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/article" 
          required 
          disabled={loading}
          className="w-full bg-zinc-900/50 border border-zinc-800/80 focus:border-zinc-700 focus:outline-none rounded-lg py-3 pl-12 pr-32 text-zinc-200 placeholder:text-zinc-600 transition-colors disabled:opacity-50"
        />
        <div className="absolute right-1.5">
          <button 
            type="submit" 
            disabled={loading || !url}
            className="flex items-center justify-center gap-2 bg-zinc-100 hover:bg-white text-zinc-900 font-medium text-sm px-4 py-1.5 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
          >
            {loading ? (
              <Spinner size={16} className="animate-spin" />
            ) : (
              'Scrape'
            )}
          </button>
        </div>
      </form>

      <AnimatePresence mode="wait">
        {error && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0, height: 0 }}
            className="flex items-center gap-2 text-rose-400 text-sm"
          >
            <WarningCircle size={16} />
            <span>{error}</span>
          </motion.div>
        )}
        {successMsg && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0, height: 0 }}
            className="flex items-center gap-2 text-emerald-400 text-sm"
          >
            <CheckCircle size={16} />
            <span>{successMsg}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default InputForm;
