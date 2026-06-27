import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import QuestionTable from '../components/QuestionTable';
import type { Question } from '../components/QuestionTable';
import { 
  ArrowLeft, 
  Grid, 
  Hash, 
  Link as LinkIcon, 
  Layers, 
  Shuffle, 
  GitBranch, 
  Share2, 
  TrendingUp, 
  HelpCircle, 
  BookOpen, 
  CheckCircle2, 
  ChevronRight
} from 'lucide-react';

interface Concept {
  id: number;
  pattern_id: number;
  name: string;
  slug: string;
  theory_markdown: string | null;
  learning_objectives: string[];
  order_index: number;
  questions: Question[];
  solved_count: number;
  total_count: number;
}

interface Pattern {
  id: number;
  topic_id: number;
  name: string;
  slug: string;
  description: string | null;
  order_index: number;
  concepts: Concept[];
  solved_count: number;
  total_count: number;
}

interface TopicDetail {
  id: number;
  domain_id: number;
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
  patterns: Pattern[];
  prerequisites: string[];
}

const iconMap: Record<string, React.ReactNode> = {
  Grid: <Grid className="w-6 h-6 text-indigo-400" />,
  Hash: <Hash className="w-6 h-6 text-indigo-400" />,
  Link: <LinkIcon className="w-6 h-6 text-indigo-400" />,
  Layers: <Layers className="w-6 h-6 text-indigo-400" />,
  Shuffle: <Shuffle className="w-6 h-6 text-indigo-400" />,
  GitBranch: <GitBranch className="w-6 h-6 text-indigo-400" />,
  Share2: <Share2 className="w-6 h-6 text-indigo-400" />,
  TrendingUp: <TrendingUp className="w-6 h-6 text-indigo-400" />
};

const getIcon = (name: string | null) => {
  if (!name) return <HelpCircle className="w-6 h-6 text-indigo-400" />;
  return iconMap[name] || <HelpCircle className="w-6 h-6 text-indigo-400" />;
};

