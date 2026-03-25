import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { User, LogOut, CheckCircle, Send, Bot, UserRound, Loader2, Search, MapPin, Stethoscope, Syringe, Pill, Scissors, Phone, Map, Facebook, Twitter, Youtube, Github, ChevronRight, Video, ClipboardList } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Chat States
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your healthcare assistant. Ask me any medical questions you have based on your records.' }
  ]);
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationState, setConversationState] = useState('IDLE');
  const [showUpload, setShowUpload] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll chat to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch suggestions as the user types
  useEffect(() => {
    const fetchSuggestions = async () => {
      const words = input.trim().split(/\s+/);
      if (words.length >= 3) {
        try {
          const response = await axios.post(`${API_BASE}/suggestions`, 
            { text: input },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          setSuggestions(response.data.suggestions || []);
        } catch (err) {
          console.error("Suggestions error:", err);
        }
      } else {
        setSuggestions([]);
      }
    };

    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [input]);

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

  const handleSendMessage = async (e, messageOverride = null) => {
    if (e) e.preventDefault();
    
    const messageText = messageOverride || input;
    if (!messageText.trim()) return;

    const userMessage = messageText.trim();
    if (!messageOverride) setInput('');
    
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/query`, 
        { 
          query: userMessage,
          conversation_state: conversationState 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const { answer, follow_up, new_state } = response.data;

      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: answer,
        follow_up: follow_up 
      }]);

      if (new_state) {
        setConversationState(new_state);
      }

      // Show upload button if bot asks for receipt
      if (answer && answer.toLowerCase().includes('upload')) {
        setShowUpload(true);
      } else {
        setShowUpload(false);
      }
    } catch (error) {
      console.error("Error fetching AI response:", error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error connecting to the server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle receipt image upload and OCR
  const handleReceiptUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setShowUpload(false);
    setIsLoading(true);
    // Only show a clean upload confirmation, NOT the raw OCR text
    setMessages(prev => [...prev, { role: 'user', content: `📎 Uploaded: ${file.name}` }]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Step 1: Extract text using OCR
      const response = await axios.post(`${API_BASE}/upload-receipt`, formData, {
        headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${token}` }
      });

      const text = response.data.extracted_text;

      if (!text) {
        setMessages(prev => [...prev, { role: 'ai', content: 'I could not read the receipt clearly. Please try uploading a clearer image.' }]);
        return;
      }

      // Step 2: Save extracted text to backend cache
      await axios.post(`${API_BASE}/save-receipt`, { text }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Step 3: Call /query DIRECTLY with RECEIPT_READ state (fixes React async state bug)
      const queryResponse = await axios.post(`${API_BASE}/query`, {
        query: "I have uploaded my receipt.",
        conversation_state: "RECEIPT_READ"   // Pass state directly, don't rely on React state
      }, { headers: { Authorization: `Bearer ${token}` } });

      const { answer, follow_up, new_state } = queryResponse.data;

      setMessages(prev => [...prev, { role: 'ai', content: answer, follow_up }]);
      setConversationState(new_state);
      if (answer && answer.toLowerCase().includes('upload')) setShowUpload(true);

    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, there was an error processing your receipt.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Login View
  if (!token) {
    return (
      <div className="auth-container">
        {/* Practo-Style Tiered Navbar */}
        <div className="practo-nav-wrapper">
          <div className="nav-top-bar">
            <span>For Corporates <span className="badge-new">NEW</span></span>
            <span>For Providers</span>
            <span>Security & help</span>
          </div>
          <div className="nav-main-bar">
            <div className="nav-left-group">
              <div className="nav-logo" onClick={() => window.location.reload()}>
                <img src="/assets/logo.png" alt="Insove" className="h-8" />
                <span>Insove</span>
              </div>
              <div className="nav-links-main">
                <span>Find Doctors</span>
                <span>Video Consult</span>
                <span>Medicines</span>
                <span>Lab Tests</span>
                <span>Surgeries</span>
              </div>
            </div>
            <div className="nav-right-group">
              <div className="login-btn-practo" onClick={() => window.location.href = `${API_BASE}/auth/login`}>
                Login / Signup
              </div>
            </div>
          </div>
        </div>

        {/* Hero Section with Dual Search */}
        <section className="hero-practo">
          <div className="search-container-practo">
            <div className="search-loc">
              <MapPin size={20} className="text-slate-400" />
              <input type="text" placeholder="Miola, NY" className="border-none outline-none w-full text-slate-800 font-medium" />
            </div>
            <div className="search-query">
              <Search size={20} className="text-slate-400" />
              <input type="text" placeholder="Search doctors, clinics, hospitals, etc." 
                className="border-none outline-none w-full text-slate-800 font-medium" />
            </div>
          </div>

          <div className="service-tiles-row">
            {/* AI Consultation Tile - WORKING */}
            <div className="service-card" onClick={() => window.location.href = `${API_BASE}/auth/login`}>
              <div className="card-img-wrapper">
                <div className="flex flex-col items-center gap-2">
                  <Bot size={60} className="text-practo-teal" />
                  <span className="text-xs font-bold text-practo-teal uppercase tracking-widest">Insove AI</span>
                </div>
              </div>
              <div className="card-content">
                <div className="card-title">Instant AI Consult</div>
                <div className="card-sub">Connect with Insove AI within 60 secs</div>
              </div>
            </div>

            <div className="service-card">
              <div className="card-img-wrapper">
                <img src="/assets/doctor.png" alt="Find Doctor" />
              </div>
              <div className="card-content">
                <div className="card-title">Find Doctors Near You</div>
                <div className="card-sub">Confirmed appointments</div>
              </div>
            </div>

            <div className="service-card">
              <div className="card-img-wrapper">
                <ClipboardList size={60} className="text-practo-teal opacity-40" />
              </div>
              <div className="card-content">
                <div className="card-title">Lab Tests</div>
                <div className="card-sub">Sample collection at your home</div>
              </div>
            </div>
          </div>

          {/* Direct Working Action Buttons */}
          <div className="hero-action-buttons">
            <button 
              className="ai-chat-btn"
              onClick={() => window.location.href = `${API_BASE}/auth/login`}
            >
              <Bot size={24} />
              CHAT WITH AI NOW
            </button>
            <button 
              className="google-login-btn"
              onClick={() => window.location.href = `${API_BASE}/auth/login`}
            >
              <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" className="h-6" />
              CONTINUE WITH GOOGLE
            </button>
          </div>
        </section>

        {/* Common Health Concerns Gallery */}
        <section className="concerns-section">
          <div className="section-header">
            <div>
              <h2>Consult top doctors online for any health concern</h2>
              <p className="text-slate-500 mt-2">Private online consultations with verified doctors in all specialties with most common diseases like (influenza, migraine, asthma, dengue)</p>
            </div>
            <div className="view-all">View All Specialties</div>
          </div>

          <div className="concerns-grid">
            <div className="concern-item">
              <div className="concern-circle">
                <img src="/assets/influenza.png" alt="Influenza" onError={(e) => e.target.src = "https://cdn-icons-png.flaticon.com/512/2855/2855132.png"} />
              </div>
              <div className="concern-label">Influenza (Flu)</div>
            </div>
            <div className="concern-item">
              <div className="concern-circle">
                <img src="/assets/migraine.png" alt="Migraine" onError={(e) => e.target.src = "https://cdn-icons-png.flaticon.com/512/2966/2966486.png"} />
              </div>
              <div className="concern-label">Migraine / Headache</div>
            </div>
            <div className="concern-item">
              <div className="concern-circle">
                <img src="/assets/asthma.png" alt="Asthma" onError={(e) => e.target.src = "https://cdn-icons-png.flaticon.com/512/3663/3663854.png"} />
              </div>
              <div className="concern-label">Asthma / Breathing</div>
            </div>
            <div className="concern-item">
              <div className="concern-circle">
                <img src="/assets/dengue.png" alt="Dengue" onError={(e) => e.target.src = "https://cdn-icons-png.flaticon.com/512/5661/5661332.png"} />
              </div>
              <div className="concern-label">Dengue / Mosquito Fever</div>
            </div>
          </div>
        </section>

        {/* Practo-Style Multi-column Footer */}
        <footer className="practo-footer-wrapper">
          <div className="footer-main-grid">
            <div className="footer-col">
              <h4>Insove</h4>
              <ul>
                <li>About</li>
                <li>Blog</li>
                <li>Careers</li>
                <li>Press</li>
                <li>Contact Us</li>
              </ul>
            </div>
            <div className="footer-col">
              <h4>For patients</h4>
              <ul>
                <li>Search for doctors</li>
                <li>Read health articles</li>
                <li>Order medicines</li>
                <li>Insove AI Consult</li>
                <li>Health app</li>
              </ul>
            </div>
            <div className="footer-col">
              <h4>For doctors</h4>
              <ul>
                <li>Insove Profile</li>
                <li>Insove Consult</li>
                <li>Insove Health Feed</li>
              </ul>
            </div>
            <div className="footer-col">
              <h4>For hospitals</h4>
              <ul>
                <li>Insta by Insove</li>
                <li>Qikwell by Insove</li>
                <li>Insove Profile</li>
              </ul>
            </div>
            <div className="footer-col">
              <h4>More</h4>
              <ul>
                <li>Help</li>
                <li>Developers</li>
                <li>Privacy Policy</li>
                <li>Terms & Conditions</li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            <div className="footer-logo">Insove</div>
            <div className="footer-socials">
              <Facebook />
              <Twitter />
              <Youtube />
              <Github />
            </div>
            <div className="footer-copy">
              Copyright © 2026, Insove Medical Healthcare. All rights reserved. <br />
              Your trusted partner in digital health accessibility and AI-driven medical records.
            </div>
          </div>
        </footer>
      </div>
    );
  }

  // Dashboard / Chat Interface
  const getUserInfo = () => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const email = payload.sub;
      let name = payload.name;

      if (!name || name === 'User' || name.toLowerCase() === name) {
        const rawName = (name && name !== 'User') ? name : email.split('@')[0];
        const cleanName = rawName.replace(/[0-9._-]/g, ' ').trim();
        name = cleanName.split(/\s+/).map(word =>
          word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');
      }

      return { email, name };
    } catch (e) {
      return { email: 'Authenticated User', name: 'User' };
    }
  };

  const user = getUserInfo();

  return (
    <div className="relative min-h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      <div className="relative z-10 h-full flex flex-col">

        {/* Navbar */}
        <div className="w-full bg-white px-8 py-4 border-b border-slate-200 flex justify-between items-center shadow-sm z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
          <h2 className="text-2xl font-black italic tracking-tighter text-blue-600">healthcare.ai</h2>
        </div>

        <div className="flex items-center gap-6">
          {/* User Profile Micro-Display */}
          <div className="flex items-center gap-3 hidden md:flex">
            <div className="text-right">
              <p className="text-sm font-bold text-slate-900 leading-tight">{user.name}</p>
              <p className="text-xs text-slate-500">{user.email}</p>
            </div>
            <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center border border-slate-200">
              <User size={20} className="text-slate-400" />
            </div>
          </div>

          <button onClick={logout} className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-600" title="Logout">
            <LogOut size={20} />
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 max-w-4xl w-full mx-auto p-4 flex flex-col gap-4 overflow-hidden relative">

        {/* Messages List */}
        <div className="flex-1 overflow-y-auto space-y-6 px-2 pb-32 pt-8 scrollbar-hide">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex items-start gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>

              {/* AI Avatar */}
              {msg.role === 'ai' && (
                <div className="w-10 h-10 rounded-2xl bg-blue-600 flex justify-center items-center shrink-0 shadow-lg mt-1">
                  <Bot size={22} className="text-white" />
                </div>
              )}

              {/* Message Bubble */}
              <div
                className={`max-w-[80%] rounded-[2rem] px-6 py-4 shadow-sm text-sm leading-relaxed ${msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-white border border-slate-200 text-slate-700 rounded-tl-sm'
                  }`}
              >
                <div className="space-y-3">
                  <p>{msg.content}</p>
                  {msg.follow_up && msg.follow_up.question && (
                    <div className="mt-4 pt-4 border-t border-slate-100 space-y-3">
                      <p className="font-bold text-blue-600 flex items-center gap-2">
                        <CheckCircle size={14} />
                        {msg.follow_up.question}
                      </p>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => {
                            const question = msg.follow_up.question.toLowerCase();
                            let yesMsg = '';
                            if (question.includes('schedule') || question.includes('medicines')) {
                              yesMsg = `Yes, I am taking my medicines as per the prescribed schedule.`;
                            } else if (question.includes('feeling') || question.includes('better')) {
                              yesMsg = `Yes, I am feeling better with the current treatment.`;
                            } else if (question.includes('medication')) {
                              yesMsg = `Yes, I am taking medications for ${msg.follow_up.disease}.`;
                            } else if (question.includes('remedies') || question.includes('control')) {
                              yesMsg = `Yes, I would like to know about the remedies for ${msg.follow_up.disease}.`;
                            } else {
                              yesMsg = `Yes, I am experiencing these symptoms for ${msg.follow_up.disease}.`;
                            }
                            handleSendMessage(null, yesMsg);
                          }}
                          className="bg-blue-50 text-blue-600 px-4 py-2 rounded-xl text-xs font-bold hover:bg-blue-100 transition-colors"
                        >
                          Yes
                        </button>
                        <button 
                          onClick={() => {
                            const question = msg.follow_up.question.toLowerCase();
                            let noMsg = '';
                            if (question.includes('schedule') || question.includes('medicines')) {
                              noMsg = `No, I am not taking my medicines as per the prescribed schedule.`;
                            } else if (question.includes('feeling') || question.includes('better')) {
                              noMsg = `No, I am not feeling better yet with the current treatment.`;
                            } else if (question.includes('medication')) {
                              noMsg = `No, I am not taking any medications for ${msg.follow_up.disease}.`;
                            } else if (question.includes('remedies') || question.includes('control')) {
                              noMsg = `No, I don't need remedies for ${msg.follow_up.disease}.`;
                            } else {
                              noMsg = `No, I don't have these symptoms for ${msg.follow_up.disease}.`;
                            }
                            handleSendMessage(null, noMsg);
                          }}
                          className="bg-slate-50 text-slate-500 px-4 py-2 rounded-xl text-xs font-bold hover:bg-slate-100 transition-colors"
                        >
                          No
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* User Avatar */}
              {msg.role === 'user' && (
                <div className="w-10 h-10 rounded-2xl bg-slate-200 flex justify-center items-center shrink-0 mt-1">
                  <UserRound size={22} className="text-slate-500" />
                </div>
              )}
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex items-start gap-4 justify-start">
              <div className="w-10 h-10 rounded-2xl bg-blue-600 flex justify-center items-center shrink-0 shadow-lg mt-1">
                <Loader2 size={22} className="text-white animate-spin" />
              </div>
              <div className="bg-white border border-slate-200 text-slate-400 rounded-[2rem] rounded-tl-sm px-6 py-4 text-sm flex items-center gap-2">
                Analyzing healthcare records...
              </div>
            </div>
          )}
          {/* Receipt Upload Button - shown after bot requests it */}
          {showUpload && (
            <div className="flex items-start gap-4 justify-start">
              <div className="w-10 h-10 rounded-2xl bg-blue-600 flex justify-center items-center shrink-0 shadow-lg mt-1">
                <Bot size={22} className="text-white" />
              </div>
              <div className="bg-white border border-blue-200 rounded-[2rem] rounded-tl-sm px-6 py-4 shadow-sm">
                <p className="text-sm text-slate-600 mb-3">Click below to upload your receipt image:</p>
                <label className="cursor-pointer bg-blue-600 text-white px-5 py-2 rounded-xl text-xs font-bold hover:bg-blue-700 transition-colors inline-block">
                  📎 Upload Receipt
                  <input type="file" accept="image/*" className="hidden" onChange={handleReceiptUpload} />
                </label>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion Chips */}
        {suggestions.length > 0 && (
          <div className="absolute bottom-24 left-0 right-0 px-4 flex flex-wrap gap-2 justify-center animate-in fade-in slide-in-from-bottom-2 duration-300">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => {
                  const currentInput = input.trim().toLowerCase();
                  const suggestion = s.toLowerCase();

                  // If suggestion starts with what the user already typed, use the suggestion as the whole text
                  // Otherwise, append it normally.
                  if (suggestion.startsWith(currentInput)) {
                    setInput(s);
                  } else {
                    setInput(prev => `${prev.trim()} ${s}`.trim());
                  }
                  setSuggestions([]); // Clear suggestions after selection
                }}
                className="bg-white border border-blue-100 text-blue-600 px-4 py-1.5 rounded-full text-xs font-bold shadow-sm hover:bg-blue-50 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input Form at Bottom */}
        <div className="absolute bottom-6 left-0 right-0 px-4 md:px-0">
          <form
            onSubmit={handleSendMessage}
            className="bg-white border border-slate-200 p-2 rounded-[2rem] shadow-[0_10px_40px_-10px_rgba(0,0,0,0.05)] flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about symptoms, treatments, or healthcare data..."
              className="flex-1 bg-transparent px-6 py-3 outline-none text-slate-700 placeholder:text-slate-400 text-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="bg-blue-600 text-white p-3 md:px-6 rounded-full font-bold text-sm tracking-wide disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span className="hidden md:inline">Send</span>
              <Send size={18} />
            </button>
          </form>
        </div>

      </div>
    </div>
  </div>
  );
}

export default App;
