'use client';

import React from 'react';
import { ExternalLink, Star, GitFork, AlertCircle, Clock, Skull, CheckCircle2 } from 'lucide-react';
import RiskBadge from './RiskBadge';

interface Diagnosis {
  root_cause: string;
  failure_category: string;
  technical_debt_level: string;
  summary: string;
  key_takeaways: string[];
  tavily_context?: string;
}

interface Repository {
  id: number;
  name: string;
  full_name: string;
  html_url: string;
  description: string;
  stars: number;
  forks: number;
  open_issues: number;
  last_commit_date: string;
  abandonment_score: number;
  is_abandoned: boolean;
  language: string;
  diagnosis?: Diagnosis;
}

export default function GraveyardCard({ repo }: { repo: Repository }) {
  const score = repo.abandonment_score || 0;
  const scoreColor = score > 60 ? 'text-red-400 bg-red-500/10 border-red-500/30' : score > 30 ? 'text-amber-400 bg-amber-500/10 border-amber-500/30' : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';

  return (
    <div className="glass-card p-6 rounded-2xl border border-gray-800 flex flex-col justify-between relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-red-600/5 rounded-full blur-2xl group-hover:bg-indigo-600/10 transition-colors" />

      <div>
        <div className="flex items-start justify-between mb-3">
          <div>
            <a
              href={repo.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-base font-bold text-gray-100 hover:text-indigo-400 transition-colors flex items-center gap-1.5"
            >
              <Skull className="w-4 h-4 text-gray-400 group-hover:text-indigo-400" />
              <span>{repo.full_name}</span>
              <ExternalLink className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
            </a>
            <p className="text-xs text-gray-400 line-clamp-2 mt-1">
              {repo.description || 'No description provided.'}
            </p>
          </div>

          <div className={`px-2.5 py-1 rounded-full border text-xs font-mono font-bold flex items-center space-x-1 ${scoreColor}`}>
            <span>SCORE: {score}/100</span>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono text-gray-400 mb-4 pb-3 border-b border-gray-800/80">
          <span className="flex items-center space-x-1">
            <Star className="w-3.5 h-3.5 text-yellow-500" />
            <span>{repo.stars}</span>
          </span>
          <span className="flex items-center space-x-1">
            <GitFork className="w-3.5 h-3.5 text-blue-400" />
            <span>{repo.forks}</span>
          </span>
          <span className="flex items-center space-x-1">
            <AlertCircle className="w-3.5 h-3.5 text-red-400" />
            <span>{repo.open_issues} issues</span>
          </span>
          {repo.last_commit_date && (
            <span className="flex items-center space-x-1 text-gray-500">
              <Clock className="w-3.5 h-3.5" />
              <span>{new Date(repo.last_commit_date).toLocaleDateString()}</span>
            </span>
          )}
        </div>

        {repo.diagnosis && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-indigo-400 uppercase tracking-wider font-semibold">
                Failure Category: {repo.diagnosis.failure_category}
              </span>
              <RiskBadge level={repo.diagnosis.technical_debt_level} size="sm" />
            </div>

            <div className="p-3 rounded-xl bg-gray-950/60 border border-gray-800 text-xs">
              <p className="font-semibold text-gray-200 mb-1">
                Root Cause: <span className="font-normal text-gray-300">{repo.diagnosis.root_cause}</span>
              </p>
              <p className="text-gray-400 text-xs leading-relaxed mt-1">
                {repo.diagnosis.summary}
              </p>
            </div>

            {repo.diagnosis.key_takeaways && repo.diagnosis.key_takeaways.length > 0 && (
              <div className="mt-2">
                <span className="text-[11px] font-mono text-gray-400 uppercase block mb-1.5">Key Avoidance Takeaways:</span>
                <ul className="space-y-1">
                  {repo.diagnosis.key_takeaways.map((t, idx) => (
                    <li key={idx} className="text-xs text-gray-300 flex items-start space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                      <span>{t}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
