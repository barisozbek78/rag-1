import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

export default function Dashboard() {
  const [queue, setQueue] = useState([]);

  useEffect(() => {
    // Poll queue status
    const fetchQueue = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/queue`);
        const data = await res.json();
        setQueue(data.jobs || []);
      } catch (e) {
        console.error(e);
      }
    };
    
    fetchQueue();
    const interval = setInterval(fetchQueue, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-4">System Status</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-xl font-bold mb-4">Worker Queue</h3>
          {queue.length === 0 ? (
            <p className="text-gray-500">No active jobs.</p>
          ) : (
            <ul className="space-y-2">
              {queue.map(job => (
                <li key={job.id} className="border p-2 rounded flex justify-between">
                  <span>{job.db}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100'
                  }`}>
                    {job.status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
          <div className="flex flex-col gap-2">
            <a href="/database/create" className="text-blue-600 hover:underline">Create New Database</a>
            <a href="/database/upload" className="text-blue-600 hover:underline">Upload Files</a>
            <a href="/query" className="text-blue-600 hover:underline">Query System</a>
          </div>
        </div>
      </div>
    </Layout>
  );
}

