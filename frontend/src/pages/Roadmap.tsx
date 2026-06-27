import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { 
  Grid, 
  Hash, 
  Link as LinkIcon, 
  Layers, 
  Shuffle, 
  GitBranch, 
  Share2, 
  TrendingUp, 
  HelpCircle, 
  Lock, 
  CheckCircle2, 
  ArrowLeft
} from 'lucide-react';

interface Topic {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  order_index: number;
  icon: string | null;
  unlock_percentage: number;
  learning_objectives: string[];
  total_questions: number;
  solved_count: number;
  is_unlocked: boolean;
  prerequisites: string[];
}

interface DomainHeader {
  name: string;
  slug: string;
  description: string | null;
}

interface RoadmapData {
  domain: DomainHeader;
  topics: Topic[];
}

const iconMap: Record<string, React.ReactNode> = {
  Grid: <Grid className="w-5 h-5" />,
  Hash: <Hash className="w-5 h-5" />,
  Link: <LinkIcon className="w-5 h-5" />,
  Layers: <Layers className="w-5 h-5" />,
  Shuffle: <Shuffle className="w-5 h-5" />,
  GitBranch: <GitBranch className="w-5 h-5" />,
  Share2: <Share2 className="w-5 h-5" />,
  TrendingUp: <TrendingUp className="w-5 h-5" />
};

const getIcon = (name: string | null) => {
  if (!name) return <HelpCircle className="w-5 h-5" />;
  return iconMap[name] || <HelpCircle className="w-5 h-5" />;
};

