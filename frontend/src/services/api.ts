const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface User {
  id: string;
  email: string;
  name: string | null;
}

export interface PromptResponse {
  id: string;
  prompt_text: string;
  created_at: string;
  responses?: LLMResponse[];
}

export interface LLMResponse {
  id: string;
  provider: string;
  model_used?: string;
  response_text?: string;
  response_time_ms?: number;
  error_message?: string;
  created_at: string;
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }


  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get user');
    return response.json();
  }

  async logout(): Promise<void> {
    await fetch(`${API_URL}/api/auth/logout`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    localStorage.removeItem('token');
  }

  async createPrompt(prompt: string, providers: string[]): Promise<EventSource> {
    const token = localStorage.getItem('token');
    const eventSource = new EventSource(
      `${API_URL}/api/prompts?prompt=${encodeURIComponent(prompt)}&providers=${providers.join(',')}`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      } as any
    );
    return eventSource;
  }

  async createPromptSSE(
    prompt: string,
    providers: string[],
    onMessage: (data: any) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    // Use fetch with ReadableStream for SSE (supports POST and custom headers)
    console.log('Sending prompt request:', { prompt, providers });
    const response = await fetch(`${API_URL}/api/prompts`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ prompt, providers }),
    });

    console.log('Response status:', response.status, response.statusText);
    if (!response.ok) {
      const error = new Error('Failed to create prompt');
      onError?.(error);
      throw error;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      const error = new Error('No response body');
      onError?.(error);
      throw error;
    }

    console.log('Starting to read SSE stream...');
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        console.log('Read chunk:', { done, hasValue: !!value, valueLength: value?.length });
        
        if (done) {
          console.log('Stream ended');
          break;
        }

        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          console.log('Decoded chunk:', chunk);
          console.log('Buffer before adding chunk:', buffer);
          buffer += chunk;
          console.log('Buffer after adding chunk (length:', buffer.length, '):', buffer);
          console.log('Looking for \\n\\n, indexOf result:', buffer.indexOf('\n\n'));
          
          // SSE format: "event: message\ndata: {...}\n\n"
          // Process complete messages (ending with \n\n or \r\n\r\n)
          let processedCount = 0;
          let messageEnd;
          // Try both \n\n and \r\n\r\n
          while ((messageEnd = buffer.indexOf('\n\n')) !== -1 || (messageEnd = buffer.indexOf('\r\n\r\n')) !== -1) {
            processedCount++;
            console.log(`Found message #${processedCount} at index ${messageEnd}`);
            const message = buffer.substring(0, messageEnd);
            buffer = buffer.substring(messageEnd + 2);
            console.log('Extracted message:', message);
            console.log('Remaining buffer:', buffer);
            
            if (!message.trim()) {
              console.log('Skipping empty message');
              continue;
            }
            
            console.log('Processing SSE message:', message);
            const lines = message.split('\n');
            let dataStr = '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                dataStr = line.slice(6).trim();
              }
            }

            console.log('Extracted dataStr:', dataStr);
            if (dataStr) {
              try {
                const data = JSON.parse(dataStr);
                console.log('SSE data received and calling onMessage:', data);
                onMessage(data);
                
                if (data.type === 'complete') {
                  console.log('SSE stream complete');
                  onComplete?.();
                } else if (data.type === 'error') {
                  console.error('SSE error:', data.message);
                  onError?.(new Error(data.message || 'Unknown error'));
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e, 'Raw data:', dataStr);
              }
            } else {
              console.warn('No data found in message');
            }
          }
          console.log('Processed', processedCount, 'messages in this chunk');
          console.log('Buffer after processing:', buffer);
        }
      }
      
      // Process any remaining data in buffer after stream ends
      if (buffer.trim()) {
        console.log('Processing remaining buffer after stream end:', buffer);
        // Split by double newline (try both \n\n and \r\n\r\n)
        const messages = buffer.split(/\n\n|\r\n\r\n/);
        console.log('Split into', messages.length, 'messages');
        for (let i = 0; i < messages.length; i++) {
          const message = messages[i];
          if (!message.trim()) {
            console.log(`Skipping empty message ${i}`);
            continue;
          }
          
          console.log(`Processing message ${i}:`, message);
          const lines = message.split(/\n|\r\n/);
          let dataStr = '';
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              dataStr = line.slice(6).trim();
            }
          }
          console.log(`Extracted dataStr from message ${i}:`, dataStr);
          if (dataStr) {
            try {
              const data = JSON.parse(dataStr);
              console.log(`SSE data from remaining buffer message ${i}:`, data);
              onMessage(data);
              if (data.type === 'complete') {
                onComplete?.();
              }
            } catch (e) {
              console.error(`Failed to parse remaining buffer message ${i}:`, e, 'Data:', dataStr);
            }
          } else {
            console.warn(`No data found in message ${i}`);
          }
        }
      }
    } catch (error) {
      console.error('Error reading SSE stream:', error);
      onError?.(error as Error);
      throw error;
    }
  }

  async getPrompt(promptId: string): Promise<PromptResponse> {
    const response = await fetch(`${API_URL}/api/prompts/${promptId}`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get prompt');
    return response.json();
  }

  async getPrompts(page: number = 1, limit: number = 20): Promise<{
    prompts: PromptResponse[];
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await fetch(`${API_URL}/api/prompts?page=${page}&limit=${limit}`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get prompts');
    return response.json();
  }

  // API Key Management
  async getAPIKeys(): Promise<Array<{
    provider: string;
    masked_key: string;
    has_key: boolean;
    created_at: string | null;
  }>> {
    const response = await fetch(`${API_URL}/api/keys`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get API keys');
    return response.json();
  }

  async saveAPIKey(provider: string, apiKey: string): Promise<{ message: string }> {
    const response = await fetch(`${API_URL}/api/keys`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save API key');
    }
    return response.json();
  }

  async deleteAPIKey(provider: string): Promise<{ message: string }> {
    const response = await fetch(`${API_URL}/api/keys/${provider}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete API key');
    }
    return response.json();
  }

  async testAPIKey(provider: string): Promise<{ valid: boolean; message: string }> {
    const response = await fetch(`${API_URL}/api/keys/${provider}/test`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to test API key');
    }
    return response.json();
  }
}

export const apiService = new ApiService();

