import React, { useState, useRef, useEffect } from 'react';
import Layout from '../../components/Layout';
import DatabaseSelector from '../../components/DatabaseSelector';
import LLMSelector from '../../components/LLMSelector';

export default function ChatPage() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState('');
  const [provider, setProvider] = useState('openai');
  const [model, setModel] = useState('gpt-4');
  
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! Select a database and ask me anything about your documents.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchDbs = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/db`);
        setDatabases(await res.json());
      } catch (e) {}
    };
    fetchDbs();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedDb) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const assistantMsgId = Date.now();
    setMessages(prev => [...prev, { role: 'assistant', content: '', id: assistantMsgId }]);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/query/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          db_name: selectedDb,
          messages: [...messages, userMsg],
          llm_provider: provider,
          llm_model: model
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let assistantResponse = "";

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunkValue = decoder.decode(value);
        
        const lines = chunkValue.split('\n\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.replace('data: ', '');
                if (data === '[DONE]') break;
                
                // Handle newlines escaped in backend
                const cleanData = data.replace(/\\n/g, '\n');
                assistantResponse += cleanData;
                
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMsgId ? { ...msg, content: assistantResponse } : msg
                ));
            }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Could not reach backend.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100vh-100px)]">
        <div className="bg-white p-4 shadow flex gap-4 items-center z-10">
          <div className="w-1/3">
            <DatabaseSelector databases={databases} selectedDb={selectedDb} onSelect={setSelectedDb} />
          </div>
          <div className="flex-1">
             <LLMSelector selectedProvider={provider} selectedModel={model} onChange={(p, m) => {setProvider(p); setModel(m)}} />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-100">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none' 
                  : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
              }`}>
                {/* Content Render */}
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {loading && (
             <div className="flex justify-start">
                <div className="bg-white border p-3 rounded-2xl rounded-bl-none text-sm text-gray-500 flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                </div>
             </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-white border-t">
          <div className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={selectedDb ? "Ask about your documents..." : "Select a database to start chatting"}
              disabled={!selectedDb || loading}
              className="flex-1 p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-gray-50"
            />
            <button
              onClick={handleSend}
              disabled={!selectedDb || loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