const renderMarkdown = (md: string | null) => {
  if (!md) return '';
  let html = md;
  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, (_match, p1) => {
    return `<pre class="bg-slate-950 border border-slate-900 text-indigo-300 p-4 rounded-xl font-mono text-xs overflow-x-auto my-4">${p1.trim()}</pre>`;
  });
  // Inline code
  html = html.replace(/`([^`\n]+)`/g, '<code class="bg-slate-950 text-indigo-400 px-1.5 py-0.5 rounded font-mono text-xs border border-slate-900">$1</code>');
  // Headers
  html = html.replace(/^### (.*$)/gim, '<h4 class="text-sm font-bold text-white mt-4 mb-2">$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3 class="text-base font-bold text-white mt-5 mb-2">$1</h3>');
  html = html.replace(/^# (.*$)/gim, '<h2 class="text-lg font-bold text-white mt-6 mb-3 border-b border-slate-900 pb-1">$1</h2>');
  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-white">$1</strong>');
  // Lists
  html = html.replace(/^\s*-\s+(.*$)/gim, '<li class="ml-4 list-disc text-slate-300 my-1">$1</li>');
  // Paragraphs
  const lines = html.split('\n');
  const processed = lines.map(line => {
    const t = line.trim();
    if (!t) return '<br/>';
    if (t.startsWith('<h') || t.startsWith('<li') || t.startsWith('<pre') || t.endsWith('</pre>') || t.startsWith('<code') || t.startsWith('<br')) {
      return line;
    }
    return `<p class="text-slate-350 text-sm leading-relaxed my-2">${line}</p>`;
  });
  return processed.join('\n');
};

const TopicPage: React.FC = () => {
  const { topicSlug } = useParams<{ topicSlug: string }>();
  const navigate = useNavigate();
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopic = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/topics/${topicSlug}`);
        if (response.data.success) {
          const topicData = response.data.data;
          setTopic(topicData);
          
          // Select the first concept by default
          if (topicData.patterns.length > 0 && topicData.patterns[0].concepts.length > 0) {
            setSelectedConcept(topicData.patterns[0].concepts[0]);
          }
        } else {
          setError(response.data.error || 'Failed to load topic');
        }
      } catch (err: any) {
        setError(err.response?.data?.error || err.message || 'Error loading topic');
      } finally {
        setLoading(false);
      }
    };

    fetchTopic();
  }, [topicSlug]);

  const handleToggleSolve = async (questionId: number, currentStatus: string) => {
    if (!topic || !selectedConcept) return;
    const newStatus = currentStatus === 'solved' ? 'unsolved' : 'solved';

    try {
      const response = await api.patch(`/api/questions/${questionId}/solve`, {
        status: newStatus
      });

      if (response.data.success) {
        // Sync local states immediately
        const updateResult = response.data.data;
        
        const updatedPatterns = topic.patterns.map((p) => {
          const updatedConcepts = p.concepts.map((c) => {
            const updatedQuestions = c.questions.map((q) => {
              if (q.id === questionId) {
                return { ...q, status: newStatus };
              }
              return q;
            });
            const solved = updatedQuestions.filter((q) => q.status === 'solved').length;
            
            const newConcept = { 
              ...c, 
              questions: updatedQuestions,
              solved_count: solved
            };
            
            // If this is the active concept, update selectedConcept state too
            if (c.id === selectedConcept.id) {
              setSelectedConcept(newConcept);
            }
            return newConcept;
          });

          const solved = updatedConcepts.reduce((sum, c) => sum + c.solved_count, 0);
          return {
            ...p,
            concepts: updatedConcepts,
            solved_count: solved
          };
        });

        setTopic({
          ...topic,
          solved_count: updateResult.topic_solved_count,
          patterns: updatedPatterns
        });
      }
    } catch (err: any) {
      console.error('Failed to update solve status', err);
    }
  };

  const handleToggleBookmark = async (questionId: number, currentBookmark: boolean) => {
    if (!topic || !selectedConcept) return;
    const newBookmark = !currentBookmark;

    try {
      const response = await api.patch(`/api/questions/${questionId}/bookmark`, {
        bookmark: newBookmark
      });

      if (response.data.success) {
        // Sync local states immediately
        const updatedPatterns = topic.patterns.map((p) => {
          const updatedConcepts = p.concepts.map((c) => {
            const updatedQuestions = c.questions.map((q) => {
              if (q.id === questionId) {
                return { ...q, bookmark: newBookmark };
              }
              return q;
            });
            
            const newConcept = { 
              ...c, 
              questions: updatedQuestions
            };
            
            if (c.id === selectedConcept.id) {
              setSelectedConcept(newConcept);
            }
            return newConcept;
          });

          return {
            ...p,
            concepts: updatedConcepts
          };
        });

        setTopic({
          ...topic,
          patterns: updatedPatterns
        });
      }
    } catch (err: any) {
      console.error('Failed to update bookmark', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col justify-center items-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-slate-400 text-sm mt-3">Loading topic workspace...</span>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="text-center py-16 bg-slate-900/30 border border-slate-800 rounded-xl p-8 max-w-lg mx-auto mt-12">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Topic</h2>
        <p className="text-slate-400 mb-6">{error || 'An unexpected error occurred.'}</p>
        <Link to="/domains/dsa/roadmap" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors">
          Back to Roadmap
        </Link>
      </div>
    );
  }

  const completionPct = topic.total_questions > 0 ? (topic.solved_count / topic.total_questions) * 100 : 0;

  return (
    <div className="py-4">
      {/* Back to Roadmap button */}
      <button 
        onClick={() => navigate('/domains/dsa/roadmap')}
        className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-6 font-semibold transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Roadmap
      </button>

      {/* Header bar */}
      <div className="bg-slate-900/35 border border-slate-900 rounded-2xl p-6 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-indigo-500/10 rounded-xl border border-indigo-500/25">
            {getIcon(topic.icon)}
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white mb-1.5">{topic.name}</h1>
            <p className="text-slate-400 text-sm max-w-lg leading-relaxed">{topic.description}</p>
          </div>
        </div>

        {/* Progress details */}
        <div className="w-full md:w-64 bg-slate-950/40 p-4 border border-slate-900 rounded-xl flex-shrink-0">
          <div className="flex justify-between items-center text-xs mb-2">
            <span className="text-slate-400 font-semibold">Topic Progress</span>
            <span className="text-indigo-400 font-bold">{topic.solved_count} / {topic.total_questions} Solved</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-850">
            <div 
              className="bg-indigo-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${completionPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Two Pane Content */}
      <div className="grid lg:grid-cols-4 gap-8">
        {/* Left sidebar: Patterns / Concepts tree */}
        <div className="lg:col-span-1 space-y-6">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 font-mono px-1">
            Patterns & Concepts
          </h2>
          <div className="space-y-4">
            {topic.patterns.map((pattern) => (
              <div key={pattern.id} className="bg-slate-900/20 border border-slate-900 rounded-xl p-3 space-y-2">
                <div className="flex justify-between items-center px-1 pb-1 border-b border-slate-900">
                  <span className="font-bold text-xs text-white truncate max-w-[120px]">{pattern.name}</span>
                  <span className="text-[10px] font-mono font-bold bg-indigo-500/10 text-indigo-400 px-1.5 py-0.2 border border-indigo-500/15 rounded">
                    {pattern.solved_count}/{pattern.total_count}
                  </span>
                </div>
                
                <div className="space-y-1 pt-1">
                  {pattern.concepts.map((concept) => {
                    const isActive = selectedConcept?.id === concept.id;
                    const isConceptSolved = concept.total_count > 0 && concept.solved_count === concept.total_count;

                    return (
                      <button
                        key={concept.id}
                        onClick={() => setSelectedConcept(concept)}
                        className={`w-full flex items-center justify-between p-2 rounded-lg text-left text-xs font-semibold transition-all group ${
                          isActive 
                            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-650/10' 
                            : 'text-slate-400 hover:bg-slate-900/40 hover:text-white'
                        }`}
                      >
                        <div className="flex items-center gap-2 truncate">
                          <ChevronRight className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-600 group-hover:text-indigo-400'}`} />
                          <span className="truncate">{concept.name}</span>
                        </div>
                        {isConceptSolved ? (
                          <CheckCircle2 className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-white' : 'text-emerald-400'}`} />
                        ) : (
                          <span className={`text-[10px] font-mono font-medium ${isActive ? 'text-indigo-200' : 'text-slate-500'}`}>
                            {concept.solved_count}/{concept.total_count}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right pane: Workbench area */}
        <div className="lg:col-span-3 space-y-8">
          {selectedConcept ? (
            <>
              {/* Theory Markdown Card */}
              <div className="bg-slate-900/20 border border-slate-900 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <BookOpen className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-xl font-extrabold text-white">Concept Explanation</h2>
                </div>
                
                {/* Custom Parsed theory markup */}
                <div 
                  className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(selectedConcept.theory_markdown) }}
                />

                {/* Concept objectives */}
                {selectedConcept.learning_objectives.length > 0 && (
                  <div className="mt-6 pt-6 border-t border-slate-900">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                      Learning Objectives
                    </h4>
                    <ul className="grid md:grid-cols-2 gap-2 text-xs text-slate-400">
                      {selectedConcept.learning_objectives.map((obj, i) => (
                        <li key={i} className="flex items-center gap-2 bg-slate-950/30 p-2 border border-slate-900/60 rounded-lg">
                          <CheckCircle2 className="w-4 h-4 text-indigo-500 flex-shrink-0" />
                          <span>{obj}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Practice Questions Panel */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-extrabold text-white">Concept Questions</h3>
                    <p className="text-slate-500 text-xs mt-0.5">Solve these challenges to achieve master level validation.</p>
                  </div>
                  <span className="text-xs font-mono font-bold px-2 py-1 bg-slate-950 border border-slate-900 rounded text-slate-400">
                    {selectedConcept.solved_count} / {selectedConcept.total_count} Solved
                  </span>
                </div>

                {/* Inline Question Table component */}
                <QuestionTable 
                  questions={selectedConcept.questions}
                  onToggleSolve={handleToggleSolve}
                  onToggleBookmark={handleToggleBookmark}
                />
              </div>
            </>
          ) : (
            <div className="text-center py-24 bg-slate-900/10 border border-slate-900 rounded-2xl flex flex-col justify-center items-center">
              <BookOpen className="w-12 h-12 text-slate-700 mb-4" />
              <h3 className="text-lg font-bold text-slate-400">No Concept Selected</h3>
              <p className="text-slate-500 text-sm mt-1 max-w-xs">Please select a pattern concept from the left sidebar to start learning.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopicPage;
