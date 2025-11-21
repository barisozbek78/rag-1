import React, { useState } from 'react';
import Layout from '../../components/Layout';
import { useRouter } from 'next/router';

export default function CreateDBPage() {
  const [name, setName] = useState('');
  const router = useRouter();

  const handleCreate = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/api/db/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      if (res.ok) {
        router.push('/database/upload');
      } else {
        alert('Failed to create DB');
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-4">Create New Database</h2>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <label className="block mb-2">Database Name</label>
        <input 
          type="text" 
          value={name} 
          onChange={(e) => setName(e.target.value)}
          className="w-full border p-2 rounded mb-4"
          placeholder="Project_Alpha"
        />
        <button 
          onClick={handleCreate}
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
        >
          Create Database
        </button>
      </div>
    </Layout>
  );
}

