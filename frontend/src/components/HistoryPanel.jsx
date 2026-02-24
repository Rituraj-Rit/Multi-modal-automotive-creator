import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  History, 
  Loader2, 
  Trash2, 
  Search,
  Image as ImageIcon,
  FileText,
  ExternalLink,
  X
} from 'lucide-react';
import { getHistory, deleteHistoryItem, searchSimilar } from '../services/api';

function HistoryPanel() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await getHistory(20);
      if (response.success) {
        setHistory(response.history);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await deleteHistoryItem(id);
      setHistory(prev => prev.filter(item => item.id !== id));
      if (selectedItem?.id === id) {
        setSelectedItem(null);
      }
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    try {
      const response = await searchSimilar(searchQuery, 5);
      if (response.success) {
        setSearchResults(response.results);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Search Bar */}
      <div className="card mb-6">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Search your generations..."
              className="input-field pl-10"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={searching || !searchQuery.trim()}
            className="btn-secondary"
          >
            {searching ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
          </button>
        </div>
      </div>

      {/* Search Results */}
      <AnimatePresence>
        {searchResults && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Search Results</h3>
                <button
                  onClick={() => {
                    setSearchResults(null);
                    setSearchQuery('');
                  }}
                  className="text-dark-400 hover:text-dark-200"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              {searchResults.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {searchResults.map((result) => (
                    <div
                      key={result.id}
                      onClick={() => setSelectedItem(result.metadata)}
                      className="bg-dark-800 rounded-lg p-3 cursor-pointer hover:bg-dark-700 transition-colors"
                    >
                      {result.metadata?.image_url && (
                        <img
                          src={result.metadata.image_url}
                          alt="Result"
                          className="w-full h-32 object-cover rounded-lg mb-2"
                        />
                      )}
                      <p className="text-sm text-dark-300 line-clamp-2">
                        {result.metadata?.prompt || 'No prompt available'}
                      </p>
                      <p className="text-xs text-dark-500 mt-1">
                        Similarity: {((1 - (result.distance || 0)) * 100).toFixed(1)}%
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-dark-400">No similar results found</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* History Grid */}
      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-400 mb-4" />
          <p className="text-dark-400">Loading history...</p>
        </div>
      ) : history.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {history.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card cursor-pointer hover:border-primary-500/50 transition-colors group"
              onClick={() => setSelectedItem(item)}
            >
              {/* Image */}
              <div className="relative aspect-video bg-dark-800 rounded-lg mb-3 overflow-hidden">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.prompt}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <ImageIcon className="w-8 h-8 text-dark-600" />
                  </div>
                )}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <ExternalLink className="w-6 h-6 text-white" />
                </div>
              </div>
              
              {/* Info */}
              <div className="space-y-2">
                <p className="text-sm text-dark-200 line-clamp-2">{item.prompt}</p>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-dark-500">{formatDate(item.created_at)}</p>
                  <button
                    onClick={(e) => handleDelete(item.id, e)}
                    className="text-dark-500 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <History className="w-12 h-12 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-400">No generation history yet</p>
          <p className="text-dark-500 text-sm">Create your first automotive concept!</p>
        </div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedItem && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedItem(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-dark-800 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {selectedItem.image_url && (
                <img
                  src={selectedItem.image_url}
                  alt={selectedItem.prompt}
                  className="w-full h-auto rounded-t-xl"
                />
              )}
              <div className="p-6">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">Prompt</h3>
                    <p className="text-dark-300">{selectedItem.prompt}</p>
                  </div>
                  <button
                    onClick={() => setSelectedItem(null)}
                    className="text-dark-400 hover:text-dark-200"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                {selectedItem.narrative && (
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-primary-400" />
                      Narrative
                    </h3>
                    <div className="bg-dark-900 rounded-lg p-4 text-dark-200">
                      {selectedItem.narrative}
                    </div>
                  </div>
                )}
                
                <p className="text-sm text-dark-500">
                  Created: {formatDate(selectedItem.created_at)}
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default HistoryPanel;
