import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/auth/Login';
import { Register } from './components/auth/Register';
import { VerifyEmail } from './components/auth/VerifyEmail';
import { ForgotPassword } from './components/auth/ForgotPassword';
import { ResetPassword } from './components/auth/ResetPassword';
import { ResendVerification } from './components/auth/ResendVerification';
import { PromptInput } from './components/PromptInput';
import { ResultsTabs } from './components/ResultsTabs';
import { Settings } from './components/Settings';
import { apiService } from './services/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [responses, setResponses] = useState<Record<string, { provider: string; text: string; done: boolean }>>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (prompt: string, providers: string[]) => {
    setLoading(true);
    setResponses({});
    console.log('Starting prompt submission:', { prompt, providers });
    
    try {
      await apiService.createPromptSSE(
        prompt,
        providers,
        (data) => {
          console.log('Callback received data:', data);
          if (data.type === 'chunk') {
            // Append chunk to existing response text
            console.log('Received chunk for provider:', data.provider);
            setResponses((prev) => {
              const existing = prev[data.provider];
              return {
                ...prev,
                [data.provider]: {
                  provider: data.provider,
                  text: (existing?.text || '') + (data.text || ''),
                  done: false,
                },
              };
            });
          } else if (data.type === 'response') {
            // Final response message (complete)
            console.log('Updating final response for provider:', data.provider);
            setResponses((prev) => {
              const updated = {
                ...prev,
                [data.provider]: {
                  provider: data.provider,
                  text: data.text || prev[data.provider]?.text || '',
                  done: data.done || false,
                },
              };
              console.log('Updated responses:', updated);
              return updated;
            });
          } else if (data.type === 'error') {
            console.error('Error from provider:', data.provider, data.message);
            setResponses((prev) => {
              return {
                ...prev,
                [data.provider]: {
                  provider: data.provider,
                  text: `Error: ${data.message || 'Unknown error'}`,
                  done: true,
                },
              };
            });
          } else if (data.type === 'complete') {
            console.log('Stream complete, setting loading to false');
            setLoading(false);
          }
        },
        (error) => {
          console.error('Error in SSE stream:', error);
          setLoading(false);
        },
        () => {
          console.log('SSE stream onComplete called');
          setLoading(false);
        }
      );
    } catch (error) {
      console.error('Error submitting prompt:', error);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">LLM Aggregator</h1>
            </div>
            <div className="flex items-center space-x-4">
              {user && (
                <div className="flex items-center space-x-3">
                  <Link to="/settings" className="text-sm text-gray-700 hover:text-gray-900">
                    Settings
                  </Link>
                  <span className="text-sm text-gray-700">{user.name || user.email}</span>
                  <button
                    onClick={logout}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          <PromptInput onSubmit={handleSubmit} loading={loading} />
          {Object.keys(responses).length > 0 ? (
            <ResultsTabs responses={responses} loading={loading} />
          ) : (
            loading && <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">Waiting for responses...</div>
          )}
        </div>
      </main>
    </div>
  );
};

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/resend-verification" element={<ResendVerification />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
