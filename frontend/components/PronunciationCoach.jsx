"use client";

import React, { useState, useEffect } from "react";
import AudioVisualizer from "./AudioVisualizer";
import { api } from "../lib/api";
import { AudioRecorder } from "../lib/audioRecorder";
import { Mic, X, Check, Target as TargetIcon, Zap, Loader2, PlaySquare } from "lucide-react";
import { Card, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";

// Helper Circular Progress Component
const CircularProgress = ({ value, label, colorClass = "text-theme", strokeClass = "stroke-theme" }) => {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-20 h-20 flex items-center justify-center">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="6"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            strokeWidth="6"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`transition-all duration-1000 ease-out ${strokeClass}`}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className={`text-lg font-black ${colorClass}`}>{value}</span>
        </div>
      </div>
      <span className="text-xs text-white/40 font-bold mt-2 uppercase tracking-widest">{label}</span>
    </div>
  );
};

export default function PronunciationCoach({ expectedText, onClose }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recorder, setRecorder] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const r = new AudioRecorder();
    setRecorder(r);
    return () => {
      r.stop();
    };
  }, []);

  const handleToggleRecord = async () => {
    if (isRecording) {
      setIsRecording(false);
      setIsAnalyzing(true);
      setError(null);

      const audioBlob = await recorder.stop();
      if (!audioBlob) {
        setError("Kayıt alınamadı. Lütfen tekrar deneyin.");
        setIsAnalyzing(false);
        return;
      }

      try {
        console.log("================ API REQUEST START ================");
        console.log("Expected Text:", expectedText);
        console.log("Audio Blob Size:", audioBlob.size);
        
        const data = await api.analyzePronunciation(audioBlob, expectedText);
        
        console.log("================ FRONTEND PARSED JSON ================");
        console.log(data);
        console.log("======================================================");
        
        setResult(data);
      } catch (err) {
        console.error("================ API REQUEST ERROR ================");
        console.error(err);
        if (err.status === 403) {
          setError("Günlük telaffuz sınırınıza ulaştınız. Sınırsız koçluk için Lingofy Premium'a geçin!");
        } else {
          setError(err.message || "Analiz sırasında bir hata oluştu.");
        }
      } finally {
        setIsAnalyzing(false);
      }
    } else {
      const started = await recorder.start();
      if (started) {
        setIsRecording(true);
        setResult(null);
        setError(null);
      } else {
        setError("Mikrofona erişilemedi.");
      }
    }
  };

  // Safe fallback renderer for arrays
  const renderList = (items, emptyMsg = "Veri bulunamadı.") => {
    if (!Array.isArray(items) || items.length === 0) return <p className="text-[13px] opacity-60 m-0">{emptyMsg}</p>;
    return (
      <ul className="space-y-2.5 m-0 p-0 list-none">
        {items.map((item, idx) => (
          <li key={idx} className="flex items-start gap-2.5 text-[13px]">
            <span className="mt-1 w-1.5 h-1.5 rounded-full bg-current opacity-60 shrink-0"></span>
            <span className="opacity-90 leading-relaxed font-medium">{item}</span>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-xl p-4 overflow-y-auto animate-fade-in">
      <div className="w-full max-w-6xl my-auto bg-zinc-950/90 border border-white/10 rounded-3xl shadow-2xl flex flex-col overflow-hidden relative backdrop-blur-3xl animate-slide-up">
        
        {/* Glow Effects */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-theme-600/20 blur-[100px] pointer-events-none rounded-full"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-600/20 blur-[100px] pointer-events-none rounded-full"></div>

        {/* Header */}
        <div className="flex justify-between items-center px-8 py-6 border-b border-white/5 relative z-10 shrink-0">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/5 rounded-xl border border-white/5 shadow-sm">
              <Mic className="w-5 h-5 text-theme-300" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight m-0">
              AI Pronunciation Coach
            </h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full w-10 h-10">
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8 relative z-10 custom-scrollbar">
          
          {/* Top Section: Target Text & Recording */}
          <div className="flex flex-col items-center mb-12">
            <h3 className="text-theme-400 uppercase tracking-widest text-xs font-black mb-4">Hedef Cümle</h3>
            <p className="text-2xl md:text-4xl lg:text-5xl font-black text-white text-center leading-tight max-w-4xl drop-shadow-md tracking-tight m-0">
              "{expectedText}"
            </p>

            <div className="mt-12 flex flex-col items-center">
              <button
                onClick={handleToggleRecord}
                disabled={isAnalyzing}
                className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isRecording
                    ? "bg-red-500 scale-110 shadow-glow"
                    : isAnalyzing
                    ? "bg-white/5 cursor-not-allowed border border-white/10"
                    : "bg-theme hover:bg-theme-400 hover:scale-105 shadow-glow"
                }`}
              >
                {/* Pulse Rings */}
                {isRecording && (
                  <>
                    <div className="absolute inset-0 rounded-full border border-red-500 animate-ping opacity-75"></div>
                    <div className="absolute -inset-4 rounded-full border border-red-500/50 animate-ping opacity-50" style={{ animationDelay: "0.2s" }}></div>
                  </>
                )}

                {isAnalyzing ? (
                  <Loader2 className="w-8 h-8 text-white animate-spin" />
                ) : isRecording ? (
                  <div className="w-8 h-8 bg-white rounded-md"></div> // Stop Icon
                ) : (
                  <Mic className="w-10 h-10 text-white ml-0.5" />
                )}
              </button>
              
              <div className="mt-8 w-full max-w-md h-12">
                <AudioVisualizer isRecording={isRecording} color={isRecording ? "#ef4444" : "rgba(255,255,255,0.1)"} />
              </div>

              {error && (
                <div className="mt-6 flex flex-col items-center animate-fade-in">
                  <div className="bg-red-500/10 px-5 py-3 rounded-xl border border-red-500/20 text-center">
                    <p className="text-red-400 text-sm font-semibold m-0">{error}</p>
                  </div>
                  {error.includes("Premium") && (
                    <Button onClick={() => window.location.href="/pricing"} variant="primary" className="mt-4 rounded-full px-6">
                      Planı Yükselt
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Results Analysis */}
          {result && !error && (
            <div className="animate-fade-in space-y-8 border-t border-white/5 pt-10">
              
              <div className="flex flex-col lg:flex-row gap-8">
                {/* Left Side: Technical Scores */}
                <div className="flex-1 space-y-8">
                  {/* Score Cards Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="relative overflow-hidden group border-white/5 bg-white/5">
                      <div className="absolute inset-0 bg-theme-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      <CardContent className="p-5">
                        <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-2 m-0">Overall</p>
                        <p className={`text-4xl font-black m-0 ${result.overall_score >= 80 ? 'text-theme-400' : 'text-yellow-400'}`}>
                          {result.overall_score}
                        </p>
                      </CardContent>
                    </Card>
                    <Card className="relative overflow-hidden group border-white/5 bg-white/5">
                      <CardContent className="p-5">
                        <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-2 m-0">Accuracy</p>
                        <p className="text-4xl font-black text-white m-0">{result.accuracy}%</p>
                      </CardContent>
                    </Card>
                    <Card className="relative overflow-hidden group border-white/5 bg-white/5">
                      <CardContent className="p-5">
                        <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-2 m-0">Fluency</p>
                        <p className="text-4xl font-black text-white m-0">{result.fluency}%</p>
                      </CardContent>
                    </Card>
                    <Card className="relative overflow-hidden group border-white/5 bg-white/5">
                      <CardContent className="p-5">
                        <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-2 m-0">CEFR</p>
                        <p className="text-4xl font-black text-purple-400 m-0">{result.cefr_level}</p>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Circular Detailed Metrics */}
                  <Card className="border-white/5 bg-white/5">
                    <CardContent className="p-6 md:p-8">
                      <h3 className="text-white font-bold mb-8 flex items-center gap-2 m-0 text-base">
                        <TargetIcon className="w-5 h-5 text-theme-400" />
                        Teknik Detaylar
                      </h3>
                      <div className="flex flex-wrap justify-around items-center gap-6">
                        <CircularProgress value={result.rhythm} label="Ritim" colorClass="text-blue-400" strokeClass="stroke-blue-400" />
                        <CircularProgress value={result.stress} label="Vurgu" colorClass="text-purple-400" strokeClass="stroke-purple-400" />
                        <CircularProgress value={result.intonation} label="Tonlama" colorClass="text-pink-400" strokeClass="stroke-pink-400" />
                        <CircularProgress value={result.confidence} label="Güven" colorClass="text-yellow-400" strokeClass="stroke-yellow-400" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Word Analysis Table */}
                  <Card className="border-white/5 bg-white/5 overflow-hidden">
                    <div className="px-6 py-5 border-b border-white/5 bg-white/[0.02]">
                      <h3 className="text-white font-bold flex items-center gap-2 m-0 text-base">
                        <PlaySquare className="w-5 h-5 text-theme-400" />
                        Kelime Bazlı Analiz
                      </h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="text-white/30 uppercase tracking-wider border-b border-white/5 text-[10px] font-black">
                            <th className="px-6 py-4">Kelime</th>
                            <th className="px-6 py-4">Durum</th>
                            <th className="px-6 py-4">IPA (Hata)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {result.words.map((w, i) => (
                            <tr key={i} className="hover:bg-white/5 transition-colors group">
                              <td className="px-6 py-4 font-bold text-white text-[15px]">{w.word}</td>
                              <td className="px-6 py-4">
                                <span className={`px-3 py-1.5 rounded-md text-[11px] font-bold border ${
                                  w.status === "correct" ? "bg-theme-500/10 text-theme-400 border-theme-500/20" :
                                  w.status === "close" ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" :
                                  "bg-red-500/10 text-red-400 border-red-500/20"
                                }`}>
                                  {w.status === "correct" ? "Doğru" : w.status === "close" ? "Yakın" : "Yanlış"}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-white/40 font-mono text-xs">{w.ipa || "-"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </Card>

                </div>

                {/* Right Side: AI Coach Panel */}
                <div className="w-full lg:w-[450px] shrink-0 bg-gradient-to-br from-theme-900/30 to-purple-900/20 border border-theme-500/30 rounded-2xl shadow-xl flex flex-col p-1 relative overflow-hidden">
                  <div className="absolute inset-0 bg-noise opacity-[0.03]"></div>
                  
                  <div className="flex items-center gap-4 mb-4 sticky top-0 bg-black/40 backdrop-blur-md z-10 p-4 rounded-xl border border-white/5 mx-1 mt-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-theme-500 to-purple-600 rounded-xl flex items-center justify-center text-xl shadow-glow border border-white/20 shrink-0">
                      ✨
                    </div>
                    <div>
                      <h3 className="text-white font-bold m-0 text-base">Lingofy AI Coach</h3>
                      <p className="text-theme-300 text-xs font-semibold m-0 mt-0.5">Akıllı & Kişisel Öğretmen</p>
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-6 p-5">
                    
                    {/* Genel Değerlendirme (Summary) */}
                    <div>
                      <h4 className="text-[10px] font-black text-theme-400 uppercase tracking-widest mb-3 m-0">Genel Değerlendirme</h4>
                      <div className="text-white/80 text-[14px] leading-relaxed bg-black/40 p-5 rounded-2xl border border-white/5 shadow-inner font-medium">
                        {result.summary}
                      </div>
                    </div>

                    {/* Güçlü Yönler & Geliştirilecek Alanlar (Strengths/Weaknesses) */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-theme-500/10 border border-theme-500/20 p-4.5 rounded-2xl">
                        <h4 className="text-[10px] font-black text-theme-400 uppercase tracking-widest mb-3 m-0">Güçlü Yönler</h4>
                        <div className="text-theme-100">
                          {renderList(result.strengths, "Belirgin güçlü yön yok.")}
                        </div>
                      </div>
                      <div className="bg-red-500/10 border border-red-500/20 p-4.5 rounded-2xl">
                        <h4 className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-3 m-0">Geliştirilecek</h4>
                        <div className="text-red-100">
                          {renderList(result.weaknesses, "Geliştirilecek alan bulunmadı.")}
                        </div>
                      </div>
                    </div>

                    {/* Öneriler (Suggestions) */}
                    <div>
                      <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-3 m-0">Pratik Önerileri</h4>
                      <div className="bg-black/40 p-5 rounded-2xl border border-white/5 shadow-inner text-blue-100">
                        {renderList(result.suggestions, "Öneri bulunamadı.")}
                      </div>
                    </div>

                    {/* Sonraki Hedef (Next Goal) & Motivasyon (Motivation) */}
                    <div className="grid grid-cols-1 gap-4 mt-8">
                      <div className="flex items-start gap-4 bg-yellow-500/10 border border-yellow-500/20 p-5 rounded-2xl">
                        <div className="text-2xl shrink-0 mt-0.5">🎯</div>
                        <div>
                          <h4 className="text-[10px] font-black text-yellow-500 uppercase tracking-widest mb-1.5 m-0">Bir Sonraki Hedef</h4>
                          <p className="text-[14px] font-bold text-yellow-100/90 leading-snug m-0">{result.next_goal}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-start gap-4 bg-purple-500/10 border border-purple-500/20 p-5 rounded-2xl">
                        <div className="text-2xl shrink-0 mt-0.5">💡</div>
                        <div>
                          <h4 className="text-[10px] font-black text-purple-400 uppercase tracking-widest mb-1.5 m-0">AI Insight</h4>
                          <p className="text-[14px] font-semibold text-purple-100/90 leading-snug m-0">"{result.insight}"</p>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
