'use client';

import React, { useState } from 'react';
import { Map, ShieldAlert, CheckCircle2, Clock, ChevronDown, ChevronUp, AlertTriangle, ArrowDown } from 'lucide-react';
import RiskBadge from './RiskBadge';

interface RiskCheckpoint {
  title: string;
  risk_level: string;
  warning: string;
  prevention_strategy: string;
  evidence_repos: string[];
}

interface RoadmapPhase {
  phase_number: number;
  title: string;
  description: string;
  estimated_duration: string;
  key_deliverables: string[];
  risk_checkpoints: RiskCheckpoint[];
}

export default function RoadmapView({ phases }: { phases: RoadmapPhase[] }) {
  const [expandedPhase, setExpandedPhase] = useState<number | null>(1);

  if (!phases || phases.length === 0) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-gray-800 text-gray-400 text-sm">
        No roadmap generated.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Map className="w-5 h-5 text-indigo-400" />
            <span>Risk-Annotated Execution Roadmap</span>
          </h3>
          <p className="text-xs text-gray-400">
            5-Phase development sequence with proactive risk checkpoints derived from dead repo failure analysis.
          </p>
        </div>
      </div>

      <div className="relative border-l-2 border-indigo-500/30 ml-4 pl-6 space-y-8">
        {phases.map((phase) => {
          const isExpanded = expandedPhase === phase.phase_number;

          return (
            <div key={phase.phase_number} className="relative group">
              {/* Phase Number Node Marker */}
              <div className="absolute -left-[35px] top-1 w-8 h-8 rounded-full bg-indigo-600 text-white font-mono font-bold text-xs flex items-center justify-center border-4 border-[#090D16] shadow-lg shadow-indigo-500/30">
                {phase.phase_number}
              </div>

              <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
                {/* Header */}
                <button
                  onClick={() => setExpandedPhase(isExpanded ? null : phase.phase_number)}
                  className="w-full p-5 text-left flex items-start justify-between bg-gray-900/40 hover:bg-gray-900/80 transition-colors"
                >
                  <div>
                    <div className="flex items-center space-x-3 mb-1">
                      <span className="font-mono text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                        PHASE 0{phase.phase_number}
                      </span>
                      <span className="text-xs text-gray-500 flex items-center gap-1 font-mono">
                        <Clock className="w-3.5 h-3.5" />
                        {phase.estimated_duration}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-gray-100">
                      {phase.title}
                    </h4>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-gray-400 font-mono hidden sm:inline">
                      {phase.risk_checkpoints.length} Risk Alert{phase.risk_checkpoints.length > 1 ? 's' : ''}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </button>

                {/* Body Content */}
                {isExpanded && (
                  <div className="p-6 border-t border-gray-800/80 space-y-6">
                    <p className="text-sm text-gray-300 leading-relaxed">
                      {phase.description}
                    </p>

                    {/* Deliverables */}
                    <div>
                      <h5 className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2 font-semibold">
                        Key Phase Deliverables:
                      </h5>
                      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {phase.key_deliverables.map((del, idx) => (
                          <li key={idx} className="text-xs text-gray-200 flex items-center space-x-2 bg-gray-950/40 p-2.5 rounded-xl border border-gray-800">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                            <span>{del}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Risk Checkpoints (The Core Graveyard Innovation!) */}
                    <div>
                      <h5 className="text-xs font-mono text-amber-400 uppercase tracking-wider mb-3 font-semibold flex items-center gap-1.5">
                        <ShieldAlert className="w-4 h-4 text-amber-400" />
                        <span>Proactive Graveyard Risk Checkpoints:</span>
                      </h5>

                      <div className="space-y-3">
                        {phase.risk_checkpoints.map((risk, rIdx) => (
                          <div
                            key={rIdx}
                            className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-2 relative"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-xs text-amber-300 flex items-center gap-1.5">
                                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                                {risk.title}
                              </span>
                              <RiskBadge level={risk.risk_level} size="sm" />
                            </div>

                            <p className="text-xs text-gray-300 leading-relaxed">
                              <strong className="text-red-300">Failure Warning: </strong>
                              {risk.warning}
                            </p>

                            <div className="pt-2 border-t border-amber-500/10 text-xs">
                              <span className="font-mono text-emerald-400 font-semibold block mb-1">
                                Preventive Strategy:
                              </span>
                              <span className="text-gray-300 block">{risk.prevention_strategy}</span>
                            </div>

                            {risk.evidence_repos && risk.evidence_repos.length > 0 && (
                              <div className="pt-1 text-[11px] font-mono text-gray-400 flex items-center gap-2">
                                <span>Evidence Repos:</span>
                                <div className="flex gap-1">
                                  {risk.evidence_repos.map((repoName, eIdx) => (
                                    <span key={eIdx} className="px-2 py-0.5 rounded bg-gray-900 text-indigo-300 border border-gray-800">
                                      {repoName}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
