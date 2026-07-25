'use client';

import React from 'react';
import Link from 'next/link';
import { Skull, ShieldAlert, Cpu, Github, Sparkles } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-gray-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Skull className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-gradient tracking-tight">GRAVEYARD MINING</span>
            <span className="block text-[10px] text-gray-400 font-mono tracking-widest uppercase">Risk Intelligence Platform</span>
          </div>
        </Link>

        <div className="flex items-center space-x-6">
          <div className="hidden md:flex items-center space-x-4 text-xs font-mono text-gray-400">
            <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>7 APIs Active</span>
            </span>
            <span className="flex items-center space-x-1 text-gray-400">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>gpt-4o-mini</span>
            </span>
          </div>

          <a 
            href="https://github.com" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="flex items-center space-x-2 text-xs font-medium text-gray-300 hover:text-white px-3 py-1.5 rounded-lg bg-gray-800/60 hover:bg-gray-800 border border-gray-700/60 transition-colors"
          >
            <Github className="w-4 h-4" />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </header>
  );
}
