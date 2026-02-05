import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, Database, FileText, ChevronDown, ChevronUp, Loader2, BarChart3, RefreshCcw, File } from "lucide-react";

// --- CONFIGURATION ---
const API_URL = "http://127.0.0.1:8000/api/chat";
const PDF_URL = "http://127.0.0.1:8000/static/"; // Base URL for PDFs

function App() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello! I am your Enterprise Chatbot. Accessing secure Infosys database...", thoughts: null, sources: [] }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  
  // Dashboard Metrics State
  const [metrics, setMetrics] = useState({
    latency: "0.0s",
    confidence: "100%",
    tokens: 0,
    total_queries: 0
  });

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const clearChat = () => {
    setMessages([{ role: "bot", text: "Chat history cleared. System ready.", thoughts: null, sources: [] }]);
    setMetrics({ latency: "0.0s", confidence: "100%", tokens: 0, total_queries: 0 });
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(API_URL, { query: userMsg.text });
      
      const botMsg = { 
        role: "bot", 
        text: response.data.answer, 
        thoughts: response.data.thoughts,
        sources: response.data.sources 
      };
      
      setMessages((prev) => [...prev, botMsg]);
      
      // Update Dashboard
      setMetrics({
        latency: response.data.metrics.latency,
        confidence: response.data.metrics.confidence,
        tokens: response.data.metrics.tokens,
        total_queries: metrics.total_queries + 1
      });

    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { role: "bot", text: "⚠️ Server Error. Check Backend Console.", thoughts: null }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans overflow-hidden">
      
      {/* --- LEFT: MAIN CHAT AREA (75% Width) --- */}
      <div className="flex-1 flex flex-col h-full max-w-5xl mx-auto shadow-2xl bg-white md:my-4 md:rounded-2xl overflow-hidden border border-gray-200">
        
        {/* HEADER */}
        <div className="bg-white border-b border-gray-100 p-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-800 text-lg tracking-tight">Enterprise Chatbot</h1>
              <p className="text-xs text-green-600 font-medium flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                Secure Connection
              </p>
            </div>
          </div>
          <button onClick={clearChat} className="p-2 hover:bg-gray-100 rounded-full text-gray-500 transition-colors" title="Reset Chat">
            <RefreshCcw className="w-5 h-5" />
          </button>
        </div>

        {/* MESSAGES */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] ${msg.role === "user" ? "bg-indigo-600 text-white" : "bg-white border border-gray-200 text-gray-800"} rounded-2xl p-5 shadow-sm`}>
                <div className="leading-relaxed whitespace-pre-wrap">{msg.text}</div>

                {/* --- SOURCE LINKS (NEW) --- */}
                {msg.role === "bot" && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.sources.map((source, i) => (
                      <a 
                        key={i} 
                        href={`${PDF_URL}${source}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 bg-gray-100 hover:bg-indigo-50 text-xs text-gray-600 hover:text-indigo-600 px-2 py-1 rounded-md transition-colors border border-gray-200"
                      >
                        <File className="w-3 h-3" />
                        {source}
                      </a>
                    ))}
                  </div>
                )}

                {/* --- REASONING ACCORDION --- */}
                {msg.role === "bot" && msg.thoughts && <ThinkingSection thoughts={msg.thoughts} />}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-indigo-600 animate-spin" />
                <span className="text-sm text-gray-500 font-medium">Analyzing Documents & Graph...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* INPUT */}
        <div className="p-5 bg-white border-t border-gray-100">
          <div className="relative flex items-center bg-gray-50 border border-gray-200 rounded-2xl px-2 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
            <input
              type="text"
              className="flex-1 bg-transparent border-none outline-none p-4 text-gray-700 placeholder-gray-400"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && sendMessage()}
              disabled={loading}
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className={`p-3 rounded-xl transition-all ${input.trim() ? "bg-indigo-600 text-white shadow-lg shadow-indigo-200 hover:scale-105" : "bg-gray-200 text-gray-400"}`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* --- RIGHT: DASHBOARD SIDEBAR (25% Width) --- */}
      <div className="hidden md:flex flex-col w-80 bg-white border-l border-gray-200 h-full p-6">
        <div className="flex items-center gap-2 mb-8 text-gray-800">
          <BarChart3 className="w-5 h-5" />
          <h2 className="font-bold text-lg">Live Metrics</h2>
        </div>

        <div className="space-y-6">
          <MetricCard label="Latency" value={metrics.latency} color="text-emerald-600" />
          <MetricCard label="Confidence" value={metrics.confidence} color="text-blue-600" />
          <MetricCard label="Tokens Generated" value={metrics.tokens} color="text-purple-600" />
          <MetricCard label="Total Queries" value={metrics.total_queries} color="text-orange-600" />
        </div>

        <div className="mt-auto bg-indigo-50 rounded-xl p-4 border border-indigo-100">
          <h3 className="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-2">System Status</h3>
          <div className="space-y-2">
            <StatusRow label="Graph DB" status="Active" />
            <StatusRow label="Vector DB" status="Active" />
            <StatusRow label="LLM Engine" status="Llama-3" />
          </div>
        </div>
      </div>

    </div>
  );
}

// --- SUB-COMPONENTS ---

function MetricCard({ label, value, color }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
      <p className="text-xs text-gray-500 font-medium uppercase">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}

function StatusRow({ label, status }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-gray-600">{label}</span>
      <span className="flex items-center gap-1 text-green-600 font-medium">
        <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> {status}
      </span>
    </div>
  );
}

function ThinkingSection({ thoughts }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="mt-4 border-t border-gray-100 pt-3">
      <button onClick={() => setIsOpen(!isOpen)} className="flex items-center gap-2 text-xs font-semibold text-gray-500 hover:text-indigo-600 transition-colors w-full">
        {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        {isOpen ? "Hide Reasoning" : "View Reasoning"}
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
            <div className="grid grid-cols-1 gap-3 mt-3">
              <div className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-2 text-indigo-700">
                  <Database className="w-3 h-3" />
                  <span className="text-[10px] font-bold uppercase">Graph Data</span>
                </div>
                <p className="text-xs text-indigo-900 font-mono opacity-80 break-words">{thoughts.graph}</p>
              </div>
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-2 text-emerald-700">
                  <FileText className="w-3 h-3" />
                  <span className="text-[10px] font-bold uppercase">Vector Context</span>
                </div>
                <p className="text-xs text-emerald-900 font-mono opacity-80 line-clamp-4">{thoughts.vector}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;