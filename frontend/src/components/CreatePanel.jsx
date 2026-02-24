import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Image as ImageIcon, 
  FileText, 
  Loader2, 
  Copy, 
  Check,
  Download,
  RefreshCw,
  Wand2
} from 'lucide-react';
import { generateBoth, generateNarrative, generateImage } from '../services/api';

function CreatePanel() {
  const [prompt, setPrompt] = useState('');
  const [mode, setMode] = useState('both'); // 'both', 'narrative', 'image'
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  // Image options
  const [imageSize, setImageSize] = useState('1024x1024');
  const [imageQuality, setImageQuality] = useState('standard');
  const [imageStyle, setImageStyle] = useState('vivid');

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      
      if (mode === 'both') {
        response = await generateBoth(prompt, {
          image_size: imageSize,
          image_quality: imageQuality,
          image_style: imageStyle,
        });
      } else if (mode === 'narrative') {
        response = await generateNarrative(prompt);
      } else if (mode === 'image') {
        response = await generateImage(prompt, {
          size: imageSize,
          quality: imageQuality,
          style: imageStyle,
        });
      }

      if (response.success) {
        setResult(response);
      } else {
        setError(response.error || 'Generation failed');
      }
    } catch (err) {
      setError(err.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setPrompt('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Mode Selection */}
      <div className="flex gap-4 mb-6">
        {[
          { id: 'both', label: 'Both', icon: Sparkles },
          { id: 'narrative', label: 'Narrative', icon: FileText },
          { id: 'image', label: 'Image', icon: ImageIcon },
        ].map((m) => {
          const Icon = m.icon;
          return (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                mode === m.id
                  ? 'bg-primary-500 text-white'
                  : 'bg-dark-800 text-dark-400 hover:bg-dark-700 hover:text-dark-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              {m.label}
            </button>
          );
        })}
      </div>

      {/* Input Section */}
      <div className="card mb-6">
        <label className="block text-sm font-medium text-dark-300 mb-2">
          Describe your automotive concept
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., A futuristic electric sports car with sleek aerodynamic lines, inspired by nature, featuring organic curves and sustainable materials..."
          className="input-field h-32 resize-none"
          disabled={loading}
        />

        {/* Image Options */}
        {mode !== 'narrative' && (
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Size</label>
              <select
                value={imageSize}
                onChange={(e) => setImageSize(e.target.value)}
                className="input-field"
                disabled={loading}
              >
                <option value="1024x1024">Square (1024×1024)</option>
                <option value="1024x1792">Portrait (1024×1792)</option>
                <option value="1792x1024">Landscape (1792×1024)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Quality</label>
              <select
                value={imageQuality}
                onChange={(e) => setImageQuality(e.target.value)}
                className="input-field"
                disabled={loading}
              >
                <option value="standard">Standard</option>
                <option value="hd">HD</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Style</label>
              <select
                value={imageStyle}
                onChange={(e) => setImageStyle(e.target.value)}
                className="input-field"
                disabled={loading}
              >
                <option value="vivid">Vivid</option>
                <option value="natural">Natural</option>
              </select>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            className="btn-primary flex items-center gap-2 flex-1 justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5" />
                Generate
              </>
            )}
          </button>
          <button
            onClick={handleReset}
            disabled={loading}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-5 h-5" />
            Reset
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-6 text-red-400"
        >
          {error}
        </motion.div>
      )}

      {/* Results Section */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Narrative Result */}
          {(mode === 'both' || mode === 'narrative') && result.narrative && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary-400" />
                  Generated Narrative
                </h3>
                <button
                  onClick={() => handleCopy(result.narrative)}
                  className="text-dark-400 hover:text-dark-200 transition-colors"
                >
                  {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                </button>
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 text-dark-200 whitespace-pre-wrap">
                {result.narrative}
              </div>
            </div>
          )}

          {/* Image Result */}
          {(mode === 'both' || mode === 'image') && result.image_url && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <ImageIcon className="w-5 h-5 text-primary-400" />
                  Generated Image
                </h3>
                <a
                  href={result.image_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-dark-400 hover:text-dark-200 transition-colors"
                >
                  <Download className="w-5 h-5" />
                </a>
              </div>
              <div className="relative rounded-lg overflow-hidden bg-dark-800">
                <img
                  src={result.image_url}
                  alt="Generated car design"
                  className="w-full h-auto"
                />
                {result.revised_prompt && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 p-3">
                    <p className="text-xs text-dark-300">
                      <span className="font-medium">Revised Prompt:</span> {result.revised_prompt}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card text-center py-12">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-dark-400">
            {mode === 'both' 
              ? 'Generating narrative and image...' 
              : mode === 'narrative' 
                ? 'Generating narrative...' 
                : 'Creating your car design...'}
          </p>
        </div>
      )}
    </div>
  );
}

export default CreatePanel;
