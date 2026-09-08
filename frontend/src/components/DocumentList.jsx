import { useState, useEffect } from 'react';
import { DownloadSimple, TextAa, X, FileText, SpinnerGap } from '@phosphor-icons/react';
import { motion, AnimatePresence } from 'motion/react';

const DocumentList = ({ refreshTrigger }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/documents');
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (doc, e) => {
    e.stopPropagation();
    const blob = new Blob([doc.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${doc.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <SpinnerGap size={24} className="animate-spin text-zinc-600" />
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-zinc-800/60">
          <h2 className="text-sm font-medium text-zinc-400 tracking-wide uppercase">
            Scraped Documents
          </h2>
          <span className="text-xs font-mono text-zinc-500 bg-zinc-900 px-2 py-1 rounded">
            {documents.length} items
          </span>
        </div>

        {documents.length === 0 ? (
          <div className="py-12 text-center flex flex-col items-center gap-3 text-zinc-500">
            <FileText size={32} className="opacity-20" />
            <p className="text-sm">No documents extracted yet.</p>
          </div>
        ) : (
          <ul className="flex flex-col">
            {documents.map((doc) => (
              <li 
                key={doc.id} 
                className="group flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-4 border-b border-zinc-800/40 hover:bg-zinc-900/30 px-2 -mx-2 rounded-lg cursor-pointer transition-colors"
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex flex-col gap-1.5 overflow-hidden">
                  <h3 className="text-zinc-200 font-medium truncate pr-4 leading-snug">
                    {doc.title}
                  </h3>
                  <div className="flex items-center gap-3 text-xs text-zinc-500 font-mono">
                    <span className="truncate max-w-[200px] sm:max-w-[300px]">
                      {doc.url}
                    </span>
                    <span className="w-1 h-1 rounded-full bg-zinc-700"></span>
                    <span>
                      {new Date(doc.created_at).toLocaleDateString(undefined, { 
                        month: 'short', day: 'numeric', year: 'numeric' 
                      })}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={(e) => { e.stopPropagation(); setSelectedDoc(doc); }}
                    className="flex items-center gap-2 text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-zinc-800/50 hover:bg-zinc-700/50 px-3 py-1.5 rounded-md transition-colors"
                  >
                    <TextAa size={16} />
                    <span>View</span>
                  </button>
                  <button 
                    onClick={(e) => handleDownload(doc, e)}
                    className="flex items-center gap-2 text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-zinc-800/50 hover:bg-zinc-700/50 px-3 py-1.5 rounded-md transition-colors"
                  >
                    <DownloadSimple size={16} />
                    <span>TXT</span>
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <AnimatePresence>
        {selectedDoc && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-zinc-950/80 backdrop-blur-sm"
            onClick={() => setSelectedDoc(null)}
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0, y: 10 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 10 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800/60 bg-zinc-900/50">
                <h3 className="text-zinc-200 font-medium truncate pr-4">
                  {selectedDoc.title}
                </h3>
                <button 
                  onClick={() => setSelectedDoc(null)}
                  className="text-zinc-500 hover:text-zinc-200 transition-colors bg-transparent border-none p-1"
                >
                  <X size={20} />
                </button>
              </div>
              <div className="p-5 overflow-y-auto font-mono text-sm leading-relaxed text-zinc-400 bg-zinc-950/30">
                <pre className="whitespace-pre-wrap break-words">
                  {selectedDoc.content}
                </pre>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default DocumentList;
