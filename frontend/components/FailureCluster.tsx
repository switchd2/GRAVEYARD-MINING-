'use client';

import React from 'react';
import { Layers, ShieldAlert, GitBranch, Sparkles } from 'lucide-react';
import RiskBadge from './RiskBadge';

interface Cluster {
  id: number;
  cluster_name: string;
  description: string;
  repo_count: number;
  risk_level: string;
  affected_repos: string[];
}

export default function FailureCluster({ clusters }: { clusters: Cluster[] }) {
  if (!clusters || clusters.length === 0) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-gray-800 text-gray-400 text-sm">
        No failure clusters detected yet.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            <span>Failure Pattern Clusters</span>
          </h3>
          <p className="text-xs text-gray-400">
            Grouped from vector embeddings of discovered dead repository diagnoses using HDBSCAN.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clusters.map((cluster, idx) => (
          <div
            key={idx}
            className="glass-card p-5 rounded-2xl border border-gray-800 flex flex-col justify-between relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-purple-600/10 rounded-full blur-xl" />

            <div>
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-bold text-sm text-gray-100 pr-2 leading-tight">
                  {cluster.cluster_name}
                </h4>
                <RiskBadge level={cluster.risk_level} size="sm" />
              </div>

              <p className="text-xs text-gray-300 mb-4 leading-relaxed">
                {cluster.description}
              </p>
            </div>

            <div className="pt-3 border-t border-gray-800/80 flex items-center justify-between text-xs font-mono text-gray-400">
              <span className="flex items-center gap-1">
                <GitBranch className="w-3.5 h-3.5 text-indigo-400" />
                <span>{cluster.repo_count} Impacted Repos</span>
              </span>

              <div className="flex -space-x-1.5 overflow-hidden">
                {cluster.affected_repos.map((r, rIdx) => (
                  <span
                    key={rIdx}
                    title={r}
                    className="w-5 h-5 rounded-full bg-indigo-900/80 border border-indigo-500/40 text-[9px] font-bold text-indigo-300 flex items-center justify-center uppercase"
                  >
                    {r.charAt(0)}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
