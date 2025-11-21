import React from 'react';

export default function DatabaseSelector({ databases, selectedDb, onSelect }) {
  return (
    <div className="p-4">
      <label className="block text-sm font-bold mb-2">Select Database</label>
      <select 
        value={selectedDb} 
        onChange={(e) => onSelect(e.target.value)}
        className="w-full p-2 border rounded bg-white"
      >
        <option value="">-- Select DB --</option>
        {databases.map(db => (
          <option key={db} value={db}>{db}</option>
        ))}
      </select>
    </div>
  );
}

