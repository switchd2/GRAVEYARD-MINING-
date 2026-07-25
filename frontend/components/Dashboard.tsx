'use client';

import React, { useState } from 'react';
import Navbar from './Navbar';
import GraveyardCard from './GraveyardCard';
import FailureCluster from './FailureCluster';
import DependencyHealth from './DependencyHealth';
import RoadmapView from './RoadmapView';
import { Skull, Layers, ShieldCheck, Map, ArrowLeft, RefreshCw, Cpu } from 'lucide-react';
import Link from 'next/link';

interface DashboardProps {
  data: any;
}

export default function Dashboard({ data }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<'graveyard' | 'clusters' | 'dependencies' | 'roadmap'>('roadmap');

  if (!data) return null;

  const repoCount = data.repositories?.length || 0;
  const clusterCount = data.failure_clusters?.length || 0;
  const depCount = data.dependency_reports?.length || 0;
  const phaseCount = data.roadmap?.phases?.length || 0;

  return (
    <div className="min-h-screen bg-[#090D16] text-gray-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Top Header */}
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <Link
              href="/"
              className="inline-flex items-center text-xs font-mono text-gray-400 hover:text-indigo-400 mb-2 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5 mr-1" />
              Analyze Another Project
            </Link>
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
              <span>{data.project_name}</span>
            </h1>
            <p className="text-sm text-gray-400 mt-1 max-w-2xl">
              {data.description}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {data.tech_stack?.map((tech: string, idx: number) => (
              <span
                key={idx}
                className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-indigo-950/60 text-indigo-300 border border-indigo-500/30"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>

        {/* Telemetry Quick Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass-card p-4 rounded-xl border border-gray-800 flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
              <Skull className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-xl font-bold text-white font-mono">{repoCount}</span>
              <span className="text-xs text-gray-400">Dead Repos Mined</span>
            </div>
          </div>

          <div className="glass-card p-4 rounded-xl border border-gray-800 flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-xl font-bold text-white font-mono">{clusterCount}</span>
              <span className="text-xs text-gray-400">Failure Clusters</span>
            </div>
          </div>

          <div className="glass-card p-4 rounded-xl border border-gray-800 flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-xl font-bold text-white font-mono">{depCount}</span>
              <span className="text-xs text-gray-400">Dependencies Audited</span>
            </div>
          </div>

          <div className="glass-card p-4 rounded-xl border border-gray-800 flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Map className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-xl font-bold text-white font-mono">{phaseCount}</span>
              <span className="text-xs text-gray-400">Annotated Phases</span>
            </div>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-gray-800 space-x-2">
          {[
            { id: 'roadmap', label: 'Risk-Annotated Roadmap', icon: Map, count: phaseCount },
            { id: 'graveyard', label: 'Discovered Dead Repos', icon: Skull, count: repoCount },
            { id: 'clusters', label: 'Failure Pattern Clusters', icon: Layers, count: clusterCount },
            { id: 'dependencies', label: 'Dependency Health', icon: ShieldCheck, count: depCount },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`pb-3 px-4 font-semibold text-xs sm:text-sm flex items-center space-x-2 border-b-2 transition-all ${
                  isActive
                    ? 'border-indigo-500 text-indigo-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                <span className="ml-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-gray-800 text-gray-300">
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Main Tab Content */}
        <div className="pt-2">
          {activeTab === 'roadmap' && (
            <RoadmapView phases={data.roadmap?.phases || []} />
          )}

          {activeTab === 'graveyard' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Skull className="w-5 h-5 text-red-400" />
                  <span>Discovered Inactive/Abandoned Repositories</span>
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.repositories?.map((repo: any) => (
                  <GraveyardCard key={repo.id} repo={repo} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'clusters' && (
            <FailureCluster clusters={data.failure_clusters || []} />
          )}

          {activeTab === 'dependencies' && (
            <DependencyHealth reports={data.dependency_reports || []} />
          )}
        </div>
      </main>
    </div>
  );
}