const Roadmap: React.FC = () => {
  const { domainSlug } = useParams<{ domainSlug: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<RoadmapData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRoadmap = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/domains/${domainSlug || 'dsa'}/roadmap`);
        if (response.data.success) {
          setData(response.data.data);
        } else {
          setError(response.data.error || 'Failed to load roadmap');
        }
      } catch (err: any) {
        setError(err.response?.data?.error || err.message || 'Error loading roadmap');
      } finally {
        setLoading(false);
      }
    };

    fetchRoadmap();
  }, [domainSlug]);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col justify-center items-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-slate-400 text-sm mt-3">Loading interactive roadmap...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-16 bg-slate-900/30 border border-slate-800 rounded-xl p-8 max-w-lg mx-auto mt-12">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Roadmap</h2>
        <p className="text-slate-400 mb-6">{error || 'An unexpected error occurred.'}</p>
        <Link to="/domains" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors">
          Back to Paths
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Header */}
      <div className="mb-12 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <button 
            onClick={() => navigate('/domains')}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-4 font-semibold transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Tracks
          </button>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-2">
            {data.domain.name} Roadmap
          </h1>
          <p className="text-slate-400 text-sm max-w-xl">
            {data.domain.description}
          </p>
        </div>
        
        {/* Overall progress card */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 md:w-64">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-slate-400 font-semibold">Overall Completion</span>
            <span className="text-xs text-indigo-400 font-bold">
              {data.topics.reduce((acc, curr) => acc + curr.solved_count, 0)} / {data.topics.reduce((acc, curr) => acc + curr.total_questions, 0)} Solved
            </span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-850">
            <div 
              className="bg-indigo-500 h-full rounded-full transition-all duration-550"
              style={{
                width: `${
                  (data.topics.reduce((acc, curr) => acc + curr.solved_count, 0) / 
                   Math.max(data.topics.reduce((acc, curr) => acc + curr.total_questions, 0), 1)) * 100
                }%`
              }}
            />
          </div>
        </div>
      </div>

      {/* Nodes Map */}
      <div className="relative pl-8 md:pl-0 mt-8">
        {/* Connection Line */}
        <div className="absolute left-[26px] md:left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-indigo-500/80 via-purple-500/40 to-slate-900 -translate-x-1/2 -z-10" />

        <div className="space-y-16">
          {data.topics.map((topic, index) => {
            const isCompleted = topic.total_questions > 0 && topic.solved_count === topic.total_questions;
            const isInProgress = topic.solved_count > 0 && topic.solved_count < topic.total_questions;
            const isLeft = index % 2 === 0;
            const completionPct = topic.total_questions > 0 ? (topic.solved_count / topic.total_questions) * 100 : 0;

            // Node visual class builder
            let nodeClass = '';
            let ringClass = '';
            if (!topic.is_unlocked) {
              nodeClass = 'bg-slate-950/80 border-slate-900 text-slate-500';
            } else if (isCompleted) {
              nodeClass = 'bg-emerald-950/20 border-emerald-500/60 hover:border-emerald-400 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.15)]';
              ringClass = 'ring-4 ring-emerald-500/10';
            } else if (isInProgress) {
              nodeClass = 'bg-indigo-950/20 border-indigo-500 hover:border-indigo-400 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.2)] animate-pulse-slow';
              ringClass = 'ring-4 ring-indigo-500/10';
            } else {
              nodeClass = 'bg-slate-900/90 border-slate-700 hover:border-slate-500 text-white';
            }

            return (
              <div 
                key={topic.slug} 
                className={`relative flex flex-col md:flex-row items-start md:items-center ${
                  isLeft ? 'md:flex-row-reverse' : ''
                }`}
              >
                {/* Connector dot on the center line */}
                <div 
                  className={`absolute left-0 md:left-1/2 top-4 md:top-1/2 w-4 h-4 rounded-full -translate-x-[23px] md:-translate-x-[7px] -translate-y-1/2 z-10 border-2 transition-all duration-300 ${
                    !topic.is_unlocked 
                      ? 'bg-slate-950 border-slate-800' 
                      : isCompleted 
                        ? 'bg-emerald-500 border-white' 
                        : 'bg-indigo-500 border-white shadow-[0_0_8px_rgba(99,102,241,0.8)]'
                  }`}
                />

                {/* Topic card */}
                <div className={`w-full md:w-[45%] flex flex-col ${isLeft ? 'md:text-right md:items-end' : 'md:text-left md:items-start'}`}>
                  <div 
                    onClick={() => {
                      if (topic.is_unlocked) {
                        navigate(`/topics/${topic.slug}`);
                      }
                    }}
                    className={`w-full rounded-2xl border backdrop-blur-xl p-5 transition-all duration-300 ${
                      topic.is_unlocked ? 'cursor-pointer hover:-translate-y-0.5' : 'cursor-not-allowed'
                    } ${nodeClass} ${ringClass}`}
                  >
                    <div className={`flex items-center gap-3 mb-3 ${isLeft ? 'md:flex-row-reverse' : ''}`}>
                      <div className={`p-2 rounded-lg ${
                        !topic.is_unlocked 
                          ? 'bg-slate-950/40 text-slate-600' 
                          : isCompleted 
                            ? 'bg-emerald-500/10 text-emerald-400' 
                            : 'bg-indigo-500/10 text-indigo-400'
                      }`}>
                        {getIcon(topic.icon)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-bold text-base text-white">{topic.name}</h3>
                          {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400 fill-emerald-950/20" />}
                          {!topic.is_unlocked && <Lock className="w-3.5 h-3.5 text-slate-600" />}
                        </div>
                        <span className="text-slate-500 text-[10px] uppercase tracking-wider font-mono">
                          Topic {topic.order_index}
                        </span>
                      </div>
                    </div>

                    <p className="text-slate-400 text-xs leading-relaxed mb-4">
                      {topic.description || 'Dive into advanced concepts, learn algorithmic patterns, and solve hand-picked challenge questions.'}
                    </p>

                    {/* Progress details */}
                    {topic.is_unlocked ? (
                      <div>
                        <div className="flex justify-between items-center mb-1 text-[11px] font-mono">
                          <span className="text-slate-500">Solved: {topic.solved_count}/{topic.total_questions}</span>
                          <span className={`${isCompleted ? 'text-emerald-400' : 'text-indigo-400'} font-bold`}>
                            {Math.round(completionPct)}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-950/80 rounded-full h-1 overflow-hidden border border-slate-900">
                          <div 
                            className={`h-full rounded-full transition-all duration-500 ${
                              isCompleted ? 'bg-emerald-500' : 'bg-indigo-500'
                            }`}
                            style={{ width: `${completionPct}%` }}
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="p-2.5 bg-slate-950/60 border border-slate-900/60 rounded-lg flex items-start gap-2">
                        <Lock className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
                        <span className="text-[10px] text-slate-500 leading-normal">
                          Locked. Complete {Math.round(topic.unlock_percentage * 100)}% of:{' '}
                          <span className="text-indigo-400/80 font-semibold">{topic.prerequisites.join(', ') || 'previous topics'}</span>.
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Empty buffer box for md screen alignment */}
                <div className="hidden md:block w-[10%]" />
                <div className="hidden md:block w-[45%]" />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Roadmap;
