import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface APIKeyStatus {
  provider: string;
  masked_key: string;
  has_key: boolean;
  created_at: string | null;
}

const PROVIDERS = [
  { id: 'openai', name: 'OpenAI', placeholder: 'sk-...' },
  { id: 'anthropic', name: 'Anthropic', placeholder: 'sk-ant-...' },
  { id: 'google', name: 'Google', placeholder: 'AIza...' },
];

export const Settings = () => {
  const [keys, setKeys] = useState<APIKeyStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Record<string, string>>({});
  const [testing, setTesting] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState<Record<string, string>>({});

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAPIKeys();
      setKeys(data);
    } catch (error: any) {
      console.error('Failed to load API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (provider: string) => {
    const apiKey = editing[provider]?.trim();
    if (!apiKey) {
      setErrors({ ...errors, [provider]: 'API key cannot be empty' });
      return;
    }

    try {
      setErrors({ ...errors, [provider]: '' });
      setSuccess({ ...success, [provider]: '' });
      await apiService.saveAPIKey(provider, apiKey);
      setEditing({ ...editing, [provider]: '' });
      setSuccess({ ...success, [provider]: 'API key saved successfully!' });
      await loadKeys();
    } catch (error: any) {
      setErrors({ ...errors, [provider]: error.message || 'Failed to save API key' });
    }
  };

  const handleDelete = async (provider: string) => {
    if (!confirm(`Are you sure you want to delete the API key for ${provider}?`)) {
      return;
    }

    try {
      setErrors({ ...errors, [provider]: '' });
      await apiService.deleteAPIKey(provider);
      setSuccess({ ...success, [provider]: 'API key deleted successfully!' });
      await loadKeys();
    } catch (error: any) {
      setErrors({ ...errors, [provider]: error.message || 'Failed to delete API key' });
    }
  };

  const handleTest = async (provider: string) => {
    const keyStatus = keys.find(k => k.provider === provider);
    if (!keyStatus?.has_key) {
      setErrors({ ...errors, [provider]: 'No API key configured. Please save a key first.' });
      return;
    }

    try {
      setTesting({ ...testing, [provider]: true });
      setErrors({ ...errors, [provider]: '' });
      setSuccess({ ...success, [provider]: '' });
      const result = await apiService.testAPIKey(provider);
      setSuccess({ ...success, [provider]: result.message || 'API key is valid!' });
    } catch (error: any) {
      setErrors({ ...errors, [provider]: error.message || 'API key test failed' });
    } finally {
      setTesting({ ...testing, [provider]: false });
    }
  };

  const getProviderInfo = (providerId: string) => {
    return PROVIDERS.find(p => p.id === providerId) || { id: providerId, name: providerId, placeholder: 'Enter API key...' };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">LLM Aggregator</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-800">
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">API Key Settings</h2>
          <p className="text-sm text-gray-600 mb-6">
            Configure your API keys for each LLM provider. Keys are encrypted and stored securely.
          </p>

          <div className="space-y-6">
            {PROVIDERS.map((provider) => {
              const keyStatus = keys.find(k => k.provider === provider.id);
              const hasKey = keyStatus?.has_key || false;
              const isEditing = editing[provider.id] !== undefined;
              const providerInfo = getProviderInfo(provider.id);

              return (
                <div key={provider.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 capitalize">
                        {providerInfo.name}
                      </h3>
                      {hasKey && (
                        <p className="text-sm text-gray-500 mt-1">
                          Configured: {keyStatus?.masked_key || '****'}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      {hasKey && (
                        <>
                          <span className="text-green-600 text-sm">✓</span>
                          <button
                            onClick={() => handleTest(provider.id)}
                            disabled={testing[provider.id]}
                            className="px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded hover:bg-blue-100 disabled:opacity-50"
                          >
                            {testing[provider.id] ? 'Testing...' : 'Test'}
                          </button>
                          <button
                            onClick={() => handleDelete(provider.id)}
                            className="px-3 py-1 text-sm bg-red-50 text-red-600 rounded hover:bg-red-100"
                          >
                            Delete
                          </button>
                        </>
                      )}
                      {!hasKey && (
                        <span className="text-gray-400 text-sm">Not configured</span>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <input
                      type="password"
                      placeholder={providerInfo.placeholder}
                      value={isEditing ? editing[provider.id] : ''}
                      onChange={(e) =>
                        setEditing({ ...editing, [provider.id]: e.target.value })
                      }
                      onFocus={() => {
                        if (!isEditing) {
                          setEditing({ ...editing, [provider.id]: '' });
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSave(provider.id)}
                        disabled={!editing[provider.id]?.trim()}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {hasKey ? 'Update' : 'Save'}
                      </button>
                      {isEditing && (
                        <button
                          onClick={() => {
                            const newEditing = { ...editing };
                            delete newEditing[provider.id];
                            setEditing(newEditing);
                            setErrors({ ...errors, [provider.id]: '' });
                            setSuccess({ ...success, [provider.id]: '' });
                          }}
                          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                    {errors[provider.id] && (
                      <p className="text-sm text-red-600">{errors[provider.id]}</p>
                    )}
                    {success[provider.id] && (
                      <p className="text-sm text-green-600">{success[provider.id]}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
};

