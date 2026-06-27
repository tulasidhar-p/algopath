import React from 'react';
import { ExternalLink, Star, CheckCircle, Circle, Clock } from 'lucide-react';

export interface Question {
  id: number;
  concept_id: number;
  title: string;
  difficulty: string;
  source: string;
  url: string;
  estimated_solve_time: number;
  is_important: boolean;
  order_index: number;
  status: string; // unsolved, solved, revisit
  bookmark: boolean;
  notes: string | null;
  tags: string[];
  companies: string[];
}

interface QuestionTableProps {
  questions: Question[];
  onToggleSolve: (questionId: number, currentStatus: string) => void;
  onToggleBookmark: (questionId: number, currentBookmark: boolean) => void;
}

const QuestionTable: React.FC<QuestionTableProps> = ({ 
  questions, 
  onToggleSolve, 
  onToggleBookmark 
}) => {

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return (
          <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Easy
          </span>
        );
      case 'medium':
        return (
          <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            Medium
          </span>
        );
      case 'hard':
        return (
          <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
            Hard
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/20">
            {difficulty}
          </span>
        );
    }
  };

  const getSourceBadge = (source: string) => {
    return (
      <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded bg-slate-950 border border-slate-800 text-slate-400 uppercase">
        {source}
      </span>
    );
  };

  if (questions.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-900/10 border border-slate-900 border-dashed rounded-xl">
        <p className="text-slate-500 text-sm">No questions available for this concept.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto border border-slate-900 bg-slate-900/10 rounded-xl">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-900 text-xs font-semibold text-slate-400 bg-slate-950/40">
            <th className="py-4 px-6 w-12 text-center">Status</th>
            <th className="py-4 px-6">Question Title</th>
            <th className="py-4 px-4 w-28 text-center">Difficulty</th>
            <th className="py-4 px-4 w-32 text-center">Platform</th>
            <th className="py-4 px-4 w-28 text-center">Solve Time</th>
            <th className="py-4 px-4 w-16 text-center">Bookmark</th>
            <th className="py-4 px-6 w-32 text-center">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-900/80 text-sm">
          {questions.map((q) => {
            const isSolved = q.status === 'solved';
            return (
              <tr 
                key={q.id} 
                className={`hover:bg-slate-900/20 transition-colors group ${
                  isSolved ? 'bg-emerald-950/5' : ''
                }`}
              >
                {/* Solved Toggler Checkbox */}
                <td className="py-4 px-6 text-center">
                  <button 
                    onClick={() => onToggleSolve(q.id, q.status)}
                    className="focus:outline-none focus:ring-0"
                  >
                    {isSolved ? (
                      <CheckCircle className="w-5 h-5 text-emerald-500 fill-emerald-500/10 transition-transform group-hover:scale-105" />
                    ) : (
                      <Circle className="w-5 h-5 text-slate-600 transition-colors hover:text-indigo-400" />
                    )}
                  </button>
                </td>

                {/* Question Title & Importance tag */}
                <td className="py-4 px-6">
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <a 
                        href={q.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="font-semibold text-slate-200 hover:text-indigo-400 flex items-center gap-1.5 transition-colors"
                      >
                        {q.title}
                        <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-slate-500 transition-opacity" />
                      </a>
                      {q.is_important && (
                        <span className="text-[10px] px-1.5 py-0.2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded uppercase font-bold tracking-wider">
                          Must Do
                        </span>
                      )}
                    </div>
                    {/* Companies & tags list */}
                    {(q.companies.length > 0 || q.tags.length > 0) && (
                      <div className="flex flex-wrap items-center gap-1.5 mt-1 text-[11px] text-slate-500">
                        {q.companies.slice(0, 3).map((c) => (
                          <span key={c} className="bg-slate-900 px-1.5 py-0.5 rounded text-[10px] text-slate-400">
                            {c}
                          </span>
                        ))}
                        {q.tags.slice(0, 3).map((t) => (
                          <span key={t} className="text-slate-500 font-mono">
                            #{t.toLowerCase().replace(' ', '-')}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </td>

                {/* Difficulty */}
                <td className="py-4 px-4 text-center">
                  {getDifficultyBadge(q.difficulty)}
                </td>

                {/* Platform */}
                <td className="py-4 px-4 text-center">
                  {getSourceBadge(q.source)}
                </td>

                {/* Solve Time */}
                <td className="py-4 px-4 text-center">
                  <div className="flex items-center justify-center gap-1 text-slate-400 font-mono text-xs">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>{q.estimated_solve_time}m</span>
                  </div>
                </td>

                {/* Bookmark Toggler Star */}
                <td className="py-4 px-4 text-center">
                  <button 
                    onClick={() => onToggleBookmark(q.id, q.bookmark)}
                    className="focus:outline-none text-slate-500 hover:text-amber-500 transition-colors"
                  >
                    <Star 
                      className={`w-5 h-5 transition-transform hover:scale-110 ${
                        q.bookmark ? 'text-amber-500 fill-amber-500' : 'text-slate-600'
                      }`} 
                    />
                  </button>
                </td>

                {/* Action button */}
                <td className="py-4 px-6 text-center">
                  <div className="flex justify-center items-center gap-2">
                    <a 
                      href={q.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white rounded border border-slate-850 hover:border-slate-700 text-xs font-semibold flex items-center gap-1 transition-colors"
                    >
                      Solve <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default QuestionTable;
