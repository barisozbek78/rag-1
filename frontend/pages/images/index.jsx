import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import DatabaseSelector from '../../components/DatabaseSelector';

export default function ImagesPage() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState('');
  const [images, setImages] = useState([]);

  useEffect(() => {
    // Fetch DBs
    const fetchDbs = async () => {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/api/db`);
      setDatabases(await res.json());
    };
    fetchDbs();
  }, []);

  useEffect(() => {
    if (selectedDb) {
      const fetchImages = async () => {
         const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
         const res = await fetch(`${API_URL}/api/images/${selectedDb}`);
         const data = await res.json();
         setImages(data.images || []);
      };
      fetchImages();
    }
  }, [selectedDb]);

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-4">Extracted Images</h2>
      <DatabaseSelector databases={databases} selectedDb={selectedDb} onSelect={setSelectedDb} />
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        {images.map(img => (
          <div key={img.id} className="border rounded p-2 bg-white">
            <img src={img.url} alt={img.name} className="w-full h-40 object-cover mb-2" />
            <p className="text-xs truncate">{img.name}</p>
          </div>
        ))}
      </div>
    </Layout>
  );
}

