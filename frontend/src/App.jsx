import React, { useState, useRef, useEffect } from "react";
import ChatMessage from "./components/ChatMessage";
import "./styles/app.css";

const API_URL = import.meta.env.VITE_API_URL || "";

const WELCOME_MESSAGE = {
  role: "assistant",
  content:
    "What's good! I'm the **Playmaker Bot** — powered by CEO Matty J's documented playbooks. 🏆\n\nAsk me anything about entrepreneurship, building brands, the Turo game, car rentals, or scaling your business. I've got the plays Matty's already documented.\n\n**What's on your mind?**",
};

export default function App() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMessage = { role: "user", content: trimmed };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const history = newMessages
        .filter((m) => m !== WELCOME_MESSAGE)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch(`${API_URL}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, history }),
      });

      if (!res.ok) throw new Error("Failed to get response");
      const data = await res.json();
      setMessages([...newMessages, { role: "assistant", content: data.reply }]);
    } catch {
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content:
            "My bad — something went wrong on my end. Try again in a sec. 💪",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <div className="logo-icon">▶</div>
          <div>
            <h1 className="header-title">PLAYMAKER BOT</h1>
            <p className="header-subtitle">Powered by CEO Matty J's Playbooks</p>
          </div>
        </div>
        <div className="header-badge">MR. DOCUMENT THE PROCESS</div>
      </header>

      <main className="chat-area">
        <div className="messages">
          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-avatar">▶</div>
              <div className="message-bubble typing">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="input-area">
        <form onSubmit={sendMessage} className="input-form">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the Playmaker anything..."
            className="chat-input"
            disabled={loading}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={loading || !input.trim()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M22 2L11 13"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M22 2L15 22L11 13L2 9L22 2Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </form>
        <p className="disclaimer">
          Playmaker Bot uses Matty's documented content. For personalized strategy, book a session with{" "}
          <a href="https://www.instagram.com/ceomattyj/" target="_blank" rel="noopener noreferrer">
            @ceomattyj
          </a>
        </p>
      </footer>
    </div>
  );
}
