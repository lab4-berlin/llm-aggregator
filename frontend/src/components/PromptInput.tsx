import { useState } from 'react';

interface PromptInputProps {
  onSubmit: (prompt: string, providers: string[]) => void;
  loading: boolean;
}

const PROVIDERS = ['openai', 'anthropic', 'google'];

export const PromptInput = ({ onSubmit, loading }: PromptInputProps) => {
  const [prompt, setPrompt] = useState('');
  const [selectedProviders, setSelectedProviders] = useState<string[]>(['openai']);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && selectedProviders.length > 0) {
      onSubmit(prompt, selectedProviders);
    }
  };

  const toggleProvider = (provider: string) => {
    setSelectedProviders((prev) =>
      prev.includes(provider)
        ? prev.filter((p) => p !== provider)
        : [...prev, provider]
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Enter your prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Type your prompt here..."
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select LLM Providers
          </label>
          <div className="flex flex-wrap gap-3">
            {PROVIDERS.map((provider) => (
              <label key={provider} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedProviders.includes(provider)}
                  onChange={() => toggleProvider(provider)}
                  disabled={loading}
                  className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700 capitalize">{provider}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !prompt.trim() || selectedProviders.length === 0}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Submit Prompt'}
        </button>
      </form>
    </div>
  );
};

