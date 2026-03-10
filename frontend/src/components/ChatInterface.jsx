import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function ChatInterface() {
    const [query, setQuery] = useState("");
    const [history, setHistory] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [history]);

    async function handleSend() {
        if (!query.trim()) return;

        const userMsg = { role: "user", text: query };
        setHistory((prev) => [...prev, userMsg]);
        setQuery("");
        setIsTyping(true);

        try {
            const res = await axios.post("http://localhost:8000/query", { query: userMsg.text });
            const botMsg = {
                role: "bot",
                text: res.data.answer,
                sources: res.data.sources
            };
            setHistory((prev) => [...prev, botMsg]);
        } catch (err) {
            console.error(err);
            setHistory((prev) => [
                ...prev,
                { role: "bot", text: "Sorry, something went wrong. Please check the backend connection." }
            ]);
        } finally {
            setIsTyping(false);
        }
    }

    return (
        <div className="flex flex-col h-[650px] w-full max-w-3xl bg-white rounded-2xl overflow-hidden border border-stone-200 shadow-xl">
            {/* Header / Status */}
            <div className="bg-stone-50 border-b border-stone-100 p-3 flex items-center justify-between px-6">
                <span className="text-xs font-bold text-stone-400 tracking-widest uppercase">Live Session</span>
                <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-stone-300"></div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar bg-white">
                {history.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-stone-300">
                        <div className="text-4xl mb-4 opacity-20">✒️</div>
                        <p className="font-serif text-xl text-stone-400">The page is empty.</p>
                        <p className="text-sm text-stone-300 mt-2">Ask a question to begin.</p>
                    </div>
                )}

                {history.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
                    >
                        <div
                            className={`max-w-[85%] p-5 leading-loose text-sm md:text-base ${msg.role === "user"
                                ? "bg-stone-900 text-stone-50 rounded-2xl rounded-tr-none shadow-md"
                                : "bg-stone-50 text-stone-800 border border-stone-100 rounded-2xl rounded-tl-none"
                                }`}
                        >
                            <p className="whitespace-pre-wrap font-sans">{msg.text}</p>
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div className="flex justify-start">
                        <div className="bg-stone-50 text-stone-400 rounded-full px-4 py-2 text-xs font-medium tracking-wide flex items-center gap-1 border border-stone-100">
                            AI is writing...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-6 bg-white border-t border-stone-100">
                <div className="flex gap-3 relative">
                    <input
                        type="text"
                        className="flex-1 bg-stone-50 text-stone-800 rounded-lg px-5 py-4 border border-stone-200 focus:outline-none focus:border-stone-400 focus:bg-white transition-all placeholder-stone-400 font-sans"
                        placeholder="Type your question..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        disabled={isTyping}
                    />
                    <button
                        onClick={handleSend}
                        disabled={isTyping || !query.trim()}
                        className="bg-stone-900 hover:bg-black disabled:bg-stone-200 disabled:text-stone-400 text-white px-8 rounded-lg font-semibold transition-all shadow-md active:scale-95"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
