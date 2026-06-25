"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../../lib/api";

export default function PricingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleUpgrade = async (planName) => {
    setLoading(planName);
    setError(null);
    setSuccess(null);
    try {
      const res = await api.upgradePlan(planName);
      setSuccess(res.message);
      setTimeout(() => router.push("/account"), 2000);
    } catch (err) {
      setError(err.message || "Bir hata oluştu.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#000000] text-white p-8 pb-32">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600">
            İngilizceni Zirveye Taşı
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
            Dünyanın ilk müzik tabanlı, profesyonel yapay zeka dil koçuyla tanış.
            Hedeflerine ulaşmak için sana en uygun planı seç.
          </p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl mb-8 text-center max-w-md mx-auto">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-green-500/10 border border-green-500/50 text-green-500 p-4 rounded-xl mb-8 text-center max-w-md mx-auto">
            {success} Yönlendiriliyorsunuz...
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          {/* FREE PLAN */}
          <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-3xl p-8 hover:bg-zinc-800/50 transition-all duration-300">
            <h2 className="text-2xl font-bold mb-2">Free</h2>
            <div className="text-4xl font-extrabold mb-6">
              $0<span className="text-lg text-zinc-500 font-normal">/ay</span>
            </div>
            <ul className="space-y-4 mb-8 text-zinc-300">
              <li className="flex items-center gap-3">
                <span className="text-zinc-500">✓</span> Günlük 5 Şarkı
              </li>
              <li className="flex items-center gap-3">
                <span className="text-zinc-500">✓</span> Günlük 10 AI Mesajı
              </li>
              <li className="flex items-center gap-3">
                <span className="text-zinc-500">✓</span> Günlük 5 Telaffuz Kaydı
              </li>
              <li className="flex items-center gap-3 opacity-50">
                <span className="text-zinc-700">✗</span> Sınırsız AI Koçluğu
              </li>
              <li className="flex items-center gap-3 opacity-50">
                <span className="text-zinc-700">✗</span> Detaylı Raporlar
              </li>
            </ul>
            <button
              className="w-full py-4 rounded-full font-bold bg-zinc-800 hover:bg-zinc-700 text-white transition-colors"
              disabled
            >
              Mevcut Planın
            </button>
          </div>

          {/* PRO PLAN */}
          <div className="bg-zinc-900/80 backdrop-blur-xl border-2 border-green-500 rounded-3xl p-8 transform md:scale-105 shadow-[0_0_40px_rgba(34,197,94,0.15)] relative">
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-green-500 text-black px-4 py-1 rounded-full text-sm font-bold">
              EN POPÜLER
            </div>
            <h2 className="text-2xl font-bold mb-2 text-green-400">Lingofy Pro</h2>
            <div className="text-4xl font-extrabold mb-6">
              $9.99<span className="text-lg text-zinc-500 font-normal">/ay</span>
            </div>
            <ul className="space-y-4 mb-8 text-zinc-200">
              <li className="flex items-center gap-3">
                <span className="text-green-500 font-bold">✓</span> Sınırsız Şarkı Analizi
              </li>
              <li className="flex items-center gap-3">
                <span className="text-green-500 font-bold">✓</span> Sınırsız AI Koçluğu
              </li>
              <li className="flex items-center gap-3">
                <span className="text-green-500 font-bold">✓</span> Sınırsız Telaffuz
              </li>
              <li className="flex items-center gap-3">
                <span className="text-green-500 font-bold">✓</span> 30 Günlük Gelişim Grafiği
              </li>
              <li className="flex items-center gap-3">
                <span className="text-green-500 font-bold">✓</span> Fonem Analizi
              </li>
            </ul>
            <button
              onClick={() => handleUpgrade("PRO")}
              disabled={loading}
              className="w-full py-4 rounded-full font-bold bg-green-500 hover:bg-green-400 text-black transition-colors"
            >
              {loading === "PRO" ? "Yükseltiliyor..." : "Pro'ya Geç"}
            </button>
          </div>

          {/* MASTER PLAN */}
          <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-3xl p-8 hover:bg-zinc-800/50 transition-all duration-300">
            <h2 className="text-2xl font-bold mb-2 text-purple-400">Lingofy Master</h2>
            <div className="text-4xl font-extrabold mb-6">
              $19.99<span className="text-lg text-zinc-500 font-normal">/ay</span>
            </div>
            <ul className="space-y-4 mb-8 text-zinc-300">
              <li className="flex items-center gap-3">
                <span className="text-purple-400 font-bold">✓</span> Pro'daki Her Şey
              </li>
              <li className="flex items-center gap-3">
                <span className="text-purple-400 font-bold">✓</span> IELTS/TOEFL Simülasyonu
              </li>
              <li className="flex items-center gap-3">
                <span className="text-purple-400 font-bold">✓</span> Native Seviyesinde IPA Analizi
              </li>
              <li className="flex items-center gap-3">
                <span className="text-purple-400 font-bold">✓</span> Haftalık PDF Raporu
              </li>
              <li className="flex items-center gap-3">
                <span className="text-purple-400 font-bold">✓</span> AI Mentor
              </li>
            </ul>
            <button
              onClick={() => handleUpgrade("MASTER")}
              disabled={loading}
              className="w-full py-4 rounded-full font-bold bg-zinc-100 hover:bg-white text-black transition-colors"
            >
              {loading === "MASTER" ? "Yükseltiliyor..." : "Master Ol"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
