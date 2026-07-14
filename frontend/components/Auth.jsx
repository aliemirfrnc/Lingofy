"use client";

import { useState } from "react";
import { api } from "../lib/api";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Auth({ onAuthenticated, initialMode = "login" }) {
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);

    const trimmedEmail = email.trim().toLowerCase();
    if (!EMAIL_RE.test(trimmedEmail)) {
      setError("Geçerli bir e-posta adresi gir.");
      return;
    }
    if (password.length < 8) {
      setError("Şifre en az 8 karakter olmalı.");
      return;
    }
    if (mode === "register" && password !== confirmPassword) {
      setError("Şifreler eşleşmiyor.");
      return;
    }

    setLoading(true);
    try {
      const data =
        mode === "login"
          ? await api.login(trimmedEmail, password)
          : await api.register(trimmedEmail, password);
      onAuthenticated(data.email);
    } catch (err) {
      setError(err.message || "İşlem başarısız oldu.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full bg-transparent p-0">
      <div className="flex gap-2 mb-6">
        <button
          type="button"
          className={`flex-1 p-2.5 border-none rounded-lg text-sm transition-colors cursor-pointer ${mode === "login" ? "bg-gradient-to-br from-[#7759ff] to-[#4c78ff] text-white" : "bg-white/5 text-white/50 hover:bg-white/10"}`}
          onClick={() => {
            setMode("login");
            setError(null);
          }}
        >
          Giriş yap
        </button>
        <button
          type="button"
          className={`flex-1 p-2.5 border-none rounded-lg text-sm transition-colors cursor-pointer ${mode === "register" ? "bg-gradient-to-br from-[#7759ff] to-[#4c78ff] text-white" : "bg-white/5 text-white/50 hover:bg-white/10"}`}
          onClick={() => {
            setMode("register");
            setError(null);
          }}
        >
          Kayıt ol
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1.5 text-[13px] text-white/70 font-medium">
          E-posta
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="ornek@email.com"
            autoComplete="email"
            className="p-2.5 border border-white/10 rounded-lg text-sm text-white bg-white/5 focus:outline-none focus:border-[#7a62ff] focus:ring-[3px] focus:ring-[#7759ff]/10"
            required
          />
        </label>

        <label className="flex flex-col gap-1.5 text-[13px] text-white/70 font-medium">
          Şifre
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="En az 8 karakter"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            className="p-2.5 border border-white/10 rounded-lg text-sm text-white bg-white/5 focus:outline-none focus:border-[#7a62ff] focus:ring-[3px] focus:ring-[#7759ff]/10"
            required
          />
        </label>

        {mode === "register" && (
          <label className="flex flex-col gap-1.5 text-[13px] text-white/70 font-medium">
            Şifre tekrar
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Şifreni tekrar gir"
              autoComplete="new-password"
              className="p-2.5 border border-white/10 rounded-lg text-sm text-white bg-white/5 focus:outline-none focus:border-[#7a62ff] focus:ring-[3px] focus:ring-[#7759ff]/10"
              required
            />
          </label>
        )}

        {error && <p className="m-0 text-[13px] text-red-600">{error}</p>}

        <button 
          type="submit" 
          disabled={loading}
          className="mt-1 p-3 border-none rounded-lg bg-gradient-to-br from-[#7656ff] to-[#4e7bff] text-white text-[15px] font-medium cursor-pointer shadow-[0_12px_30px_rgba(85,70,255,0.24)] disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? "Bekle..." : mode === "login" ? "Giriş yap" : "Kayıt ol"}
        </button>
      </form>
    </div>
  );
}
