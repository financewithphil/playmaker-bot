import React from "react";
import ReactMarkdown from "react-markdown";
import "../styles/message.css";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      {!isUser && <div className="message-avatar">▶</div>}
      <div className={`message-bubble ${isUser ? "user-bubble" : "bot-bubble"}`}>
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
      {isUser && <div className="message-avatar user-avatar">YOU</div>}
    </div>
  );
}
