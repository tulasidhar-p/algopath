import React, { useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Flame, LogOut, ShieldAlert, Award, CalendarDays, Compass } from 'lucide-react';

const Navbar: React.FC = () => {
  const auth = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  if (!auth) return null;
  const { user, logout } = auth;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white group-hover:scale-105 transition-transform">
            A
          </div>
          <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            AlgoPath
          </span>
        </Link>

        <div className="flex items-center gap-6">
          {user ? (
            <>
              <div className="hidden md:flex items-center gap-1">
                <Link
                  to="/domains"
                  className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                    isActive('/domains') ? 'text-indigo-400 bg-indigo-500/5' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Compass className="w-4 h-4" />
                  Tracks
                </Link>

                <Link
                  to="/domains/dsa/roadmap"
                  className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                    location.pathname.includes('/roadmap') ? 'text-indigo-400 bg-indigo-500/5' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Award className="w-4 h-4" />
                  Roadmap
                </Link>

                <Link
                  to="/planner"
                  className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                    isActive('/planner') ? 'text-indigo-400 bg-indigo-500/5' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <CalendarDays className="w-4 h-4" />
                  Daily Planner
                </Link>

                {user.is_admin && (
                  <Link
                    to="/admin"
                    className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                      isActive('/admin') ? 'text-purple-400 bg-purple-500/5' : 'text-slate-400 hover:text-purple-300'
                    }`}
                  >
                    <ShieldAlert className="w-4 h-4" />
                    Admin
                  </Link>
                )}
              </div>

              <div className="h-6 w-px bg-slate-800 hidden md:block" />

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1 px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-500 rounded-full text-xs font-bold animate-pulse">
                  <Flame className="w-3.5 h-3.5 fill-amber-500" />
                  <span>{user.streak_count} Day Streak</span>
                </div>

                <div className="text-right hidden sm:block">
                  <p className="text-sm font-semibold text-white leading-tight">{user.name}</p>
                  <p className="text-xs text-slate-500">{user.email}</p>
                </div>

                <button
                  onClick={handleLogout}
                  className="p-2 bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 rounded-lg transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-sm font-semibold text-slate-400 hover:text-white transition-colors">
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors shadow-lg shadow-indigo-600/15"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
