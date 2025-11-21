import React, { useState } from 'react';

export default function FileUploader({ dbName, onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files.length || !dbName) return;
    setUploading(true);
    
    const formData = new FormData();
    formData.append('db_name', dbName);
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/api/files/upload`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        alert('Files uploaded successfully! Job added to queue.');
        onUploadComplete();
      } else {
        alert('Upload failed.');
      }
    } catch (error) {
      console.error(error);
      alert('Error uploading files.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 border rounded shadow bg-gray-50">
      <h3 className="font-bold mb-2">Upload Documents</h3>
      <input type="file" multiple onChange={handleFileChange} className="mb-4" />
      <button 
        onClick={handleUpload} 
        disabled={uploading || !dbName}
        className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
      >
        {uploading ? 'Uploading...' : 'Upload & Process'}
      </button>
    </div>
  );
}

