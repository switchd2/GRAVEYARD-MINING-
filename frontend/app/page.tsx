'use client';

import React from 'react';
import Navbar from '../components/Navbar';
import InputForm from '../components/InputForm';
import { Skull, ShieldAlert, Cpu, Sparkles, GitBranch, ArrowRight, Activity, Layers } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#090D16] text-gray-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto space-y-4 pt-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Risk Intelligence for Open-Source Architecture</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Stop Re-Inventing <br />
            <span className="text-gradient">Failed Architecture</span>
          </h1>

          <p className="text-gray-400 text-sm sm:text-base leading-relaxed">
            Graveyard Mining searches thousands of abandoned GitHub repositories, diagnoses why they failed using GPT-4o-mini, audits your dependency security via OSV & Snyk, and annotates your roadmap with evidence-based risk checkpoints.
          </p>
        </div>

        {/* Input Form */}
        <InputForm />

        {/* Value Proposition Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
          <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 text-red-400 flex items-center justify-center border border-red-500/20">
              <Skull className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Dead Repo Discovery</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Mines GitHub REST API to find dead or unmaintained projects matching your tech stack & architecture goals.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Vector Failure Clustering</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Generates text-embedding-3-small vectors of LLM failure diagnoses and clusters them using HDBSCAN into common pattern warnings.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Risk-Armored Roadmap</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Injects proactive risk checkpoints into a 5-phase project execution roadmap before writing a single line of code.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t border-gray-900 py-6 text-center text-xs font-mono text-gray-600">
        Graveyard Mining — Evidence-Based Project Risk Intelligence
      </footer>
    </div>
  );
}
