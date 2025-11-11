import { useState } from 'react';

interface Response {
  provider: string;
  text: string;
  done: boolean;
}

interface ResultsTabsProps {
  responses: Record<string, Response>;
  loading: boolean;
}

export const ResultsTabs = ({ responses, loading }: ResultsTabsProps) => {
  const [activeTab, setActiveTab] = useState<string | null>(null);

  const providers = Object.keys(responses);
  if (providers.length === 0 && !loading) {
    return null;
  }

  if (providers.length > 0 && !activeTab) {
    setActiveTab(providers[0]);
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px">
          {providers.map((provider) => (
            <button
              key={provider}
              onClick={() => setActiveTab(provider)}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === provider
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="capitalize">{provider}</span>
              {responses[provider]?.done && (
                <span className="ml-2 text-green-500">✓</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {activeTab && responses[activeTab] && (
          <div className="space-y-4">
            <div className="text-sm text-gray-500">
              Provider: <span className="font-medium capitalize">{activeTab}</span>
            </div>
            <div className="bg-gray-50 rounded-md p-4 min-h-[200px]">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {responses[activeTab].text || 'Waiting for response...'}
              </pre>
            </div>
            {responses[activeTab].done && (
              <div className="text-sm text-green-600">Response complete</div>
            )}
          </div>
        )}
        {loading && providers.length === 0 && (
          <div className="text-center py-8 text-gray-500">Waiting for responses...</div>
        )}
      </div>
    </div>
  );
};

