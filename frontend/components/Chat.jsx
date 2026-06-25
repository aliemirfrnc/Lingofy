"use client";
import { useRef, useState, useEffect } from "react";
import { api } from "../lib/api";
import { Card, CardContent, CardFooter } from "./ui/Card";
import { Input } from "./ui/Input";
import { Button } from "./ui/Button";
import { Send, Loader2 } from "lucide-react";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const listRef = useRef(null);

  const scrollToBottom = () => {
    setTimeout(() => {
      listRef.current?.scrollTo({ top: 9999, behavior: "smooth" });
    }, 50);
  };

  async function handleSubmit(e) {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage("");
    setLoading(true);
    setError(null);

    setMessages((prev) => [...prev, { type: "user", text: userMessage }]);
    scrollToBottom();

    try {
      const data = await api.chat(userMessage);
      if (!data || !data.response) {
        throw new Error("Sunucudan geçerli bir yanıt alınamadı.");
      }
      setMessages((prev) => [
        ...prev,
        { type: "assistant", text: data.response },
      ]);
      scrollToBottom();
    } catch (err) {
      setError(err.message || "Mesaj gönderilemedi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="flex flex-col h-full border-white/5 animate-slide-up shadow-glass">
      <CardContent 
        className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 custom-scrollbar" 
        ref={listRef}
      >
        {messages.length === 0 && (
          <p className="text-center text-white/30 text-[13px] my-auto">Şarkı sözleri hakkında bir şey sor</p>
        )}
        
        {messages.map((item, i) => (
          <div
            key={i}
            className={`max-w-[88%] p-3 rounded-2xl text-[13px] leading-relaxed animate-fade-in
              ${item.type === "user" 
                ? "self-end bg-theme-200 border border-theme-300 text-white" 
                : "self-start bg-white/5 border border-white/10 text-white/80"
              }`}
          >
            {item.text}
          </div>
        ))}
        
        {loading && (
          <div className="max-w-[88%] p-3 rounded-2xl self-start bg-white/5 border border-white/10 text-white/80 animate-pulse flex gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        )}
      </CardContent>

      {error && <p className="text-red-400 text-xs px-4 pb-2">{error}</p>}

      <CardFooter className="p-3 border-t border-white/5 bg-black/20">
        <form onSubmit={handleSubmit} className="flex gap-2 w-full">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={loading}
            placeholder="Sözler hakkında sor..."
            className="h-10 text-sm bg-white/5 border-white/10 placeholder:text-white/30"
          />
          <Button
            type="submit"
            disabled={loading || !message.trim()}
            variant="primary"
            size="icon"
            className="h-10 w-10 shrink-0 rounded-xl"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
