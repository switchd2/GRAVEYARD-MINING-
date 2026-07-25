'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Dashboard from '../../../components/Dashboard';
import { Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const params = useParams();
  const id = params?.id;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    fetch(`${API_URL}/api/analysis/${id}`)
      .then(res => {
        if (!res.ok) throw new Error('Analysis not found');
        return res.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to fetch analysis details.');
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090D16] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
        <span className="font-mono text-xs text-gray-400">Loading analysis telemetry...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#090D16] flex flex-col items-center justify-center p-4">
        <div className="glass-card p-6 rounded-2xl border border-gray-800 text-center max-w-md space-y-4">
          <AlertCircle className="w-8 h-8 text-red-400 mx-auto" />
          <h2 className="text-lg font-bold text-white">Analysis Not Found</h2>
          <p className="text-xs text-gray-400">{error || 'Could not load analysis details.'}</p>
          <Link
            href="/"
            className="inline-block px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-xs hover:bg-indigo-500 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return <Dashboard data={data} />;
}
