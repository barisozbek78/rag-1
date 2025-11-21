import React from 'react';
import Link from 'next/link';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <nav className="bg-slate-800 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">RAG Admin Panel</h1>
          <div className="space-x-4">
            <Link href="/" className="hover:text-blue-300">Dashboard</Link>
            <Link href="/database/create" className="hover:text-blue-300">New DB</Link>
            <Link href="/database/upload" className="hover:text-blue-300">Upload</Link>
            <Link href="/query" className="hover:text-blue-300">Query</Link>
          </div>
        </div>
      </nav>
      <main className="container mx-auto p-4">
        {children}
      </main>
    </div>
  );
}

