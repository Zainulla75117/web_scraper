import { useState } from 'react';
import InputForm from './components/InputForm';
import DocumentList from './components/DocumentList';
import { motion } from 'motion/react';
import { Database } from '@phosphor-icons/react';
import './index.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleScrapeSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-[100dvh] bg-zinc-950 text-zinc-300 px-6 py-16 md:py-24">
      <main className="max-w-4xl mx-auto flex flex-col gap-16">
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col gap-4"
        >
          <div className="flex items-center gap-3 text-emerald-500">
            <Database weight="duotone" size={32} />
            <h1 className="text-xl font-medium tracking-tight text-zinc-100">RAG Scraper Hub</h1>
          </div>
          <p className="text-zinc-500 max-w-[65ch] leading-relaxed text-sm">
            Extract, clean, and store web content for Retrieval-Augmented Generation. Enter a URL to parse the text and prepare it for embedding.
          </p>
        </motion.header>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        >
          <InputForm onScrapeSuccess={handleScrapeSuccess} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <DocumentList refreshTrigger={refreshTrigger} />
        </motion.div>
      </main>
    </div>
  );
}

export default App;
