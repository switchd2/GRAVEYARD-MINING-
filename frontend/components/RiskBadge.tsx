'use client';

import React from 'react';
import { AlertTriangle, AlertOctagon, Info, ShieldAlert } from 'lucide-react';

interface RiskBadgeProps {
  level: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function RiskBadge({ level, size = 'md' }: RiskBadgeProps) {
  const normalized = (level || 'MEDIUM').toUpperCase();

  const styles = {
    CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/30',
    HIGH: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    MEDIUM: 'bg-yellow-500/10 text-yellow-300 border-yellow-500/20',
    LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  }[normalized] || 'bg-gray-500/10 text-gray-400 border-gray-500/30';

  const icons = {
    CRITICAL: <AlertOctagon className="w-3.5 h-3.5 mr-1 text-red-400" />,
    HIGH: <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-400" />,
    MEDIUM: <ShieldAlert className="w-3.5 h-3.5 mr-1 text-yellow-300" />,
    LOW: <Info className="w-3.5 h-3.5 mr-1 text-emerald-400" />,
  }[normalized] || <Info className="w-3.5 h-3.5 mr-1 text-gray-400" />;

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  }[size];

  return (
    <span className={`inline-flex items-center font-mono font-semibold rounded-full border ${styles} ${sizeClasses}`}>
      {icons}
      {normalized} RISK
    </span>
  );
}
