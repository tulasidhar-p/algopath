import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Code, Laptop, BarChart2, Brain, Lock } from 'lucide-react';

const DomainSelection: React.FC = () => {
  const navigate = useNavigate();

  const tracks = [
    {
      title: 'Data Structures & Algorithms',
      slug: 'dsa',
      description: 'Master coding patterns, complexity analysis, and clean implementation from Arrays to Dynamic Programming.',
      icon: <Code className="w-8 h-8 text-indigo-400" />,
      active: true,
      tag: 'Core Track',
      gradient: 'from-indigo-600/20 via-purple-600/5 to-transparent',
      borderColor: 'border-indigo-500/30 hover:border-indigo-500/60',
      glowColor: 'shadow-indigo-500/10'
    },
    {
      title: 'Web Development',
      slug: 'webdev',
      description: 'Build fullstack applications using React, Node.js, and modern system architectures.',
      icon: <Laptop className="w-8 h-8 text-slate-500" />,
      active: false,
      tag: 'Coming Soon',
      gradient: 'from-slate-800/10 to-transparent',
      borderColor: 'border-slate-800/80',
      glowColor: ''
    },
    {
      title: 'Data Analysis',
      slug: 'data',
      description: 'Master statistical analysis, SQL databases, Pandas, and interactive data visualization.',
      icon: <BarChart2 className="w-8 h-8 text-slate-500" />,
      active: false,
      tag: 'Coming Soon',
      gradient: 'from-slate-800/10 to-transparent',
      borderColor: 'border-slate-800/80',
      glowColor: ''
    },
    {
      title: 'AI/ML Engineering',
      slug: 'aiml',
      description: 'Dive deep into neural networks, PyTorch, LLMs, and agentic AI deployment.',
      icon: <Brain className="w-8 h-8 text-slate-500" />,
      active: false,
      tag: 'Coming Soon',
      gradient: 'from-slate-800/10 to-transparent',
      borderColor: 'border-slate-800/80',
      glowColor: ''
    }
  ];

  const handleSelect = (slug: string, active: boolean) => {
    if (active) {
      navigate(`/domains/${slug}/roadmap`);
    }
  };

  return (
    <div className="py-12 max-w-6xl mx-auto">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent mb-4">
          Select Your Learning Path
        </h1>
        <p className="text-slate-400 text-lg">
          Embark on highly structured, pattern-based learning paths designed to take you from basics to advanced mastery.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {tracks.map((track) => (
          <div
            key={track.slug}
            onClick={() => handleSelect(track.slug, track.active)}
            className={`relative overflow-hidden rounded-2xl border bg-slate-900/40 backdrop-blur-xl p-8 flex flex-col justify-between transition-all duration-300 group ${
              track.active
                ? `cursor-pointer hover:-translate-y-1 shadow-lg ${track.borderColor} ${track.glowColor}`
                : `opacity-60 border-slate-900`
            }`}
          >
            {/* Ambient Background Glow */}
            <div className={`absolute inset-0 bg-gradient-to-br ${track.gradient} -z-10`} />

            <div>
              <div className="flex items-center justify-between mb-6">
                <div className={`p-3 rounded-xl ${track.active ? 'bg-indigo-500/10' : 'bg-slate-950/40'}`}>
                  {track.icon}
                </div>
                <span
                  className={`text-xs px-3 py-1 rounded-full font-bold ${
                    track.active
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      : 'bg-slate-950 text-slate-500 border border-slate-900'
                  }`}
                >
                  {track.tag}
                </span>
              </div>

              <h3 className={`text-xl font-bold mb-3 ${track.active ? 'text-white group-hover:text-indigo-300' : 'text-slate-400'}`}>
                {track.title}
              </h3>
              
              <p className="text-slate-400 text-sm leading-relaxed mb-8">
                {track.description}
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-900">
              {track.active ? (
                <>
                  <span className="text-xs text-indigo-400 font-bold group-hover:translate-x-1 transition-transform flex items-center gap-1">
                    Start Learning &rarr;
                  </span>
                  <span className="text-xs text-slate-500 font-mono">Sprint 2 Active</span>
                </>
              ) : (
                <>
                  <span className="text-xs text-slate-500 font-semibold flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5" /> Locked
                  </span>
                  <span className="text-xs text-slate-600 font-mono">Planned</span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DomainSelection;
