import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Save, 
  Loader2, 
  Check, 
  AlertCircle,
  Info,
  ExternalLink,
  Key
} from 'lucide-react';
import { healthCheck } from '../services/api';

function SettingsPanel() {
  const [apiKey, setApiKey] = useState('');
  const [saved, setSaved] = useState(false);
  const [checking, setChecking] = useState(false);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load API key from localStorage
    const storedKey = localStorage.getItem('openai_api_key');
    if (storedKey) {
      setApiKey(storedKey);
    }
    checkHealth();
  }, []);

  const checkHealth = async () => {
    setChecking(true);
    try {
      const data = await healthCheck();
      setHealth(data);
    } catch (err) {
      setError('Could not connect to API');
    } finally {
      setChecking(false);
    }
  };

  const handleSave = () => {
    if (apiKey.trim()) {
      localStorage.setItem('openai_api_key', apiKey.trim());
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      checkHealth();
    }
  };

  const handleClear = () => {
    localStorage.removeItem('openai_api_key');
    setApiKey('');
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* API Configuration */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <Key className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">API Configuration</h3>
            <p className="text-sm text-dark-400">Configure your OpenAI API key</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              OpenAI API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              className="input-field"
            />
            <p className="text-xs text-dark-500 mt-2">
              Get your API key from{' '}
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-400 hover:text-primary-300 inline-flex items-center gap-1"
              >
                OpenAI Platform <ExternalLink className="w-3 h-3" />
              </a>
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleSave}
              disabled={!apiKey.trim()}
              className="btn-primary flex items-center gap-2"
            >
              {saved ? (
                <>
                  <Check className="w-5 h-5" />
                  Saved!
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Key
                </>
              )}
            </button>
            <button
              onClick={handleClear}
              disabled={!apiKey}
              className="btn-secondary"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Connection Status */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Connection Status</h3>
          <button
            onClick={checkHealth}
            disabled={checking}
            className="text-sm text-primary-400 hover:text-primary-300"
          >
            {checking ? 'Checking...' : 'Check again'}
          </button>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-dark-700">
            <span className="text-dark-400">API Status</span>
            <span className={`flex items-center gap-2 ${
              health?.status === 'healthy' ? 'text-green-400' : 'text-red-400'
            }`}>
              {health?.status === 'healthy' ? (
                <>
                  <Check className="w-4 h-4" /> Connected
                </>
              ) : (
                <>
                  <AlertCircle className="w-4 h-4" /> Not Connected
                </>
              )}
            </span>
          </div>
          
          <div className="flex items-center justify-between py-2 border-b border-dark-700">
            <span className="text-dark-400">OpenAI</span>
            <span className="text-dark-300">
              {health?.services?.openai === 'configured' ? 'Configured' : 'Not configured'}
            </span>
          </div>
          
          <div className="flex items-center justify-between py-2 border-b border-dark-700">
            <span className="text-dark-400">ChromaDB</span>
            <span className="text-dark-300">
              {health?.services?.chromadb || 'Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
            <Info className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">About</h3>
            <p className="text-sm text-dark-400">Multimodal Automotive Creator</p>
          </div>
        </div>

        <div className="text-dark-300 space-y-2">
          <p>
            A multimodal GenAI application for Automotive concept visualization that integrates 
            LLMs with Image Generation models to translate textual prompts into both descriptive 
            narratives and high-fidelity visual representations.
          </p>
          
          <div className="mt-4 p-3 bg-dark-800 rounded-lg">
            <h4 className="font-medium text-white mb-2">Features</h4>
            <ul className="text-sm text-dark-400 space-y-1">
              <li>• Generate automotive descriptions with GPT-4</li>
              <li>• Create car designs with DALL-E 3</li>
              <li>• Chat with an automotive AI assistant</li>
              <li>• Store and search generation history</li>
            </ul>
          </div>
          
          <div className="mt-4 p-3 bg-dark-800 rounded-lg">
            <h4 className="font-medium text-white mb-2">Tech Stack</h4>
            <ul className="text-sm text-dark-400 space-y-1">
              <li>• Backend: FastAPI (Python)</li>
              <li>• Frontend: React + Vite</li>
              <li>• LLM: OpenAI GPT-4</li>
              <li>• Image Gen: DALL-E 3</li>
              <li>• Vector DB: ChromaDB</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-400"
        >
          {error}
        </motion.div>
      )}
    </div>
  );
}

export default SettingsPanel;
