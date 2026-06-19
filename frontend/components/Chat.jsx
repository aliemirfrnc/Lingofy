import { useState } from "react";
import { api } from "../lib/api";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage("");
    setLoading(true);
    setError(null);

    setMessages((prev) => [...prev, { type: "user", text: userMessage }]);

    try {
      const data = await api.chat(userMessage);
      setMessages((prev) => [
        ...prev,
        { type: "assistant", text: data.response },
      ]);
    } catch (err) {
      if (err.message.includes("429")) {
        setError("Günlük mesaj limitine ulaştın.");
      } else {
        setError("Mesaj gönderilemedi.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <ul>
        {messages.map((item, index) => (
          <li key={index}>
            {item.type}: {item.text}
          </li>
        ))}
      </ul>

      {error && <p>{error}</p>}

      <form onSubmit={handleSubmit}>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}
