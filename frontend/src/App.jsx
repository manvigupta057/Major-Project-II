import React, { useState, useEffect } from 'react';
import { User, LogOut, CheckCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Handle URL token after Google Redirect
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('access_token');
    if (urlToken) {
      localStorage.setItem('token', urlToken);
      setToken(urlToken);
      window.history.replaceState({}, document.title, "/");
    }
  }, []);

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  // Login View
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a] p-6 font-sans">
        <div className="max-w-md w-full bg-[#111] border border-white/10 p-12 rounded-[40px] shadow-2xl text-center space-y-10">
          <div className="space-y-3">
            <h1 className="text-5xl font-black tracking-tighter text-blue-600 italic underline decoration-blue-600 underline-offset-8 uppercase">healthcare.ai</h1>
            <p className="text-slate-500 text-sm tracking-widest uppercase font-medium">Healthcare RAG</p>
          </div>
          <button 
            onClick={() => window.location.href = `${API_BASE}/auth/login`}
            className="w-full py-5 bg-blue-600 text-white font-bold rounded-2xl flex items-center justify-center gap-4 hover:bg-blue-700 transition-all transform hover:scale-[1.02] active:scale-95 duration-200 shadow-xl"
          >
            <img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" className="w-6 h-6 bg-white rounded-full p-0.5" alt="google" />
            Sign in with Google
          </button>
        </div>
      </div>
    );
  }

  // Day 3 Completed View: Login Successful / Dashboard Placeholder
  const getUserInfo = () => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const email = payload.sub;
      let name = payload.name;

      // General Name Beautifier for all users
      if (!name || name === 'User' || name.toLowerCase() === name) {
        // 1. Start with email prefix or current name
        const rawName = (name && name !== 'User') ? name : email.split('@')[0];
        
        // 2. Remove numbers and common separators (. _ -)
        const cleanName = rawName.replace(/[0-9._-]/g, ' ').trim();
        
        // 3. Proper Case: "john doe" -> "John Doe"
        name = cleanName.split(/\s+/).map(word => 
          word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');

        // Note: If names are concatenated like "manvigupta", we keep them as "Manvigupta" 
        // unless they were separated by symbols. This is the safest general approach.
      }

      return { email, name };
    } catch (e) {
      return { email: 'Authenticated User', name: 'User' };
    }
  };

  const user = getUserInfo();

  return (
    <div className="h-screen bg-white flex flex-col items-center p-4 md:px-20 md:py-10 font-sans text-slate-900">
      {/* Navbar */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-10 pb-6 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
          <h2 className="text-2xl font-black italic tracking-tighter text-blue-600">healthcare.ai</h2>
        </div>
        <button onClick={logout} className="group flex items-center gap-2 px-4 py-2 hover:bg-slate-50 rounded-full transition-all text-slate-400 hover:text-slate-600">
          <span className="text-xs font-bold uppercase tracking-widest hidden md:block">Logout</span>
          <LogOut size={18} />
        </button>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center text-center space-y-8 animate-in fade-in zoom-in duration-500">
        <div className="bg-blue-50 p-8 rounded-full">
          <CheckCircle size={80} className="text-blue-600" />
        </div>
        <div className="space-y-4">
          <h3 className="text-4xl font-bold text-slate-900 tracking-tight">Login Successful</h3>
          <p className="text-slate-500 max-w-lg text-lg">
            Welcome to <span className="text-blue-600 font-bold uppercase">healthcare.ai</span>. 
          </p>
        </div>
        
        <div className="w-full max-w-md mt-8">
          <div className="p-8 bg-slate-50 rounded-[40px] border border-slate-100 text-left space-y-6 shadow-sm">
            <h4 className="font-bold text-blue-600 uppercase text-xs tracking-[0.2em] mb-2 px-1">User Profile</h4>
            <div className="flex items-center gap-4">
               <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center border border-slate-200 shadow-sm">
                  <User size={32} className="text-blue-500" />
               </div>
               <div className="space-y-1">
                  <p className="text-xl font-bold text-slate-900">{user.name || 'User'}</p>
                  <p className="text-sm font-medium text-slate-400">{user.email}</p>
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
