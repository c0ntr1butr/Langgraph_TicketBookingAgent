import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hi, I am your AI Ticket Booking Agent. Tell me your source, destination, date, and budget.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: userMessage,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: userMessage,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: res.data.response || res.data.error || "No response from backend.",
        },
      ]);
    } catch{
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Backend error. Please check if FastAPI is running on port 8000.",
        },
      ]);
    }

    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="page">
      <div className="chat-card">
        <div className="header">
          <h1>AI Ticket Booking Agent</h1>
          <p>LangGraph + Ollama + FastAPI</p>
        </div>

        <div className="messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-row ${
                msg.role === "user" ? "user-row" : "bot-row"
              }`}
            >
              <div className={`message ${msg.role}`}>
                <pre>{msg.text}</pre>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row bot-row">
              <div className="message bot">Thinking...</div>
            </div>
          )}
        </div>

        <div className="input-box">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Example: Find train from Bangalore to Hyderabad tomorrow under 1500"
          />
          <button onClick={sendMessage} disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;