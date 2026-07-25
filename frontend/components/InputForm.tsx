'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Layers, Search, Loader2, CheckCircle2, ArrowRight } from 'lucide-react';

const COMMON_STACKS = [
  'Next.js', 'React', 'FastAPI', 'Python', 'Node.js', 
  'PostgreSQL', 'Tailwind', 'Docker', 'OpenAI', 'Prisma', 
  'Redis', 'TypeScript', 'MongoDB', 'Flutter'
];

export default function InputForm() {
  const router = useRouter();
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedStack, setSelectedStack] = useState<string[]>(['Next.js', 'FastAPI', 'PostgreSQL']);
  const [customStackInput, setCustomStackInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stepText, setStepText] = useState('');

  const toggleStack = (tech: string) => {
    if (selectedStack.includes(tech)) {
      setSelectedStack(selectedStack.filter(s => s !== tech));
    } else {
      setSelectedStack([...selectedStack, tech]);
    }
  };

  const addCustomStack = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && customStackInput.trim()) {
      e.preventDefault();
      if (!selectedStack.includes(customStackInput.trim())) {
        setSelectedStack([...selectedStack, customStackInput.trim()]);
      }
      setCustomStackInput('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim() || !description.trim()) return;

    setIsLoading(true);
    setStepText('Mining GitHub for dead repositories...');

    try {
      setTimeout(() => setStepText('Diagnosing failure reasons via GPT-4o-mini...'), 3000);
      setTimeout(() => setStepText('Checking OSV, Snyk & Socket dependency health...'), 6000);
      setTimeout(() => setStepText('Clustering failure vectors & injecting risk annotations...'), 9000);

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName,
          description: description,
          tech_stack: selectedStack
        })
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      router.push(`/dashboard/${data.id}`);
    } catch (err) {
      console.error(err);
      alert('Error conducting analysis. Ensure FastAPI backend is running on http://localhost:8000');
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto glass-panel p-8 rounded-2xl border border-gray-800 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-600/10 rounded-full blur-3xl -z-10" />
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl -z-10" />

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-indigo-400" />
          <span>Mine Graveyard Signals</span>
        </h2>
        <p className="text-gray-400 text-sm mt-1">
          Input your project idea to discover dead open-source repos, diagnose failure causes, and build a risk-armored roadmap.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-xs font-mono font-medium text-gray-300 uppercase tracking-wider mb-2">
            Project Name
          </label>
          <input
            type="text"
            required
            placeholder="e.g. AI Resume Customizer"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            disabled={isLoading}
            className="w-full bg-gray-900/80 border border-gray-700/80 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-medium text-sm transition-all"
          />
        </div>

        <div>
          <label className="block text-xs font-mono font-medium text-gray-300 uppercase tracking-wider mb-2">
            Project Description & Architecture Goal
          </label>
          <textarea
            required
            rows={4}
            placeholder="Describe core functionality, key features, target users, and intended architecture..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isLoading}
            className="w-full bg-gray-900/80 border border-gray-700/80 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm transition-all"
          />
        </div>

        <div>
          <label className="block text-xs font-mono font-medium text-gray-300 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>Tech Stack Selection</span>
            <span className="text-[10px] text-indigo-400">Click to toggle or type custom tag + Enter</span>
          </label>
          
          <div className="flex flex-wrap gap-2 mb-3">
            {COMMON_STACKS.map((tech) => {
              const isSelected = selectedStack.includes(tech);
              return (
                <button
                  key={tech}
                  type="button"
                  onClick={() => toggleStack(tech)}
                  disabled={isLoading}
                  className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-all ${
                    isSelected
                      ? 'bg-indigo-600/30 text-indigo-300 border-indigo-500/60 shadow-sm shadow-indigo-500/20'
                      : 'bg-gray-900/50 text-gray-400 border-gray-800 hover:border-gray-700 hover:text-gray-200'
                  }`}
                >
                  {isSelected && <CheckCircle2 className="w-3.5 h-3.5 inline mr-1 text-indigo-400" />}
                  {tech}
                </button>
              );
            })}
          </div>

          <input
            type="text"
            placeholder="Add custom library or framework (press Enter)..."
            value={customStackInput}
            onChange={(e) => setCustomStackInput(e.target.value)}
            onKeyDown={addCustomStack}
            disabled={isLoading}
            className="w-full bg-gray-900/40 border border-gray-800 rounded-lg px-3 py-2 text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !projectName.trim() || !description.trim()}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-semibold text-sm hover:opacity-95 shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <div className="flex items-center space-x-3">
              <Loader2 className="w-5 h-5 animate-spin text-white" />
              <span className="font-mono text-xs text-indigo-100">{stepText}</span>
            </div>
          ) : (
            <>
              <span>Run Graveyard Mining Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
