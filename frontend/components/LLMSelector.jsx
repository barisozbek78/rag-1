import React from 'react';

export default function LLMSelector({ selectedProvider, selectedModel, onChange }) {
  const providers = [
    { 
      id: 'openai', 
      name: 'OpenAI', 
      models: ['gpt-4', 'gpt-4o', 'gpt-3.5-turbo'] 
    },
    { 
      id: 'openrouter', 
      name: 'OpenRouter (Multi-Model)', 
      models: [
        'google/gemini-pro-1.5',
        'anthropic/claude-3-opus',
        'anthropic/claude-3-sonnet',
        'meta-llama/llama-3-70b-instruct',
        'mistralai/mixtral-8x22b-instruct',
        'x-ai/grok-1' // Example slug, check OpenRouter for exact slug if available
      ] 
    },
    { 
      id: 'ollama', 
      name: 'Ollama (Local)', 
      models: ['llama3', 'mistral', 'gemma'] 
    },
  ];

  const handleProviderChange = (e) => {
    const provider = e.target.value;
    const defaultModel = providers.find(p => p.id === provider).models[0];
    onChange(provider, defaultModel);
  };

  const handleModelChange = (e) => {
    onChange(selectedProvider, e.target.value);
  };

  const currentModels = providers.find(p => p.id === selectedProvider)?.models || [];

  return (
    <div className="flex gap-4">
      <div className="flex-1">
        <select 
          value={selectedProvider} 
          onChange={handleProviderChange} 
          className="w-full p-2 border rounded bg-gray-50 text-sm font-medium"
        >
          {providers.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>
      <div className="flex-1">
        <select 
          value={selectedModel} 
          onChange={handleModelChange} 
          className="w-full p-2 border rounded bg-gray-50 text-sm"
        >
          {currentModels.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>
    </div>
  );
}
