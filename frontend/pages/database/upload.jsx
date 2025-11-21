import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import DatabaseSelector from '../../components/DatabaseSelector';
import FileUploader from '../../components/FileUploader';

export default function UploadPage() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState('');

  useEffect(() => {
    const fetchDbs = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/db`);
        const data = await res.json();
        setDatabases(data || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchDbs();
  }, []);

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-4">Upload to Database</h2>
      <div className="max-w-xl mx-auto bg-white p-6 rounded shadow">
        <DatabaseSelector 
          databases={databases} 
          selectedDb={selectedDb} 
          onSelect={setSelectedDb} 
        />
        
        {selectedDb && (
          <div className="mt-6">
            <FileUploader 
              dbName={selectedDb} 
              onUploadComplete={() => alert('Files added to queue')} 
            />
          </div>
        )}
      </div>
    </Layout>
  );
}

